# pylint: disable=no-member
import abc
import dataclasses
import time

import google.generativeai.client

from llm.base import LLMProvider, LLMQueryResult, TokenCounters


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
    _model: google.generativeai.GenerativeModel | None = dataclasses.field(init=False, default=None)
    __usage_counters: dict[str, int] = dataclasses.field(init=False, default_factory=dict)
    __last_check_time: float = dataclasses.field(init=False, default=0)

    @property
    @abc.abstractmethod
    def model(self) -> str:
        pass

    @classmethod
    def connect(cls, config: dict[str, str]) -> LLMProvider:
        if not cls._model:
            google.generativeai.configure(
                api_key=config.get("api_key"),
            )
            cls._model = google.generativeai.GenerativeModel(
                model_name=cls.model,
            )
            cls.__usage_counters = {
                'TPM': 0,
                'RPM': 0,
            }
        return cls()

    def query(self, query: str) -> LLMQueryResult:
        if not self._model:
            raise ValueError("Model not initialized")
        if self._are_limits_exceeded():
            self._logger.error("Usage limits exceeded. Waiting for the next minute to continue.")
            time.sleep(60)
        query_response = self._model.generate_content(query)
        result = LLMQueryResult(
            query=query,
            result=query_response.text,
            tokens=TokenCounters(
                prompt=query_response.usage_metadata.prompt_token_count,
                total=query_response.usage_metadata.total_token_count,
            )
        )
        self._update_usage_counters(result.tokens)
        return result

    def _are_limits_exceeded(self) -> bool:
        current_time = time.time()
        if current_time - self.__last_check_time > 60:
            self.__usage_counters['TPM'] = 0
            self.__usage_counters['RPM'] = 0
            self.__last_check_time = current_time
        if self.__usage_counters['TPM'] >= MAX_TPM_PER_MODEL[self.model]:
            return True
        return not self.__usage_counters['RPM'] < MAX_RPM_PER_MODEL[self.model]

    def _update_usage_counters(self, tokens: TokenCounters) -> None:
        self.__usage_counters['TPM'] += tokens['total']
        self.__usage_counters['RPM'] += 1

    def count_tokens(self, query: str) -> int:
        if not self._model:
            raise ValueError("Model not initialized")
        return self._model.count_tokens(query)


@dataclasses.dataclass
class GeminiOnePro(GoogleAI):
    model: str = "gemini-1.0-pro"


@dataclasses.dataclass
class GeminiOneHalfFlash(GoogleAI):
    model: str = "gemini-1.5-flash"
