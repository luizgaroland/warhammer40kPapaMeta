# services/web-scraper/tests/test_faction_list_normalized.py

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.wahapedia.extractors.faction_list import FactionListExtractor
from tests.base_test_extractor import BaseTestExtractor

class TestFactionListExtractor(BaseTestExtractor):
    """Test class for FactionListExtractor with normalized structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.extractor_class = FactionListExtractor
        self.extractor = self.create_mock_extractor(FactionListExtractor)

    def test_constructor_defaults(self):
        """Test constructor with default parameters."""
        extractor = FactionListExtractor()
        self.assertEqual(extractor.version_id, "10th")
        self.assertTrue(extractor.publish_to_redis)
        self.assertEqual(extractor.rate_limit_min, 2.0)
        self.assertEqual(extractor.rate_limit_max, 3.0)

    def test_constructor_custom_params(self):
        """Test constructor with custom parameters."""
        extractor = FactionListExtractor(
            version_id="9th",
            publish_to_redis=False,
            rate_limit_min=1.0,
            rate_limit_max=2.0
        )
        self.assertEqual(extractor.version_id, "9th")
        self.assertFalse(extractor.publish_to_redis)
        self.assertEqual(extractor.rate_limit_min, 1.0)
        self.assertEqual(extractor.rate_limit_max, 2.0)

    def test_extract_faction_code(self):
        """Test faction code extraction from URL."""
        test_cases = [
            ('/wh40k10ed/factions/space-marines/', 'space-marines'),
            ('/wh40k10ed/factions/astra-militarum', 'astra-militarum'),
            ('https://wahapedia.ru/wh40k10ed/factions/orks/', 'orks'),
            ('/invalid/url', ''),
        ]
        
        for url, expected_code in test_cases:
            with self.subTest(url=url):
                result = self.extractor._extract_faction_code(url)
                self.assertEqual(result, expected_code)

    @patch('scrapers.wahapedia.extractors.faction_list.URLS', {'quick_start': '/test/quick-start/'})
    def test_extract_factions_success(self):
        """Test successful faction extraction."""
        # Load fixture HTML
        html_content = self.load_fixture('faction_dropdown.html')
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_factions()
            
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            
            # Verify first faction has required fields
            if result:
                self.assert_valid_faction_data(result[0])
                
            # Verify extracted_data is updated
            self.assertEqual(self.extractor.extracted_data, result)

    def test_extract_factions_no_soup(self):
        """Test faction extraction when fetch_and_parse returns None."""
        with patch.object(self.extractor, 'fetch_and_parse', return_value=None):
            result = self.extractor.extract_factions()
            self.assertEqual(result, [])
            self.extractor.publisher.publish_status.assert_called_with(
                'error', 
                {'task': 'faction_extraction', 'error': 'Failed to fetch quick start page'}
            )

    def test_extract_factions_no_nav_button(self):
        """Test faction extraction when navigation button is not found."""
        html_content = '<html><body><div>No nav button here</div></body></html>'
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_factions()
            self.assertEqual(result, [])
            self.extractor.publisher.publish_status.assert_called_with(
                'error',
                {'task': 'faction_extraction', 'error': 'Could not find faction navigation button'}
            )

    def test_extract_factions_no_dropdown(self):
        """Test faction extraction when dropdown content is not found."""
        html_content = '''
        <html>
            <body>
                <div class="NavBtn_Factions">Factions</div>
                <div class="other-content">No dropdown here</div>
            </body>
        </html>
        '''
        
        with self.patch_fetch_and_parse(html_content):
            result = self.extractor.extract_factions()
            self.assertEqual(result, [])
            self.extractor.publisher.publish_status.assert_called_with(
                'error',
                {'task': 'faction_extraction', 'error': 'Could not find faction dropdown content'}
            )

    def test_save_factions_to_json(self):
        """Test saving factions to JSON file."""
        test_factions = self.sample_factions.copy()
        self.extractor.factions = test_factions
        
        filename = os.path.join(self.test_output_dir, 'test_factions.json')
        result = self.extractor.save_factions_to_json(filename)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        import json
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_factions)

    def test_get_extraction_summary(self):
        """Test extraction summary generation."""
        self.extractor.factions = self.sample_factions
        self.extractor.extracted_data = self.sample_factions
        
        summary = self.extractor.get_extraction_summary()
        
        self.assertEqual(summary['extractor_type'], 'FactionListExtractor')
        self.assertEqual(summary['version_id'], '10th')
        self.assertEqual(summary['total_extracted'], len(self.sample_factions))
        self.assertFalse(summary['publish_to_redis'])  # Disabled in mock

class TestFactionListExtractorIntegration(BaseTestExtractor):
    """Integration tests for FactionListExtractor."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        super().setUp()
        self.extractor = FactionListExtractor(publish_to_redis=False)

    def test_full_extraction_workflow(self):
        """Test complete extraction workflow with real HTML."""
        # This test would use real HTML content
        # For now, we'll mock it but structure it for real testing
        html_content = self.load_fixture('faction_dropdown.html')
        
        with patch.object(self.extractor, 'fetch_and_parse') as mock_fetch:
            mock_fetch.return_value = self.create_mock_soup(html_content)
            
            # Extract factions
            result = self.extractor.extract_factions()
            
            # Verify results
            self.assertIsInstance(result, list)
            if result:
                for faction in result:
                    self.assert_valid_faction_data(faction)
            
            # Test saving
            if result:
                output_file = self.save_test_output(result, 'faction_extraction_test.json')
                self.assertTrue(os.path.exists(output_file))

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestFactionListExtractor))
    suite.addTest(unittest.makeSuite(TestFactionListExtractorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)