"""
Base Scraper Service
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseScraperService(ABC):
    def __init__(self, context):
        self.context = context
        self.version_id = context.get_version_id()
        self.service_name = self.__class__.__name__

    @abstractmethod
    def get_factions(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_army_rules(self, faction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_detachments(self, faction: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_enhancements(self, detachment: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_units(self, faction: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_wargear(self, unit: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def validate_faction_dict(self, faction: Dict[str, Any]) -> bool:
        required_fields = ["name", "code"]
        return all(field in faction for field in required_fields)
