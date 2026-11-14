"""
Master Test Runner for ALS SubZero.
Developed by Samin Sami.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).

Executes all unit, integration, and flight persistence tests.
"""

import os
import sys
import unittest

# Ensure src is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
