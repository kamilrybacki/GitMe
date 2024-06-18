#!/bin/bash

export GITME__GITHUB_USERNAME="your_username"
export GITME__GITHUB_TOKEN="your_token"
export GITME__LLM_PROVIDER_API_KEY="your_api_key"
export GITME__EXTRA_REPOS="repo1,repo2,repo3"

python \
    run.py
