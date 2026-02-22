"""Unit tests for reservation_system.generate_sample_data.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest import mock

from reservation_system import generate_sample_data


class TestGenerateSampleData(unittest.TestCase):
    """Tests for the generate() and main() functions."""

    def test_generate_creates_files(self) -> None:
        """generate() creates three JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "data")
            with mock.patch.object(
                generate_sample_data, "SAMPLE_DIR", target,
            ):
                generate_sample_data.generate()
            for filename in (
                "hotels.json",
                "customers.json",
                "reservations.json",
            ):
                path = os.path.join(target, filename)
                self.assertTrue(os.path.isfile(path))
                with open(path, encoding="utf-8") as fh:
                    data = json.load(fh)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)

    def test_main_function(self) -> None:
        """main() entry point calls generate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "data")
            with mock.patch.object(
                generate_sample_data, "SAMPLE_DIR", target,
            ):
                generate_sample_data.main()
            self.assertTrue(
                os.path.isfile(
                    os.path.join(target, "hotels.json"),
                )
            )


if __name__ == "__main__":
    unittest.main()
