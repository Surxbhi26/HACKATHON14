import os
import re

from dotenv import load_dotenv
from groq import Groq

from memory import get_full_history, get_history, save_message
from rag import format_rag_for_llm, has_documents, search_documents
from tools import format_search_for_llm, web_search

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def _looks_like_follow_up(query: str) -> bool:
    query_lower = query.lower().strip()
    words = set(re.findall(r"\b[\w']+\b", query_lower))

    follow_up_phrases = [
        "tell me more",
        "what about it",
        "what about that",
        "who created it",
        "who made it",
        "how about it",
        "and then",
        "what about this",
    ]
    if any(phrase in query_lower for phrase in follow_up_phrases):
        return True

    pronouns = {"it", "that", "this", "they", "them", "he", "she", "those", "these", "one", "ones"}
    return len(words) <= 8 and bool(words & pronouns)


def _latest_assistant_mode(history: list) -> str:
    for message in reversed(history):
        if message.get("role") == "assistant" and message.get("mode"):
            return message["mode"]
    return "general"


def decide_mode(query: str, history: list, full_history: list) -> str:
    """
    Decide whether the query should use general, web, or rag mode.
    """
    query_lower = query.lower()
    last_mode = _latest_assistant_mode(full_history)

    web_keywords = [
        "today",
        "current",
        "latest",
        "news",
        "weather",
        "price",
        "stock",
        "live",
        "right now",
        "breaking",
        "recent",
        "who won",
        "score",
        "election",
        "trending",
        "bitcoin",
        "crypto",
        "market",
        "forecast",
        "headline",
    ]

    rag_keywords = [
        "document",
        "documents",
        "pdf",
        "uploaded",
        "upload",
        "policy",
        "handbook",
        "proposal",
        "report",
        "file",
        "summarize",
        "summarise",
        "according to",
        "in the document",
        "leave policy",
        "onboarding",
        "company policy",
        "enterprise",
    ]

    if _looks_like_follow_up(query) and last_mode in {"web", "rag", "general"}:
        return last_mode

    if any(keyword in query_lower for keyword in web_keywords):
        return "web"

    if any(keyword in query_lower for keyword in rag_keywords):
        return "rag"

    if has_documents() and last_mode == "rag":
        return "rag"

    return "general"


def run_agent(query: str, session_id: str, forced_mode: str = "auto") -> dict:
    """
    Main agent function.
    Returns dict with response, mode, and sources.
    """
    history = get_history(session_id)
    full_history = get_full_history(session_id)

    if forced_mode in {"general", "web", "rag"}:
        mode = forced_mode
    else:
        mode = decide_mode(query, history, full_history)
    sources = []
    prompt = ""

    if mode == "web":
        search_results = web_search(query)
        if search_results.startswith("Search failed:") or search_results.startswith("No results found"):
            prompt = build_general_prompt(
                query,
                history,
                extra_context=f"Web search could not retrieve live results.\n{search_results}",
            )
        else:
            prompt = format_search_for_llm(query, search_results)
            sources = extract_sources(search_results)

    elif mode == "rag":
        doc_results = search_documents(query)
        if doc_results == "NO_DOCUMENTS":
            answer = (
                "I do not have any uploaded documents yet. "
                "Please upload one or more PDFs in the sidebar, then ask the question again."
            )
            save_message(session_id, "user", query, mode)
            save_message(session_id, "assistant", answer, mode)
            return {
                "answer": answer,
                "mode": mode,
                "sources": [],
            }

        if isinstance(doc_results, str) and doc_results.startswith("Document search failed:"):
            prompt = build_general_prompt(
                query,
                history,
                extra_context=doc_results,
            )
        else:
            prompt = format_rag_for_llm(query, doc_results)
            sources = extract_rag_sources(doc_results)

    if mode == "general":
        prompt = build_general_prompt(query, history)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    answer = response.choices[0].message.content

    save_message(session_id, "user", query, mode)
    save_message(session_id, "assistant", answer, mode)

    return {
        "answer": answer,
        "mode": mode,
        "sources": sources,
    }


def build_general_prompt(query: str, history: list, extra_context: str = "") -> str:
    """Build prompt with conversation history for general queries."""
    messages = []
    for item in history[-6:]:
        messages.append(f"{item['role'].capitalize()}: {item['content']}")

    history_text = "\n".join(messages) if messages else "No previous conversation."
    extra_context_text = f"\n{extra_context}\n" if extra_context else ""

    return f"""You are NeoMind, an intelligent enterprise AI assistant.
You are helpful, precise, and professional.
Always provide a complete and detailed answer.
Never say you cannot answer - do your best with available knowledge.

Conversation History:
{history_text}

{extra_context_text}
Current Question: {query}

Provide a clear, helpful response:"""


def extract_sources(search_results: str) -> list:
    """Extract source URLs from search results."""
    sources = []
    for line in search_results.split("\n"):
        if line.startswith("Source:"):
            url = line.replace("Source:", "").strip()
            if url and url != "N/A":
                sources.append(url)
    return sources[:3]


def extract_rag_sources(doc_results) -> list:
    sources = []
    for doc in doc_results or []:
        source = doc.get("source", "Unknown")
        page = doc.get("page", "?")
        sources.append(f"{source} (Page {page})")
    return sources[:3]
