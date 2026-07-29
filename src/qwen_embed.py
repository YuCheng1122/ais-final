"""Local embedding helper (Qwen3-Embedding-0.6B via sentence-transformers).

Used only for the exploratory "did the model seem aware of this milestone"
semantic signal in score_steps.py -- never for deciding anchor-based
reached-ness (see METHODOLOGY.md).
"""

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "Qwen/Qwen3-Embedding-0.6B"


def load_model(name: str = DEFAULT_MODEL) -> SentenceTransformer:
    return SentenceTransformer(name)


def embed(model: SentenceTransformer, texts: list[str]):
    # Qwen3-Embedding encodes in bfloat16 by default; util.cos_sim needs
    # matching float32 tensors on both sides or it errors/misbehaves.
    return model.encode(texts, convert_to_tensor=True).float()
