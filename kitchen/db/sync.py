import asyncio
import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse

import psycopg
from sqlalchemy import inspect, MetaData, Table, Column, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.ddl import CreateTable

from core.config import settings
from db.base import Base

logger = logging.getLogger(__name__)

async def ensure_database_exists() -> bool:
    """
    Check if the database exists and create it if it doesn't.
    
    Returns:
        bool: True if the database was created, False if it already existed
    """
    db_url = settings.SQLALCHEMY_DATABASE_URI
    parsed_url = urlparse(db_url)
    
    # Extract database name from the path
    db_name = parsed_url.path.lstrip('/')
    
    # Create connection string to postgres database
    admin_db_url = f"postgresql://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}/postgres"
    
    try:
        # Connect to the default postgres database
        async with await psycopg.AsyncConnection.connect(admin_db_url, autocommit=True) as conn:
            async with conn.cursor() as cur:
                # Check if our database exists
                await cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = await cur.fetchone()
                
                if not exists:
                    logger.info(f"Database '{db_name}' does not exist. Creating...")
                    # Create database with proper quoting to handle special characters
                    await cur.execute(f'CREATE DATABASE "{db_name}"')
                    logger.info(f"Database '{db_name}' created successfully")
                    return True
                else:
                    logger.info(f"Database '{db_name}' already exists")
                    return False
    except Exception as e:
        logger.error(f"Error ensuring database exists: {str(e)}")
        raise

async def get_existing_tables(engine: AsyncEngine) -> Dict[str, Table]:
    """
    Get all existing tables from the database.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        Dict[str, Table]: Dictionary of table name to Table object
    """
    existing_tables = {}
    
    async with engine.connect() as conn:
        # Define a function to run synchronously that performs the inspection
        def inspect_tables(connection):
            inspector = inspect(connection)
            metadata = MetaData()
            table_names = inspector.get_table_names()
            
            tables = {}
            for table_name in table_names:
                # Get columns
                columns_info = inspector.get_columns(table_name)
                
                # Create Table object with columns
                columns = []
                for col in columns_info:
                    columns.append(Column(col['name'], col['type']))
                
                table = Table(table_name, metadata, *columns)
                tables[table_name] = table
                
            return tables
        
        # Run the inspection function synchronously
        existing_tables = await conn.run_sync(inspect_tables)
    
    return existing_tables

async def sync_models_with_db(engine: AsyncEngine) -> None:
    """
    Synchronize SQLAlchemy models with the database schema.
    
    This function will:
    1. Create missing tables
    2. Add missing columns to existing tables
    
    Args:
        engine: SQLAlchemy async engine
    """
    model_metadata = Base.metadata
    
    # Get existing tables
    existing_tables = await get_existing_tables(engine)
    
    # Find tables to create
    tables_to_create = []
    for table_name, table in model_metadata.tables.items():
        if table_name not in existing_tables:
            tables_to_create.append(table)
    
    # Create missing tables
    if tables_to_create:
        logger.info(f"Creating {len(tables_to_create)} new tables")
        async with engine.begin() as conn:
            # Use run_sync to create tables
            await conn.run_sync(lambda sync_conn: 
                model_metadata.create_all(sync_conn, tables=tables_to_create)
            )
            for table in tables_to_create:
                logger.info(f"Created table: {table.name}")
    
    # Add missing columns to existing tables
    for table_name, model_table in model_metadata.tables.items():
        if table_name in existing_tables:
            existing_table = existing_tables[table_name]
            
            # Find missing columns
            existing_columns = {col.name for col in existing_table.columns}
            model_columns = {col.name: col for col in model_table.columns}
            
            missing_columns = []
            for col_name, column in model_columns.items():
                if col_name not in existing_columns:
                    missing_columns.append((col_name, column))
            
            # Add missing columns
            if missing_columns:
                logger.info(f"Adding {len(missing_columns)} new columns to table '{table_name}'")
                async with engine.begin() as conn:
                    for col_name, column in missing_columns:
                        # Generate ALTER TABLE statement
                        col_type = column.type.compile(engine.dialect)
                        nullable_str = "" if column.nullable else " NOT NULL"
                        default_str = f" DEFAULT {column.default.arg}" if column.default is not None and column.default.arg is not None else ""
                        
                        alter_stmt = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type}{nullable_str}{default_str}'
                        await conn.execute(text(alter_stmt))
                        logger.info(f"Added column '{col_name}' to table '{table_name}'") 