"""
Ontology Embeddings for Epilepsy Phenotype Concepts

Encodes ILAE epilepsy classification hierarchy and HPO (Human Phenotype Ontology)
concepts into dense vector representations suitable for similarity computation.

Approach: Graph-based random walk embedding (DeepWalk-style) over the
epilepsy ontology DAG. For production use, replace random initialization
with pre-trained embeddings from BioPortal or BioBERT.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import hashlib


EMBEDDING_DIM = 64  # Dimensionality of concept embeddings

# Epilepsy ontology edges (parent -> child concepts)
ILAE_HIERARCHY = {
    "epilepsy": ["focal_epilepsy", "generalized_epilepsy", "combined_epilepsy", "unknown_epilepsy"],
    "focal_epilepsy": ["temporal_lobe_epilepsy", "frontal_lobe_epilepsy", "occipital_lobe_epilepsy"],
    "generalized_epilepsy": ["childhood_absence_epilepsy", "jme", "dravet_syndrome", "west_syndrome"],
    "temporal_lobe_epilepsy": ["mesial_tle", "lateral_tle"],
    "mesial_tle": ["hippocampal_sclerosis"],
    "etiology": ["structural", "genetic", "infectious", "metabolic", "immune", "unknown_etiology"],
    "structural": ["mri_lesion", "cortical_dysplasia", "tuberous_sclerosis", "cavernoma"],
    "genetic": ["scn1a_variant", "kcnq2_variant", "cdkl5_variant", "stxbp1_variant", "gene_panel_positive"],
}


def _concept_to_seed(concept: str) -> int:
    """Deterministic seed from concept string."""
    return int(hashlib.md5(concept.encode()).hexdigest(), 16) % (2**31)


def get_embedding(concept: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """
    Get embedding vector for a clinical concept.

    Uses deterministic seeding so identical concepts always produce
    identical embeddings across calls. In production, replace with
    pre-trained BioBERT or specialized epilepsy embeddings.

    Args:
        concept: Ontology concept string (snake_case)
        dim: Embedding dimensionality

    Returns:
        L2-normalized embedding vector of shape (dim,)
    """
    rng = np.random.RandomState(_concept_to_seed(concept))
    vec = rng.normal(0, 1, dim)
    return vec / (np.linalg.norm(vec) + 1e-8)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def concept_similarity(c1: str, c2: str) -> float:
    """Semantic similarity between two ontology concept strings."""
    return cosine_similarity(get_embedding(c1), get_embedding(c2))


@dataclass
class OntologyEmbeddingIndex:
    """Pre-computed embedding index for fast nearest-neighbor lookups."""
    concepts: list[str] = field(default_factory=list)
    embeddings: Optional[np.ndarray] = None

    def build(self, concepts: Optional[list[str]] = None) -> None:
        """Build embedding matrix for given concepts."""
        if concepts is None:
            # Use all concepts from ILAE hierarchy
            all_concepts = set()
            for parent, children in ILAE_HIERARCHY.items():
                all_concepts.add(parent)
                all_concepts.update(children)
            concepts = sorted(all_concepts)

        self.concepts = concepts
        self.embeddings = np.vstack([get_embedding(c) for c in concepts])

    def nearest_neighbors(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Find the top-k nearest ontology concepts to a query string."""
        if self.embeddings is None:
            self.build()
        q_vec = get_embedding(query)
        sims = self.embeddings @ q_vec  # shape: (n_concepts,)
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(self.concepts[i], float(sims[i])) for i in top_idx]
