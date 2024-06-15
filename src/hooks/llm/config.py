import dataclasses
import typing

import pydantic
import tenacity


class LLMConfigDictionary(typing.TypedDict):
    name: str
    connection: dict[str, str]
    retry: dict[str, int | None]


@dataclasses.dataclass(kw_only=True)
class RetryConfig():
    delay: int = dataclasses.field(default=1)
    retries: int = dataclasses.field(default=1)

    _wait: tenacity.wait.WaitBaseT = dataclasses.field(init=False)
    _stop: tenacity.stop.StopBaseT = dataclasses.field(init=False)

    def __post_init__(self):
        self._wait = tenacity.wait_fixed(self.delay)
        self._stop = tenacity.stop_after_attempt(self.retries)

    def get_policy_config(self) -> dict[str, int]:
        return {
            field.name: getattr(self, field.name)
            for field in dataclasses.fields(self)
            if field.name.startswith("_")
        }


class LLMProviderConfig(pydantic.BaseModel):
    connection: dict[str, str] = pydantic.Field(
        title="Connection",
        description="Connection configuration specific for the LLM provider",
    )
    retry: dict[str, int | None]
    _retry: RetryConfig = pydantic.PrivateAttr()

    @pydantic.field_validator('retry')
    @classmethod
    def check_retry(cls, retry_config: dict[str, int | None]):
        if not retry_config:
            raise ValueError("Retry configuration is required")
        return cls.__check_retry_config(retry_config)

    @classmethod
    def __check_retry_config(cls, config: dict[str, int | None]) -> dict[str, int | None]:
        cls._retry = RetryConfig(**config)  # type: ignore
        return config
