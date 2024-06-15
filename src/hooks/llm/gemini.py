# pylint: disable=no-member
import abc
import dataclasses

import google.generativeai.client

from hooks.llm.base import LLMProvider


@dataclasses.dataclass
class GoogleAI(LLMProvider, abc.ABC):
    _model: google.generativeai.GenerativeModel | None = dataclasses.field(init=False, default=None)

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
        return cls()

    def query(self, query: str) -> str:
        if not self._model:
            raise ValueError("Model not initialized")
        return self._model.generate_content(query).text


@dataclasses.dataclass
class GeminiOnePro(GoogleAI):
    model: str = "gemini-1.0-pro"
