# pylint: disable=no-member
import abc
import dataclasses
import logging
import time

import google.generativeai.client

from gitme.llm.base import LLMProvider, LLMQueryResult, TokenCounters


# Limits below are taken from: https://aistudio.google.com/app/plan_information

MAX_TPM_PER_MODEL: dict[str, int] = {
    "gemini-1.0-pro": 32_000,
    "gemini-1.5-flash": 1_000_000,
}

MAX_RPM_PER_MODEL: dict[str, int] = {
    "gemini-1.0-pro": 2,
    "gemini-1.5-flash": 15,
}


@dataclasses.dataclass
class GoogleAI(LLMProvider, abc.ABC):
    _model: google.generativeai.GenerativeModel
    _limits: dict[str, int] = dataclasses.field(default_factory=dict)
    _usage_counters: dict[str, int] = dataclasses.field(default_factory=dict)
    _last_check_time: float = dataclasses.field(init=False, default=0)

    @property
    @abc.abstractmethod
    def model(self) -> str:
        pass

    @classmethod
    def connect(cls, config: dict[str, str]) -> LLMProvider:
        google.generativeai.configure(
            api_key=config.get("api_key"),
        )
        return cls(
            _model=google.generativeai.GenerativeModel(
                model_name=cls.model,
            ),
            _limits={
                'TPM': MAX_TPM_PER_MODEL[cls.model],  # type: ignore
                'RPM': MAX_RPM_PER_MODEL[cls.model],  # type: ignore
            },
            _usage_counters={
                'TPM': 0,
                'RPM': 0,
            }
        )

    def query(self, query: str) -> LLMQueryResult:
        tokens_to_send = self.count_tokens(query)
        self.log(f"Sending {tokens_to_send} tokens to the model.")
        if self._are_limits_exceeded(tokens_to_send):
            self.log("Usage limits exceeded. Waiting for the next minute to continue.", level=logging.WARNING)
            time.sleep(60)
        query_response = self._model.generate_content(query)
        result = LLMQueryResult(
            query=query,
            result=query_response.text,
            tokens=TokenCounters(
                prompt=tokens_to_send,
                total=query_response.usage_metadata.total_token_count,
            )
        )
        self._update_usage_counters(result.tokens)
        self.log(f"Provider generated {result.tokens['total'] - tokens_to_send} tokens in response.")
        return result

    def _are_limits_exceeded(self, requested_tokens: int) -> bool:
        current_time = time.time()
        if current_time - self._last_check_time > 60:
            self._usage_counters['TPM'] = 0
            self._usage_counters['RPM'] = 0
            self._last_check_time = current_time
        if self._usage_counters['TPM'] >= self._limits['TPM']:
            return True
        if self._usage_counters['TPM'] + requested_tokens > self._limits['TPM']:
            return True
        return not self._usage_counters['RPM'] < self._limits['RPM']

    def _update_usage_counters(self, tokens: TokenCounters) -> None:
        self._usage_counters['TPM'] += tokens['total']
        self._usage_counters['RPM'] += 2

    def count_tokens(self, query: str) -> int:
        return self._model.count_tokens(query).total_tokens


@dataclasses.dataclass
class GeminiOnePro(GoogleAI):
    model: str = "gemini-1.0-pro"


@dataclasses.dataclass
class GeminiOneHalfFlash(GoogleAI):
    model: str = "gemini-1.5-flash"
