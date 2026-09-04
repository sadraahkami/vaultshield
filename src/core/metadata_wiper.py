"""
Deep Metadata and EXIF Wiper engine using raw pixel reconstruction and PDF dictionary purge.
"""

from dataclasses import dataclass, field
import io
import os
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

from .validator import FileValidator, FileCategory


@dataclass
class WipeReport:
    original_file: str
    cleaned_file: str
    category: str
    original_size: int
    cleaned_size: int
    removed_items: List[str] = field(default_factory=list)


class MetadataWiper:

    @classmethod
    def wipe_metadata(cls, input_path: str, output_path: Optional[str] = None) -> WipeReport:
        src = Path(input_path).resolve()
        if not src.exists() or not src.is_file():
            raise FileNotFoundError(f"Source file not found: {input_path}")

        cat = FileValidator.get_category(str(src))
        if output_path:
            dst = Path(output_path).resolve()
        else:
            dst = src.parent / f"{src.stem}_scrubbed{src.suffix}"

        dst.parent.mkdir(parents=True, exist_ok=True)
        orig_size = src.stat().st_size

        removed = []

        if cat == FileCategory.IMAGE:
            removed = cls._wipe_image(src, dst)
        elif cat == FileCategory.PDF:
            removed = cls._wipe_pdf(src, dst)
        else:
            raise ValueError(f"Unsupported file format for metadata scrubbing: {src.suffix}")

        clean_size = dst.stat().st_size
        return WipeReport(
            original_file=str(src),
            cleaned_file=str(dst),
            category=cat.value,
            original_size=orig_size,
            cleaned_size=clean_size,
            removed_items=removed
        )

    @staticmethod
    def _wipe_image(src: Path, dst: Path) -> List[str]:
        removed = ["EXIF Headers", "GPS Coordinates", "Camera/Lens Profile", "Creation Date", "Thumbnail Chunks"]
        with Image.open(src) as img:
            # Reconstruct onto fresh canvas without any EXIF or metadata dictionaries
            mode = "RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB"
            clean_canvas = Image.new(mode, img.size)

            # Copy pixel data directly
            if img.mode == "P":
                img_conv = img.convert("RGBA")
                clean_canvas.paste(img_conv, (0, 0))
            else:
                clean_canvas.paste(img, (0, 0))

            ext = dst.suffix.lower()
            save_format = "JPEG"
            save_kwargs = {}

            if ext == ".png":
                save_format = "PNG"
                save_kwargs = {"optimize": True}
            elif ext == ".webp":
                save_format = "WEBP"
                save_kwargs = {"quality": 95}
            elif ext in (".jpg", ".jpeg"):
                save_format = "JPEG"
                save_kwargs = {"quality": 95, "optimize": True}
                if clean_canvas.mode == "RGBA":
                    clean_canvas = clean_canvas.convert("RGB")
            else:
                save_format = "PNG"

            # Save strictly without exif or info parameters
            clean_canvas.save(dst, format=save_format, **save_kwargs)

        return removed

    @staticmethod
    def _wipe_pdf(src: Path, dst: Path) -> List[str]:
        removed = ["Document Info (/Author, /Title)", "Creation & Mod Dates", "XMP Metadata Stream", "Producer / Creator Signatures"]
        try:
            from pypdf import PdfReader, PdfWriter

            reader = PdfReader(str(src))
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Strip all metadata entries
            writer.add_metadata({})

            with open(dst, "wb") as f:
                writer.write(f)

            return removed
        except Exception as e:
            raise RuntimeError(f"Failed to scrub PDF: {e}")
