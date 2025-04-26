# LightRAG Quickstart Guide

## Setup and Launch

1. Open terminal and navigate to the project root:
   ```bash
   cd C:\Dev\HexMerlin\LightRAG
   ```

2. Activate the Python virtual environment:
   ```bash
   .\.venv\Scripts\activate
   ```

3. Start PostgreSQL database (using Docker):
   ```bash
   docker-compose -f PostgreSQL/docker-compose.yml up -d
   ```

4. For graph storage, ensure Neo4j is running:
   ```bash
   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/neo-neo- neo4j:latest
   ```

5. Make sure Ollama is running and pull the embedding model:
   ```bash
   ollama pull bge-m3:latest
   ```

6. Import the miniature knowledge graph:
   ```bash
   python import_kg.py
   ```
   Note: This script will clear any existing vector database files in the rag_storage directory.

7. Start the LightRAG server:
   ```bash
   python -m lightrag.api.lightrag_server
   ```

8. Access the Web UI in your browser:
   ```
   http://localhost:9621
   ```

## Viewing the Knowledge Graph

1. In the Web UI, click on the "Knowledge Graph" tab in the top navigation bar
2. To load the graph, use the dropdown menu in the top-left corner:
   - Select "*" to view all entities
   - Select a specific entity name to focus on that part of the graph
3. The graph will display with nodes colored according to entity types
4. You can:
   - Drag nodes to reposition them
   - Click on nodes to view their properties in the right panel
   - Use the search box to find specific entities
   - Use the controls in the bottom-left to change layout and zoom

Note: The graph is not loaded automatically and requires selecting a label from the dropdown to display.

## Stopping the Server

1. Press `Ctrl+C` in the terminal to stop the server

2. Stop the PostgreSQL database:
   ```bash
   docker-compose -f PostgreSQL/docker-compose.yml down
   ```

3. Stop the Neo4j database:
   ```bash
   docker stop neo4j
   docker rm neo4j
   ```

## Troubleshooting

If you encounter issues with the knowledge graph import:

1. Make sure Ollama is running and the embedding model is installed
2. Check that the knowledge graph JSON file has the correct format with `entity_id` fields
3. Try cleaning the storage directory manually by deleting all files in `./rag_storage` that start with "vdb_"
4. Check the console output for specific error messages

## Important Configuration Notes

- All configuration is in the `.env` file, with minimal workspace settings in `config.ini`
- Default storage directory is `./rag_storage` 
- Default input directory is `./inputs`

The key configuration settings in `.env` are:

```
# For PostgreSQL
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage

# For Neo4j graph storage
LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
```

### Future planned extension: Import Your Own Custom Knowledge Graph

To switch to using the full knowledge graph (when ready):

1. Edit the `import_kg.py` file
2. Comment out the mini graph path:
   ```python
   # KG_PATH = Path("C:/Dev/HexMerlin/clarity/json_output/knowledge_graph_MINI.json")  # Mini knowledge graph
   ```
3. Uncomment the full graph path:
   ```python
   KG_PATH = Path("C:/Dev/HexMerlin/clarity/json_output/knowledge_graph.json")      # Full knowledge graph
   ```
4. Run the script:
   ```bash
   python import_kg.py
   ```

This script reads the knowledge graph from the specified path and imports it into the default LightRAG storage directory (`./rag_storage`).

For database setup details and troubleshooting, see [DATABASE_SETUP.md](./DATABASE_SETUP.md). 