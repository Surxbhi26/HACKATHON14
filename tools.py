from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def web_search(query: str, max_results: int = 4) -> str:
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            },
            timeout=10,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for item in soup.select(".result"):
            title_link = item.select_one(".result__title a")
            snippet = item.select_one(".result__snippet")
            if not title_link:
                continue

            href = title_link.get("href", "")
            source = urljoin("https://duckduckgo.com", href)

            results.append(
                {
                    "title": title_link.get_text(" ", strip=True),
                    "href": source,
                    "body": snippet.get_text(" ", strip=True) if snippet else "No summary available.",
                }
            )

            if len(results) >= max_results:
                break

        if not results:
            return f"No results found for: {query}"

        formatted = []
        for index, result in enumerate(results, 1):
            formatted.append(
                f"Result {index}:\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"Source: {result.get('href', 'N/A')}\n"
                f"Summary: {result.get('body', 'N/A')}"
            )

        return "\n---\n".join(formatted)
    except Exception as error:
        return f"Search failed: {error}"


def format_search_for_llm(query: str, search_results: str) -> str:
    return f"""You are NeoMind, a helpful AI assistant.
Answer the user's question using the search results below.
Use only the provided web results when making factual claims and cite the sources.

User Question: {query}

Search Results:
{search_results}

Provide a concise but complete answer with source citations."""
