"""
Database adapter factory
Returns the appropriate database adapter based on configuration.
Precedence: PostgreSQL > MongoDB > JSON (only one backend active).
"""

import os
from .base import DatabaseAdapter
from .json_adapter import JSONAdapter
from .mongodb_adapter import MongoDBAdapter
from .postgresql_adapter import PostgreSQLAdapter


def get_database_adapter() -> DatabaseAdapter:
    """
    Factory function to get the appropriate database adapter
    based on environment configuration.

    Returns:
        DatabaseAdapter: PostgreSQLAdapter, MongoDBAdapter, or JSONAdapter
    """
    use_postgresql = os.getenv('USE_POSTGRESQL', 'false').lower() == 'true'
    use_mongodb = os.getenv('USE_MONGODB', 'false').lower() == 'true'

    if use_postgresql:
        database_url = os.getenv(
            'DB_URL',
            os.getenv('DATABASE_URL', 'postgresql://localhost:5432/smart_attendance')
        )
        return PostgreSQLAdapter(connection_url=database_url)
    if use_mongodb:
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        mongodb_database = os.getenv('MONGODB_DATABASE', 'smart_attendance')
        return MongoDBAdapter(
            connection_uri=mongodb_uri,
            database_name=mongodb_database
        )
    base_dir = os.getenv('JSON_BASE_DIR', 'static')
    return JSONAdapter(base_dir=base_dir)
