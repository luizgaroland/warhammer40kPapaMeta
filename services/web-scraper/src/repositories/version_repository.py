# services/web-scraper/src/repositories/version_repository.py
"""
Version Repository for database operations related to game versions
"""
from typing import Optional, Dict, Any
from sqlalchemy import text
from src.database import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class VersionRepository:
    """
    Handles all database operations for game versions.
    This is the only place where version-related database queries happen.
    """

    def __init__(self, version_id: str):
        """
        Initialize repository with a version ID.

        Args:
            version_id: Version identifier from .env (e.g., "10th")
        """
        self.version_id = version_id
        self._ensure_db_initialized()

    def _ensure_db_initialized(self):
        """Ensure database is initialized."""
        if not db_manager.engine:
            db_manager.initialize()

    def get_version_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the current version snapshot from database.

        Returns:
            Dictionary with snapshot data or None if not found
        """
        try:
            with db_manager.engine.connect() as conn:
                query = text("""
                    SELECT
                        vs.id as snapshot_id,
                        vs.effective_date,
                        vs.is_current,
                        wmv.id as major_version_id,
                        wmv.version_number,
                        wmv.name as major_version_name,
                        wmv.release_date
                    FROM warhammer_major_versions wmv
                    LEFT JOIN version_snapshots vs ON vs.major_version_id = wmv.id
                    WHERE wmv.version_number = :version_id
                    AND vs.is_current = TRUE
                    LIMIT 1
                """)

                result = conn.execute(
                        query,
                        {"version_id": self.version_id}
                        ).first()

                if result:
                    return {
                            'snapshot_id': result.snapshot_id,
                            'major_version_id': result.major_version_id,
                            'version_number': result.version_number,
                            'version_name': result.major_version_name,
                            'effective_date': result.effective_date.isoformat() if result.effective_date else None,
                            'release_date': result.release_date.isoformat() if result.release_date else None,
                            'is_current': result.is_current
                            }

                logger.warning(
                        "no_version_snapshot_found",
                        version_id=self.version_id
                        )
                return None

        except Exception as e:
            logger.error("failed_to_get_version_snapshot", error=str(e))
            return None

    def get_or_create_version(self) -> Optional[int]:
        """
        Get or create the major version in database.

        Returns:
            major_version_id or None if failed
        """
        try:
            with db_manager.engine.connect() as conn:
                # First try to get existing
                query = text("""
                    SELECT id FROM warhammer_major_versions 
                    WHERE version_number = :version_id
                """)

                result = conn.execute(
                        query,
                        {"version_id": self.version_id}
                        ).first()

                if result:
                    return result.id

                # Create if doesn't exist
                insert_query = text("""
                    INSERT INTO warhammer_major_versions 
                    (version_number, name, release_date, is_current)
                    VALUES (:version_id, :name, CURRENT_DATE, TRUE)
                    RETURNING id
                """)

                result = conn.execute(
                        insert_query,
                        {
                            "version_id": self.version_id,
                            "name": f"{self.version_id} Edition"
                            }
                        )
                conn.commit()

                return result.scalar()

        except Exception as e:
            logger.error("failed_to_get_or_create_version", error=str(e))
            return None
