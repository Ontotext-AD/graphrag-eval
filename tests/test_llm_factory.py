from pytest import raises

from graphrag_eval.llm_factory import (
    LLMConfig,
    GenerationConfig,
    EmbeddingConfig,
)


def test_config_ok():
    c = LLMConfig(
        generation=GenerationConfig(
            provider="generation_provider",
            model="generation_model",
            temperature=0.5,
            max_tokens=100
        ),
        embedding=EmbeddingConfig(
            provider="embedding_provider",
            model="embedding_model"
        )
    )
    assert getattr(c.generation, "provider") == "generation_provider"
    assert getattr(c.generation, "model") == "generation_model"
    assert getattr(c.generation, "temperature") == 0.5
    assert getattr(c.generation, "max_tokens") == 100
    assert getattr(c.embedding, "provider") == "embedding_provider"
    assert getattr(c.embedding, "model") == "embedding_model"


def test_config_optional():
    c = LLMConfig(
        generation=GenerationConfig(
            provider="generation_provider",
            model="generation_model",
            temperature=0.5,
            max_tokens=100,
            optional_int=1,
            optional_float=999999999.9999,
            optional_str="test",
            optional_bool=True,
            optional_null=None,
        ),
        embedding=EmbeddingConfig(
            provider="embedding_provider",
            model="embedding_model"
        ),
    )
    assert getattr(c.generation, "optional_int") == 1
    assert getattr(c.generation, "optional_float") == 999999999.9999
    assert getattr(c.generation, "optional_str") == "test"
    assert getattr(c.generation, "optional_bool") is True
    assert getattr(c.generation, "optional_null") is None


def test_config_invalid_temperature():
    with raises(ValueError):
        LLMConfig(
            generation=GenerationConfig(
                provider="generation_provider",
                model="generation_model",
                temperature=-0.5,
                max_tokens=100
            ),
            embedding=EmbeddingConfig(
                provider="embedding_provider",
                model="embedding_model"
            )
        )
    with raises(ValueError):
        LLMConfig(
            generation=GenerationConfig(
                provider="generation_provider",
                model="generation_model",
                temperature=2.1,
                max_tokens=100
            ),
            embedding=EmbeddingConfig(
                provider="embedding_provider",
                model="embedding_model"
            )
        )


def test_config_invalid_max_tokens():
    with raises(ValueError):
        LLMConfig(
            generation=GenerationConfig(
                provider="generation_provider",
                model="generation_model",
                temperature=0.5,
                max_tokens=-5
            ),
            embedding=EmbeddingConfig(
                provider="embedding_provider",
                model="embedding_model"
            )
        )

    with raises(ValueError):
        LLMConfig(
            generation=GenerationConfig(
                provider="generation_provider",
                model="generation_model",
                temperature=0.5,
                max_tokens=0
            ),
            embedding=EmbeddingConfig(
                provider="embedding_provider",
                model="embedding_model"
            )
        )
