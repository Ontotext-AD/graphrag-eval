from pydantic import BaseModel, Field


class GenerationConfig(BaseModel):
    provider: str
    name: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1)


class EmbeddingConfig(BaseModel):
    provider: str
    name: str


class Config(BaseModel):
    generation: GenerationConfig
    embedding: EmbeddingConfig


def call(config: Config, prompt: str) -> str:
    import litellm
    try:
        response = litellm.completions(
            model=config.generation.provider + "/" + config.generation.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.generation.temperature
        )
        return response.choices[0].message.content.strip("\n")
    except Exception as e:
        return str(e).replace("\n", "    ")
