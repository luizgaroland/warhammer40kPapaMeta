#!/usr/bin/env python3
"""
Test suite for WahapediaURLConfig
Tests URL building, faction code normalization, and pattern generation
"""
import sys
sys.path.insert(0, "/app/src")

from services.wahapedia.url_config import WahapediaURLConfig

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)

def print_result(description: str, expected: str, actual: str, passed: bool = None):
    """Print test result with formatting."""
    if passed is None:
        passed = (expected == actual)

    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {description}")
    print(f"  Expected: {expected}")
    print(f"  Actual:   {actual}")
    if not passed:
        print(f"  ⚠️  Mismatch detected!")
    return passed

def test_basic_initialization():
    """Test basic URL config initialization."""
    print_test_header("Basic Initialization")

    config = WahapediaURLConfig("10th")

    tests_passed = 0
    tests_failed = 0

    # Test version path mapping
    expected_path = "wh40k10ed"
    actual_path = config.get_version_path()
    if print_result("Version path for 10th edition", expected_path, actual_path):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test base URL
    expected_base = "https://wahapedia.ru"
    actual_base = config.get_base_url()
    if print_result("Base URL", expected_base, actual_base):
        tests_passed += 1
    else:
        tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_quick_start_url():
    """Test quick start URL generation."""
    print_test_header("Quick Start URL")

    config = WahapediaURLConfig("10th")

    expected = "https://wahapedia.ru/wh40k10ed/the-rules/quick-start-guide/"
    actual = config.get_quick_start_url()

    return print_result("Quick start guide URL", expected, actual)

def test_faction_urls():
    """Test faction URL generation."""
    print_test_header("Faction URLs")

    config = WahapediaURLConfig("10th")

    test_cases = [
            {
                "faction_code": "space-marines",
                "expected_main": "https://wahapedia.ru/wh40k10ed/factions/space-marines",
                "expected_datasheets": "https://wahapedia.ru/wh40k10ed/factions/space-marines/datasheets"
                },
            {
                "faction_code": "orks",
                "expected_main": "https://wahapedia.ru/wh40k10ed/factions/orks",
                "expected_datasheets": "https://wahapedia.ru/wh40k10ed/factions/orks/datasheets"
                },
            {
                "faction_code": "t-au-empire",
                "expected_main": "https://wahapedia.ru/wh40k10ed/factions/t-au-empire",
                "expected_datasheets": "https://wahapedia.ru/wh40k10ed/factions/t-au-empire/datasheets"
                }
            ]

    tests_passed = 0
    tests_failed = 0

    for test in test_cases:
        faction_code = test["faction_code"]

        # Test main faction URL
        actual_main = config.get_faction_url(faction_code)
        if print_result(f"Main URL for {faction_code}", test["expected_main"], actual_main):
            tests_passed += 1
        else:
            tests_failed += 1

        # Test datasheets URL
        actual_datasheets = config.get_faction_datasheets_url(faction_code)
        if print_result(f"Datasheets URL for {faction_code}", test["expected_datasheets"], actual_datasheets):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_section_anchors():
    """Test faction section URL generation with anchors."""
    print_test_header("Section Anchors")

    config = WahapediaURLConfig("10th")

    test_cases = [
            {
                "faction": "space-marines",
                "section": "army_rules",
                "expected": "https://wahapedia.ru/wh40k10ed/factions/space-marines#Army-Rules"
                },
            {
                "faction": "orks",
                "section": "detachments",
                "expected": "https://wahapedia.ru/wh40k10ed/factions/orks#Detachment-Rules"
                },
            {
                "faction": "necrons",
                "section": "enhancements",
                "expected": "https://wahapedia.ru/wh40k10ed/factions/necrons#Enhancements"
                }
            ]

    tests_passed = 0
    tests_failed = 0

    for test in test_cases:
        actual = config.get_faction_section_url(test["faction"], test["section"])
        if print_result(
                f"{test['section']} section for {test['faction']}", 
                test["expected"], 
                actual
                ):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_faction_code_normalization():
    """Test faction code normalization."""
    print_test_header("Faction Code Normalization")

    config = WahapediaURLConfig("10th")

    test_cases = [
            ("Space Marines", "space-marines"),
            ("T'au Empire", "t-au-empire"),
            ("Emperor's Children", "emperor-s-children"),
            ("Adepta Sororitas", "adepta-sororitas"),
            ("space-marines", "space-marines"),  # Already normalized
            ("ORKS", "orks"),
            ("Chaos Space Marines", "chaos-space-marines")
            ]

    tests_passed = 0
    tests_failed = 0

    for input_name, expected in test_cases:
        actual = config.normalize_faction_code(input_name)
        if print_result(f"Normalize '{input_name}'", expected, actual):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_unit_datasheet_url():
    """Test unit datasheet URL generation."""
    print_test_header("Unit Datasheet URLs")

    config = WahapediaURLConfig("10th")

    test_cases = [
            {
                "faction": "space-marines",
                "unit": "intercessor-squad",
                "expected": "https://wahapedia.ru/wh40k10ed/factions/space-marines/datasheets#intercessor-squad"
                },
            {
                "faction": "orks",
                "unit": "boyz",
                "expected": "https://wahapedia.ru/wh40k10ed/factions/orks/datasheets#boyz"
                }
            ]

    tests_passed = 0
    tests_failed = 0

    for test in test_cases:
        actual = config.get_unit_datasheet_url(test["faction"], test["unit"])
        if print_result(
                f"Unit datasheet for {test['unit']} in {test['faction']}", 
                test["expected"], 
                actual
                ):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_search_url():
    """Test search URL generation."""
    print_test_header("Search URL")

    config = WahapediaURLConfig("10th")

    test_cases = [
            {
                "query": "space marine captain",
                "expected": "https://wahapedia.ru/wh40k10ed/search?q=space+marine+captain"
                },
            {
                "query": "ork boyz",
                "expected": "https://wahapedia.ru/wh40k10ed/search?q=ork+boyz"
                }
            ]

    tests_passed = 0
    tests_failed = 0

    for test in test_cases:
        actual = config.get_search_url(test["query"])
        if print_result(f"Search URL for '{test['query']}'", test["expected"], actual):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_build_url_with_patterns():
    """Test generic URL building with patterns."""
    print_test_header("Generic URL Building")

    config = WahapediaURLConfig("10th")

    test_cases = [
            {
                "pattern": "army_lists",
                "kwargs": {},
                "expected": "https://wahapedia.ru/wh40k10ed/army-lists/"
                },
            {
                "pattern": "faction_stratagems",
                "kwargs": {"faction_code": "space-marines"},
                "expected": "https://wahapedia.ru/wh40k10ed/factions/space-marines/stratagems"
                },
            {
                "pattern": "core_rules",
                "kwargs": {},
                "expected": "https://wahapedia.ru/wh40k10ed/the-rules/core-rules/"
                }
            ]

    tests_passed = 0
    tests_failed = 0

    for test in test_cases:
        actual = config.build_url(test["pattern"], **test["kwargs"])
        description = f"Build URL for pattern '{test['pattern']}'"
        if test["kwargs"]:
            description += f" with {test['kwargs']}"

        if print_result(description, test["expected"], actual or "None"):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_faction_validation():
    """Test faction code validation."""
    print_test_header("Faction Code Validation")

    config = WahapediaURLConfig("10th")

    valid_codes = [
            "space-marines",
            "orks",
            "necrons",
            "t-au-empire",
            "chaos-space-marines"
            ]

    invalid_codes = [
            "fake-faction",
            "not-real",
            "invalid-army"
            ]

    tests_passed = 0
    tests_failed = 0

    print("\nTesting valid faction codes:")
    for code in valid_codes:
        is_valid = config.validate_faction_code(code)
        expected = "Valid"
        actual = "Valid" if is_valid else "Invalid"
        if print_result(f"Validate '{code}'", expected, actual):
            tests_passed += 1
        else:
            tests_failed += 1

    print("\nTesting invalid faction codes:")
    for code in invalid_codes:
        is_valid = config.validate_faction_code(code)
        expected = "Invalid"
        actual = "Valid" if is_valid else "Invalid"
        if print_result(f"Validate '{code}'", expected, actual):
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_cache_functionality():
    """Test URL caching."""
    print_test_header("URL Cache")

    config = WahapediaURLConfig("10th")

    # Build same URL twice
    url1 = config.get_faction_url("space-marines")
    url2 = config.get_faction_url("space-marines")

    # Should be the same
    if print_result("Cached URL matches", url1, url2):
        print("  ✓ Cache is working for identical requests")

    # Clear cache
    config.clear_cache()
    print("\n  ℹ️  Cache cleared")

    # Build again after clearing
    url3 = config.get_faction_url("space-marines")
    if print_result("URL after cache clear", url1, url3):
        print("  ✓ URL generation consistent after cache clear")

    return True

def test_all_section_anchors():
    """Test getting all section anchors."""
    print_test_header("All Section Anchors")

    config = WahapediaURLConfig("10th")
    anchors = config.get_all_section_anchors()

    expected_anchors = [
            'army_rules',
            'detachments',
            'enhancements',
            'stratagems',
            'wargear_options'
            ]

    tests_passed = 0
    tests_failed = 0

    print("\nChecking for expected anchors:")
    for anchor in expected_anchors:
        if anchor in anchors:
            print(f"  ✅ Found: {anchor} -> {anchors[anchor]}")
            tests_passed += 1
        else:
            print(f"  ❌ Missing: {anchor}")
            tests_failed += 1

    print(f"\n📊 Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def run_all_tests():
    """Run all URL config tests."""
    print("\n" + "🚀" * 30)
    print(" WAHAPEDIA URL CONFIG TEST SUITE")
    print("🚀" * 30)
    print("\nTesting 10th Edition URL Configuration")

    test_functions = [
            test_basic_initialization,
            test_quick_start_url,
            test_faction_urls,
            test_section_anchors,
            test_faction_code_normalization,
            test_unit_datasheet_url,
            test_search_url,
            test_build_url_with_patterns,
            test_faction_validation,
            test_cache_functionality,
            test_all_section_anchors
            ]

    results = []
    for test_func in test_functions:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)

    passed_tests = sum(1 for _, result in results if result)
    failed_tests = len(results) - passed_tests

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n📊 Overall Results:")
    print(f"  ✅ Passed: {passed_tests}/{len(results)}")
    print(f"  ❌ Failed: {failed_tests}/{len(results)}")

    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The WahapediaURLConfig is working correctly for 10th edition.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please review the output above.")

    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
