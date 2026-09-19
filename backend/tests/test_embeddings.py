import math
from app.services.embeddings.local import LocalEmbeddingProvider, get_embedding_provider


def test_embedding_provider_singleton_and_dimensions():
    provider1 = get_embedding_provider()
    provider2 = LocalEmbeddingProvider()
    assert provider1 is provider2
    assert provider1.dimension == 384


def test_embedding_single_and_batch():
    provider = get_embedding_provider()
    vec = provider.embed_text("Monthly electricity bill of 1500 USD")
    assert len(vec) == 384
    # Check L2-normalization (unit length ~= 1.0)
    norm = math.sqrt(sum(x * x for x in vec))
    assert pytest_approx_equal(norm, 1.0, tolerance=1e-4)

    batch = provider.embed_texts(["First statement line", "Second transaction line"])
    assert len(batch) == 2
    assert len(batch[0]) == 384
    assert len(batch[1]) == 384


def pytest_approx_equal(a, b, tolerance=1e-4):
    return abs(a - b) <= tolerance
