# services/web-scraper/src/database.py
"""
Database connection and management for Wahapedia Scraper
"""
import sys
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Generator

from sqlalchemy import (
    create_engine, text, Engine, 
    Column, Integer, String, DateTime, Boolean, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database_url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        
    def initialize(self) -> bool:
        """Initialize database connection"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # Don't pool connections in container environment
                echo=settings.is_development,  # Log SQL in development
                future=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info("database_connected", postgres_version=version)
                
            return True
            
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("database_test_failed", error=str(e))
            return False
    
    def verify_schema(self) -> dict:
        """Verify that expected tables exist"""
        expected_tables = [
            'warhammer_major_versions',
            'warhammer_updates', 
            'version_snapshots',
            'factions',
            'faction_versions',
            'detachments',
            'enhancements',
            'units',
            'unit_versions',
            'unit_enhancement_compatibility',
            'wargear',
            'unit_wargear_options',
            'wahapedia_scrape_state',
            'source_mappings',
            'scrape_logs',
            'redis_messages'
        ]
        
        results = {}
        
        try:
            with self.engine.connect() as conn:
                # Check which tables exist
                query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                existing_tables = {row[0] for row in conn.execute(query)}
                
                for table in expected_tables:
                    results[table] = table in existing_tables
                
                # Count tables
                total_expected = len(expected_tables)
                total_found = sum(1 for v in results.values() if v)
                
                logger.info(
                    "schema_verification_complete",
                    tables_found=total_found,
                    tables_expected=total_expected,
                    missing=[k for k, v in results.items() if not v]
                )
                
        except Exception as e:
            logger.error("schema_verification_failed", error=str(e))
            
        return results
    
    def create_test_entry(self) -> bool:
        """Create a test entry to verify write permissions"""
        try:
            with self.engine.connect() as conn:
                # Try to insert a test scrape log
                query = text("""
                    INSERT INTO scrape_logs 
                    (source, scrape_type, status, started_at, items_processed)
                    VALUES 
                    (:source, :scrape_type, :status, :started_at, :items_processed)
                    RETURNING id
                """)
                
                result = conn.execute(
                    query,
                    {
                        "source": "test",
                        "scrape_type": "connection_test",
                        "status": "completed",
                        "started_at": datetime.now(),
                        "items_processed": 0
                    }
                )
                conn.commit()
                
                test_id = result.scalar()
                logger.info("database_write_test_successful", test_id=test_id)
                
                # Clean up test entry
                conn.execute(text("DELETE FROM scrape_logs WHERE id = :id"), {"id": test_id})
                conn.commit()
                
                return True
                
        except Exception as e:
            logger.error("database_write_test_failed", error=str(e))
            return False
    
    def get_current_version(self) -> Optional[dict]:
        """Get current game version from database"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT 
                        vs.id as version_snapshot_id,
                        wmv.version_number as major_version,
                        wu.version_code as update_code,
                        wu.name as update_name,
                        vs.effective_date
                    FROM version_snapshots vs
                    JOIN warhammer_major_versions wmv ON vs.major_version_id = wmv.id
                    LEFT JOIN warhammer_updates wu ON vs.update_id = wu.id
                    WHERE vs.is_current = TRUE
                    LIMIT 1
                """)
                
                result = conn.execute(query).first()
                
                if result:
                    return {
                        "snapshot_id": result[0],
                        "major_version": result[1],
                        "update_code": result[2],
                        "update_name": result[3],
                        "effective_date": result[4].isoformat() if result[4] else None
                    }
                
                return None
                
        except Exception as e:
            logger.error("get_current_version_failed", error=str(e))
            return None
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("database_connections_closed")


# Global database manager instance
db_manager = DatabaseManager()


def init_database() -> bool:
    """Initialize the database connection"""
    return db_manager.initialize()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions"""
    with db_manager.get_session() as session:
        yield session


def test_database_connection():
    """Test database connectivity and schema"""
    logger.info("Testing database connection...")
    
    # Initialize connection
    if not db_manager.initialize():
        logger.error("Failed to initialize database connection")
        return False
    
    # Test basic connectivity
    if not db_manager.test_connection():
        logger.error("Database connection test failed")
        return False
    
    logger.info("✓ Database connection successful")
    
    # Verify schema
    schema_results = db_manager.verify_schema()
    missing_tables = [k for k, v in schema_results.items() if not v]
    
    if missing_tables:
        logger.warning(f"Missing tables: {missing_tables}")
        logger.info("Run 'make init-db' to create the schema")
        return False
    
    logger.info("✓ Database schema verified")
    
    # Test write permissions
    if not db_manager.create_test_entry():
        logger.error("Database write test failed")
        return False
    
    logger.info("✓ Database write permissions confirmed")
    
    # Get current version
    version = db_manager.get_current_version()
    if version:
        logger.info(f"✓ Current game version: {version['major_version']} - {version['update_name']}")
    else:
        logger.warning("No current version set in database")
    
    return True
