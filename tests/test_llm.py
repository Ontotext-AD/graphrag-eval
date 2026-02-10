from pytest import raises

from graphrag_eval.llm import Config


def test_config_ok():
    c = Config(name="openai/gpt-3.5-turbo", temperature=0.5, max_tokens=100)
    assert getattr(c, "name") == "openai/gpt-3.5-turbo"
    assert getattr(c, "temperature") == 0.5
    assert getattr(c, "max_tokens") == 100


def test_config_optional():
    c = Config(
        name="openai/gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=100,
        optional_int=1,
        optional_float=999999999.9999,
        optional_str="test",
        optional_bool=True,
        optional_null=None,
    )
    assert getattr(c, "optional_int") == 1
    assert getattr(c, "optional_float") == 999999999.9999
    assert getattr(c, "optional_str") == "test"
    assert getattr(c, "optional_bool") is True
    assert getattr(c, "optional_null") is None


def test_config_invalid_name():
    with raises(ValueError):
        Config(name="invalid_name", temperature=0.5, max_tokens=100)

    with raises(ValueError):
        Config(name="too/many/parts", temperature=0.5, max_tokens=100)


def test_config_invalid_temperature():
    with raises(ValueError):
        Config(name="openai/gpt-3.5-turbo", temperature=-0.1, max_tokens=100)

    with raises(ValueError):
        Config(name="openai/gpt-3.5-turbo", temperature=2.1, max_tokens=100)


def test_config_invalid_max_tokens():
    with raises(ValueError):
        Config(name="openai/gpt-3.5-turbo", temperature=0.5, max_tokens=-1)

    with raises(ValueError):
        Config(name="openai/gpt-3.5-turbo", temperature=0.5, max_tokens=0)
