from __future__ import annotations
import abc
import dataclasses
import logging
import typing

import tenacity

import gitme.llm.config


class TokenCounters(typing.TypedDict):
    prompt: int
    total: int


@dataclasses.dataclass(kw_only=True, frozen=True)
class LLMQueryResult:
    query: str
    result: str
    tokens: TokenCounters


@dataclasses.dataclass
class LLMProvider(abc.ABC):
    _logger: logging.Logger = dataclasses.field(init=False, default=logging.getLogger(__name__))

    __instance: LLMProvider | None = dataclasses.field(init=False, default=None)
    __retry_policy: tenacity.Retrying | None = dataclasses.field(init=False, default=None)

    # pylint: disable=protected-access
    @classmethod
    def initialize(cls, configuration: gitme.llm.config.LLMConfigDictionary) -> LLMProvider:
        if not cls.__instance:
            parsed_config = gitme.llm.config.LLMProviderConfig(
                connection=configuration["connection"],
                retry=configuration["retry"],
            )
            cls.__retry_policy = tenacity.Retrying(**{
                field.removeprefix('_'): getattr(parsed_config._retry, field)
                for field in parsed_config._retry.get_policy_config()
                if field.startswith("_")
            } | {
                "reraise": True
            })
            setattr(cls, "connect", cls.__retry_policy.wraps(cls.connect))
            cls.__instance = cls.connect(
                parsed_config.connection
            )
        return cls.__instance

    def set_logger(self, logger: logging.Logger) -> None:
        self._logger = logger

    @classmethod
    @abc.abstractmethod
    def connect(cls, config: dict[str, str]) -> LLMProvider:  # pylint: disable=redefined-outer-name
        pass

    @abc.abstractmethod
    def query(self, query: str) -> LLMQueryResult:
        pass

    @abc.abstractmethod
    def count_tokens(self, query: str) -> int:
        pass

    def log(self, message_data: typing.Any, level: int = logging.INFO) -> None:
        self._logger.log(
            level=level,
            msg=str(message_data)
        )
