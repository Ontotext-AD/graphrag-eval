from pydantic import BaseModel, ConfigDict, Field, model_validator


class Config(BaseModel):
    name: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1)
    model_config = ConfigDict(extra='allow')

    @model_validator(mode="after")
    def validate_config(self):
        if len(self.name.split("/")) != 2:
            msg = "'name' format should be '<provider>/<model_name_and_version>'"
            raise ValueError(msg)
        return self

    

def call(config: Config, prompt: str) -> str:
    import litellm
    try:
        response = litellm.completions(
            messages=[{"role": "user", "content": prompt}],
            **config.dict()
        )
        return response.choices[0].message.content.strip("\n")
    except Exception as e:
        return str(e).replace("\n", "    ")
