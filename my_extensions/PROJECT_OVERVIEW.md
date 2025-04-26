# LightRAG Project Overview for AI

## Project Context

- Fork of open-source LightRAG (LR)
- Goal: Run LightRAG Server (LRS) with Web UI query functionality
- All custom code in `my_extensions/` folder for clean separation
- Follow standard LightRAG setup patterns to minimize errors

## Core Components (All Run Locally)

- Ollama: Provides LLMs and embedding models
- Neo4j: Knowledge Graph storage
- PostgreSQL: Vector embeddings and other data storage

## Key Concepts

- LightRAG: Retrieval-Augmented Generation system using knowledge graphs and vector embeddings
- **IMPORTANT**: We use ONLY LightRAG Server mode (Web UI/API) - NOT the programmatic Python mode
- LightRAG Server provides a web interface for queries at http://localhost:9621

## Run Procedure

- Follow `my_extensions/QUICKSTART.md` exactly (update if needed, but maintain alignment)
- This document is the authoritative reference for running the system

## Environment Note

Use `env` file for environment settings (not `.env` due to Cursor restrictions)

## Implementation Approach

- Prioritize simplicity and cleanest solutions
- No external dependencies or backward compatibility requirements
- Focus on stable, standard setup aligned with QUICKSTART.md
- Always check custom setup first when troubleshooting errors
