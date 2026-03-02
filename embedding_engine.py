import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> np.ndarray:
    """Encode a single string into a normalised embedding vector.

    Normalising to unit length means cosine similarity reduces to a dot product,
    which is faster to compute at query time.

    Args:
        text: The string to embed.

    Returns:
        1-D numpy array of floats.
    """
    return _model.encode(text, normalize_embeddings=True)


def compute_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Return the cosine similarity between two normalised embedding vectors.

    Because both vectors are already unit-normalised, cosine similarity equals
    the dot product, so no division is needed.

    Args:
        a: Normalised embedding array.
        b: Normalised embedding array.

    Returns:
        Similarity score in [-1, 1]. Higher means more similar.
    """
    return float(np.dot(a, b))


def batch_embed(texts: dict[str, str]) -> dict[str, np.ndarray]:
    """Encode a mapping of company keys to positioning text in a single batch.

    Batch encoding is significantly faster than calling generate_embedding in a
    loop because the model processes all sequences in one forward pass.

    Args:
        texts: Dict mapping company_key to positioning text string.

    Returns:
        Dict mapping company_key to its normalised embedding array.
    """
    keys = list(texts.keys())
    vectors = _model.encode(list(texts.values()), normalize_embeddings=True)
    return {key: vectors[i] for i, key in enumerate(keys)}
