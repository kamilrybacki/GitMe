import os
import logging

import hooks.gh
import hooks.llm.utils


def start() -> None:
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    profile = hooks.gh.GithubProfile.connect(username, token)
    logging.root = profile.logger  # type: ignore
    logging.root.info("Successfully connected to Github!")

    llm_client = hooks.llm.utils.get_provider({
        "name": "G1P",
        "connection": {
            "api_key": os.getenv("AI_PROVIDER_API_KEY")
        },
        "retry": {
            "delay": 1,
            "retries": 3
        }
    })

    logging.root.info(llm_client.query("Hello!"))


if __name__ == "__main__":
    start()
