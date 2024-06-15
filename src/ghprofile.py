from __future__ import annotations
import dataclasses
import logging
import string
import random

import github
import github.Auth
import github.ContentFile
import github.Repository

import metadata


@dataclasses.dataclass
class GithubProfile:
    username: str

    logger: logging.Logger = dataclasses.field(init=False, default_factory=logging.getLogger)

    __client: github.Github = dataclasses.field(init=False, default_factory=github.Github)
    __instance: GithubProfile | None = dataclasses.field(default=None, init=False)

    # pylint: disable=protected-access
    @classmethod
    def connect(cls, username: str, token: str) -> GithubProfile:
        if not cls.__instance:
            new_instance = cls(username)
            authentication_data = github.Auth.Token(token)
            new_client = github.Github(auth=authentication_data)
            new_instance.logger = getattr(
                new_client._Github__requester,  # type: ignore
                '_logger',
            )
            retry_handler = getattr(
                new_client._Github__requester,  # type: ignore
                '_Requester__retry',
            )
            setattr(
                retry_handler,
                '__logger',
                new_instance.logger,
            )
            cls._patch_logger(new_instance.logger)
            new_instance.__client = new_client  # pylint: disable=unused-private-member
            new_instance.check_token_permissions()
            cls.__instance = new_instance
        return cls.__instance

    @staticmethod
    def _patch_logger(logger: logging.Logger) -> None:
        parent_logger: logging.Logger = logger.parent  # type: ignore
        parent_logger.setLevel(logging.INFO)
        parent_logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        parent_logger.addHandler(handler)

    def check_token_permissions(self) -> None:
        user_readme_repo: github.Repository.Repository = self.__client.get_repo(
            f'{self.__client.get_user().login}/{self.__client.get_user().login}'
        )

        random_commit_message = ''.join([
            random.choice(
                string.ascii_letters + string.digits
            )
            for _ in range(10)
        ])

        # Temporarily disable logging to prevent token leakage
        self.logger.setLevel(logging.CRITICAL)
        try:
            user_readme_repo.get_readme()
        except github.GithubException as failed_read_operation:
            raise github.BadCredentialsException(
                status=403,
                data={
                    'message': 'Token has insufficient read permissions!',
                }
            ) from failed_read_operation
        try:
            created_file: github.ContentFile.ContentFile = user_readme_repo.create_file(
                path=f'{random_commit_message}',
                message=random_commit_message,
                content=random_commit_message,
                branch='main'
            ).get('content')  # type: ignore
            user_readme_repo.delete_file(
                path=created_file.path,
                message=random_commit_message,
                sha=created_file.sha,
                branch='main'
            )
            raise github.BadCredentialsException(
                status=403,
                data={
                    'message': 'Token has unnecessary read and write permissions! Aborting to prevent misuse',
                }
            )
        except github.GithubException:  # We want this to happen, because it means the token has only read permissions
            self.logger.setLevel(logging.INFO)
            self.log("Token has only read permissions. Proceeding.")
            return

    def log(self, message: str, level: int = logging.INFO) -> None:
        self.logger.log(level, message)

    @property
    def _repositories(self) -> list[github.Repository.Repository]:
        return list(self.__client.get_user().get_repos())

    @property
    def repositories(self) -> list[metadata.RepositoryMetadata]:
        self.log(f"Fetching repositories for {self.username}")
        return [
            metadata.RepositoryMetadata(repo)
            for repo in self._repositories
        ]

    def get_repo_readme(self, repo: github.Repository.Repository) -> str:
        try:
            return repo.get_readme().decoded_content.decode('utf-8')
        except github.UnknownObjectException:
            return ''
        except github.GithubException as other_error:
            raise github.UnknownObjectException(
                status=404,
                data={
                    'message': 'Repo does not exist or is private',
                }
            ) from other_error

    def __repr__(self) -> str:
        return f'<GithubProfile username={self.username}>'

    def __post_init__(self) -> None:
        self.logger.info(f", default_factory=logging.getLoggerConnected to Github as {self.username}")
