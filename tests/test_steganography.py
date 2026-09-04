"""
Unit tests for AES-256-GCM LSB Steganography in VaultShield.
"""

from pathlib import Path
import tempfile
import unittest
from PIL import Image

from src.core.steganography import SteganographyVault


class TestSteganography(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

        # Create carrier image (200x200 RGB has 120,000 bits = ~15 KB capacity)
        self.carrier_p = self.tmp_path / "carrier.png"
        img = Image.new("RGB", (200, 200), color=(100, 150, 200))
        img.save(self.carrier_p, format="PNG")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_hide_and_extract_text(self):
        stego_p = self.tmp_path / "stego.png"
        secret_msg = "Top-Secret Cryptographic Message: 12345"
        passphrase = "UltraStrongPassword#2026"

        success = SteganographyVault.hide_payload(
            carrier_image_path=str(self.carrier_p),
            output_image_path=str(stego_p),
            passphrase=passphrase,
            secret_data=secret_msg.encode("utf-8"),
            is_file=False
        )
        self.assertTrue(success)
        self.assertTrue(stego_p.exists())

        # Extract with correct password
        extracted = SteganographyVault.extract_payload(str(stego_p), passphrase)
        self.assertFalse(extracted.is_file)
        self.assertEqual(extracted.text, secret_msg)

    def test_extract_with_wrong_password_fails(self):
        stego_p = self.tmp_path / "stego_wrong.png"
        secret_msg = "Classified intelligence"
        passphrase = "CorrectPassword123"

        SteganographyVault.hide_payload(
            carrier_image_path=str(self.carrier_p),
            output_image_path=str(stego_p),
            passphrase=passphrase,
            secret_data=secret_msg.encode("utf-8")
        )

        with self.assertRaises(ValueError):
            # Wrong password should fail AES-GCM decryption
            SteganographyVault.extract_payload(str(stego_p), "WrongPassword999")


if __name__ == "__main__":
    unittest.main()
