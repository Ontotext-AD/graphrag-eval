from pytest import raises

from graphrag_eval.llm import Config, GenerationConfig, EmbeddingConfig


def test_config_ok():
    c = Config(
        generation=GenerationConfig(
            provider="openai",
            name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=100
        ),
        embedding=EmbeddingConfig(
            provider="openai",
            name="text-embedding-ada-002"
        )
    )
    assert getattr(c.generation, "provider") == "openai"
    assert getattr(c.generation, "name") == "gpt-3.5-turbo"
    assert getattr(c.generation, "temperature") == 0.5
    assert getattr(c.generation, "max_tokens") == 100
    assert getattr(c.embedding, "provider") == "openai"
    assert getattr(c.embedding, "name") == "text-embedding-ada-002"


def test_config_optional():
    c = Config(
        generation=GenerationConfig(
            provider="openai",
            name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=100,
            optional_int=1,
            optional_float=999999999.9999,
            optional_str="test",
            optional_bool=True,
            optional_null=None,
        ),
        embedding=EmbeddingConfig(
            provider="openai",
            name="text-embedding-ada-002"
        ),
    )
    assert getattr(c.generation, "optional_int") == 1
    assert getattr(c.generation, "optional_float") == 999999999.9999
    assert getattr(c.generation, "optional_str") == "test"
    assert getattr(c.generation, "optional_bool") is True
    assert getattr(c.generation, "optional_null") is None


def test_config_invalid_temperature():
    with raises(ValueError):
        Config(
            generation=GenerationConfig(
                provider="openai",
                name="gpt-3.5-turbo",
                temperature=-0.5,
                max_tokens=100
            ),
            embedding=EmbeddingConfig(
                provider="openai",
                name="text-embedding-ada-002"
            )
        )
    with raises(ValueError):
        Config(
            generation=GenerationConfig(
                provider="openai",
                name="gpt-3.5-turbo",
                temperature=2.1,
                max_tokens=100
            ),
            embedding=EmbeddingConfig(
                provider="openai",
                name="text-embedding-ada-002"
            )
        )


def test_config_invalid_max_tokens():
    with raises(ValueError):
        Config(
            generation=GenerationConfig(
                provider="openai",
                name="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=-1
            ),
            embedding=EmbeddingConfig(
                provider="openai",
                name="text-embedding-ada-002"
            )
        )

    with raises(ValueError):
        Config(
            generation=GenerationConfig(
                provider="openai",
                name="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=0
            ),
            embedding=EmbeddingConfig(
                provider="openai",
                name="text-embedding-ada-002"
            )
        )
