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
        "name": "G1HF",
        "connection": {
            "api_key": os.getenv("GITME__LLM_PROVIDER_API_KEY", "")
        },
        "retry": {
            "delay": 1,
            "retries": 3
        }
    })
    llm_client.set_logger(profile.logger)

    requested_repos = os.getenv("GITME__EXTRA_REPOS", "").split(",")
    if requested_repos:
        profile.log(f"Additional repos to be analyzed: {', '.join(requested_repos)}")

    all_repositories = [
        *profile.pinned_repositories,
        *[
            metadata.RepositoryMetadata.from_repo(
                profile.get_repo(repo_name)
            )
            for repo_name in requested_repos
        ]
    ]
    for repo in all_repositories[:1]:
        profile.log(f"Processing {repo.name}")
        prompt = llm.prompts.generate_prompt(
            description=repo.description,
            technologies=repo.technologies,
            readme=repo.readme or "No README available. Use the repository description."
        )
        summary = llm_client.query(prompt)
        llm_client.log(f"Query: {summary.query}")
        llm_client.log(f"Result: {summary.result}")


if __name__ == "__main__":
    start()
