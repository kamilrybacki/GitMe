import math
import logging
import random
import string

import google.generativeai
from google.generativeai.types.generation_types import BaseGenerateContentResponse
from google.generativeai.protos import GenerateContentResponse, CountTokensResponse
import pytest

import gitme.config
import gitme.llm.base
import gitme.llm.providers.google
import gitme.llm.setup


class MockGenerativeModel(google.generativeai.GenerativeModel):
    def generate_content(self, prompt: str) -> BaseGenerateContentResponse:
        return BaseGenerateContentResponse(
            done=True,
            result=GenerateContentResponse(
                usage_metadata=GenerateContentResponse.UsageMetadata(
                    total_token_count=len(prompt.split())
                ),
            ),
            iterator=None
        )

    def count_tokens(self, prompt: str) -> CountTokensResponse:
        return CountTokensResponse(
            total_tokens=len(prompt.split())
        )


# pylint: disable=all
class MockGoogleAI(gitme.llm.providers.google.GoogleAI):
    model: str = "mockini-1.0-pro"
    _tokens_to_send: int = 0

    @classmethod
    def connect(cls, config: dict[str, str]) -> gitme.llm.base.LLMProvider:
        return cls(
            _model=MockGenerativeModel(model_name=cls.model),
            _limits={
                'TPM': 0,
                'RPM': 0,
            },
            _usage_counters={
                'TPM': 0,
                'RPM': 0,
            }
        )

    def query(self, query: str) -> gitme.llm.base.LLMQueryResult:
        if self._are_limits_exceeded(
            self._tokens_to_send
        ):
            raise ValueError("Usage limits exceeded")
        usage_data = gitme.llm.base.TokenCounters(
            prompt=self._tokens_to_send,
            total=self._tokens_to_send
        )
        self._update_usage_counters(usage_data)
        return gitme.llm.base.LLMQueryResult(
            query=query,
            result="Mocked result",
            tokens=usage_data
        )


@pytest.mark.parametrize(
    "limit, which_limit",
    [
        (
            random.randint(1, 100),
            random.choice(['TPM', 'RPM'])
        )
        for _ in range(100)
    ]
)
def test_token_limiter(
    limit: int,
    which_limit: str,
) -> None:
    provider = MockGoogleAI.connect({})
    provider._limits = {
        'TPM': limit if which_limit == 'TPM' else math.inf,
        'RPM': limit if which_limit == 'RPM' else math.inf
    }
    provider._tokens_to_send = limit + 1 if which_limit == 'TPM' else 1
    iterations = limit + 1 if which_limit == 'RPM' else 1
    with pytest.raises(ValueError):
        for _ in range(iterations):
            provider.query("Some query")


@pytest.mark.parametrize(
    "name",
    [
        model
        for model in gitme.llm.setup.__AVAILABLE_PROVIDERS.keys()
        if model.startswith("G")
    ]
)
def test_google_model(name: str, monkeypatch) -> None:
    fake_api_key = "AI" + ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(37)
    )
    provider_config = gitme.config.LLMProviderConfig(
        name=name,
        connection={
            "api_key": fake_api_key
        },
        retry={
            "delay": 1,
            "attempts": 3
        }
    )
    monkeypatch.setattr(
        "google.generativeai.configure",
        lambda api_key: logging.info(f"Configured with mock api key: {api_key}")
    )
    provider: gitme.llm.base.LLMProvider = gitme.llm.setup.get_provider(provider_config)
    provider._model = MockGenerativeModel(model_name=provider.model)  # type: ignore
    with pytest.raises(ValueError):
        provider.query("Some query")
