# LightRAG Quickstart Guide

## Setup and Launch

1. Ensure Docker Desktop is running

2. Open terminal and navigate to the project root:

   ```bash
   cd C:\Dev\HexMerlin\LightRAG
   ```

3. Activate the Python virtual environment:

   ```bash
   .\.venv\Scripts\activate
   ```

4. Start PostgreSQL database (using Docker):

   ```bash
   docker-compose -f my_extensions/PostgreSQL/docker-compose.yml up -d
   ```

5. Make sure Ollama service is running and pull the embedding model:

   ```bash
   # Start Ollama service if not already running
   ollama serve
   
   # In a new terminal window, pull the embedding model
   ollama pull bge-m3:latest
   ```

6. Start LightRAG server and Neo4j using the main docker-compose file:

   ```bash
   docker-compose -f my_extensions/docker-compose.yml up -d
   ```

   This single command will:
   - Start the Neo4j database
   - Start the LightRAG server with the web UI
   - Mount necessary data volumes and configuration files

7. Import miniature knowledge graph and other input data in standard way:

 TODO

  
8. Access the Web UI in your browser:

   ```html
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

1. Stop the LightRAG server and Neo4j:

   ```bash
   docker-compose down
   ```

2. Stop the PostgreSQL database:

   ```bash
   docker-compose -f my_extensions/PostgreSQL/docker-compose.yml down
   ```
