"""
Command-Line Interface (CLI) runner for VaultShield.
"""

import argparse
import os
from pathlib import Path
import sys
from typing import List

from ..core.metadata_wiper import MetadataWiper
from ..core.steganography import SteganographyVault
from ..core.shredder import FileShredder


def run_cli(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="vaultshield",
        description="VaultShield - Deep Metadata Wiper, AES-256 Steganography & DoD File Shredder"
    )

    subparsers = parser.add_subparsers(dest="command", help="Security operations")

    # Command 1: Wipe
    p_wipe = subparsers.add_parser("wipe", help="Scrub EXIF and metadata from image or PDF")
    p_wipe.add_argument("file", help="File to scrub")
    p_wipe.add_argument("-o", "--output", help="Output file path (default: <filename>_scrubbed.<ext>)")

    # Command 2: Hide
    p_hide = subparsers.add_parser("hide", help="Invisibly embed encrypted payload into PNG/BMP image")
    p_hide.add_argument("carrier", help="Cover image path (PNG or BMP)")
    p_hide.add_argument("-p", "--passphrase", required=True, help="AES-256-GCM encryption passphrase")
    p_hide.add_argument("-m", "--message", help="Confidential text message to embed")
    p_hide.add_argument("-f", "--file", help="Confidential file to embed")
    p_hide.add_argument("-o", "--output", default="stego_vault.png", help="Output stego image path")

    # Command 3: Extract
    p_ext = subparsers.add_parser("extract", help="Extract and decrypt hidden payload from stego image")
    p_ext.add_argument("stego", help="Stego image path (PNG)")
    p_ext.add_argument("-p", "--passphrase", required=True, help="Decryption passphrase")
    p_ext.add_argument("-o", "--output", help="Output file path if payload was an embedded file")

    # Command 4: Shred
    p_shred = subparsers.add_parser("shred", help="Permanently destroy file with multi-pass DoD overwrite")
    p_shred.add_argument("file", help="File to destroy")
    p_shred.add_argument("--passes", type=int, choices=[1, 3, 7], default=3, help="Overwrite passes (default: 3 DoD)")
    p_shred.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 1

    try:
        if parsed.command == "wipe":
            report = MetadataWiper.wipe_metadata(parsed.file, parsed.output)
            print(f"[+] Metadata scrubbed successfully!")
            print(f"    Output: {report.cleaned_file}")
            print(f"    Purged: {', '.join(report.removed_items)}")

        elif parsed.command == "hide":
            if parsed.file:
                fp = Path(parsed.file).resolve()
                if not fp.exists():
                    print(f"[Error] Secret file not found: {parsed.file}", file=sys.stderr)
                    return 1
                with open(fp, "rb") as f:
                    secret_bytes = f.read()
                is_file = True
                fn = fp.name
            elif parsed.message:
                secret_bytes = parsed.message.encode("utf-8")
                is_file = False
                fn = ""
            else:
                print("[Error] Either -m (message) or -f (file) must be provided.", file=sys.stderr)
                return 1

            SteganographyVault.hide_payload(
                carrier_image_path=parsed.carrier,
                output_image_path=parsed.output,
                passphrase=parsed.passphrase,
                secret_data=secret_bytes,
                is_file=is_file,
                filename=fn
            )
            print(f"[+] Secret encrypted with AES-256-GCM and embedded into: {parsed.output}")

        elif parsed.command == "extract":
            payload = SteganographyVault.extract_payload(parsed.stego, parsed.passphrase)
            if payload.is_file:
                out_fn = parsed.output or payload.filename or "extracted_file.bin"
                with open(out_fn, "wb") as f:
                    f.write(payload.data)
                print(f"[+] Extracted decrypted file saved to: {out_fn}")
            else:
                print(f"[+] Decrypted Secret Message:")
                print(payload.text)

        elif parsed.command == "shred":
            if not parsed.yes:
                ans = input(f"Are you sure you want to PERMANENTLY destroy '{parsed.file}'? (y/N): ")
                if ans.strip().lower() != "y":
                    print("Aborted.")
                    return 0

            report = FileShredder.shred_file(parsed.file, passes=parsed.passes)
            if report.success:
                print(f"[+] File permanently destroyed in {report.duration_seconds}s ({report.passes_completed} passes).")
            else:
                print(f"[Error] Failed to shred file.", file=sys.stderr)
                return 1

    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        return 1

    return 0
