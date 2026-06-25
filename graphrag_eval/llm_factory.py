from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ragas.llms.base import InstructorBaseRagasLLM
    from ragas.embeddings.base import BaseRagasEmbeddings, BaseRagasEmbedding


class GenerationConfig(BaseModel):
    provider: str
    model: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    model_config = ConfigDict(extra='allow')


class EmbeddingConfig(BaseModel):
    provider: str
    model: str
    model_config = ConfigDict(extra='allow')


class LLMConfig(BaseModel):
    generation: GenerationConfig
    embedding: EmbeddingConfig | None = None


def create_llm(
    config: LLMConfig | None
) -> InstructorBaseRagasLLM | None:
    if config:
        import litellm
        from ragas.llms import llm_factory

        litellm.drop_params = True  # Remove unsupported params from requests
        params = config.generation.model_dump()
        ragas_llm = llm_factory(
            provider="litellm",
            model=f"{params.pop('provider')}/{params.pop('model')}",
            client=litellm.acompletion,
            **params,
        )
        ragas_llm.is_async = True
        return ragas_llm
    return None


def create_embedder(
    config: LLMConfig | None
) -> BaseRagasEmbeddings | BaseRagasEmbedding | None:
    if config and config.embedding:
        import litellm
        from ragas.embeddings.base import embedding_factory

        litellm.drop_params = True  # Remove unsupported params from requests
        params = config.embedding.model_dump()
        ragas_embedder = embedding_factory(
            provider="litellm",
            model=f"{params.pop('provider')}/{params.pop('model')}",
            client=litellm.acompletion,
            **params,
        )
        return ragas_embedder
    return None
