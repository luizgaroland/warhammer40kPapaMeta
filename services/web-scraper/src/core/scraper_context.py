"""
Scraper Context - No database dependency
"""
import sys
sys.path.insert(0, "/app/src")

from core.version_controller import VersionController

class ScraperContext:
    def __init__(self):
        self.version_controller = VersionController()
        self._snapshot_data = None
    
    def get_version_id(self):
        return self.version_controller.get_version_id()
    
    def get_snapshot_id(self):
        return None
    
    def get_context(self):
        return {
            "version_id": self.version_controller.get_version_id(),
            "version_name": self.version_controller.get_version_name(),
            "snapshot_id": None,
            "has_database": False
        }
