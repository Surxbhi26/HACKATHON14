import os
import re
import zipfile
from xml.etree import ElementTree as ET

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()

document_chunks = []
vectorizer = None
document_matrix = None


def _load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file_handle:
        return file_handle.read()


def _load_docx_file(file_path: str) -> str:
    with zipfile.ZipFile(file_path) as archive:
        xml_data = archive.read("word/document.xml")

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(xml_data)
    paragraphs = []

    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        if texts:
            paragraphs.append("".join(texts))

    return "\n".join(paragraphs)


def load_documents(file_paths: list) -> str:
    """
    Load PDF documents and build a local TF-IDF search index.
    """
    global document_chunks, vectorizer, document_matrix

    try:
        loaded_pages = []

        for file_path in file_paths:
            lower_path = file_path.lower()

            if lower_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                loaded_pages.extend(loader.load())
            elif lower_path.endswith(".txt"):
                loaded_pages.append(
                    type("LoadedText", (), {
                        "page_content": _load_text_file(file_path),
                        "metadata": {"source": file_path, "page": 1},
                    })()
                )
            elif lower_path.endswith(".docx"):
                loaded_pages.append(
                    type("LoadedText", (), {
                        "page_content": _load_docx_file(file_path),
                        "metadata": {"source": file_path, "page": 1},
                    })()
                )

        if not loaded_pages:
            return "No supported documents loaded."

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
        )
        chunks = splitter.split_documents(loaded_pages)

        prepared_chunks = []
        texts = []

        for chunk in chunks:
            content = chunk.page_content.strip()
            if not content:
                continue

            prepared_chunks.append(
                {
                    "source": os.path.basename(chunk.metadata.get("source", "Unknown")),
                    "page": chunk.metadata.get("page", "?"),
                    "content": content,
                }
            )
            texts.append(content)

        if not texts:
            return "No searchable text could be extracted from the uploaded documents."

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        document_matrix = vectorizer.fit_transform(texts)
        document_chunks = prepared_chunks

        return f"Successfully loaded {len(loaded_pages)} pages into {len(document_chunks)} searchable chunks."
    except Exception as error:
        return f"Error loading documents: {error}"


def search_documents(query: str, k: int = 3):
    """
    Search loaded documents for relevant content.
    """
    global document_chunks, vectorizer, document_matrix

    if not document_chunks or vectorizer is None or document_matrix is None:
        return "NO_DOCUMENTS"

    try:
        query_vector = vectorizer.transform([query])
        if query_vector.nnz == 0:
            return []

        scores = (document_matrix @ query_vector.T).toarray().ravel()
        ranked_indices = scores.argsort()[::-1]

        results = []
        for index in ranked_indices:
            if scores[index] <= 0:
                continue

            chunk = document_chunks[index]
            results.append(
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "content": chunk["content"],
                    "score": float(scores[index]),
                }
            )

            if len(results) >= k:
                break

        return results
    except Exception as error:
        return f"Document search failed: {error}"


def format_rag_for_llm(query: str, doc_results) -> str:
    """
    Format document results into a prompt for the LLM.
    """
    if isinstance(doc_results, str):
        return f"""You are a helpful assistant with access to enterprise documents.
Answer the user's question based ONLY on the provided document context.
If the answer is not in the documents, say so clearly.

User Question: {query}

Document Retrieval Status:
{doc_results}

Provide a precise answer based on the documents above."""

    if not doc_results:
        return f"""You are a helpful assistant with access to enterprise documents.
Answer the user's question based ONLY on the provided document context.
If the answer is not in the documents, say so clearly.

User Question: {query}

No relevant document chunks were found.

Provide a brief response explaining that the answer was not found in the uploaded documents."""

    formatted_chunks = []
    for index, doc in enumerate(doc_results, 1):
        formatted_chunks.append(
            f"Chunk {index}:\n"
            f"Source: {doc['source']} (Page {doc['page']})\n"
            f"Content: {doc['content']}"
        )

    return f"""You are a helpful assistant with access to enterprise documents.
Answer the user's question based ONLY on the provided document context.
If the answer is not in the documents, say so clearly.

User Question: {query}

Relevant Document Content:
{chr(10).join(formatted_chunks)}

Provide a precise answer based on the documents above.
Always mention which document/page you got the information from."""


def has_documents() -> bool:
    return bool(document_chunks)
