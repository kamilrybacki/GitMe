from __future__ import annotations
import dataclasses

import github.Repository


@dataclasses.dataclass
class RepositoryMetadata:
    name: str = dataclasses.field(init=False)
    readme: str = dataclasses.field(init=False)
    description: str = dataclasses.field(init=False)
    technologies: list[str] = dataclasses.field(init=False, default_factory=list)

    @classmethod
    def from_repo(cls, repo: github.Repository.Repository) -> RepositoryMetadata:
        metadata = cls()
        metadata.name = repo.full_name
        try:
            metadata.readme = repo.get_readme().decoded_content.decode(encoding='utf-8')
        except github.UnknownObjectException:
            metadata.readme = ''
        metadata.description = repo.description
        metadata.technologies = [
            *repo.get_languages().keys()
        ]
        return metadata
