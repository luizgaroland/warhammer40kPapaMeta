#!/usr/bin/env python3
"""
Test suite for Service Factory and scraper services
"""
import sys
sys.path.insert(0, "/app/src")

print("Starting Service Factory Tests...")
print("=" * 60)

try:
    from core.service_factory import ServiceFactory, get_service_factory
    from core.base_scraper_service import BaseScraperService
    print("✅ Successfully imported modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_service_factory_creation():
    """Test that service factory can be created."""
    print("\n📝 Test 1: Service Factory Creation")
    print("-" * 40)

    try:
        factory = ServiceFactory()
        print("  ✓ Factory instance created")

        services = factory.get_available_services()
        print(f"  ✓ Available services: {services}")

        if "wahapedia" in services:
            print("  ✓ Wahapedia service is registered")
        else:
            print("  ✗ Wahapedia service NOT found!")
            return False

        print("  ✅ Test PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Test FAILED: {e}")
        return False

def test_wahapedia_service_creation():
    """Test creating Wahapedia service."""
    print("\n📝 Test 2: Wahapedia Service Creation")
    print("-" * 40)

    try:
        factory = get_service_factory()
        print("  ✓ Got factory singleton")

        service = factory.create_service("wahapedia")
        print(f"  ✓ Created service: {service.__class__.__name__}")

        if isinstance(service, BaseScraperService):
            print("  ✓ Service is instance of BaseScraperService")
        else:
            print("  ✗ Service is NOT a BaseScraperService!")
            return False

        print(f"  ✓ Service name: {service.service_name}")
        print(f"  ✓ Version ID: {service.version_id}")

        if service.version_id == "10th":
            print("  ✓ Version matches expected (10th)")
        else:
            print(f"  ✗ Version mismatch! Expected: 10th, Got: {service.version_id}")
            return False

        print("  ✅ Test PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_default_service():
    """Test getting default service from config."""
    print("\n📝 Test 3: Default Service")
    print("-" * 40)

    try:
        factory = get_service_factory()
        print("  ✓ Got factory singleton")

        service = factory.get_default_service()
        print(f"  ✓ Got default service: {service.service_name}")

        if service is not None:
            print("  ✓ Default service exists")
        else:
            print("  ✗ Default service is None!")
            return False

        print("  ✅ Test PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Test FAILED: {e}")
        return False

def test_wahapedia_service_methods():
    """Test Wahapedia service methods."""
    print("\n📝 Test 4: Wahapedia Service Methods")
    print("-" * 40)

    try:
        factory = get_service_factory()
        service = factory.create_service("wahapedia")
        print("  ✓ Created Wahapedia service")

        # Test get_factions method
        print("\n  Testing get_factions()...")
        factions = service.get_factions()

        if factions:
            print(f"  ✓ Retrieved {len(factions)} factions")
            print("  Sample factions:")
            for i, faction in enumerate(factions[:3], 1):
                print(f"    {i}. {faction.get(name, Unknown)} ({faction.get(code, N/A)})")

                # Check required fields
                if "source" in faction:
                    print(f"       - Source: {faction[source]}")
                if "version_id" in faction:
                    print(f"       - Version: {faction[version_id]}")
        else:
            print("  ⚠️  No factions retrieved")

        # Test get_army_rules method
        print("\n  Testing get_army_rules()...")
        if factions:
            test_faction = factions[0]
            army_rules = service.get_army_rules(test_faction)
            if army_rules:
                print(f"  ✓ Got army rules for {test_faction.get(name)}")
                print(f"    - Rule: {army_rules}")
            else:
                print(f"  ℹ️  No army rules returned (may not be implemented)")

        print("  ✅ Test PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all service factory tests."""
    print("\n" + "🚀" * 30)
    print(" SERVICE FACTORY TEST SUITE")
    print("🚀" * 30)

    tests = [
            test_service_factory_creation,
            test_wahapedia_service_creation,
            test_default_service,
            test_wahapedia_service_methods
            ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Unexpected error in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check output above for details.")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
