from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms.base import InstructorBaseRagasLLM
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
tuple[InstructorBaseRagasLLM | None, BaseRagasEmbedding | None]:
    if config.llm:
        from openai import AsyncOpenAI
        from ragas.llms import llm_factory

        client = AsyncOpenAI()
        ragas_llm = llm_factory(
            provider=config.llm.generation.provider,
            model=config.llm.generation.model,
            client=client
        )
        if config.llm.embedding:
            from ragas.embeddings.base import embedding_factory
            
            ragas_embedder = embedding_factory(
                provider=config.llm.embedding.provider, 
                model=config.llm.embedding.model,
                client=client
            )
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
