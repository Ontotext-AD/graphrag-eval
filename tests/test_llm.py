from pytest import raises

from graphrag_eval import evaluation
from graphrag_eval import llm
from graphrag_eval.llm import (
    GenerationConfig,
    EmbeddingConfig,
    create_llm_and_embeddings,
)


def test_config_ok():
    c = llm.Config(
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
    c = llm.Config(
        generation=llm.GenerationConfig(
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
        llm.Config(
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
        llm.Config(
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
        llm.Config(
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

    with raises(ValueError):
        llm.Config(
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


def test_create_llm_and_embeddings_no_llm_config():    
    llm, embeddings = create_llm_and_embeddings(evaluation.Config())
    assert llm is None
    assert embeddings is None


def test_create_llm_and_embeddings_llm_config_no_embedding_config():
    config = evaluation.Config(
        llm=llm.Config(
            generation=GenerationConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=100
            )
        )
    )
    llm_, embeddings = create_llm_and_embeddings(config)
    assert llm_ is not None
    assert llm_.provider == "openai"
    assert llm_.model == "gpt-3.5-turbo"
    assert llm_.is_async
    assert embeddings is None


def test_create_llm_and_embeddings_llm_config_embedding_config():
    config = evaluation.Config(
        llm=llm.Config(
            generation=GenerationConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=100
            ),
            embedding=EmbeddingConfig(
                provider="openai",
                model="text-embedding-ada-002"
            ),
        ),
    )
    llm_, embeddings = create_llm_and_embeddings(config)
    assert llm_ is not None
    assert llm_.provider == "openai"
    assert llm_.model == "gpt-3.5-turbo"
    assert llm_.is_async
    assert embeddings is not None
    assert embeddings.model == "text-embedding-ada-002"
    assert embeddings.is_async
