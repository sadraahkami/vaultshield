"""
Military-Grade Steganography Vault using AES-256-GCM Authenticated Encryption and LSB Injection.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import struct
from typing import Optional, Tuple
from PIL import Image

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

MAGIC_HEADER = b"VLT1"
PBKDF2_ITERATIONS = 100_000


@dataclass
class StegoPayload:
    is_file: bool
    filename: str
    data: bytes

    @property
    def text(self) -> str:
        try:
            return self.data.decode("utf-8")
        except Exception:
            return f"<Binary data: {len(self.data)} bytes>"


class SteganographyVault:

    @classmethod
    def _derive_key(cls, passphrase: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS
        )
        return kdf.derive(passphrase.encode("utf-8"))

    @classmethod
    def hide_payload(
        cls,
        carrier_image_path: str,
        output_image_path: str,
        passphrase: str,
        secret_data: bytes,
        is_file: bool = False,
        filename: str = ""
    ) -> bool:
        if not passphrase:
            raise ValueError("Passphrase cannot be empty.")

        carrier_p = Path(carrier_image_path).resolve()
        out_p = Path(output_image_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        # 1. Prepare and serialize payload
        clean_fn = Path(filename).name if filename else ""
        fn_bytes = clean_fn.encode("utf-8")[:255]
        fn_len = len(fn_bytes)

        raw_payload = struct.pack(f"?B{fn_len}s", is_file, fn_len, fn_bytes) + secret_data

        # 2. Encrypt using AES-256-GCM
        salt = os.urandom(16)
        key = cls._derive_key(passphrase, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, raw_payload, None)

        # 3. Build binary envelope: [4B Magic] + [16B Salt] + [12B Nonce] + [4B Length] + [Ciphertext]
        envelope = (
            MAGIC_HEADER +
            salt +
            nonce +
            struct.pack(">I", len(ciphertext)) +
            ciphertext
        )

        total_bits_needed = len(envelope) * 8

        # 4. Open carrier image and check capacity
        with Image.open(carrier_p) as img:
            rgb_img = img.convert("RGB")
            w, h = rgb_img.size
            raw_bytes = bytearray(rgb_img.tobytes())

        if total_bits_needed > len(raw_bytes):
            raise ValueError(
                f"Payload too large for this image. Needs {len(envelope)} bytes, "
                f"but carrier only has capacity for {len(raw_bytes) // 8} bytes."
            )

        # 5. Embed bits into LSB of raw channel bytes
        bit_idx = 0
        for byte in envelope:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                raw_bytes[bit_idx] = (raw_bytes[bit_idx] & ~1) | bit
                bit_idx += 1

        # 6. Save as lossless PNG
        stego_img = Image.frombytes("RGB", (w, h), bytes(raw_bytes))
        stego_img.save(out_p, format="PNG", optimize=True)

        return out_p.exists()

    @classmethod
    def extract_payload(cls, stego_image_path: str, passphrase: str) -> StegoPayload:
        if not passphrase:
            raise ValueError("Passphrase cannot be empty.")

        src_p = Path(stego_image_path).resolve()
        if not src_p.exists():
            raise FileNotFoundError(f"Stego image not found: {stego_image_path}")

        with Image.open(src_p) as img:
            rgb_img = img.convert("RGB")
            raw_bytes = rgb_img.tobytes()

        # Helper function to read N bytes from the bitstream starting at bit_offset
        def read_bytes(bit_offset: int, num_bytes: int) -> Tuple[bytes, int]:
            byte_arr = bytearray()
            for b_i in range(num_bytes):
                byte_val = 0
                for bit_pos in range(8):
                    idx = bit_offset + b_i * 8 + bit_pos
                    if idx >= len(raw_bytes):
                        raise ValueError("Unexpected end of carrier bitstream.")
                    byte_val = (byte_val << 1) | (raw_bytes[idx] & 1)
                byte_arr.append(byte_val)
            return bytes(byte_arr), bit_offset + num_bytes * 8

        # 1. Read Magic Header
        offset = 0
        magic, offset = read_bytes(offset, len(MAGIC_HEADER))
        if magic != MAGIC_HEADER:
            raise ValueError("No VaultShield hidden payload detected in this image.")

        # 2. Read Salt (16B) & Nonce (12B) & Length (4B)
        salt, offset = read_bytes(offset, 16)
        nonce, offset = read_bytes(offset, 12)
        len_bytes, offset = read_bytes(offset, 4)
        ciphertext_len = struct.unpack(">I", len_bytes)[0]

        if ciphertext_len <= 0 or ciphertext_len > (len(raw_bytes) // 8):
            raise ValueError("Corrupted payload metadata length.")

        # 3. Read Ciphertext
        ciphertext, offset = read_bytes(offset, ciphertext_len)

        # 4. Decrypt AES-256-GCM
        try:
            key = cls._derive_key(passphrase, salt)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise ValueError("Decryption failed. Incorrect passphrase or altered image.")

        # 5. Unpack payload metadata
        is_file, fn_len = struct.unpack("?B", plaintext[:2])
        filename = plaintext[2:2 + fn_len].decode("utf-8", errors="replace")
        actual_data = plaintext[2 + fn_len:]

        return StegoPayload(is_file=is_file, filename=filename, data=actual_data)
