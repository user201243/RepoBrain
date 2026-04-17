from __future__ import annotations

from types import SimpleNamespace

import pytest

from repobrain.config import ProviderConfig, RepoBrainConfig
from repobrain.engine.providers import (
    CohereReranker,
    GeminiEmbeddingProvider,
    GeminiReranker,
    LocalHashEmbeddingProvider,
    OpenAIEmbeddingProvider,
    RemoteProviderError,
    VoyageEmbeddingProvider,
    build_provider_bundle,
    inspect_provider_status,
)


def test_local_hash_embedding_is_stable_across_instances() -> None:
    left = LocalHashEmbeddingProvider(dimensions=32)
    right = LocalHashEmbeddingProvider(dimensions=32)

    assert left.embed(["payment retry handler"]) == right.embed(["payment retry handler"])


def test_openai_embedding_provider_uses_sdk_client_ordered_by_index() -> None:
    captured: dict[str, object] = {}

    class FakeEmbeddings:
        def create(self, model: str, input: list[str]) -> SimpleNamespace:
            captured["model"] = model
            captured["input"] = input
            return SimpleNamespace(
                data=[
                    SimpleNamespace(index=1, embedding=[0.0, 1.0]),
                    SimpleNamespace(index=0, embedding=[1.0, 0.0]),
                ]
            )

    provider = OpenAIEmbeddingProvider(model="test-openai-model", client=SimpleNamespace(embeddings=FakeEmbeddings()))

    assert provider.embed(["first", "second"]) == [[1.0, 0.0], [0.0, 1.0]]
    assert captured == {"model": "test-openai-model", "input": ["first", "second"]}


def test_voyage_embedding_provider_uses_sdk_client() -> None:
    captured: dict[str, object] = {}

    class FakeVoyageClient:
        def embed(self, texts: list[str], model: str, input_type: str) -> SimpleNamespace:
            captured["texts"] = texts
            captured["model"] = model
            captured["input_type"] = input_type
            return SimpleNamespace(embeddings=[[0.1, 0.2], [0.3, 0.4]])

    provider = VoyageEmbeddingProvider(model="test-voyage-model", input_type="query", client=FakeVoyageClient())

    assert provider.embed(["auth", "payment"]) == [[0.1, 0.2], [0.3, 0.4]]
    assert captured == {"texts": ["auth", "payment"], "model": "test-voyage-model", "input_type": "query"}


def test_cohere_reranker_uses_sdk_client() -> None:
    captured: dict[str, object] = {}

    class FakeCohereClient:
        def rerank(self, model: str, query: str, documents: list[str], top_n: int) -> SimpleNamespace:
            captured["model"] = model
            captured["query"] = query
            captured["documents"] = documents
            captured["top_n"] = top_n
            return SimpleNamespace(results=[SimpleNamespace(relevance_score=0.87654321)])

    provider = CohereReranker(model="test-rerank-model", client=FakeCohereClient())

    assert provider.score("payment retry", "retry handler") == 0.876543
    assert captured == {
        "model": "test-rerank-model",
        "query": "payment retry",
        "documents": ["retry handler"],
        "top_n": 1,
    }


def test_gemini_embedding_provider_uses_sdk_client() -> None:
    captured: dict[str, object] = {}

    class FakeGeminiModels:
        def embed_content(self, model: str, contents: list[str], config: object) -> SimpleNamespace:
            captured["model"] = model
            captured["contents"] = contents
            captured["config"] = config
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=[0.1, 0.2]),
                    SimpleNamespace(values=[0.3, 0.4]),
                ]
            )

    provider = GeminiEmbeddingProvider(
        model="gemini-embedding-test",
        output_dimensionality=768,
        task_type="SEMANTIC_SIMILARITY",
        client=SimpleNamespace(models=FakeGeminiModels()),
    )

    assert provider.embed(["auth", "payment"]) == [[0.1, 0.2], [0.3, 0.4]]
    assert captured["model"] == "gemini-embedding-test"
    assert captured["contents"] == ["auth", "payment"]


def test_gemini_reranker_uses_flash_model_and_parses_score() -> None:
    captured: dict[str, object] = {}

    class FakeGeminiModels:
        def generate_content(self, model: str, contents: str) -> SimpleNamespace:
            captured["model"] = model
            captured["contents"] = contents
            return SimpleNamespace(text="0.82")

    provider = GeminiReranker(model="gemini-3-flash-preview", client=SimpleNamespace(models=FakeGeminiModels()))

    assert provider.score("payment retry", "retry handler") == 0.82
    assert captured["model"] == "gemini-3-flash-preview"
    assert "payment retry" in str(captured["contents"])


def test_remote_provider_reports_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    provider = OpenAIEmbeddingProvider()

    with pytest.raises(RemoteProviderError, match="OPENAI_API_KEY"):
        provider.embed(["auth callback"])


def test_provider_bundle_uses_configured_remote_models(tmp_path) -> None:
    config = RepoBrainConfig.default(tmp_path)
    config.providers = ProviderConfig(
        embedding="voyage",
        reranker="cohere",
        options={
            "voyage_embedding_model": "voyage-test",
            "voyage_input_type": "query",
            "cohere_rerank_model": "rerank-test",
        },
    )

    bundle = build_provider_bundle(config)

    assert isinstance(bundle.embedder, VoyageEmbeddingProvider)
    assert bundle.embedder.model == "voyage-test"
    assert bundle.embedder.input_type == "query"
    assert isinstance(bundle.reranker, CohereReranker)
    assert bundle.reranker.model == "rerank-test"


def test_provider_bundle_uses_configured_gemini_models(tmp_path) -> None:
    config = RepoBrainConfig.default(tmp_path)
    config.providers = ProviderConfig(
        embedding="gemini",
        reranker="gemini",
        options={
            "gemini_embedding_model": "gemini-embedding-test",
            "gemini_output_dimensionality": 1536,
            "gemini_task_type": "RETRIEVAL_DOCUMENT",
            "gemini_rerank_model": "gemini-3-flash-preview",
        },
    )

    bundle = build_provider_bundle(config)

    assert isinstance(bundle.embedder, GeminiEmbeddingProvider)
    assert bundle.embedder.model == "gemini-embedding-test"
    assert bundle.embedder.output_dimensionality == 1536
    assert bundle.embedder.task_type == "RETRIEVAL_DOCUMENT"
    assert isinstance(bundle.reranker, GeminiReranker)
    assert bundle.reranker.model == "gemini-3-flash-preview"


def test_remote_provider_status_explains_missing_requirements(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = RepoBrainConfig.default(tmp_path)
    config.providers = ProviderConfig(embedding="openai", reranker="local")

    status = inspect_provider_status(config)

    assert status["embedding"]["ready"] is False
    assert status["embedding"]["requires_network"] is True
    assert "OPENAI_API_KEY" in status["embedding"]["missing"]
    assert status["reranker"]["ready"] is True


def test_gemini_provider_status_explains_missing_requirements(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    config = RepoBrainConfig.default(tmp_path)
    config.providers = ProviderConfig(embedding="gemini", reranker="gemini")

    status = inspect_provider_status(config)

    assert status["embedding"]["ready"] is False
    assert status["embedding"]["requires_network"] is True
    assert "GEMINI_API_KEY" in status["embedding"]["missing"]
    assert status["reranker"]["ready"] is False
    assert "GEMINI_API_KEY" in status["reranker"]["missing"]
