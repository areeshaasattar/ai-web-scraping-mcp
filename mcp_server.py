import os
import sys

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

from utils import clean_html_to_text

load_dotenv()

mcp = FastMCP("docs")

SERPER_URL = "https://google.serper.dev/search"


docs_urls = {
    "langchain": "https://docs.langchain.com",
    "llama-index": "https://docs.llamaindex.ai/en/stable",
    "openai": "https://platform.openai.com/docs",
    "uv": "https://docs.astral.sh/uv",
}



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


async def fetch_url(url: str):

    try:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                timeout=30.0,
                follow_redirects=True,
            )

            if response.status_code != 200:

                print(
                    f"Skipping URL: {url} "
                    f"(HTTP {response.status_code})",
                    file=sys.stderr,
                )

                return None

        cleaned_response = clean_html_to_text(response.text)

        return cleaned_response

    except Exception as e:

        print(
            f"Failed to fetch URL: {url} | Error: {e}",
            file=sys.stderr,
        )

        return None



@mcp.tool()
async def get_docs(query: str, library: str):

    # Check whether library is supported
    if library not in docs_urls:

        raise ValueError(
            f"Library '{library}' not supported by this tool. "
            f"Supported libraries: {list(docs_urls.keys())}"
        )

    search_query = f"site:{docs_urls[library]} {query}"

    print(
        f"SEARCH QUERY: {search_query}",
        file=sys.stderr,
    )

    results = await search_web(search_query)

    print(
        f"SEARCH RESULTS: {results}",
        file=sys.stderr,
    )

    if not results or not results.get("organic"):

        print(
            "NO SEARCH RESULTS FOUND",
            file=sys.stderr,
        )

        return "No results found."

    text_parts = []

    for result in results["organic"]:

        link = result.get("link", "")

        print(
            f"FOUND LINK: {link}",
            file=sys.stderr,
        )

        if not link:

            continue

        raw = await fetch_url(link)

        print(
            f"EXTRACTED TEXT LENGTH: {len(raw) if raw else 0}",
            file=sys.stderr,
        )

        if raw:

            labeled = (
                f"SOURCE: {link}\n\n"
                f"{raw}"
            )

            text_parts.append(labeled)

    print(
        f"TOTAL SOURCES: {len(text_parts)}",
        file=sys.stderr,
    )

    if not text_parts:

        return (
            "Search results were found, "
            "but documentation text could not be extracted."
        )

    return "\n\n".join(text_parts)


def main():

    mcp.run(transport="stdio")


if __name__ == "__main__":

    main()
