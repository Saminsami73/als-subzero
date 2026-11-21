# master test runner for als subzero
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    run = unittest.TextTestRunner(verbosity=2)
    result = run.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)