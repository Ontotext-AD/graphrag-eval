from graphrag_eval import evaluation
from graphrag_eval.llm_factory import (
    LLMConfig,
    GenerationConfig,
    EmbeddingConfig,
    create_llm,
    create_embedder,
)


def test_create_llm_and_embeddings_no_llm_config():
    llm = create_llm(evaluation.Config().llm)
    embedder = create_embedder(evaluation.Config().llm)
    assert llm is None
    assert embedder is None


def test_create_llm_and_embeddings_llm_config_no_embedding_config():
    config = evaluation.Config(
        llm=LLMConfig(
            generation=GenerationConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=100
            )
        )
    )
    llm = create_llm(config.llm)
    embedder = create_embedder(config.llm)
    assert llm is not None
    assert llm.model == "openai/gpt-3.5-turbo"
    assert embedder is None


def test_create_llm_and_embeddings_llm_config_embedding_config():
    config = evaluation.Config(
        llm=LLMConfig(
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
    llm = create_llm(config.llm)
    embedder = create_embedder(config.llm)
    assert llm is not None
    assert llm.model == "openai/gpt-3.5-turbo"
    assert embedder is not None
    assert embedder.model == "openai/text-embedding-ada-002"
