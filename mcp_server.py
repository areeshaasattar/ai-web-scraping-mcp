import os
import sys

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

from utils import clean_html_to_text


# Load environment variables
load_dotenv()


# Create MCP server
mcp = FastMCP("docs")


# Serper API
SERPER_URL = "https://google.serper.dev/search"


# Supported documentation libraries
docs_urls = {
    "langchain": "https://docs.langchain.com",
    "llama-index": "https://docs.llamaindex.ai/en/stable",
    "openai": "https://platform.openai.com/docs",
    "uv": "https://docs.astral.sh/uv",
}


# ---------------------------------------------------------
# Search the web using Serper API
# ---------------------------------------------------------

async def search_web(query: str) -> dict | None:

    payload = {
        "q": query,
        "num": 2,
    }

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            SERPER_URL,
            json=payload,
            headers=headers,
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()


# ---------------------------------------------------------
# Fetch webpage and extract clean text
# ---------------------------------------------------------

async def fetch_url(url: str):

    try:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                timeout=30.0,
                follow_redirects=True,
            )

            # Don't crash the entire tool if a search result is broken
            if response.status_code != 200:

                print(
                    f"Skipping URL: {url} "
                    f"(HTTP {response.status_code})",
                    file=sys.stderr,
                )

                return None

        # Extract readable text from HTML
        cleaned_response = clean_html_to_text(response.text)

        return cleaned_response

    except Exception as e:

        print(
            f"Failed to fetch URL: {url} | Error: {e}",
            file=sys.stderr,
        )

        return None


# ---------------------------------------------------------
# MCP Tool: Get documentation
# ---------------------------------------------------------

@mcp.tool()
async def get_docs(query: str, library: str):

    # Check whether library is supported
    if library not in docs_urls:

        raise ValueError(
            f"Library '{library}' not supported by this tool. "
            f"Supported libraries: {list(docs_urls.keys())}"
        )

    # Restrict Google/Serper search to the selected documentation
    search_query = f"site:{docs_urls[library]} {query}"

    print(
        f"SEARCH QUERY: {search_query}",
        file=sys.stderr,
    )

    # Search the web
    results = await search_web(search_query)

    print(
        f"SEARCH RESULTS: {results}",
        file=sys.stderr,
    )

    # Check if Serper returned organic results
    if not results or not results.get("organic"):

        print(
            "NO SEARCH RESULTS FOUND",
            file=sys.stderr,
        )

        return "No results found."

    # Store extracted documentation
    text_parts = []

    # Process each search result
    for result in results["organic"]:

        # Serper uses lowercase "link"
        link = result.get("link", "")

        print(
            f"FOUND LINK: {link}",
            file=sys.stderr,
        )

        # Skip result if URL is missing
        if not link:

            continue

        # Fetch webpage
        raw = await fetch_url(link)

        print(
            f"EXTRACTED TEXT LENGTH: {len(raw) if raw else 0}",
            file=sys.stderr,
        )

        # Add extracted content
        if raw:

            labeled = (
                f"SOURCE: {link}\n\n"
                f"{raw}"
            )

            text_parts.append(labeled)

    # Debug information
    print(
        f"TOTAL SOURCES: {len(text_parts)}",
        file=sys.stderr,
    )

    # If pages were found but text extraction failed
    if not text_parts:

        return (
            "Search results were found, "
            "but documentation text could not be extracted."
        )

    # Return all documentation
    return "\n\n".join(text_parts)


# ---------------------------------------------------------
# Start MCP server
# ---------------------------------------------------------

def main():

    mcp.run(transport="stdio")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    main()
