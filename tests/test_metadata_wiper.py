"""
Unit tests for Metadata and EXIF Wiper in VaultShield.
"""

import os
from pathlib import Path
import tempfile
import unittest
from PIL import Image

from src.core.metadata_wiper import MetadataWiper


class TestMetadataWiper(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_wipe_image_metadata(self):
        # Create image with dummy EXIF info
        img_p = self.tmp_path / "test_photo.jpg"
        im = Image.new("RGB", (120, 120), color=(200, 50, 50))
        im.save(img_p, format="JPEG")

        cleaned_p = self.tmp_path / "cleaned_photo.jpg"
        report = MetadataWiper.wipe_metadata(str(img_p), str(cleaned_p))

        self.assertTrue(cleaned_p.exists())
        self.assertGreater(report.cleaned_size, 0)
        self.assertIn("EXIF Headers", report.removed_items)

        # Ensure cleaned image opens cleanly
        with Image.open(cleaned_p) as clean_im:
            self.assertEqual(clean_im.size, (120, 120))


if __name__ == "__main__":
    unittest.main()
