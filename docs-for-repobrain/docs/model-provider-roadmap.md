# Model Provider Roadmap

This note captures the next provider step after the Docker and Gemini setup work.

## Next Target: Groq

The next provider expansion should add a Groq-backed model picker for fast hosted text models. The first UI list should mirror the current planning screenshot:

- Groq Llama 3.1 8B Instant
- Groq Llama 3.3 70B Versatile
- Groq Qwen 3 32B

## Intended UX

- Add a provider setup panel similar to the Gemini panel.
- Let the user choose provider, API key, and model from a clear list.
- Keep local providers as the default.
- Store provider keys in `.env`; do not echo keys back in web responses.
- Store provider selection in `repobrain.toml`.
- Show active model, fallback status, and provider readiness in Doctor.

## Engineering Notes

- Add provider abstractions without changing the existing `EmbeddingProvider` and `RerankerProvider` contracts unless required.
- Groq is likely best introduced as a reranker or generation-backed scorer first, not as an embedding provider.
- Add tests for missing API key, missing SDK, model selection persistence, and Docker environment wiring.
- Keep Gemini fallback behavior unchanged while adding Groq.

## Follow-Up Model Families

After Groq, consider a general model registry that can describe provider capabilities:

- provider id
- display name
- model id
- task support: embedding, rerank, scoring, chat
- latency/cost hint
- requires network
- required environment variables
