#!/usr/bin/env python3
"""
Test Runner for SmartLib Manager

This script runs all tests for the library management system and provides
a comprehensive test report.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all test suites and generate a comprehensive report."""
    print("="*60)
    print("SMARTLIB MANAGER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Discover and load all test modules
    test_modules = []
    
    # Try to import test modules
    try:
        from test_app import (
            AuthenticationTests,
            DashboardTests,
            BookManagementTests,
            BorrowingTests,
            QRCodeTests,
            DatabaseTests
        )
        test_modules.extend([
            ('Authentication Tests', AuthenticationTests),
            ('Dashboard Tests', DashboardTests),
            ('Book Management Tests', BookManagementTests),
            ('Borrowing Tests', BorrowingTests),
            ('QR Code Tests', QRCodeTests),
            ('Database Tests', DatabaseTests)
        ])
        print("✓ Loaded unit test modules")
    except ImportError as e:
        print(f"⚠ Could not load unit test modules: {e}")
    
    try:
        from test_integration import IntegrationTestCase
        test_modules.append(('Integration Tests', IntegrationTestCase))
        print("✓ Loaded integration test modules")
    except ImportError as e:
        print(f"⚠ Could not load integration test modules: {e}")
    
    if not test_modules:
        print("❌ No test modules found!")
        return False
    
    print(f"\nFound {len(test_modules)} test suites")
    print()
    
    # Run each test suite
    total_tests = 0
    total_failures = 0
    total_errors = 0
    suite_results = []
    
    for suite_name, test_class in test_modules:
        print(f"Running {suite_name}...")
        print("-" * 40)
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        # Capture test output
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            buffer=True
        )
        
        # Run tests
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Calculate results
        suite_tests = result.testsRun
        suite_failures = len(result.failures)
        suite_errors = len(result.errors)
        suite_success = suite_tests - suite_failures - suite_errors
        suite_time = end_time - start_time
        
        # Update totals
        total_tests += suite_tests
        total_failures += suite_failures
        total_errors += suite_errors
        
        # Store results
        suite_results.append({
            'name': suite_name,
            'tests': suite_tests,
            'failures': suite_failures,
            'errors': suite_errors,
            'success': suite_success,
            'time': suite_time,
            'output': stream.getvalue()
        })
        
        # Print summary for this suite
        if suite_failures == 0 and suite_errors == 0:
            status = "✓ PASSED"
        else:
            status = "❌ FAILED"
        
        print(f"{status} - {suite_success}/{suite_tests} tests passed ({suite_time:.2f}s)")
        
        # Print failures and errors if any
        if suite_failures > 0:
            print(f"\nFailures in {suite_name}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if suite_errors > 0:
            print(f"\nErrors in {suite_name}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
        
        print()
    
    # Print comprehensive summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_success = total_tests - total_failures - total_errors
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful: {total_success}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Detailed breakdown by suite
    print("DETAILED BREAKDOWN:")
    print("-" * 40)
    for result in suite_results:
        status = "PASS" if result['failures'] == 0 and result['errors'] == 0 else "FAIL"
        print(f"{result['name']:<25} {status:<6} {result['success']}/{result['tests']:<8} ({result['time']:.2f}s)")
    
    print()
    
    # Overall result
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALL TESTS PASSED!")
        overall_success = True
    else:
        print("❌ SOME TESTS FAILED")
        overall_success = False
    
    print(f"\nCompleted at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return overall_success

def run_specific_test(test_name):
    """Run a specific test suite."""
    test_mapping = {
        'auth': 'test_app.AuthenticationTests',
        'dashboard': 'test_app.DashboardTests',
        'books': 'test_app.BookManagementTests',
        'borrow': 'test_app.BorrowingTests',
        'qr': 'test_app.QRCodeTests',
        'db': 'test_app.DatabaseTests',
        'integration': 'test_integration.IntegrationTestCase'
    }
    
    if test_name not in test_mapping:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_mapping.keys())}")
        return False
    
    module_path = test_mapping[test_name]
    module_name, class_name = module_path.split('.')
    
    try:
        module = __import__(module_name, fromlist=[class_name])
        test_class = getattr(module, class_name)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Could not import test module: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    print("Checking dependencies...")
    
    required_modules = [
        'flask',
        'werkzeug',
        'qrcode',
        'PIL'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} (missing)")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing dependencies: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies are available")
    return True

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            return check_dependencies()
        elif command == 'all':
            if not check_dependencies():
                return False
            return run_all_tests()
        elif command in ['auth', 'dashboard', 'books', 'borrow', 'qr', 'db', 'integration']:
            if not check_dependencies():
                return False
            return run_specific_test(command)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python run_tests.py [check|all|auth|dashboard|books|borrow|qr|db|integration]")
            return False
    else:
        # Default: run all tests
        if not check_dependencies():
            return False
        return run_all_tests()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)