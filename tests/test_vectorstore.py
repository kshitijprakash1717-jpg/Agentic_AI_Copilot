from types import SimpleNamespace

import pytest

from app.rag import vectorstore


def test_gemini_embedding_dimension():
    assert vectorstore.get_embedding_dimension("gemini-embedding-001") == 3072


def test_unsupported_embedding_model_fails_explicitly():
    with pytest.raises(ValueError, match="Unsupported embedding model"):
        vectorstore.get_embedding_dimension("unknown-embedding-model")


def test_embeddings_use_configured_gemini_credentials_and_dimension(monkeypatch):
    captured = {}

    class FakeEmbeddings:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(vectorstore, "_embeddings", None)
    monkeypatch.setattr(vectorstore, "GoogleGenerativeAIEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(vectorstore.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        vectorstore.settings, "embedding_model", "gemini-embedding-001"
    )

    embeddings = vectorstore.get_embeddings()

    assert isinstance(embeddings, FakeEmbeddings)
    assert captured["model"] == "gemini-embedding-001"
    assert captured["api_key"].get_secret_value() == "test-key"
    assert captured["output_dimensionality"] == 3072


def test_missing_gemini_key_fails_explicitly(monkeypatch):
    monkeypatch.setattr(vectorstore, "_embeddings", None)
    monkeypatch.setattr(vectorstore.settings, "gemini_api_key", "")

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is missing"):
        vectorstore.get_embeddings()


def test_incompatible_pinecone_index_is_not_deleted(monkeypatch):
    class FakeIndexList:
        def names(self):
            return ["existing-index"]

    class FakePinecone:
        def __init__(self, *, api_key):
            assert api_key == "test-pinecone-key"

        def list_indexes(self):
            return FakeIndexList()

        def describe_index(self, name):
            assert name == "existing-index"
            return SimpleNamespace(dimension=768)

        def delete_index(self, *, name):
            pytest.fail(f"Existing index {name!r} must not be deleted")

    monkeypatch.setattr(vectorstore, "Pinecone", FakePinecone)
    monkeypatch.setattr(vectorstore.settings, "pinecone_api_key", "test-pinecone-key")
    monkeypatch.setattr(vectorstore.settings, "pinecone_index_name", "existing-index")
    monkeypatch.setattr(
        vectorstore.settings, "embedding_model", "gemini-embedding-001"
    )

    with pytest.raises(RuntimeError, match="it was not deleted"):
        vectorstore.ensure_index()
