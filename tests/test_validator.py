"""
Unit tests for FileValidator in VaultShield.
"""

from pathlib import Path
import tempfile
import unittest
from PIL import Image

from src.core.validator import FileValidator, FileCategory


class TestFileValidator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_category_detection(self):
        self.assertEqual(FileValidator.get_category("photo.jpg"), FileCategory.IMAGE)
        self.assertEqual(FileValidator.get_category("image.png"), FileCategory.IMAGE)
        self.assertEqual(FileValidator.get_category("doc.pdf"), FileCategory.PDF)
        self.assertEqual(FileValidator.get_category("notes.txt"), FileCategory.OTHER)

    def test_stego_capacity(self):
        carrier = self.tmp_path / "test.png"
        img = Image.new("RGB", (100, 100))  # 10,000 pixels * 3 channels / 8 = 3750 bytes - 64 = 3686
        img.save(carrier, format="PNG")

        capacity = FileValidator.get_stego_capacity_bytes(str(carrier))
        self.assertGreater(capacity, 3000)
        self.assertTrue(FileValidator.is_valid_carrier_image(str(carrier)))


if __name__ == "__main__":
    unittest.main()
