import os

import gitme.gh
import gitme.llm.setup
import gitme.llm.prompts
import gitme.metadata


def start() -> None:
    username = os.getenv("GITME__GITHUB_USERNAME")
    token = os.getenv("GITME__GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    profile = gitme.gh.GithubProfile.connect(username, token)
    profile.log("Successfully connected to Github!")

    llm_client = gitme.llm.setup.get_provider({
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

    additional_repos = []
    if requested_repos := os.getenv("GITME__EXTRA_REPOS"):
        additional_repos = requested_repos.split(",") if "," in requested_repos else [requested_repos]
        profile.log(f"Additional repos to be analyzed: {requested_repos}")

    all_repositories = [
        *profile.pinned_repositories, 
    ] + [
            gitme.metadata.RepositoryMetadata.from_repo(
                profile.get_repo(repo_name)
            )
            for repo_name in additional_repos
            if repo_name
    ] if additional_repos else [*profile.pinned_repositories]
    profile.log(f"Repositories: {', '.join([
        repo.name
        for repo in all_repositories
    ])}")

    for repo in all_repositories[:1]:
        profile.log(f"Processing {repo.name}")
        prompt = gitme.llm.prompts.generate_prompt(
            description=repo.description,
            technologies=repo.technologies,
            readme=repo.readme or "No README available. Use the repository description."
        )
        summary = llm_client.query(prompt)
        llm_client.log(f"Query: {summary.query}")
        llm_client.log(f"Result: {summary.result}")


if __name__ == "__main__":
    start()
