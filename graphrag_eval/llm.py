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


class Config(BaseModel):
    generation: GenerationConfig
    embedding: EmbeddingConfig | None = None


def create_llm_and_embedder(config: "evaluation.Config") -> \
tuple[Optional["InstructorBaseRagasLLM"], Optional["BaseRagasEmbedding"]]:
    if config.llm:
        import litellm
        from ragas.llms import llm_factory

        ragas_llm = llm_factory(
            provider="litellm",
            model=f"{config.llm.generation.provider}/{config.llm.generation.model}",
            client=litellm.acompletion,
        )
        ragas_llm.is_async = True

        if config.llm.embedding:
            from ragas.embeddings.base import embedding_factory
            
            ragas_embedder = embedding_factory(
                provider="litellm",
                model=config.llm.embedding.model,
            )
            ragas_embedder.is_async = True
            
            return ragas_llm, ragas_embedder
        return ragas_llm, None
    return None, None


def generate(config: GenerationConfig, prompt: str) -> str:
    import litellm
    try:
        response = litellm.completion(
            messages=[{"role": "user", "content": prompt}],
            **config.model_dump()
        )
        return response.choices[0].message.content.strip("\n")
    except Exception as e:
        return str(e).replace("\n", "    ")
