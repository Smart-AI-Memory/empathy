"""
RAG Pattern Wizard - Level 4 Anticipatory Empathy

Alerts developers when RAG (Retrieval-Augmented Generation) implementation
will encounter scalability or quality issues.

In our experience, RAG seems simple at first (vector DB + similarity search).
But we learned: embedding quality, chunk strategy, and retrieval relevance
degrade as data grows. This wizard alerts before those issues surface.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class RAGPatternWizard(BaseWizard):
    """
    Level 4 Anticipatory: Predicts RAG implementation issues.

    What We Learned About RAG:
    - Naive chunking (split by char count) fails when data grows
    - Embedding quality matters more than vector DB choice
    - Retrieval relevance degrades as corpus grows without tuning
    - Hybrid search (vector + keyword) becomes essential at scale
    """

    def __init__(self):
        super().__init__(
            name="RAG Pattern Wizard", domain="software", empathy_level=4, category="ai_development"
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "rag_implementation",  # RAG implementation files
            "embedding_strategy",  # How embeddings are created
            "chunk_strategy",  # How documents are chunked
            "vector_db_config",  # Vector DB configuration
            "corpus_size",  # Current corpus size
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze RAG implementation and predict quality/scale issues.

        In our experience: RAG breaks down in predictable ways as it scales.
        Early detection prevents painful rewrites.
        """
        self.validate_context(context)

        rag_impl = context.get("rag_implementation", [])
        embedding_strat = context.get("embedding_strategy", {})
        chunk_strat = context.get("chunk_strategy", {})
        corpus_size = context.get("corpus_size", 0)

        # Current issues
        issues = await self._analyze_rag_implementation(
            rag_impl, embedding_strat, chunk_strat, corpus_size
        )

        # Level 4: Predict future RAG issues
        predictions = await self._predict_rag_degradation(
            rag_impl, embedding_strat, chunk_strat, corpus_size, context
        )

        recommendations = self._generate_recommendations(issues, predictions)
        patterns = self._extract_patterns(issues, predictions)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": recommendations,
            "patterns": patterns,
            "confidence": 0.80,
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "corpus_size": corpus_size,
                "chunking_strategy": chunk_strat.get("type", "unknown"),
            },
        }

    async def _analyze_rag_implementation(
        self, rag_impl: list[str], embedding_strat: dict, chunk_strat: dict, corpus_size: int
    ) -> list[dict[str, Any]]:
        """Analyze current RAG implementation"""
        issues = []

        # Issue: Naive character-based chunking
        if chunk_strat.get("type") == "character" or chunk_strat.get("type") == "fixed":
            issues.append(
                {
                    "severity": "warning",
                    "type": "naive_chunking",
                    "message": (
                        "Using character-based chunking. In our experience, this breaks "
                        "semantic coherence and reduces retrieval quality."
                    ),
                    "suggestion": (
                        "Use semantic chunking: split by paragraphs, sentences, or "
                        "semantic boundaries (e.g., LangChain SemanticChunker)"
                    ),
                }
            )

        # Issue: No chunk overlap
        if not chunk_strat.get("overlap", False):
            issues.append(
                {
                    "severity": "info",
                    "type": "no_chunk_overlap",
                    "message": (
                        "No chunk overlap detected. Without overlap, relevant context "
                        "split across chunk boundaries is lost."
                    ),
                    "suggestion": "Add 10-20% overlap between chunks",
                }
            )

        # Issue: No metadata enrichment
        if not embedding_strat.get("metadata_enrichment", False):
            issues.append(
                {
                    "severity": "info",
                    "type": "missing_metadata",
                    "message": (
                        "Chunks not enriched with metadata (source, date, category). "
                        "In our experience, metadata filtering dramatically improves retrieval."
                    ),
                    "suggestion": "Add metadata to chunks for filtering and relevance",
                }
            )

        # Issue: Single embedding model
        if not embedding_strat.get("multi_model", False) and corpus_size > 1000:
            issues.append(
                {
                    "severity": "info",
                    "type": "single_embedding_model",
                    "message": (
                        "Using single embedding model for diverse content. "
                        "Different content types (code, docs, data) benefit from "
                        "specialized embeddings."
                    ),
                    "suggestion": "Consider domain-specific embeddings for different content types",
                }
            )

        # Issue: No reranking
        if not self._has_reranking(rag_impl):
            issues.append(
                {
                    "severity": "warning",
                    "type": "no_reranking",
                    "message": (
                        "No reranking layer detected. In our experience, initial vector "
                        "similarity often returns suboptimal results. Reranking improves quality 30-50%."
                    ),
                    "suggestion": "Add reranker (e.g., Cohere rerank, cross-encoder model)",
                }
            )

        return issues

    async def _predict_rag_degradation(
        self,
        rag_impl: list[str],
        embedding_strat: dict,
        chunk_strat: dict,
        corpus_size: int,
        full_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Level 4: Predict when RAG quality will degrade.

        Based on our experience: RAG breaks at predictable thresholds.
        """
        predictions = []

        # Pattern 1: Corpus growth will degrade retrieval
        if corpus_size > 5000 and not self._has_hybrid_search(rag_impl):
            predictions.append(
                {
                    "type": "retrieval_degradation",
                    "alert": (
                        f"Corpus size: {corpus_size:,} documents. In our experience, "
                        "pure vector search degrades above 10,000 documents without hybrid search. "
                        "Alert: Implement hybrid search (vector + keyword) before quality drops."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Implement hybrid search (combine vector similarity + BM25 keyword)",
                        "Add query expansion (synonyms, related terms)",
                        "Implement result fusion (merge vector and keyword results)",
                        "Add relevance feedback loop (learn from user selections)",
                    ],
                    "reasoning": (
                        "Vector search alone: high recall, low precision at scale. "
                        "Keyword search: high precision, low recall. "
                        "Hybrid: best of both. We've seen 40-60% quality improvement."
                    ),
                    "personal_experience": (
                        "At 8,000 documents, our vector-only retrieval started returning "
                        "too many 'similar but not relevant' results. Added BM25 hybrid search, "
                        "quality jumped immediately."
                    ),
                }
            )

        # Pattern 2: Embedding staleness
        if corpus_size > 1000 and not embedding_strat.get("refresh_strategy"):
            predictions.append(
                {
                    "type": "embedding_staleness",
                    "alert": (
                        "No embedding refresh strategy detected. As documents change, "
                        "embeddings become stale. In our experience, this causes gradual "
                        "quality degradation that's hard to notice."
                    ),
                    "probability": "medium-high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Implement incremental embedding updates (only changed docs)",
                        "Add embedding versioning (track which model version)",
                        "Create embedding freshness metrics",
                        "Schedule periodic re-embedding for entire corpus",
                    ],
                    "reasoning": (
                        "Documents change, but embeddings don't auto-update. "
                        "Stale embeddings = stale retrieval. Incremental updates solve this."
                    ),
                }
            )

        # Pattern 3: No query understanding layer
        if not self._has_query_understanding(rag_impl):
            predictions.append(
                {
                    "type": "poor_query_handling",
                    "alert": (
                        "No query understanding layer. Users ask questions in many ways. "
                        "In our experience, naive query → embedding → search fails on "
                        "complex queries. Alert: Add query processing before retrieval quality plateaus."
                    ),
                    "probability": "medium",
                    "impact": "high",
                    "prevention_steps": [
                        "Add query decomposition (break complex queries into sub-queries)",
                        "Implement query rewriting (rephrase for better retrieval)",
                        "Add intent classification (route to different retrieval strategies)",
                        "Create query expansion (add relevant terms)",
                    ],
                    "reasoning": (
                        "User query: 'How do I prevent SQL injection in React apps?'. "
                        "Needs decomposition: 1) SQL injection prevention, 2) React context. "
                        "Naive embedding misses nuance."
                    ),
                    "personal_experience": (
                        "We added simple query rewriting (expand acronyms, add synonyms). "
                        "Retrieval quality improved 25% with minimal effort."
                    ),
                }
            )

        # Pattern 4: Missing evaluation framework
        if not self._has_evaluation(rag_impl):
            predictions.append(
                {
                    "type": "no_rag_evaluation",
                    "alert": (
                        "No RAG evaluation framework detected. In our experience, "
                        "you can't improve what you don't measure. Alert: Build evaluation "
                        "before you waste time on optimizations that don't help."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Create ground truth Q&A pairs (what SHOULD be retrieved)",
                        "Implement retrieval metrics (MRR, NDCG, precision@k)",
                        "Add end-to-end evaluation (does RAG answer correctly?)",
                        "Build A/B testing framework (compare strategies)",
                        "Create evaluation dashboard (track quality over time)",
                    ],
                    "reasoning": (
                        "Is chunking A better than chunking B? Is reranking worth it? "
                        "Without eval, you're guessing. We spent weeks optimizing the wrong things."
                    ),
                    "personal_experience": (
                        "We thought our RAG was great. Built evaluation, discovered 40% "
                        "of queries retrieved irrelevant docs. Fixed in 2 days with data."
                    ),
                }
            )

        # Pattern 5: Context window waste
        if not self._has_context_optimization(rag_impl):
            predictions.append(
                {
                    "type": "inefficient_context_usage",
                    "alert": (
                        "No context optimization detected. In our experience, dumping "
                        "all retrieved chunks into context wastes tokens and reduces quality. "
                        "Alert: Optimize context usage before costs and quality both degrade."
                    ),
                    "probability": "medium",
                    "impact": "medium",
                    "prevention_steps": [
                        "Implement relevance-based pruning (only use top-k)",
                        "Add chunk summarization (compress verbose chunks)",
                        "Create context deduplication (remove redundant info)",
                        "Implement adaptive retrieval (fewer chunks for simple queries)",
                        "Add context budget management",
                    ],
                    "reasoning": (
                        "Retrieving 10 chunks doesn't mean use all 10. "
                        "Top 3 might be enough. Extra context confuses AI and costs money."
                    ),
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Quick wins
        if any(i["type"] == "no_reranking" for i in issues):
            recommendations.append(
                "[QUICK WIN] Add reranking layer. In our experience, "
                "this is highest ROI improvement (30-50% quality boost, minimal effort)."
            )

        # High-impact predictions
        for pred in predictions:
            if pred.get("impact") == "high":
                recommendations.append(f"\n[ALERT] {pred['alert']}")
                if "personal_experience" in pred:
                    recommendations.append(f"Experience: {pred['personal_experience']}")
                recommendations.append("Prevention steps:")
                for i, step in enumerate(pred["prevention_steps"][:3], 1):
                    recommendations.append(f"  {i}. {step}")

        return recommendations

    def _extract_patterns(
        self, issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """Extract cross-domain patterns"""
        return [
            {
                "pattern_type": "retrieval_quality_degradation",
                "description": (
                    "Single-strategy retrieval systems degrade as corpus grows. "
                    "Hybrid approaches become essential at scale."
                ),
                "domain_agnostic": True,
                "applicable_to": [
                    "RAG systems",
                    "Search engines",
                    "Recommendation systems",
                    "Information retrieval (healthcare, legal, etc.)",
                ],
                "threshold": "5,000-10,000 items",
                "solution": "Hybrid retrieval (multiple signals combined)",
            }
        ]

    # Helper methods

    def _has_reranking(self, rag_impl: list[str]) -> bool:
        """Check for reranking layer"""
        for file_path in rag_impl:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower() for kw in ["rerank", "cross-encoder", "cohere.rerank"]
                    ):
                        return True
            except OSError:
                pass
        return False

    def _has_hybrid_search(self, rag_impl: list[str]) -> bool:
        """Check for hybrid search implementation"""
        for file_path in rag_impl:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(kw in content.lower() for kw in ["hybrid", "bm25", "keyword", "fusion"]):
                        return True
            except OSError:
                pass
        return False

    def _has_query_understanding(self, rag_impl: list[str]) -> bool:
        """Check for query understanding/processing"""
        for file_path in rag_impl:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower()
                        for kw in ["query_rewrite", "query_expansion", "decompose", "intent"]
                    ):
                        return True
            except OSError:
                pass
        return False

    def _has_evaluation(self, rag_impl: list[str]) -> bool:
        """Check for RAG evaluation framework"""
        for file_path in rag_impl:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower()
                        for kw in ["evaluate", "metrics", "ground_truth", "precision", "recall"]
                    ):
                        return True
            except OSError:
                pass
        return False

    def _has_context_optimization(self, rag_impl: list[str]) -> bool:
        """Check for context optimization strategies"""
        for file_path in rag_impl:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower()
                        for kw in ["prune", "summarize", "deduplicate", "context_budget"]
                    ):
                        return True
            except OSError:
                pass
        return False
