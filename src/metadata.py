import dataclasses
import logging

import github.Repository


@dataclasses.dataclass
class RepositoryMetadata:
    repo: github.Repository.Repository

    name: str = dataclasses.field(init=False)
    readme: str = dataclasses.field(init=False)
    description: str = dataclasses.field(init=False)
    technologies: list[str] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self):
        self.name = self.repo.full_name
        try:
            self.readme = self.repo.get_readme().decoded_content.decode(encoding='utf-8')
        except github.UnknownObjectException:
            logging.info(f"Repository {self.name} has no README file")
            self.readme = ''
        self.description = self.repo.description
        self.technologies = [*self.repo.get_languages().keys()]
