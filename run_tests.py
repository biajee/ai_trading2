#!/usr/bin/env python3
"""Test runner for AI Trading Arena"""
import unittest
import sys
import os

def run_all_tests():
    """Run all unit tests and display results"""
    print("="*70)
    print("AI Trading Arena - Test Suite")
    print("="*70)
    print()

    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    # Return 0 if all tests passed, 1 otherwise
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run tests from a specific module"""
    print(f"Running tests from: {test_module}")
    print("="*70)
    print()

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    # Clean up any test artifacts
    if os.path.exists('arena_state.json'):
        os.remove('arena_state.json')

    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        sys.exit(run_specific_test(test_module))
    else:
        # Run all tests
        sys.exit(run_all_tests())
