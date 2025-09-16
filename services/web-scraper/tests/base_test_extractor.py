# services/web-scraper/tests/base_test_extractor.py

import unittest
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import json
import os

class BaseTestExtractor(unittest.TestCase):
    """Base test class for extractors with common test utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.test_output_dir = os.path.join(os.path.dirname(__file__), 'output')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Common test data
        self.sample_faction = {
            'name': 'Space Marines',
            'url': 'https://wahapedia.ru/wh40k10ed/factions/space-marines',
            'code': 'space-marines'
        }
        
        self.sample_factions = [
            {
                'name': 'Space Marines',
                'url': 'https://wahapedia.ru/wh40k10ed/factions/space-marines',
                'code': 'space-marines'
            },
            {
                'name': 'Astra Militarum',
                'url': 'https://wahapedia.ru/wh40k10ed/factions/astra-militarum',
                'code': 'astra-militarum'
            },
            {
                'name': 'Orks',
                'url': 'https://wahapedia.ru/wh40k10ed/factions/orks',
                'code': 'orks'
            }
        ]

    def load_fixture(self, filename: str) -> str:
        """
        Load HTML fixture from fixtures directory.
        
        Args:
            filename: Name of the fixture file
            
        Returns:
            HTML content as string
        """
        fixture_path = os.path.join(self.test_fixtures_dir, filename)
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return f.read()

    def create_mock_soup(self, html_content: str):
        """
        Create a mock BeautifulSoup object from HTML content.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Mock BeautifulSoup object
        """
        from bs4 import BeautifulSoup
        return BeautifulSoup(html_content, 'html.parser')

    def assert_valid_faction_data(self, faction_data: Dict[str, str]):
        """
        Assert that faction data has required fields.
        
        Args:
            faction_data: Faction data dictionary
        """
        required_fields = ['name', 'url', 'code']
        for field in required_fields:
            self.assertIn(field, faction_data, f"Missing required field: {field}")
            self.assertTrue(faction_data[field], f"Empty value for field: {field}")

    def assert_extraction_result(self, result: Optional[Dict[str, Any]], expected_fields: List[str]):
        """
        Assert that extraction result has expected structure.
        
        Args:
            result: Extraction result dictionary
            expected_fields: List of expected field names
        """
        if result is None:
            self.fail("Extraction result should not be None")
            
        for field in expected_fields:
            self.assertIn(field, result, f"Missing expected field: {field}")
            self.assertTrue(result[field], f"Empty value for field: {field}")

    def create_mock_extractor(self, extractor_class, **kwargs):
        """
        Create a mock extractor with disabled Redis publishing.
        
        Args:
            extractor_class: Extractor class to instantiate
            **kwargs: Additional constructor arguments
            
        Returns:
            Mock extractor instance
        """
        # Disable Redis publishing for tests
        kwargs['publish_to_redis'] = False
        
        # Create extractor instance
        extractor = extractor_class(**kwargs)
        
        # Mock the publisher to avoid Redis calls
        extractor.publisher = Mock()
        
        return extractor

    def patch_fetch_and_parse(self, html_content: str):
        """
        Patch fetch_and_parse method to return mock HTML content.
        
        Args:
            html_content: HTML content to return
            
        Returns:
            Mock patch object
        """
        mock_soup = self.create_mock_soup(html_content)
        return patch.object(self.extractor, 'fetch_and_parse', return_value=mock_soup)

    def save_test_output(self, data: Any, filename: str) -> str:
        """
        Save test data to output file for inspection.
        
        Args:
            data: Data to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = os.path.join(self.test_output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        return output_path

    def tearDown(self):
        """Clean up after tests."""
        # Clean up any test output files if needed
        pass

class TestExtractorValidation(BaseTestExtractor):
    """Test class for extractor validation methods."""
    
    def test_faction_data_validation(self):
        """Test faction data validation."""
        # Valid faction data
        valid_faction = self.sample_faction.copy()
        self.assertTrue(self.extractor.validate_faction_data(valid_faction))
        
        # Missing required fields
        invalid_factions = [
            {'name': 'Test'},  # Missing url and code
            {'name': 'Test', 'url': 'http://test.com'},  # Missing code
            {'name': '', 'url': 'http://test.com', 'code': 'test'},  # Empty name
        ]
        
        for invalid_faction in invalid_factions:
            with self.subTest(faction=invalid_faction):
                self.assertFalse(self.extractor.validate_faction_data(invalid_faction))

class TestExtractorPublishing(BaseTestExtractor):
    """Test class for extractor publishing functionality."""
    
    def test_publish_status_disabled(self):
        """Test that publishing is disabled when publish_to_redis=False."""
        extractor = self.create_mock_extractor(self.extractor_class, publish_to_redis=False)
        result = extractor.publish_status('test', {'data': 'test'})
        self.assertTrue(result)  # Should return True when disabled
        extractor.publisher.publish_status.assert_not_called()

    def test_publish_status_enabled(self):
        """Test that publishing works when publish_to_redis=True."""
        extractor = self.create_mock_extractor(self.extractor_class, publish_to_redis=True)
        extractor.publisher.publish_status.return_value = True
        
        result = extractor.publish_status('test', {'data': 'test'})
        self.assertTrue(result)
        extractor.publisher.publish_status.assert_called_once_with('test', {'data': 'test'})

class TestExtractorFileOperations(BaseTestExtractor):
    """Test class for extractor file operations."""
    
    def test_save_to_json_success(self):
        """Test successful JSON saving."""
        test_data = [{'test': 'data'}]
        filename = 'test_output.json'
        
        result = self.extractor.save_to_json(test_data, filename)
        self.assertTrue(result)
        
        # Verify file was created
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)
        
        # Clean up
        os.remove(filename)

    def test_save_to_json_empty_data(self):
        """Test JSON saving with empty data."""
        result = self.extractor.save_to_json([], 'test.json')
        self.assertFalse(result)

    def test_save_to_json_invalid_path(self):
        """Test JSON saving with invalid path."""
        result = self.extractor.save_to_json([{'test': 'data'}], '/invalid/path/test.json')
        self.assertFalse(result)