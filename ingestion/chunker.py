from dataclasses import dataclass
from typing import List, Optional
import re
from numpy import dot
from numpy.linalg import norm

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_STRATEGY,
    CHUNK_SEMANTIC_SIMILARITY,
)

from ingestion import embedder as _embedder


@dataclass
class Chunk:
    text: str
    page_number: int
    parent_id: Optional[str] = None


# Supported chunking strategies
SUPPORTED_STRATEGIES = {"recursive", "structure", "parent-child", "semantic"}


def _recursive_split(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_text(text)


def _structure_split(text: str) -> List[str]:
    """Naive structure-based split: split on double newlines or headings.

    This is a heuristic: splits on two or more newlines, and on lines that look like headings
    (e.g., start with uppercase and end without a period) to create higher-level sections.
    """
    # split on two or more newlines to get paragraphs/sections
    parts = re.split(r"\n{2,}", text)

    # further split very large parts using recursive splitter
    out: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > CHUNK_SIZE * 4:
            out.extend(_recursive_split(p))
        else:
            out.append(p)

    return out


def _parent_child_split(text: str) -> List[Chunk]:
    """Create parent sections with child recursive chunks.

    Returns a flat list of Chunk objects where children have `parent_id` set to their parent text id.
    Parent id is a simple index-based id.
    """
    parents = _structure_split(text)
    out: List[Chunk] = []
    for i, p in enumerate(parents):
        parent_id = f"parent-{i}"
        # add parent as a chunk (could be optional)
        out.append(Chunk(text=p.strip(), page_number=0, parent_id=None))
        # create children
        children = _recursive_split(p)
        for c in children:
            out.append(Chunk(text=c.strip(), page_number=0, parent_id=parent_id))

    return out


def _semantic_group(parts: List[str], threshold: float) -> List[str]:
    """Group adjacent parts whose embeddings are similar above threshold."""
    if not parts:
        return []

    embeddings = _embedder.create_embeddings(parts)

    grouped: List[str] = []
    buf = parts[0]
    buf_emb = embeddings[0]

    for i in range(1, len(parts)):
        emb = embeddings[i]
        sim = 0.0
        try:
            sim = float(dot(buf_emb, emb) / (norm(buf_emb) * norm(emb)))
        except Exception:
            sim = 0.0

        if sim >= threshold:
            # merge
            buf = f"{buf}\n\n{parts[i]}"
            # recompute buffer embedding (simple average)
            buf_emb = [(a + b) / 2.0 for a, b in zip(buf_emb, emb)]
        else:
            grouped.append(buf.strip())
            buf = parts[i]
            buf_emb = emb

    if buf:
        grouped.append(buf.strip())

    return grouped


def create_chunks(pages, strategy: Optional[str] = None) -> List[Chunk]:
    """Create chunks according to CHUNK_STRATEGY.

    Strategies supported: `recursive`, `structure`, `parent-child`, `semantic`.
    """
    all_chunks: List[Chunk] = []

    for page in pages:
        text = page.text or ""

        effective = strategy or CHUNK_STRATEGY

        if effective == "structure":
            parts = _structure_split(text)
            for p in parts:
                all_chunks.append(Chunk(text=p, page_number=page.page_number))

        elif effective == "parent-child":
            pcs = _parent_child_split(text)
            # parent-child split used page_number from page
            for c in pcs:
                c.page_number = page.page_number
                all_chunks.append(c)

        elif effective == "semantic":
            # start from recursive parts, then group semantically
            parts = _recursive_split(text)
            grouped = _semantic_group(parts, CHUNK_SEMANTIC_SIMILARITY)
            for g in grouped:
                all_chunks.append(Chunk(text=g, page_number=page.page_number))

        else:
            # default recursive
            parts = _recursive_split(text)
            for p in parts:
                all_chunks.append(Chunk(text=p, page_number=page.page_number))

    return all_chunks
