import os
import logging

import hooks.profile


def main() -> None:
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    if not username or not token:
        raise ValueError("Please provide GITHUB_USERNAME and GITHUB_TOKEN environment variables")

    profile = hooks.profile.GithubProfile.connect(username, token)
    logging.info(f"Successfully connected to {profile.get_repo(username).full_name}")


if __name__ == "__main__":
    main()
