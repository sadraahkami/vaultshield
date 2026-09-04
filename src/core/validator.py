"""
File validator and steganography capacity calculator for VaultShield.
"""

from enum import Enum
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
STEGO_CARRIER_EXTENSIONS = {".png", ".bmp"}
DOC_EXTENSIONS = {".pdf"}


class FileCategory(Enum):
    IMAGE = "image"
    PDF = "pdf"
    OTHER = "other"


class FileValidator:

    @staticmethod
    def get_category(filepath: str) -> FileCategory:
        ext = Path(filepath).suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            return FileCategory.IMAGE
        elif ext in DOC_EXTENSIONS:
            return FileCategory.PDF
        return FileCategory.OTHER

    @staticmethod
    def is_valid_carrier_image(filepath: str) -> bool:
        ext = Path(filepath).suffix.lower()
        if ext not in STEGO_CARRIER_EXTENSIONS:
            return False
        try:
            with Image.open(filepath) as img:
                return img.size[0] > 0 and img.size[1] > 0
        except Exception:
            return False

    @staticmethod
    def get_stego_capacity_bytes(filepath: str) -> int:
        """
        Calculates maximum embeddable bytes using 1 LSB per RGB channel (minus 64 bytes header).
        """
        try:
            with Image.open(filepath) as img:
                rgb_img = img.convert("RGB")
                w, h = rgb_img.size
                total_bits = w * h * 3
                total_bytes = total_bits // 8
                return max(0, total_bytes - 64)
        except Exception:
            return 0
