# MCP Docs Server

A small Python project that exposes a FastMCP tool for fetching documentation from supported libraries and returning clean, readable text. The project includes a sample client that connects to the server, calls the tool, and uses Groq to answer the user's question using the retrieved documentation as context.

## What this project does

- Runs an MCP server with the `get_docs` tool
- Searches the web through the Serper API
- Fetches documentation pages and strips HTML into readable text
- Supports these libraries:
  - `langchain`
  - `llama-index`
  - `openai`
  - `uv`
- Provides a sample client for interacting with the server

## Project structure

- `mcp_server.py` — MCP server and documentation-fetching tool
- `client.py` — example client that connects to the MCP server
- `utils.py` — HTML cleanup and LLM response helpers
- `pyproject.toml` — Python dependencies and project metadata
- `.env` — local environment variables for API keys
- `README.md` — project documentation

## Requirements

- Python 3.13+
- `uv` package manager

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create a `.env` file in the project root and add your API keys:

   ```env
   SERPER_API_KEY=your_serper_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. Run the MCP server:

   ```bash
   uv run mcp_server.py
   ```

4. Run the example client:

   ```bash
   uv run client.py
   ```

## Example usage

The client currently asks:

- `How to use publish a package with uv on gitlab?`
- Library: `uv`

The server will search documentation for the selected library, collect sources, and return the extracted content for the client to use as context.

## Notes

- The `.env` file is meant for local development only and should not be committed to GitHub.
- The project uses the `FastMCP` library, `httpx`, `python-dotenv`, `trafilatura`, and `groq`.
