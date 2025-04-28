"""
Clean All Script for LightRAG

This script performs a complete cleanup of all LightRAG components:
1. Cleans Neo4j database (deletes all nodes and relationships)
2. Cleans PostgreSQL database (truncates all tables)
3. Cleans working directory (removes all files and subdirectories)

Usage:
    python my_extensions/clean_all.py

Note:
    - Requires Neo4j and PostgreSQL to be running
    - This is a destructive operation that will remove all data
"""

import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def clean_neo4j():
    """Clean Neo4j database by removing all nodes and relationships"""
    try:
        # Get Neo4j connection parameters
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        uri = uri.replace("neo4j:", "localhost:")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "neo-neo-")

        # Connect to Neo4j
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Delete all nodes and relationships
        with driver.session() as session:
            result = session.run("MATCH (n) DETACH DELETE n")
            print("✅ Neo4j database cleaned successfully")
        
        driver.close()
    except Exception as e:
        print(f"❌ Failed to clean Neo4j: {str(e)}")
        sys.exit(1)

def clean_postgresql():
    """Clean PostgreSQL database by truncating all tables"""
    try:
        # Get PostgreSQL connection parameters
        host = os.getenv("POSTGRES_HOST", "lightrag_postgres")
        # When running from host machine, use localhost instead of container name
        host = "localhost" if host == "lightrag_postgres" else host
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        database = os.getenv("POSTGRES_DATABASE", "lightrag")

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()

        # Truncate all tables
        for table in tables:
            cursor.execute(f'TRUNCATE TABLE "{table[0]}" CASCADE')
        
        print("✅ PostgreSQL database cleaned successfully")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to clean PostgreSQL: {str(e)}")
        sys.exit(1)

def clean_working_dir():
    """Clean working directory by removing all files and subdirectories"""
    try:
        # Get working directory path
        working_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_storage")))
        
        # Remove directory if it exists
        if working_dir.exists():
            shutil.rmtree(working_dir)
        
        # Create empty directory
        working_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Working directory cleaned successfully")
    except Exception as e:
        print(f"❌ Failed to clean working directory: {str(e)}")
        sys.exit(1)

def main():
    print("Starting cleanup process...")
    clean_neo4j()
    clean_postgresql()
    clean_working_dir()
    print("✅ All cleanup operations completed successfully")

if __name__ == "__main__":
    main() 