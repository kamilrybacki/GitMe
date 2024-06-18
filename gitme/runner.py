import dataclasses
import typing

import pandas

import gitme.gh
import gitme.config
import gitme.llm.base
import gitme.llm.setup
import gitme.llm.prompts


@dataclasses.dataclass
class GitMeRunner:
    config: dict[str, typing.Any] = dataclasses.field(repr=False)
    llm_provisioner: gitme.llm.base.LLMProvider = dataclasses.field(init=False, repr=False)
    github_hooks: gitme.gh.GithubProfile = dataclasses.field(init=False, repr=False)
    __parsed_configuration: gitme.config.RunnerConfig = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        """
            This function initializes the GitMeRunner class and parses the configuration.

            After the raw configuration is parsed, the configuration attribute is reset to an empty dictionary
            to prevent sensitive data from being exposed.
        """
        self.__parsed_configuration = gitme.config.RunnerConfig(self.config)
        self.config = {}

    # pylint: disable=protected-access
    def run(self) -> pandas.DataFrame:
        self.github_hooks = gitme.gh.GithubProfile.connect(
            username=self.__parsed_configuration._github.username,
            token=self.__parsed_configuration._github.token
        )
        self.llm_provisioner = gitme.llm.setup.get_provider(
            self.__parsed_configuration._llm
        )
        self.llm_provisioner.set_logger(self.github_hooks.logger)
        return pandas.DataFrame.from_records(
            data=self.summarize_repositories(
                repositories=self.get_repositories_to_analyze()
            )
        )

    def dump(self, df: pandas.DataFrame) -> None:
        """
        This function writes the DataFrame to a CSV file.
        """
        df.to_csv(
            self.__parsed_configuration.output,
            index=False
        )

    # pylint: disable=protected-access
    def get_repositories_to_analyze(self) -> list[gitme.gh.RepositoryMetadata]:
        """
        This function fetches the repositories to analyze from the GitHub profile.
        """
        if not self.__parsed_configuration._only_repos:
            all_repositories = ([
                *self.github_hooks.pinned_repositories,
            ] + [
                gitme.gh.RepositoryMetadata.from_repo(
                    self.github_hooks.get_repo(repo_name)
                )
                for repo_name in self.config
                if repo_name
            ]) if self.__parsed_configuration._add_repos else [
                *self.github_hooks.pinned_repositories
            ]
        else:
            self.github_hooks.log(f"Specified repositories to analyze: {', '.join(self.__parsed_configuration._only_repos)}")
            all_repositories = [
                gitme.gh.RepositoryMetadata.from_repo(
                    self.github_hooks.get_repo(repo_name)
                )
                for repo_name in self.__parsed_configuration._only_repos
            ]

        self.github_hooks.log(f"Repositories to analyze: {', '.join([
            repo.name
            for repo in all_repositories
        ])}")
        return all_repositories

    def summarize_repositories(
        self,
        repositories: list[gitme.gh.RepositoryMetadata],
    ) -> list[dict[str, str]]:
        """
        This is where the magic happens. We generate prompts for each repository and query the LLM model.

        The LLM model will generate a summary based on the prompt and return it to us.

        We then log the query and the result to the console.
        """
        summarized_data = []
        for repo in repositories:
            self.github_hooks.log(f"Processing {repo.name}")
            prompt = gitme.llm.prompts.generate_prompt(
                description=repo.description,
                technologies=repo.technologies,
                readme=repo.readme or "No README available. Use the repository description."
            )
            summary = self.llm_provisioner.query(prompt)
            summarized_data.append({
                'name': repo.name,
                'description': repo.description,
                'technologies': ', '.join(repo.technologies),
                'readme': repo.readme,
                'summary': summary.result
            })
        return summarized_data
