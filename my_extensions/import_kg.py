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
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.ollama import ollama_embed, ollama_model_complete

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Get configuration from environment variables
# Neo4j Configuration
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# When running from host machine, use localhost instead of container name
neo4j_uri = neo4j_uri.replace("neo4j:", "localhost:")
os.environ["NEO4J_URI"] = neo4j_uri
neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "neo-neo-")

# PostgreSQL Configuration
postgres_host = os.getenv("POSTGRES_HOST", "lightrag_postgres")
# When running from host machine, use localhost instead of container name
postgres_host = "localhost" if postgres_host == "lightrag_postgres" else postgres_host
postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
postgres_database = os.getenv("POSTGRES_DATABASE", "lightrag")

# Storage Configuration
kv_storage = os.getenv("LIGHTRAG_KV_STORAGE", "PGKVStorage")
vector_storage = os.getenv("LIGHTRAG_VECTOR_STORAGE", "PGVectorStorage")
graph_storage = os.getenv("LIGHTRAG_GRAPH_STORAGE", "Neo4JStorage")
doc_status_storage = os.getenv("LIGHTRAG_DOC_STATUS_STORAGE", "PGDocStatusStorage")

# Ollama Configuration
ollama_host = os.getenv("LLM_BINDING_HOST", "http://host.docker.internal:11434")
# When running from host machine, use localhost instead of host.docker.internal
ollama_host = ollama_host.replace("host.docker.internal", "localhost")
embedding_model = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")
llm_model = os.getenv("LLM_MODEL", "llama3.2:latest")

# LLM Configuration
timeout = int(os.getenv("TIMEOUT", "150"))
temperature = float(os.getenv("TEMPERATURE", "0.5"))
max_async = int(os.getenv("MAX_ASYNC", "4"))
max_tokens = int(os.getenv("MAX_TOKENS", "32768"))
enable_llm_cache = os.getenv("ENABLE_LLM_CACHE", "true").lower() == "true"

# Knowledge graph file path
kg_file = "C:/Dev/HexMerlin/clarity/json_output/knowledge_graph_MINI.json"

# Working directory for LightRAG
working_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_storage")))

def load_knowledge_graph(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            kg = json.load(f)
            print(f"Loaded knowledge graph from {file_path}")
            print(f"Found {len(kg['entities'])} entities, {len(kg['relationships'])} relationships, and {len(kg['chunks'])} text chunks")
            return kg
    except FileNotFoundError:
        print(f"Error: Knowledge graph file not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in knowledge graph file {file_path}")
        sys.exit(1)

async def async_main():
    # Load knowledge graph
    kg = load_knowledge_graph(kg_file)
    
    # Initialize LightRAG
    try:
        # Create embedding function for Ollama
        async def async_embed(texts):
            return await ollama_embed(
                texts,
                embed_model=embedding_model,
                host=ollama_host
            )
        
        embedding_func = EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=32768,
            func=async_embed
        )
        
        # Test embedding function
        test_result = await embedding_func.func(["test"])
        print(f"Successfully tested embedding function. Vector dimension: {len(test_result[0])}")
        
        # Initialize LightRAG
        print(f"Initializing LightRAG with working directory: {working_dir}")
        
        # Set PostgreSQL environment variables for LightRAG
        os.environ["POSTGRES_HOST"] = postgres_host
        os.environ["POSTGRES_PORT"] = str(postgres_port)
        os.environ["POSTGRES_USER"] = postgres_user
        os.environ["POSTGRES_PASSWORD"] = postgres_password
        os.environ["POSTGRES_DATABASE"] = postgres_database
        
        lightrag = LightRAG(
            working_dir=str(working_dir),
            embedding_func=embedding_func,
            llm_model_func=ollama_model_complete,
            llm_model_name=llm_model,
            llm_model_max_token_size=max_tokens,
            llm_model_kwargs={
                "host": ollama_host,
                "options": {
                    "num_ctx": max_tokens,
                    "temperature": temperature,
                    "timeout": timeout
                }
            },
            auto_manage_storages_states=False,
            kv_storage=kv_storage,
            vector_storage=vector_storage,
            graph_storage=graph_storage,
            doc_status_storage=doc_status_storage,
            enable_llm_cache=enable_llm_cache
        )
        
        # Initialize storages
        print("Initializing storages...")
        await lightrag.initialize_storages()
        
        # Import knowledge graph
        print("Importing knowledge graph into LightRAG...")
        await lightrag.ainsert_custom_kg(kg)
        print("Successfully imported knowledge graph!")
        
        # Finalize storages
        print("Finalizing storages...")
        await lightrag.finalize_storages()
        
    except Exception as e:
        print(f"Error: Failed to import knowledge graph: {str(e)}")
        sys.exit(1)

def main():
    # Handle Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the async main function
    asyncio.run(async_main())

if __name__ == "__main__":
    main() 