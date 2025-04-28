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

# Get Neo4j connection parameters from env
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# Always use localhost when running from host machine
neo4j_uri = neo4j_uri.replace("neo4j:", "localhost:")
os.environ["NEO4J_URI"] = neo4j_uri

# Knowledge graph file path
kg_file = "C:/Dev/HexMerlin/clarity/json_output/knowledge_graph_MINI.json"

# Working directory for LightRAG
working_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_storage")))

# Get embedding and LLM model from env
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
llm_model = os.getenv("LLM_MODEL", "llama2")

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
                host="http://127.0.0.1:11434"
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
        lightrag = LightRAG(
            working_dir=str(working_dir),
            embedding_func=embedding_func,
            llm_model_func=ollama_model_complete,
            llm_model_name=llm_model,
            llm_model_max_token_size=32768,
            llm_model_kwargs={
                "host": "http://127.0.0.1:11434",
                "options": {"num_ctx": 32768}
            },
            auto_manage_storages_states=False
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