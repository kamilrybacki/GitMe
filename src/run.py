import os

import ghprofile
import llm.setup
import llm.prompts
import metadata


def start() -> None:
    username = os.getenv("GITME__GITHUB_USERNAME")
    token = os.getenv("GITME__GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    profile = ghprofile.GithubProfile.connect(username, token)
    profile.log("Successfully connected to Github!")

    llm_client = llm.setup.get_provider({
        "name": "G1P",
        "connection": {
            "api_key": os.getenv("GITME__LLM_PROVIDER_API_KEY", "")
        },
        "retry": {
            "delay": 1,
            "retries": 3
        }
    })

    requested_repos = os.getenv("GITME__EXTRA_REPOS", "").split(",")
    all_repositories = [
        *profile.pinned_repositories,
        *[
            metadata.RepositoryMetadata.from_repo(
                profile.get_repo(repo_name)
            )
            for repo_name in requested_repos
        ]
    ]
    for repo in all_repositories:
        profile.log(f"Processing {repo.name}")


if __name__ == "__main__":
    start()
