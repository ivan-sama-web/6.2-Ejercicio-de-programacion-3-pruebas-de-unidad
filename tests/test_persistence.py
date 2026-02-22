"""Unit tests for reservation_system.persistence.

Covers load/save of JSON files, including corrupt and missing files.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from reservation_system.persistence import load_json, save_json


class TestLoadJson(unittest.TestCase):
    """Tests for load_json."""

    def test_load_missing_file(self) -> None:
        """Missing file returns an empty list."""
        result = load_json("/tmp/nonexistent_file_xyz.json")
        self.assertEqual(result, [])

    def test_load_valid_file(self) -> None:
        """Valid JSON list is returned as-is."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump([{"a": 1}], tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(load_json(tmp_path), [{"a": 1}])
        finally:
            os.unlink(tmp_path)

    def test_load_corrupt_json(self) -> None:
        """Corrupt JSON returns empty list with warning."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            tmp.write("{broken json!!")
            tmp_path = tmp.name
        try:
            self.assertEqual(load_json(tmp_path), [])
        finally:
            os.unlink(tmp_path)

    def test_load_non_list_json(self) -> None:
        """JSON dict (not list) returns empty list."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump({"not": "a list"}, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(load_json(tmp_path), [])
        finally:
            os.unlink(tmp_path)


class TestSaveJson(unittest.TestCase):
    """Tests for save_json."""

    def test_save_and_read_back(self) -> None:
        """Saved data should be loadable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "data.json")
            save_json(path, [{"key": "value"}])
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data, [{"key": "value"}])

    def test_save_creates_directory(self) -> None:
        """save_json creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "a", "b", "c.json")
            save_json(path, [])
            self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main()
