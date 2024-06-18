from __future__ import annotations
import dataclasses
import typing

import pydantic
import tenacity

import gitme.gh
import gitme.config
import gitme.llm.base
import gitme.llm.prompts

#     Here are the dictionaries that need to be defined by the used as
#     configuration for the RunnerConfig class:

#     Example:
#     {
#         "llm": {
#             "name": "...",
#             "connection": ...,
#             "retry": ...
#         },
#         "github": {
#             "username": ...,
#             "token": ...,
#             "only": ...,  <- optional
#             "add": ...  <- optional
#         },
#         "output": ...
#     }


class LLMConfigDictionary(typing.TypedDict):
    """
        Configuration for the LLM provider in the form of a dictionary

        name: str - Name of the LLM provider
        connection: dict[str, str] - Connection configuration specific for the LLM provider
        retry: dict[str, int | None] - Retry configuration for the LLM provider
    """
    name: str
    connection: dict[str, str]
    retry: dict[str, int | None]


class GithubConfigDictionary(typing.TypedDict):
    """
        Configuration for the GitHub profile in the form of a dictionary

        username: str - GitHub username
        token: str - GitHub read-only token
        only: str - Comma-separated list of exclusive repositories to analyze
        add: str - Comma-separated list of additional repositories to analyze
    """
    username: str
    token: str
    only: typing.Optional[str]
    add: typing.Optional[str]


class RunnerConfigDictionary(typing.TypedDict):
    """
        Configuration for the GitMeRunner in the form of a dictionary

        llm: LLMConfigDictionary - Configuration for the LLM provider
        github: GithubConfigDictionary - Configuration for the GitHub profile adapter
        output: str - Output file name
    """
    llm: LLMConfigDictionary
    github: GithubConfigDictionary
    output: str


# Below here are actual config classes that are used to parse the dictionaries
# into the internal configuration objects used by the Runner.


@dataclasses.dataclass
class RunnerConfig:
    """
        Class for managing configuration for the GitMeRunner, which is used to run the analysis.

        The actual data used by the Runner is located in the underscored, internal attributes,
        which are initialized in the __post_init__ method based on the provided configuration sections (llm, github, output).

        llm: LLMConfigDictionary - Configuration for the LLM provider
        github: GithubConfigDictionary - Configuration for the GitHub profile adapter
        output: str - Output file name
    """
    config: RunnerConfigDictionary
    output: str = dataclasses.field(init=False)
    _llm: gitme.config.LLMProviderConfig = dataclasses.field(init=False)
    _github: gitme.config.GithubProfileConfig = dataclasses.field(init=False)
    _only_repos: str = dataclasses.field(init=False)
    _add_repos: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.output = self.config["output"]
        github_section = self.config["github"]
        self._github = gitme.config.GithubProfileConfig(
            username=github_section["username"],
            token=github_section["token"],
        )
        self._only_repos = self.split_and_check_repos(
            github_section.get("only", "")
        )
        self._add_repos = self.split_and_check_repos(
            github_section.get("add", "")
        )

        self._llm = gitme.config.LLMProviderConfig(**self.config["llm"])
        self.config = {}

    def split_and_check_repos(self, repos_list: str) -> list[str]:
        cleaned_repos = []
        if not repos_list:
            return cleaned_repos
        split_repos_list = repos_list.split(",") if "," in repos_list else [repos_list]
        for repo in split_repos_list:
            if username := self.config["github"]["username"] in repo:
                repo = repo.replace(f"{username}/", "")
            if not repo:
                continue
            cleaned_repos.append(repo)
        return cleaned_repos


class GithubProfileConfig(pydantic.BaseModel):
    """
        Configuration for the GitHub profile in the form of a Pydantic model for quick validation and parsing.

        username: str - GitHub username
        token: str - GitHub read-only token
    """
    username: str = pydantic.Field(
        title="Username",
        description="GitHub username",
        min_length=1,
    )
    token: str = pydantic.Field(
        title="Token",
        description="GitHub token",
        max_length=255,
        pattern=r"^[A-Za-z0-9_]+$",
        repr=False,
    )


class LLMProviderConfig(pydantic.BaseModel):
    """
        Configuration for the LLM provider in the form of a Pydantic model for quick validation and parsing.

        Here the translation between user config for retry and the tenacity-based retry policy is done in the __post_init__ method.

        name: str - Name of the LLM provider
        connection: dict[str, str] - Connection configuration specific for the LLM provider
        retry: dict[str, int | None] - Retry configuration for the LLM provider
    """
    name: str = pydantic.Field(
        title="Name",
        description="Name of the LLM provider",
        min_length=1,
    )
    connection: dict[str, str] = pydantic.Field(
        title="Connection",
        description="Connection configuration specific for the LLM provider",
        repr=False,
    )
    retry: dict[str, int | None] = pydantic.Field(
        title="Retry",
        description="Retry configuration for the LLM provider",
    )
    _retry: RetryConfig = pydantic.PrivateAttr()

    @pydantic.field_validator('retry')
    @classmethod
    def check_retry(cls, retry_config: dict[str, int | None]) -> dict[str, int | None]:
        if not retry_config:
            raise ValueError("Retry configuration is required")
        return cls.__check_retry_config(retry_config)

    @classmethod
    def __check_retry_config(cls, config: dict[str, int | None]) -> dict[str, int | None]:
        cls._retry = RetryConfig(**config)  # type: ignore
        return config


@dataclasses.dataclass(kw_only=True)
class RetryConfig():
    """
        Class for managing retry configuration for the LLM provider,
        which is used to retry the connection in case of failure.

        Human-readable configuration is transformed into tenacity-based wrappers in the __post_init__ method, that are used to decorate
        connection methods in the LLM provider.

        delay: int - Delay between attempts in seconds
        attempts: int - Number of attempts before throwing an RetryError
    """
    delay: int = dataclasses.field(default=1)
    attempts: int = dataclasses.field(default=1)

    _wait: tenacity.wait.WaitBaseT = dataclasses.field(init=False)
    _stop: tenacity.stop.StopBaseT = dataclasses.field(init=False)

    def __post_init__(self):
        self._wait = tenacity.wait_fixed(self.delay)
        self._stop = tenacity.stop_after_attempt(self.attempts)

    def get_policy_config(self) -> dict[str, int]:
        return {
            field.name: getattr(self, field.name)
            for field in dataclasses.fields(self)
            if field.name.startswith("_")
        }
