import time
from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from pydantic import SecretStr

from app.core.config import get_settings


settings = get_settings()

_embeddings: GoogleGenerativeAIEmbeddings | None = None
_vectorstore: PineconeVectorStore | None = None

EMBEDDING_DIMENSIONS = {
    "gemini-embedding-001": 3072,
}

INDEX_READY_TIMEOUT_SECONDS = 300


def get_embedding_dimension(model_name: str | None = None) -> int:
    name = (model_name or settings.embedding_model).strip().lower()
    for supported_model, dimension in EMBEDDING_DIMENSIONS.items():
        if supported_model in name:
            return dimension

    raise ValueError(
        f"Unsupported embedding model '{model_name or settings.embedding_model}' for Pinecone. "
        "Supported model: gemini-embedding-001."
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")
        dimension = get_embedding_dimension()
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            api_key=SecretStr(settings.gemini_api_key),
            output_dimensionality=dimension,
        )
    return _embeddings


def ensure_index():
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing")

    desired_dimension = get_embedding_dimension()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index_names = pc.list_indexes().names()

    if settings.pinecone_index_name in index_names:
        index_info = pc.describe_index(settings.pinecone_index_name)
        current_dimension = getattr(index_info, "dimension", None)
        if current_dimension is None and isinstance(index_info, dict):
            current_dimension = index_info.get("dimension")

        if current_dimension is not None and current_dimension != desired_dimension:
            raise RuntimeError(
                f"Pinecone index '{settings.pinecone_index_name}' has dimension "
                f"{current_dimension}, but '{settings.embedding_model}' requires "
                f"{desired_dimension}. Configure a new index or migrate the existing "
                "index; it was not deleted."
            )
    else:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=desired_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        deadline = time.monotonic() + INDEX_READY_TIMEOUT_SECONDS
        while True:
            index_info = pc.describe_index(settings.pinecone_index_name)
            status = getattr(index_info, "status", {})
            is_ready = (
                status.get("ready", False)
                if isinstance(status, dict)
                else getattr(status, "ready", False)
            )
            if is_ready:
                break
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Pinecone index '{settings.pinecone_index_name}' did not become "
                    f"ready within {INDEX_READY_TIMEOUT_SECONDS} seconds."
                )
            time.sleep(1)

    return pc.Index(settings.pinecone_index_name)


def get_vectorstore() -> PineconeVectorStore:
    global _vectorstore
    if _vectorstore is None:
        index = ensure_index()
        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=get_embeddings(),
            namespace=settings.pinecone_namespace,
        )
    return _vectorstore


def get_retriever():
    return get_vectorstore().as_retriever(search_kwargs={"k": settings.top_k})


def add_documents(chunks: Sequence[Document]) -> list[str]:
    return get_vectorstore().add_documents(list(chunks))
