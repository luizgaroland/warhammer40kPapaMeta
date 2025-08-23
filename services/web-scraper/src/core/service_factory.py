"""
Service Factory
"""
import sys
sys.path.insert(0, "/app/src")

from typing import Dict, Type, Optional, List
from core.base_scraper_service import BaseScraperService
from core.scraper_context import ScraperContext

class ServiceFactory:
    def __init__(self):
        self.context = ScraperContext()
        self._services = {}
        self._register_default_services()

    def _register_default_services(self):
        try:
            from services.wahapedia.wahapedia_service import WahapediaService
            self.register_service("wahapedia", WahapediaService)
        except ImportError as e:
            print(f"Could not import WahapediaService: {e}")

    def register_service(self, name: str, service_class: Type[BaseScraperService]):
        if not issubclass(service_class, BaseScraperService):
            raise ValueError(f"{service_class} must extend BaseScraperService")
        self._services[name] = service_class

    def create_service(self, service_name: Optional[str] = None) -> BaseScraperService:
        name = service_name or "wahapedia"
        if name not in self._services:
            available = list(self._services.keys())
            raise ValueError(f"Service {name} not registered. Available: {available}")
        service_class = self._services[name]
        return service_class(self.context)

    def get_available_services(self) -> List[str]:
        return list(self._services.keys())

    def get_default_service(self) -> BaseScraperService:
        return self.create_service()

_factory_instance = None

def get_service_factory() -> ServiceFactory:
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ServiceFactory()
    return _factory_instance
