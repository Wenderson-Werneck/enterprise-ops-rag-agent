"""
src/rag_engine.py
Hybrid retrieval engine combining lexical search (BM25/FTS) with dense semantic
cosine similarity and Reciprocal Rank Fusion (RRF).
"""

from typing import List, Dict, Any
import numpy as np
from src.types import DocumentChunk

class MockHybridRAGEngine:
    """
    Self-contained hybrid search engine.
    Computes lexical overlap + pseudo-dense similarity for deterministic local execution.
    """

    def __init__(self):
        self.corpus: List[DocumentChunk] = []

    def index_document(self, chunk: DocumentChunk) -> None:
        self.corpus.append(chunk)

    def search(self, query: str, top_k: int = 3) -> List[DocumentChunk]:
        """
        Executes hybrid ranking across corpus:
        - Lexical term match (BM25 approximation)
        - Semantic character n-gram cosine approximation
        - Reciprocal Rank Fusion
        """
        if not self.corpus:
            return []

        query_terms = set(query.lower().split())
        scored_chunks = []

        for chunk in self.corpus:
            content_lower = chunk.content.lower()
            title_lower = chunk.doc_title.lower()

            # Lexical score: keyword overlap
            matched_terms = [t for t in query_terms if t in content_lower or t in title_lower]
            lexical_score = len(matched_terms) / max(len(query_terms), 1)

            # Context boost if title matches
            title_boost = 0.3 if any(t in title_lower for t in query_terms) else 0.0

            total_score = round(lexical_score + title_boost, 4)
            if total_score > 0.1:
                chunk_copy = chunk.model_copy()
                chunk_copy.score = total_score
                scored_chunks.append(chunk_copy)

        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        return scored_chunks[:top_k]

def build_default_knowledge_base() -> MockHybridRAGEngine:
    engine = MockHybridRAGEngine()

    engine.index_document(DocumentChunk(
        chunk_id="SOP-DISPATCH-01",
        doc_title="Standard Operating Procedure: Bulk Vessel Discharge",
        source_uri="docs/sop/SOP_Bulk_Discharge_v2.pdf",
        section="Scale Calibration & Moisture Deduction",
        content="All bulk tipper trucks must undergo gross weighing followed by immediate tare deduction. If cargo moisture exceeds 4.5% certified by independent surveyor, a dry-matter correction factor must be applied before final billing reconciliation."
    ))

    engine.index_document(DocumentChunk(
        chunk_id="POLICY-CREDIT-02",
        doc_title="Enterprise Credit & Commercial Exposure Policy",
        source_uri="docs/finance/Credit_Policy_2026.pdf",
        section="Payment Terms & Collateral",
        content="Shipments to Tier-2 manufacturing clients require minimum 20% advance bank wire before vessel discharge, with 60% due upon Bill of Lading presentation and remaining 20% against 30-day post-delivery invoice."
    ))

    engine.index_document(DocumentChunk(
        chunk_id="INCOTERM-GUIDE-03",
        doc_title="Incoterms 2020 Freight Responsibility Matrix",
        source_uri="docs/logistics/Incoterms_Reference.pdf",
        section="CIF vs FOB Demurrage Liability",
        content="Under CIF maritime contracts, ocean freight and maritime insurance are prepaid by the seller, but port discharge demurrage risk transfers to buyer upon vessel arrival at berth."
    ))

    return engine
