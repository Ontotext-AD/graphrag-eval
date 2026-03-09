from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerationConfig(BaseModel):
    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1)
    model_config = ConfigDict(extra='allow')


class EmbeddingConfig(BaseModel):
    provider: str
    model: str
    model_config = ConfigDict(extra='allow')


class Config(BaseModel):
    generation: GenerationConfig
    embedding: EmbeddingConfig | None = None


def create_llm_and_embedder(config: "evaluation.Config") -> \
tuple[Optional["InstructorBaseRagasLLM"], Optional["BaseRagasEmbedding"]]:
    if config.llm:
        import litellm
        from ragas.llms import llm_factory

        litellm.drop_params = True  # Remove unsupported params from requests

        params = config.llm.generation.model_dump()
        ragas_llm = llm_factory(
            provider="litellm",
            model=f"{params.pop('provider')}/{params.pop('model')}",
            client=litellm.acompletion,
            **params,
        )
        ragas_llm.is_async = True

        if config.llm.embedding:
            from ragas.embeddings.base import embedding_factory
            
            params = config.llm.embedding.model_dump()
            ragas_embedder = embedding_factory(
                provider="litellm",
                model=f"{params.pop('provider')}/{params.pop('model')}",
                **params,
            )
            ragas_embedder.is_async = True
            
            return ragas_llm, ragas_embedder
        return ragas_llm, None
    return None, None
