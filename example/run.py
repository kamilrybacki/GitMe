import os

from gitme.runner import GitMeRunner


if __name__ == '__main__':
    gh_username = os.getenv("GITME__GITHUB_USERNAME")
    gh_token = os.getenv("GITME__GITHUB_TOKEN")
    if not gh_username or not gh_token:
        raise ValueError("Please provide GITME__GITHUB_USERNAME and GITME__GITHUB_TOKEN environment variables")
    if not (llm_api_key := os.getenv("GITME__LLM_PROVIDER_API_KEY")):
        raise ValueError("Please provide GITME__LLM_PROVIDER_API_KEY environment variable")

    runner = GitMeRunner({
        "llm": {
            "name": "G1HF",
            "connection": {
                "api_key": llm_api_key
            },
            "retry": {
                "delay": 5,
                "attempts": 3
            }
        },
        "github": {
            "username": gh_username,
            "token": gh_token,
            "only": os.getenv("GITME__ONLY_THOSE_REPOS"),
            "add": os.getenv("GITME__EXTRA_REPOS")
        },
        "output": "/tmp/output.csv"
    })
    analyzed_data = runner.run()
    runner.dump(analyzed_data)
