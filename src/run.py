import os
import logging

import ghprofile
import llm.setup
import llm.prompts


def start() -> None:
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    profile = ghprofile.GithubProfile.connect(username, token)
    logging.root = profile.logger  # type: ignore
    logging.root.info("Successfully connected to Github!")

    llm_client = llm.setup.get_provider({
        "name": "G1P",
        "connection": {
            "api_key": os.getenv("AI_PROVIDER_API_KEY", "")
        },
        "retry": {
            "delay": 1,
            "retries": 3
        }
    })
    for repo in profile.repositories:
        logging.info(f"Processing repository {repo.name}")
        prompt = llm.prompts.generate_prompt(
            repo.readme
        )
        logging.info(f"Generated prompt for {repo.name}: {prompt}")

if __name__ == "__main__":
    start()
