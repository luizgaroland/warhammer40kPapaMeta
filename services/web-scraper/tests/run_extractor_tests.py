# services/web-scraper/tests/run_extractor_tests.py

"""
Test runner for all extractor tests.
Provides a unified way to run all extractor tests with proper reporting.
"""

import unittest
import sys
import os
from typing import List, Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def discover_and_run_tests(test_pattern: str = "test_*_normalized.py") -> Dict[str, Any]:
    """
    Discover and run all extractor tests.
    
    Args:
        test_pattern: Pattern to match test files
        
    Returns:
        Dictionary with test results summary
    """
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern=test_pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate summary
    summary = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0,
        'was_successful': result.wasSuccessful()
    }
    
    return summary

def run_specific_extractor_tests(extractor_name: str) -> Dict[str, Any]:
    """
    Run tests for a specific extractor.
    
    Args:
        extractor_name: Name of the extractor (e.g., 'faction_list', 'army_rules')
        
    Returns:
        Dictionary with test results summary
    """
    test_file = f"test_{extractor_name}_normalized.py"
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    if not os.path.exists(test_path):
        print(f"Test file not found: {test_file}")
        return {'error': f'Test file not found: {test_file}'}
    
    # Import and run specific test
    spec = unittest.TestLoader().loadTestsFromName(f"tests.{test_file.replace('.py', '')}")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(spec)
    
    summary = {
        'extractor': extractor_name,
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0,
        'was_successful': result.wasSuccessful()
    }
    
    return summary

def print_test_summary(summary: Dict[str, Any]):
    """Print a formatted test summary."""
    print("\n" + "="*60)
    print("EXTRACTOR TEST SUMMARY")
    print("="*60)
    
    if 'error' in summary:
        print(f"ERROR: {summary['error']}")
        return
    
    if 'extractor' in summary:
        print(f"Extractor: {summary['extractor']}")
    
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Result: {'PASSED' if summary['was_successful'] else 'FAILED'}")
    print("="*60)

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run extractor tests')
    parser.add_argument('--extractor', '-e', 
                       help='Run tests for specific extractor (faction_list, army_rules, etc.)')
    parser.add_argument('--pattern', '-p', 
                       default='test_*_normalized.py',
                       help='Test file pattern (default: test_*_normalized.py)')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.extractor:
        # Run specific extractor tests
        summary = run_specific_extractor_tests(args.extractor)
    else:
        # Run all tests
        summary = discover_and_run_tests(args.pattern)
    
    print_test_summary(summary)
    
    # Exit with appropriate code
    exit(0 if summary.get('was_successful', False) else 1)

if __name__ == '__main__':
    main()