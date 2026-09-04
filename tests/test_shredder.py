"""
Unit tests for DoD 5220.22-M Multi-Pass Shredder in VaultShield.
"""

from pathlib import Path
import tempfile
import unittest

from src.core.shredder import FileShredder


class TestFileShredder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_shred_file(self):
        secret_file = self.tmp_path / "financial_records.csv"
        with open(secret_file, "wb") as f:
            f.write(b"Account,Balance,SSN\n123456,1000000,999-00-1234\n" * 50)

        self.assertTrue(secret_file.exists())
        orig_size = secret_file.stat().st_size

        report = FileShredder.shred_file(str(secret_file), passes=3)

        self.assertTrue(report.success)
        self.assertEqual(report.file_size_bytes, orig_size)
        self.assertEqual(report.passes_completed, 3)
        self.assertFalse(secret_file.exists())


if __name__ == "__main__":
    unittest.main()
