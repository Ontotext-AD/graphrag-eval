from pydantic import BaseModel, Field


class Config(BaseModel):
    name: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1)


def call(config: Config, prompt: str) -> str:
    import litellm
    try:
        response = litellm.completions(
            model=config.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.temperature
        )
        return response.choices[0].message.content.strip("\n")
    except Exception as e:
        return str(e).replace("\n", "    ")
