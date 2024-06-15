from __future__ import annotations
import abc
import dataclasses

import tenacity

import hooks.llm.config
import hooks.llm.gemini


@dataclasses.dataclass
class LLMProvider(abc.ABC):
    __instance: LLMProvider | None = dataclasses.field(init=False, default=None)
    __retry_policy: tenacity.Retrying | None = dataclasses.field(init=False, default=None)

    # pylint: disable=protected-access
    @classmethod
    def initialize(cls, configuration: hooks.llm.config.LLMConfigDictionary) -> LLMProvider:
        if not cls.__instance:
            parsed_config = hooks.llm.config.LLMProviderConfig(
                connection=configuration["connection"],
                retry=configuration["retry"],
            )
            cls.__retry_policy = tenacity.Retrying(**{
                field.removeprefix('_'): getattr(parsed_config._retry, field)
                for field in parsed_config._retry.get_policy_config()
                if field.startswith("_")
            })
            setattr(cls, "connect", cls.__retry_policy.wraps(cls.connect))
            cls.__instance = cls.connect(
                parsed_config.connection
            )
        return cls.__instance

    @classmethod
    @abc.abstractmethod
    def connect(cls, config: dict[str, str]) -> LLMProvider:  # pylint: disable=redefined-outer-name
        pass

    @abc.abstractmethod
    def query(self, query: str) -> str:
        pass
