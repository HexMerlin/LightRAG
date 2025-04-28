"""
Knowledge Graph Import Script for LightRAG

This script imports a knowledge graph into the LightRAG system using both Neo4j for graph storage
and PostgreSQL for vector and key-value storage. It performs a complete reset of all databases
and working directories before import to ensure consistent results across multiple runs.

Steps:
1. Load environment variables from .env file
2. Clean all databases (Neo4j and PostgreSQL)
3. Clean working directory (remove all files and subdirectories)
4. Test Neo4j connection
5. Load and validate knowledge graph from JSON file
6. Display knowledge graph stats (entities, relationships, chunks)
7. Create embedding function for Ollama
8. Initialize LightRAG with Neo4JStorage for graph storage
9. Import knowledge graph using LightRAG's ainsert_custom_kg method
10. Verify Neo4j has been populated with entities and relationships
11. Display entity types and relationship counts

Usage:
    python my_extensions/import_kg.py

Note:
    - Requires Neo4j and PostgreSQL to be running
    - Requires Ollama server with bge-m3 embedding model
    - Clears all existing data in databases and working directory
"""

import os
import json
import sys
import asyncio
import shutil
from pathlib import Path
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.ollama import ollama_embed, ollama_model_complete
import traceback
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Override Neo4j URI to use localhost
os.environ["NEO4J_URI"] = "bolt://localhost:7687"

# Override database connection settings to use localhost when running from host
NEO4J_URI = "bolt://localhost:7687"  # Override to use localhost
POSTGRES_HOST = "localhost"  # Override to use localhost

# Handle the async nature of some operations
import nest_asyncio
nest_asyncio.apply()

# Knowledge graph file paths - using forward slashes for cross-platform compatibility
# Uncomment ONE of these paths to switch between mini or full knowledge graph
KG_PATH = Path("C:/Dev/HexMerlin/clarity/json_output/knowledge_graph_MINI.json")  # Mini knowledge graph
# KG_PATH = Path("C:/Dev/HexMerlin/clarity/json_output/knowledge_graph.json")      # Full knowledge graph

# LightRAG default working directory - using absolute path from project root
# This ensures it works correctly when script is run from root folder
WORKING_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_storage")))

# Embedding model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
EMBEDDING_HOST = "http://127.0.0.1:11434"  # Explicitly set to localhost

# LLM model configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:latest")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "32768"))

# Neo4j configuration from .env
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo-neo-")

# PostgreSQL configuration from .env
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "lightrag")

# Print connection details for debugging
print(f"Neo4j connection details:")
print(f"  URI: {NEO4J_URI}")
print(f"  Username: {NEO4J_USERNAME}")
print(f"  Password: {'*' * len(NEO4J_PASSWORD) if NEO4J_PASSWORD else 'not set'}")

print(f"\nPostgreSQL connection details:")
print(f"  Host: {POSTGRES_HOST}")
print(f"  Port: {POSTGRES_PORT}")
print(f"  Database: {POSTGRES_DATABASE}")
print(f"  Username: {POSTGRES_USER}")
print(f"  Password: {'*' * len(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else 'not set'}\n")

def clean_all_databases_and_storage():
    """Clean all databases (Neo4j, PostgreSQL) and storage directories"""
    print("\n=== CLEANING ALL DATABASES AND STORAGE ===")
    
    # 1. Clean Neo4j database
    print("Cleaning Neo4j database...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"  Found {count} nodes in Neo4j")
            
            session.run("MATCH (n) DETACH DELETE n")
            print("  All nodes and relationships deleted from Neo4j")
            
            # Verify clean
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"  Neo4j now has {count} nodes")
        driver.close()
    except Exception as e:
        print(f"  ERROR: Failed to clean Neo4j database: {e}")
        print(traceback.format_exc())
    
    # 2. Clean PostgreSQL if we're using it for vector storage
    if os.getenv("LIGHTRAG_VECTOR_STORAGE") == "PGVectorStorage":
        print("Cleaning PostgreSQL vector storage...")
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DATABASE
            )
            with conn.cursor() as cursor:
                # List all tables in lightrag schema
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND 
                          table_name LIKE 'lightrag_%'
                """)
                tables = cursor.fetchall()
                
                if tables:
                    print(f"  Found {len(tables)} LightRAG tables in PostgreSQL")
                    for table in tables:
                        tablename = table[0]
                        cursor.execute(f"TRUNCATE TABLE {tablename} CASCADE")
                        print(f"  Truncated table: {tablename}")
                else:
                    print("  No LightRAG tables found in PostgreSQL")
                
                conn.commit()
            conn.close()
            print("  PostgreSQL cleaned successfully")
        except Exception as e:
            print(f"  WARNING: Could not clean PostgreSQL: {e}")
            print("  Will continue with import, tables will be created if needed")
    
    # 3. Clean working directory
    print(f"Cleaning working directory: {WORKING_DIR}")
    try:
        if os.path.exists(WORKING_DIR):
            # Remove all files and subdirectories
            for item in os.listdir(WORKING_DIR):
                item_path = os.path.join(WORKING_DIR, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"  Removed file: {item}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"  Removed directory: {item}")
            print(f"  Working directory {WORKING_DIR} cleared")
        else:
            os.makedirs(WORKING_DIR)
            print(f"  Created new working directory: {WORKING_DIR}")
    except Exception as e:
        print(f"  ERROR: Failed to clean working directory: {e}")
        print(traceback.format_exc())
    
    print("=== CLEANING COMPLETED ===\n")

def test_neo4j_connection():
    """Test connection to Neo4j"""
    try:
        print(f"Testing connection to Neo4j at {NEO4J_URI}...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"Neo4j connection successful. Current node count: {count}")
        driver.close()
        return True
    except Exception as e:
        print(f"ERROR: Failed to connect to Neo4j database: {e}")
        print(traceback.format_exc())
        return False

def load_knowledge_graph(file_path):
    """Load knowledge graph from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
        
        # Validate entity data
        for entity in kg_data.get("entities", []):
            if "entity_id" not in entity:
                entity["entity_id"] = entity.get("entity_name", "unknown")
                
        # Validate chunk data
        for chunk in kg_data.get("chunks", []):
            if "chunk_order_index" not in chunk and "source_chunk_index" in chunk:
                chunk["chunk_order_index"] = chunk["source_chunk_index"]
            
        return kg_data
    except FileNotFoundError:
        print(f"Error: Knowledge graph file not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading knowledge graph file: {e}")
        sys.exit(1)

async def test_embedding(embedding_func):
    """Test the embedding function with a simple text"""
    try:
        print("Testing Ollama embedding function...")
        test_text = ["Test embedding function"]
        test_result = await embedding_func.func(test_text)
        print(f"Embedding test successful. Vector dimension: {len(test_result[0])}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to test embedding function: {e}")
        print(traceback.format_exc())
        return False

async def async_main():
    """Async main function to import the knowledge graph"""
    print("Using environment settings from .env file...")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"Storage type: {os.getenv('LIGHTRAG_GRAPH_STORAGE', 'Not set')}")
    
    # First, clean everything to ensure a fresh start
    clean_all_databases_and_storage()
    
    # Check Neo4j connection
    if not test_neo4j_connection():
        print("ERROR: Cannot proceed without Neo4j connection. Please check your Neo4j container.")
        return
    
    # Check if knowledge graph file exists
    if not os.path.exists(KG_PATH):
        print(f"Error: Knowledge graph file not found at {KG_PATH}")
        return
    
    # Determine which graph we're using
    is_mini = "MINI" in str(KG_PATH)
    graph_type = "miniature" if is_mini else "full"
    
    print(f"Loading {graph_type} knowledge graph from: {KG_PATH}")
    kg_data = load_knowledge_graph(KG_PATH)
    
    # Display summary
    print(f"Knowledge graph contains:")
    print(f" - {len(kg_data.get('entities', []))} entities")
    print(f" - {len(kg_data.get('relationships', []))} relationships")
    print(f" - {len(kg_data.get('chunks', []))} text chunks")
    
    try:
        # Create embedding function for Ollama
        embedding_func = EmbeddingFunc(
            embedding_dim=EMBEDDING_DIM,
            max_token_size=MAX_TOKENS,
            func=lambda texts: ollama_embed(
                texts,
                embed_model=EMBEDDING_MODEL,
                host=EMBEDDING_HOST
            )
        )
        
        # Test embedding function
        if not await test_embedding(embedding_func):
            print("ERROR: Embedding function test failed. Cannot proceed with import.")
            return
        
        # Initialize LightRAG
        print(f"Initializing LightRAG with working directory: {WORKING_DIR}")
        rag = LightRAG(
            working_dir=str(WORKING_DIR),  # Convert Path to string
            embedding_func=embedding_func,
            llm_model_func=ollama_model_complete,
            llm_model_name=LLM_MODEL,
            llm_model_max_token_size=MAX_TOKENS,
            llm_model_kwargs={
                "host": EMBEDDING_HOST,
                "options": {"num_ctx": MAX_TOKENS}
            },
            graph_storage="Neo4JStorage"  # Explicitly set graph storage to Neo4JStorage
        )
        
        # Insert knowledge graph using sync method
        print(f"Importing {graph_type} knowledge graph into LightRAG...")
        try:
            # Use the sync method
            rag.insert_custom_kg(kg_data)
            print("Knowledge graph successfully imported!")
            
            # Verify Neo4j has been populated
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"Neo4j node count after import: {count}")
                
                if count > 0:
                    # Get entity types
                    result = session.run("MATCH (n) RETURN DISTINCT labels(n) as labels")
                    labels = [record["labels"] for record in result]
                    print(f"Entity types in Neo4j: {labels}")
                    
                    # Get relationship types
                    result = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as rel_type, count(r) as count")
                    rel_types = {record["rel_type"]: record["count"] for record in result}
                    print(f"Relationship types in Neo4j: {rel_types}")
                else:
                    print("WARNING: No nodes found in Neo4j after import!")
                    print("Manually creating a test node to verify Neo4j write access...")
                    session.run("CREATE (n:Test {name: 'test_node'}) RETURN n")
                    result = session.run("MATCH (n:Test) RETURN count(n) as count")
                    count = result.single()["count"]
                    print(f"Test node count: {count}")
                    if count > 0:
                        print("Neo4j write access works correctly, but LightRAG failed to populate the graph.")
                    else:
                        print("Could not write to Neo4j database. Check permissions.")
            driver.close()
            
            print("You can now start the LightRAG server to view the knowledge graph in the WebUI.")
        except Exception as e:
            print(f"ERROR during knowledge graph import: {e}")
            print(traceback.format_exc())
            
    except ConnectionRefusedError:
        print(f"Error: Could not connect to Ollama at {EMBEDDING_HOST}. Make sure Ollama server is running.")
    except Exception as e:
        print(f"Error initializing LightRAG or importing knowledge graph: {e}")
        print(traceback.format_exc())

def main():
    """Main function that runs the async main function"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main() 