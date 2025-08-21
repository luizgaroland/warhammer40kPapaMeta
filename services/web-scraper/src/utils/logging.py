# services/web-scraper/src/utils/logging.py
"""
Logging configuration for Wahapedia Scraper Service
"""
import os
import sys
import logging
import structlog
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "/app/logs",
    service_name: str = "web-scraper",
    enable_json: bool = False
):
    """
    Configure structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        service_name: Name of the service for log identification
        enable_json: Whether to output logs in JSON format
    """
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    log_level_obj = getattr(logging, log_level.upper(), logging.INFO)
    
    # Remove existing handlers
    logging.root.handlers = []
    
    # Console handler with color support for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)
    
    # File handlers
    info_file = os.path.join(log_dir, f"{service_name}.log")
    error_file = os.path.join(log_dir, f"{service_name}.error.log")
    
    # Rotating file handler for all logs
    file_handler = RotatingFileHandler(
        info_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    
    # Format configuration
    if enable_json:
        # JSON format for production
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable format for development
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    # Configure root logger
    logging.basicConfig(
        level=log_level_obj,
        handlers=[console_handler, file_handler, error_handler],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return structlog.get_logger(service_name)


def get_logger(name: str = None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (defaults to caller's module)
    
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary log context"""
    
    def __init__(self, logger, **kwargs):
        self.logger = logger
        self.context = kwargs
        self.token = None
    
    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


class ScrapeLogger:
    """Specialized logger for scraping operations"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("scraper")
        self.start_time = None
        self.stats = {
            "items_processed": 0,
            "items_failed": 0,
            "items_skipped": 0
        }
    
    def start_scrape(self, target: str, scrape_type: str = "full"):
        """Log scrape start"""
        self.start_time = datetime.now()
        self.stats = {
            "items_processed": 0,
            "items_failed": 0,
            "items_skipped": 0
        }
        self.logger.info(
            "scrape_started",
            target=target,
            scrape_type=scrape_type,
            timestamp=self.start_time.isoformat()
        )
    
    def item_processed(self, item_type: str, item_name: str, success: bool = True):
        """Log item processing"""
        if success:
            self.stats["items_processed"] += 1
            self.logger.debug(f"processed_{item_type}", name=item_name)
        else:
            self.stats["items_failed"] += 1
            self.logger.warning(f"failed_{item_type}", name=item_name)
    
    def item_skipped(self, item_type: str, item_name: str, reason: str):
        """Log skipped item"""
        self.stats["items_skipped"] += 1
        self.logger.debug(f"skipped_{item_type}", name=item_name, reason=reason)
    
    def end_scrape(self, success: bool = True):
        """Log scrape completion"""
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        self.logger.info(
            "scrape_completed" if success else "scrape_failed",
            duration_seconds=duration,
            **self.stats
        )
        
        return self.stats
