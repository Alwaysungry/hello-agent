import os
import types

import pytest

from model_client import model_client


class FakeClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_defaults_when_env_missing(monkeypatch):
    # Ensure env vars are not set
    for key in ("LLM_MODEL_ID", "LLM_MODLE_ID", "LLM_API_KEY", "LLM_BASE_URL"):
        monkeypatch.delenv(key, raising=False)

    client = model_client.create_deepseek_model_client(client_cls=FakeClient)
    assert isinstance(client, FakeClient)
    assert client.kwargs["model"] == "deepseek-chat"
    assert client.kwargs.get("api_key") is None
    assert client.kwargs.get("base_url") is None


def test_reads_env_vars(monkeypatch):
    monkeypatch.setenv("LLM_MODEL_ID", "deepseek-chat-pro")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com")

    client = model_client.create_deepseek_model_client(client_cls=FakeClient)
    assert client.kwargs["model"] == "deepseek-chat-pro"
    assert client.kwargs["api_key"] == "test-key"
    assert client.kwargs["base_url"] == "https://api.example.com"


def test_legacy_typo_env_var_supported(monkeypatch):
    # When new var absent and legacy present, legacy should be used
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)
    monkeypatch.setenv("LLM_MODLE_ID", "legacy-id")

    client = model_client.create_deepseek_model_client(client_cls=FakeClient)
    assert client.kwargs["model"] == "legacy-id"
