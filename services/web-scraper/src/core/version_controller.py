"""
Version Controller - No external dependencies
"""

class VersionController:
    """Simple version controller with hardcoded values."""
    
    def __init__(self):
        # Hardcoded values - no config dependency
        self.version_id = "10th"
        self.version_name = "10th Edition"
    
    def get_version_id(self):
        return self.version_id
    
    def get_version_name(self):
        return self.version_name
    
    def get_version_info(self):
        return {
            "version_id": self.version_id,
            "version_name": self.version_name
        }
