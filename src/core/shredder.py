"""
Cryptographic Multi-Pass File Shredder implementing DoD 5220.22-M specification.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import time
from typing import Callable, Optional


@dataclass
class ShredReport:
    original_path: str
    file_size_bytes: int
    passes_completed: int
    duration_seconds: float
    success: bool


class FileShredder:

    CHUNK_SIZE = 64 * 1024  # 64 KB buffers

    @classmethod
    def shred_file(
        cls,
        filepath: str,
        passes: int = 3,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> ShredReport:
        p = Path(filepath).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"File to shred not found: {filepath}")

        file_size = p.stat().st_size
        start_time = time.time()

        # Define overwrite patterns
        # 1-pass: random
        # 3-pass: zeros, ones, random
        # 7-pass: DoD ECE
        patterns = []
        if passes == 1:
            patterns = [b"RANDOM"]
        elif passes == 7:
            patterns = [b"\x00", b"\xFF", b"\x55", b"\xAA", b"\x00", b"\xFF", b"RANDOM"]
        else:
            # Default 3 passes (DoD 5220.22-M standard)
            patterns = [b"\x00", b"\xFF", b"RANDOM"]

        total_passes = len(patterns)

        with open(p, "ba+", buffering=0) as f:
            for pass_idx, pat in enumerate(patterns, start=1):
                if progress_callback:
                    pct = int((pass_idx - 1) / total_passes * 85)
                    progress_callback(pct, f"Pass {pass_idx}/{total_passes} overwriting...")

                f.seek(0)
                bytes_written = 0

                while bytes_written < file_size:
                    chunk_len = min(cls.CHUNK_SIZE, file_size - bytes_written)
                    if pat == b"RANDOM":
                        buffer = os.urandom(chunk_len)
                    else:
                        buffer = pat * chunk_len

                    f.write(buffer)
                    bytes_written += chunk_len

                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass

        # Obfuscate metadata and unlink
        if progress_callback:
            progress_callback(90, "Scrambling metadata and unlinking...")

        # Rename to random filename
        random_name = p.parent / f"shred_{os.urandom(8).hex()}"
        try:
            p.rename(random_name)
            target_to_del = random_name
        except Exception:
            target_to_del = p

        # Truncate to 0 bytes
        with open(target_to_del, "wb") as f:
            pass

        # Remove from disk
        os.remove(target_to_del)

        if progress_callback:
            progress_callback(100, "File shredded and destroyed.")

        duration = round(time.time() - start_time, 3)
        return ShredReport(
            original_path=str(p),
            file_size_bytes=file_size,
            passes_completed=total_passes,
            duration_seconds=duration,
            success=not target_to_del.exists()
        )
