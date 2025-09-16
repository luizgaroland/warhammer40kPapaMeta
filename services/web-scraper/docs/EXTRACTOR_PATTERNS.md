# Warhammer 40k Web Scraper - Extractor Patterns and Best Practices

## Overview

This document outlines the normalized structure and patterns for extractors in the Warhammer 40k web scraper project. All extractors follow a consistent pattern to ensure maintainability, testability, and reliability.

## Base Architecture

### BaseExtractor Class

All extractors inherit from `BaseExtractor`, which provides:

- **Standardized Constructor**: Consistent parameters across all extractors
- **URL Configuration**: Version-aware URL management
- **Redis Publishing**: Optional Redis integration for microservice communication
- **Rate Limiting**: Configurable request throttling
- **Error Handling**: Standardized error handling and logging
- **Data Validation**: Built-in validation for common data structures
- **File Operations**: Standardized JSON saving functionality

### Constructor Pattern

```python
def __init__(self, version_id: str = "10th", publish_to_redis: bool = True, 
             rate_limit_min: float = 2.0, rate_limit_max: float = 3.0):
```

**Parameters:**
- `version_id`: Warhammer 40k edition version (default: "10th")
- `publish_to_redis`: Whether to publish results to Redis
- `rate_limit_min`: Minimum seconds between requests
- `rate_limit_max`: Maximum seconds between requests

## Extractor Structure

### 1. FactionListExtractor

**Purpose**: Extracts all available factions from Wahapedia navigation.

**Key Methods:**
- `extract_factions()`: Main extraction method
- `_extract_faction_code()`: Helper to extract faction code from URL
- `save_factions_to_json()`: Save results to JSON file

**Data Structure:**
```python
{
    'name': 'Space Marines',
    'url': 'https://wahapedia.ru/wh40k10ed/factions/space-marines',
    'code': 'space-marines'
}
```

### 2. ArmyRulesExtractor

**Purpose**: Extracts army rules for each faction.

**Key Methods:**
- `extract_army_rule_for_faction()`: Extract rule for single faction
- `extract_all_army_rules()`: Extract rules for multiple factions
- `publish_army_rules()`: Publish results to Redis
- `save_army_rules_to_json()`: Save results to JSON file

**Data Structure:**
```python
{
    'faction_name': 'Space Marines',
    'faction_code': 'space-marines',
    'faction_url': 'https://wahapedia.ru/wh40k10ed/factions/space-marines',
    'army_rule_name': 'Oath of Moment'
}
```

## Testing Framework

### BaseTestExtractor

All extractor tests inherit from `BaseTestExtractor`, which provides:

- **Test Fixtures**: Common test data and HTML fixtures
- **Mock Utilities**: Helper methods for mocking external dependencies
- **Validation Helpers**: Assertion methods for common data structures
- **File Operations**: Test-specific file handling

### Test Structure

```python
class TestFactionListExtractor(BaseTestExtractor):
    def setUp(self):
        super().setUp()
        self.extractor_class = FactionListExtractor
        self.extractor = self.create_mock_extractor(FactionListExtractor)
    
    def test_constructor_defaults(self):
        """Test constructor with default parameters."""
        # Test implementation
```

### Test Categories

1. **Unit Tests**: Test individual methods in isolation
2. **Integration Tests**: Test complete workflows with real HTML
3. **Validation Tests**: Test data validation and error handling
4. **Publishing Tests**: Test Redis publishing functionality

## Error Handling Patterns

### Validation

```python
def extract_data_for_faction(self, faction_data: Dict[str, str]) -> Optional[Dict[str, str]]:
    # Validate input using base class method
    validated_faction = self.safe_extract_faction_info(faction_data)
    if not validated_faction:
        return None
    # Continue with extraction...
```

### Status Publishing

```python
# Publish start status
self.publish_status('started', {'task': 'extraction_task'})

# Publish completion status
self.publish_status('completed', {'task': 'extraction_task', 'count': len(results)})

# Publish error status
self.publish_status('error', {'task': 'extraction_task', 'error': str(e)})
```

### Graceful Degradation

```python
try:
    result = self.extract_data()
    if result:
        self.extracted_data.append(result)
    else:
        self.logger.warning(f"Failed to extract data for {item}")
except Exception as e:
    self.logger.error(f"Error during extraction: {str(e)}")
    # Continue with next item instead of failing completely
```

## Data Flow Patterns

### 1. Single Item Extraction

```python
def extract_single_item(self, item_data: Dict[str, str]) -> Optional[Dict[str, str]]:
    # Validate input
    validated_item = self.safe_extract_faction_info(item_data)
    if not validated_item:
        return None
    
    # Fetch and parse
    soup = self.fetch_and_parse(validated_item['url'])
    if not soup:
        return None
    
    # Extract data
    extracted_data = self._extract_from_soup(soup, validated_item)
    
    return extracted_data
```

### 2. Batch Extraction

```python
def extract_all_items(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    self.logger.info(f"Starting extraction for {len(items)} items")
    self.publish_status('started', {'task': 'batch_extraction'})
    
    results = []
    for item in items:
        result = self.extract_single_item(item)
        if result:
            results.append(result)
        else:
            self.logger.warning(f"Failed to extract {item.get('name', 'unknown')}")
    
    # Update base class data
    self.extracted_data = results
    
    # Publish results
    if self.publish_to_redis and results:
        self.publish_results(results)
    
    self.publish_status('completed', {'task': 'batch_extraction', 'count': len(results)})
    return results
```

## CSS Selector Management

### Centralized Selectors

All CSS selectors are defined in `css_selectors.py`:

```python
FACTION_SELECTORS = {
    'nav_button': '.NavBtn_Factions',
    'dropdown_content': '.NavDropdown-content',
    'faction_link': '.BreakInsideAvoid a',
}

ARMY_RULE_SELECTORS = {
    'army_rules_anchor': 'a[name="Army-Rules"]',
    'columns_container': '.Columns2',
    'break_inside_avoid': '.BreakInsideAvoid',
    'rule_name': 'h3',
}
```

### Usage Pattern

```python
from scrapers.wahapedia.css_selectors import FACTION_SELECTORS

# Use selectors
faction_btn = soup.select_one(FACTION_SELECTORS['nav_button'])
```

## File Operations

### Saving Results

```python
def save_results_to_json(self, filename: str = 'results.json') -> bool:
    """Save extracted data to JSON file."""
    return super().save_to_json(self.extracted_data, filename)
```

### Loading Fixtures

```python
def load_test_fixture(self, filename: str) -> str:
    """Load HTML fixture for testing."""
    fixture_path = os.path.join(self.test_fixtures_dir, filename)
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()
```

## Best Practices

### 1. Always Validate Input

```python
# Good
validated_data = self.safe_extract_faction_info(faction_data)
if not validated_data:
    return None

# Bad
faction_name = faction_data.get('name')  # Could be None
```

### 2. Use Consistent Error Handling

```python
# Good
try:
    result = self.extract_data()
    if result:
        self.extracted_data.append(result)
except Exception as e:
    self.logger.error(f"Extraction failed: {str(e)}")
    # Continue processing

# Bad
result = self.extract_data()  # Could raise unhandled exception
```

### 3. Publish Status Updates

```python
# Good
self.publish_status('started', {'task': 'extraction'})
# ... do work ...
self.publish_status('completed', {'task': 'extraction', 'count': len(results)})

# Bad
# No status updates - microservice consumers don't know what's happening
```

### 4. Use Base Class Methods

```python
# Good
return super().save_to_json(self.extracted_data, filename)

# Bad
# Duplicating save logic in every extractor
```

### 5. Comprehensive Testing

```python
# Good
def test_extraction_success(self):
    """Test successful extraction."""
    # Test with valid data
    
def test_extraction_failure(self):
    """Test extraction failure handling."""
    # Test with invalid data
    
def test_extraction_edge_cases(self):
    """Test edge cases."""
    # Test boundary conditions
```

## Running Tests

### Run All Tests

```bash
python tests/run_extractor_tests.py
```

### Run Specific Extractor Tests

```bash
python tests/run_extractor_tests.py --extractor faction_list
python tests/run_extractor_tests.py --extractor army_rules
```

### Run with Verbose Output

```bash
python tests/run_extractor_tests.py --verbose
```

## Future Extensions

When adding new extractors, follow these patterns:

1. **Inherit from BaseExtractor**
2. **Use standardized constructor parameters**
3. **Implement validation using base class methods**
4. **Add comprehensive tests using BaseTestExtractor**
5. **Define CSS selectors in css_selectors.py**
6. **Follow the data flow patterns**
7. **Add proper error handling and status publishing**

This structure ensures consistency, maintainability, and reliability across all extractors in the Warhammer 40k web scraper project.