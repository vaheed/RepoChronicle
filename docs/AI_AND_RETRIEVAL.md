# AI Providers, Embeddings, Retrieval, and Context Budgets

## Provider contracts

The application uses separate interfaces for chat generation and embeddings. A configured chat model does not imply that the same provider/model can produce compatible embeddings.

### Chat generation

`LLMProvider` accepts a bounded message/evidence bundle and returns content, optional usage metadata, finish reason, and provider trace metadata. The OpenAI-compatible adapter targets `/chat/completions` and can support OpenAI, compatible hosted APIs, Ollama, vLLM and llama.cpp server deployments where their API contract is compatible.

Do not assume a provider is free, local, private, or license-unrestricted just because it supports an OpenAI-style URL.

### Embeddings

`EmbeddingProvider` accepts batches and returns vectors plus:
- provider/model/version;
- vector dimensions;
- normalization policy;
- input truncation/tokenizer information;
- embedding-space ID;
- model-license review record.

The built-in local adapter is planned around FastEmbed/ONNX CPU execution. It must lazily load its selected model, cache weights in a dedicated volume, and never fetch weights during Docker image build. Hosted embeddings are optional.

### Optional fine-tuning

Training is not part of the request path. The planned trainer consumes explicitly approved, redacted, versioned training examples and emits a model artifact plus a reproducible evaluation report. Fine-tuned weights are disabled by default and must pass comparison against a frozen retrieval-only baseline before promotion.

## Search strategy

- Exact symbol/file/identifier query: lexical search first; use symbol index and graph expansion.
- Natural-language code question: hybrid lexical + dense retrieval; optionally rerank a bounded candidate set.
- What changed/when/who: relational event query by timestamps/actors/source IDs, not vector search alone.
- Cross-project impact: explicit project dependency graph and symbol/call references, with evidence for each edge.
- Team discussion: retrieve only authorized, retained messages/threads; prefer recent messages and direct reply context.
- Mixed question: combine relevant retrievers and deduplicate results by evidence identity.

Recommended first ranker: weighted lexical + dense scores or Reciprocal Rank Fusion. Record retrieval parameters so evaluation is reproducible. Add learned rerankers only when offline retrieval evaluations show a measurable improvement.

## Context budget policy

Budget is explicit per request. At minimum track:
- system/developer instructions;
- MCP/tool descriptions;
- prior conversation summary;
- query and metadata;
- evidence snippets;
- expected answer reserve.

Do not estimate from repository size. Estimate from selected evidence and keep a safety margin. Evidence records should include a stable citation ID, source URL, repository/channel, commit/message/event ID, path and line range when available, timestamp, score, indexed revision, and source ACL.

Selection policy:
1. Remove duplicates and superseded evidence.
2. Keep exact-match/high-confidence evidence and diversify across files/events where useful.
3. Enforce per-source and per-thread caps to avoid one large file dominating.
4. Drop low-ranked items before truncating the highest-ranked evidence.
5. Always reserve tokens for the answer and citations.
6. If evidence does not fit, return a smaller pack or ask a targeted follow-up; do not increase context unboundedly.

The starter includes a character-budget utility as a dependency-light contract. Production must use a tokenizer appropriate to the selected model and test its estimator against actual usage.

## Citation correctness

The answer validator checks that every citation refers to an item returned in the evidence pack and that file/line/revision metadata is present for code evidence. If it cannot validate a citation, the answer must omit the claim or label it as an unverified hypothesis.

## Memory types

- **Source facts:** extracted directly from code/config/API schemas.
- **Activity facts:** commits, PR/MR discussions, issues, pipeline events and chat events.
- **Decisions:** explicit decision records or carefully sourced conclusions with evidence.
- **Summaries:** derived, time-bounded views; never a source of truth.
- **Hypotheses:** uncertain inferences shown as uncertain and never silently promoted to verified facts.

Every memory object has source evidence, `valid_from`, optional `valid_until`, verification state, model/recipe provenance if generated, and invalidation rules.
