from __future__ import annotations
import dataclasses
import logging
import string
import random

import github
import github.Auth
import github.ContentFile
import github.Repository


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
                new_client._Github__requester,
                '_logger',
            )
            retry_handler = getattr(
                new_client._Github__requester,
                '__retry',
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
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

        self.logger.setLevel(logging.CRITICAL)
        try:
            user_readme_repo.get_contents('README.md')
        except github.GithubException as failed_read_operation:
            raise github.BadCredentialsException(
                status=403,
                data={
                    'message': 'Token has insufficient read permissions!',
                }
            ) from failed_read_operation
        try:
            created_file = user_readme_repo.create_file(
                path=f'{random_commit_message}',
                message=random_commit_message,
                content=random_commit_message,
                branch='main'
            )
            user_readme_repo.delete_file(
                path=created_file.path(),
                message=random_commit_message,
                sha=created_file.sha(),
                branch='main'
            )
            raise github.BadCredentialsException(
                status=403,
                data={
                    'message': 'Token has unnecessary read and write permissions! Aborting to prevent misuse',
                }
            )
        except github.GithubException:
            self.logger.setLevel(logging.INFO)
            self.logger.info("Token has only read permissions. Proceeding.")
            return

    @property
    def repositories(self) -> list[github.Repository.Repository]:
        return list(
            self.__client.get_user().get_repos()
        )

    def __post_init__(self) -> None:
        self.logger.info(f", default_factory=logging.getLoggerConnected to Github as {self.username}")
