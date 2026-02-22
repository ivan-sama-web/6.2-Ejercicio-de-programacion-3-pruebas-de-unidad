#!/usr/bin/env python3
"""Cross-platform test runner for the Hotel Reservation System.

Usage::

    python run_tests.py          # run all tests
    python run_tests.py -v       # verbose output

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import sys
import os
import unittest


def main() -> None:
    """Discover and run all tests from the project root."""
    # Ensure the project root is on sys.path so that both
    # ``reservation_system`` and ``tests`` are importable.
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    verbosity = 2 if "-v" in sys.argv else 1

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir="tests",
        pattern="test_*.py",
        top_level_dir=project_root,
    )

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
