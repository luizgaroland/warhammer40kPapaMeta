# services/web-scraper/tests/test_army_rules_normalized.py

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.wahapedia.extractors.army_rules import ArmyRulesExtractor
from tests.base_test_extractor import BaseTestExtractor

class TestArmyRulesExtractor(BaseTestExtractor):
    """Test class for ArmyRulesExtractor with normalized structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.extractor_class = ArmyRulesExtractor
        self.extractor = self.create_mock_extractor(ArmyRulesExtractor)

    def test_constructor_defaults(self):
        """Test constructor with default parameters."""
        extractor = ArmyRulesExtractor()
        self.assertEqual(extractor.version_id, "10th")
        self.assertTrue(extractor.publish_to_redis)
        self.assertEqual(extractor.rate_limit_min, 2.0)
        self.assertEqual(extractor.rate_limit_max, 3.0)

    def test_constructor_custom_params(self):
        """Test constructor with custom parameters."""
        extractor = ArmyRulesExtractor(
            version_id="9th",
            publish_to_redis=False,
            rate_limit_min=1.0,
            rate_limit_max=2.0
        )
        self.assertEqual(extractor.version_id, "9th")
        self.assertFalse(extractor.publish_to_redis)
        self.assertEqual(extractor.rate_limit_min, 1.0)
        self.assertEqual(extractor.rate_limit_max, 2.0)

    def test_extract_army_rule_for_faction_invalid_data(self):
        """Test army rule extraction with invalid faction data."""
        invalid_factions = [
            {'name': 'Test'},  # Missing url and code
            {'name': 'Test', 'url': 'http://test.com'},  # Missing code
            {'name': '', 'url': 'http://test.com', 'code': 'test'},  # Empty name
        ]
        
        for invalid_faction in invalid_factions:
            with self.subTest(faction=invalid_faction):
                result = self.extractor.extract_army_rule_for_faction(invalid_faction)
                self.assertIsNone(result)

    def test_extract_army_rule_for_faction_no_soup(self):
        """Test army rule extraction when fetch_and_parse returns None."""
        with patch.object(self.extractor, 'fetch_and_parse', return_value=None):
            result = self.extractor.extract_army_rule_for_faction(self.sample_faction)
            self.assertIsNone(result)

    def test_extract_army_rule_for_faction_no_anchor(self):
        """Test army rule extraction when Army Rules anchor is not found."""
        html_content = '''
        <html>
            <body>
                <div class="BreakInsideAvoid">
                    <h2>Some other content</h2>
                </div>
            </body>
        </html>
        '''
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_army_rule_for_faction(self.sample_faction)
            self.assertIsNone(result)

    def test_extract_army_rule_for_faction_success(self):
        """Test successful army rule extraction."""
        html_content = '''
        <html>
            <body>
                <a name="Army-Rules"></a>
                <div class="Columns2">
                    <div class="BreakInsideAvoid">
                        <h3>Oath of Moment</h3>
                        <p>Army rule description...</p>
                    </div>
                </div>
            </body>
        </html>
        '''
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_army_rule_for_faction(self.sample_faction)
            
            self.assertIsNotNone(result)
            self.assert_extraction_result(result, [
                'faction_name', 'faction_code', 'faction_url', 'army_rule_name'
            ])
            self.assertEqual(result['faction_name'], 'Space Marines')
            self.assertEqual(result['army_rule_name'], 'Oath of Moment')

    def test_extract_army_rule_for_faction_fallback_header(self):
        """Test army rule extraction with h2 fallback when h3 is not found."""
        html_content = '''
        <html>
            <body>
                <a name="Army-Rules"></a>
                <div class="BreakInsideAvoid">
                    <h2>Combat Doctrines</h2>
                    <p>Army rule description...</p>
                </div>
            </body>
        </html>
        '''
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_army_rule_for_faction(self.sample_faction)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['army_rule_name'], 'Combat Doctrines')

    def test_extract_all_army_rules_empty_list(self):
        """Test extracting army rules from empty faction list."""
        result = self.extractor.extract_all_army_rules([])
        self.assertEqual(result, [])
        self.assertEqual(len(self.extractor.army_rules), 0)

    def test_extract_all_army_rules_success(self):
        """Test extracting army rules from multiple factions."""
        # Mock successful extraction for all factions
        with patch.object(self.extractor, 'extract_army_rule_for_faction') as mock_extract:
            mock_extract.side_effect = [
                {
                    'faction_name': 'Space Marines',
                    'faction_code': 'space-marines',
                    'faction_url': 'http://test.com/space-marines',
                    'army_rule_name': 'Oath of Moment'
                },
                {
                    'faction_name': 'Astra Militarum',
                    'faction_code': 'astra-militarum',
                    'faction_url': 'http://test.com/astra-militarum',
                    'army_rule_name': 'Born Soldiers'
                },
                None  # One faction fails
            ]
            
            result = self.extractor.extract_all_army_rules(self.sample_factions)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(len(self.extractor.army_rules), 2)
            self.assertEqual(self.extractor.extracted_data, result)
            
            # Verify status publishing
            self.extractor.publisher.publish_status.assert_called()

    def test_save_army_rules_to_json(self):
        """Test saving army rules to JSON file."""
        test_army_rules = [
            {
                'faction_name': 'Space Marines',
                'faction_code': 'space-marines',
                'faction_url': 'http://test.com/space-marines',
                'army_rule_name': 'Oath of Moment'
            }
        ]
        self.extractor.army_rules = test_army_rules
        
        filename = os.path.join(self.test_output_dir, 'test_army_rules.json')
        result = self.extractor.save_army_rules_to_json(filename)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        import json
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_army_rules)

    def test_get_extraction_summary(self):
        """Test extraction summary generation."""
        test_army_rules = [
            {
                'faction_name': 'Space Marines',
                'faction_code': 'space-marines',
                'faction_url': 'http://test.com/space-marines',
                'army_rule_name': 'Oath of Moment'
            }
        ]
        self.extractor.army_rules = test_army_rules
        self.extractor.extracted_data = test_army_rules
        
        summary = self.extractor.get_extraction_summary()
        
        self.assertEqual(summary['extractor_type'], 'ArmyRulesExtractor')
        self.assertEqual(summary['version_id'], '10th')
        self.assertEqual(summary['total_extracted'], len(test_army_rules))
        self.assertFalse(summary['publish_to_redis'])  # Disabled in mock

class TestArmyRulesExtractorIntegration(BaseTestExtractor):
    """Integration tests for ArmyRulesExtractor."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        super().setUp()
        self.extractor = ArmyRulesExtractor(publish_to_redis=False)

    def test_full_extraction_workflow(self):
        """Test complete extraction workflow with real HTML."""
        # Load fixture HTML
        html_content = self.load_fixture('faction_page.html')
        
        with patch.object(self.extractor, 'fetch_and_parse') as mock_fetch:
            mock_fetch.return_value = self.create_mock_soup(html_content)
            
            # Extract army rule for single faction
            result = self.extractor.extract_army_rule_for_faction(self.sample_faction)
            
            # Verify result
            if result:
                self.assert_extraction_result(result, [
                    'faction_name', 'faction_code', 'faction_url', 'army_rule_name'
                ])
                
                # Test saving
                output_file = self.save_test_output(result, 'army_rule_extraction_test.json')
                self.assertTrue(os.path.exists(output_file))

    def test_batch_extraction_workflow(self):
        """Test batch extraction workflow."""
        # Mock successful extraction for multiple factions
        with patch.object(self.extractor, 'extract_army_rule_for_faction') as mock_extract:
            mock_extract.side_effect = [
                {
                    'faction_name': 'Space Marines',
                    'faction_code': 'space-marines',
                    'faction_url': 'http://test.com/space-marines',
                    'army_rule_name': 'Oath of Moment'
                },
                {
                    'faction_name': 'Astra Militarum',
                    'faction_code': 'astra-militarum',
                    'faction_url': 'http://test.com/astra-militarum',
                    'army_rule_name': 'Born Soldiers'
                }
            ]
            
            # Extract army rules for multiple factions
            result = self.extractor.extract_all_army_rules(self.sample_factions[:2])
            
            # Verify results
            self.assertEqual(len(result), 2)
            for army_rule in result:
                self.assert_extraction_result(army_rule, [
                    'faction_name', 'faction_code', 'faction_url', 'army_rule_name'
                ])
            
            # Test saving
            if result:
                output_file = self.save_test_output(result, 'army_rules_batch_test.json')
                self.assertTrue(os.path.exists(output_file))

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestArmyRulesExtractor))
    suite.addTest(unittest.makeSuite(TestArmyRulesExtractorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)