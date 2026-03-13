from graphrag_eval import evaluation, llm
from graphrag_eval.llm import (
    GenerationConfig,
    EmbeddingConfig,
    create_llm,
    create_embedder,
)


def test_create_llm_and_embeddings_no_llm_config():    
    llm = create_llm(evaluation.Config())
    embedder = create_embedder(evaluation.Config())
    assert llm is None
    assert embedder is None


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
    llm_ = create_llm(config)
    embedder = create_embedder(config)
    assert llm_ is not None
    assert llm_.model == "openai/gpt-3.5-turbo"
    assert embedder is None


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
    llm_ = create_llm(config)
    embedder = create_embedder(config)
    assert llm_ is not None
    assert llm_.model == "openai/gpt-3.5-turbo"
    assert embedder is not None
    assert embedder.model == "openai/text-embedding-ada-002"
