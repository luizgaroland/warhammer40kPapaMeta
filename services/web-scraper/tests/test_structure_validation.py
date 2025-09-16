# services/web-scraper/tests/test_structure_validation.py

"""
Simple structure validation tests that don't require external dependencies.
These tests verify that the normalized extractor structure is correct.
"""

import unittest
import sys
import os
import ast
import inspect

class TestExtractorStructure(unittest.TestCase):
    """Test that extractors follow the normalized structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        self.extractors_dir = os.path.join(self.src_dir, 'scrapers', 'wahapedia', 'extractors')
    
    def test_base_extractor_exists(self):
        """Test that BaseExtractor exists and has required methods."""
        base_extractor_path = os.path.join(self.extractors_dir, 'base_extractor.py')
        self.assertTrue(os.path.exists(base_extractor_path), "BaseExtractor file should exist")
        
        # Read the file and check for required methods
        with open(base_extractor_path, 'r') as f:
            content = f.read()
            
        required_methods = [
            '__init__',
            'validate_faction_data',
            'safe_extract_faction_info',
            'publish_status',
            'save_to_json',
            'get_extraction_summary'
        ]
        
        for method in required_methods:
            self.assertIn(f'def {method}', content, f"BaseExtractor should have {method} method")
    
    def test_faction_list_extractor_structure(self):
        """Test that FactionListExtractor follows the normalized structure."""
        faction_list_path = os.path.join(self.extractors_dir, 'faction_list.py')
        self.assertTrue(os.path.exists(faction_list_path), "FactionListExtractor file should exist")
        
        with open(faction_list_path, 'r') as f:
            content = f.read()
        
        # Check inheritance
        self.assertIn('class FactionListExtractor(BaseExtractor)', content,
                     "FactionListExtractor should inherit from BaseExtractor")
        
        # Check constructor signature
        self.assertIn('def __init__(self, version_id: str = "10th", publish_to_redis: bool = True', content,
                     "Constructor should have standardized parameters")
        
        # Check required methods
        required_methods = ['extract_factions', '_extract_faction_code', 'save_factions_to_json']
        for method in required_methods:
            self.assertIn(f'def {method}', content, f"FactionListExtractor should have {method} method")
    
    def test_army_rules_extractor_structure(self):
        """Test that ArmyRulesExtractor follows the normalized structure."""
        army_rules_path = os.path.join(self.extractors_dir, 'army_rules.py')
        self.assertTrue(os.path.exists(army_rules_path), "ArmyRulesExtractor file should exist")
        
        with open(army_rules_path, 'r') as f:
            content = f.read()
        
        # Check inheritance
        self.assertIn('class ArmyRulesExtractor(BaseExtractor)', content,
                     "ArmyRulesExtractor should inherit from BaseExtractor")
        
        # Check constructor signature
        self.assertIn('def __init__(self, version_id: str = "10th", publish_to_redis: bool = True', content,
                     "Constructor should have standardized parameters")
        
        # Check required methods
        required_methods = ['extract_army_rule_for_faction', 'extract_all_army_rules', 'save_army_rules_to_json']
        for method in required_methods:
            self.assertIn(f'def {method}', content, f"ArmyRulesExtractor should have {method} method")
    
    def test_import_consistency(self):
        """Test that imports are consistent across extractors."""
        extractor_files = ['faction_list.py', 'army_rules.py']
        
        for filename in extractor_files:
            filepath = os.path.join(self.extractors_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for proper import structure
                self.assertIn('from .base_extractor import BaseExtractor', content,
                             f"{filename} should import BaseExtractor correctly")
                
                # Check for sys.path manipulation (should be present for proper imports)
                self.assertIn('sys.path.insert', content,
                             f"{filename} should have sys.path manipulation for imports")
    
    def test_test_framework_structure(self):
        """Test that the test framework follows the normalized structure."""
        test_files = [
            'base_test_extractor.py',
            'test_faction_list_normalized.py',
            'test_army_rules_normalized.py',
            'run_extractor_tests.py'
        ]
        
        for filename in test_files:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            self.assertTrue(os.path.exists(filepath), f"Test file {filename} should exist")
    
    def test_documentation_exists(self):
        """Test that documentation exists."""
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        patterns_doc = os.path.join(docs_dir, 'EXTRACTOR_PATTERNS.md')
        
        self.assertTrue(os.path.exists(docs_dir), "Documentation directory should exist")
        self.assertTrue(os.path.exists(patterns_doc), "EXTRACTOR_PATTERNS.md should exist")
    
    def test_css_selectors_centralized(self):
        """Test that CSS selectors are centralized."""
        css_selectors_path = os.path.join(self.src_dir, 'scrapers', 'wahapedia', 'css_selectors.py')
        self.assertTrue(os.path.exists(css_selectors_path), "CSS selectors file should exist")
        
        with open(css_selectors_path, 'r') as f:
            content = f.read()
        
        # Check for required selector dictionaries
        required_selectors = ['FACTION_SELECTORS', 'ARMY_RULE_SELECTORS', 'URLS']
        for selector in required_selectors:
            self.assertIn(selector, content, f"CSS selectors should contain {selector}")

class TestCodeQuality(unittest.TestCase):
    """Test code quality and consistency."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        self.extractors_dir = os.path.join(self.src_dir, 'scrapers', 'wahapedia', 'extractors')
    
    def test_no_hardcoded_paths(self):
        """Test that there are no hardcoded paths in extractors."""
        extractor_files = ['faction_list.py', 'army_rules.py', 'base_extractor.py']
        
        for filename in extractor_files:
            filepath = os.path.join(self.extractors_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for hardcoded paths (should use relative paths or os.path.join)
                hardcoded_patterns = ['/app/src', '/app/', 'sys.path.insert(0, \'/']
                for pattern in hardcoded_patterns:
                    if pattern in content:
                        # Allow sys.path.insert with relative paths
                        if 'sys.path.insert' in pattern and 'os.path.join' in content:
                            continue
                        self.fail(f"{filename} contains hardcoded path: {pattern}")
    
    def test_consistent_docstrings(self):
        """Test that methods have consistent docstrings."""
        extractor_files = ['faction_list.py', 'army_rules.py']
        
        for filename in extractor_files:
            filepath = os.path.join(self.extractors_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for method definitions with docstrings
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and not line.strip().startswith('def _'):
                        # Check if next non-empty line is a docstring
                        j = i + 1
                        while j < len(lines) and lines[j].strip() == '':
                            j += 1
                        
                        if j < len(lines):
                            next_line = lines[j].strip()
                            self.assertTrue(
                                next_line.startswith('"""') or next_line.startswith("'''"),
                                f"{filename}: Method {line.strip()} should have a docstring"
                            )

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeQuality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("STRUCTURE VALIDATION SUMMARY")
    print("="*60)
    print(f"Total Tests: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print(f"Overall Result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    print("="*60)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)