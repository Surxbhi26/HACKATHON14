from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def _try_crypto_price_quote(query: str) -> str | None:
    query_lower = query.lower()
    if "bitcoin" not in query_lower and "btc" not in query_lower and "crypto" not in query_lower:
        return None

    if not any(keyword in query_lower for keyword in ("price", "current", "live", "today", "rate")):
        return None

    coin_id = "bitcoin"
    coin_name = "Bitcoin"
    if "ethereum" in query_lower or "eth" in query_lower:
        coin_id = "ethereum"
        coin_name = "Ethereum"

    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        },
        timeout=10,
        headers={
            "accept": "application/json",
            "user-agent": "Mozilla/5.0",
        },
    )
    response.raise_for_status()
    payload = response.json()
    price = payload.get(coin_id, {}).get("usd")
    change_24h = payload.get(coin_id, {}).get("usd_24h_change")

    if price is None:
        return None

    change_text = ""
    if change_24h is not None:
        change_text = f" (24h change: {change_24h:+.2f}%)"

    return (
        "Result 1:\n"
        f"Title: {coin_name} live price\n"
        f"Source: https://www.coingecko.com/en/coins/{coin_id}\n"
        f"Summary: {coin_name} is currently ${price:,.2f} USD{change_text}."
    )


def web_search(query: str, max_results: int = 4) -> str:
    try:
        crypto_quote = _try_crypto_price_quote(query)
        if crypto_quote:
            return crypto_quote

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
