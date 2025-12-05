# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LENA Agent is a LangGraph-based AI agent that integrates RAG, HTTP requests, web search (Tavily), and Context7 MCP. It operates in three modes:
- **MCP Server** (`server.py`): For Claude Desktop via stdio/JSON-RPC
- **REST API Server** (`api_server.py`): OpenAI-compatible HTTP API at `localhost:8000`
- **Demo Server** (`demo/server.py`): Web UI for testing the API at `localhost:3000`

## Common Commands

```bash
# Install dependencies
uv sync

# Run MCP server (for Claude Desktop)
uv run server.py

# Run REST API server
uv run api_server.py

# Run demo server (requires API server running)
uv run python -m demo.server
# or after install: lena-agent-demo

# Run tests
uv run test_agent.py        # Basic agent tests (RAG, HTTP, Tavily, Context7)
uv run test_api.py          # API server tests

# Docker
docker compose up lena-agent --build      # MCP mode
docker compose up lena-agent-api --build  # API mode
docker compose up lena-agent-demo --build # Demo mode (requires API)
docker compose up lena-agent-full --build # API + Demo combined
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Entry Points                          │
│  server.py (MCP)              api_server.py (REST API)      │
│       │                              │                       │
│       └──────────┬───────────────────┘                       │
│                  ▼                                           │
│           agent/graph.py                                     │
│    (LangGraph StateGraph with agent + tools nodes)          │
│                  │                                           │
│    ┌─────────────┼─────────────┬─────────────┐              │
│    ▼             ▼             ▼             ▼              │
│ agent/rag.py  agent/tools.py  agent/context7.py             │
│ (Hybrid RAG)  (http_request)  (Context7 MCP)                │
│               (tavily_search)                                │
└─────────────────────────────────────────────────────────────┘
```

### Key Files

- **`agent/graph.py`**: LangGraph workflow definition. Contains `SYSTEM_PROMPT` and loads `config/lena_api_spec.md`. Uses `gpt-4o-mini` model.
- **`agent/rag.py`**: Hybrid retrieval (BM25 + Vector with RRF fusion). Caches embeddings in `chroma_db/`. Set `RAG_ENABLE_RERANK=true` for Flashrank re-ranking.
- **`agent/tools.py`**: HTTP request tool (auto-injects LENA API key) and Tavily search (restricted to `docs.lenalab.org`, `solution.lgcns.com`).
- **`agent/context7.py`**: Wraps Context7 MCP server via `mcp` Python client for Apache/Nginx/Tomcat docs.
- **`agent/state.py`**: AgentState TypedDict for LangGraph.

### Data Flow

1. User query enters via MCP (`ask_agent`) or REST API (`/v1/chat/completions`)
2. `agent/graph.py` processes with LangGraph (agent node -> tool node -> agent node loop)
3. Tools return results, agent synthesizes final response

## Environment Variables

Required in `.env` (see `.env.example`):
- `OPENAI_API_KEY` - Required for RAG embeddings and LLM
- `TAVILY_API_KEY` - Required for web search
- `LENA_API_URL` / `LENA_API_KEY` - Optional, auto-injected into HTTP requests

## Adding LENA API Endpoints

Define endpoints in `config/lena_api_spec.md`. The agent loads this into its system prompt and uses it to determine which API to call.

## RAG Documents

Place `.txt`, `.md`, or `.pdf` files in `docs/` folder. First run builds embeddings (10-30s), subsequent runs use cached `chroma_db/`.
