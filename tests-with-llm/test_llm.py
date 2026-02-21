from graphrag_eval import evaluation
from graphrag_eval import llm
from graphrag_eval.llm import (
    GenerationConfig,
    EmbeddingConfig,
    create_llm_and_embeddings,
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
