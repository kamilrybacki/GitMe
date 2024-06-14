import os
import logging

import hooks.profile


def main() -> None:
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    profile = hooks.profile.GithubProfile.connect(username, token)
    logging.root = profile.logger
    logging.root.info("Successfully connected to Github!")

if __name__ == "__main__":
    main()
