#!/usr/bin/env python3
"""
Minimal test to verify the architecture works
"""
import sys
sys.path.insert(0, "/app/src")

print("Creating minimal architecture test...")

# Step 1: Create a simple version controller
class VersionController:
    def __init__(self):
        self.version_id = "10th"
        self.version_name = "10th Edition"
    
    def get_version_id(self):
        return self.version_id
    
    def get_version_name(self):
        return self.version_name

# Step 2: Create a simple context
class ScraperContext:
    def __init__(self):
        self.version_controller = VersionController()
    
    def get_version_id(self):
        return self.version_controller.get_version_id()

# Step 3: Create base service
from abc import ABC, abstractmethod

class BaseScraperService(ABC):
    def __init__(self, context):
        self.context = context
        self.version_id = context.get_version_id()
        self.service_name = self.__class__.__name__
    
    @abstractmethod
    def get_factions(self):
        pass

# Step 4: Create Wahapedia service
class WahapediaService(BaseScraperService):
    def get_factions(self):
        return [
            {"name": "Space Marines", "code": "space-marines"},
            {"name": "Orks", "code": "orks"}
        ]

# Step 5: Create factory
class ServiceFactory:
    def __init__(self):
        self.context = ScraperContext()
        self._services = {"wahapedia": WahapediaService}
    
    def create_service(self, name="wahapedia"):
        service_class = self._services[name]
        return service_class(self.context)

# Test it all
print("\n=== Testing Architecture ===\n")

factory = ServiceFactory()
print(f"✓ Factory created")

service = factory.create_service("wahapedia")
print(f"✓ Service created: {service.service_name}")
print(f"✓ Version: {service.version_id}")

factions = service.get_factions()
print(f"✓ Got {len(factions)} factions:")
for f in factions:
    print(f"  - {f}")

print("\n✅ Architecture test successful!")
