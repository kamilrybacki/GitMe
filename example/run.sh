#!/bin/bash

export GITME__GITHUB_USERNAME="your_username"
export GITME__GITHUB_TOKEN="your_token"
export GITME__LLM_PROVIDER_API_KEY="your_api_key"

# These are optional and either limit the analysis to a subset of repos or add extra repos to the pinned ones. ONLY_THOSE_REPOS takes precedence.

# export GITME__EXTRA_REPOS="repo1,repo2,repo3"
# export GITME__ONLY_THOSE_REPOS="repo1,repo2,repo3"

python \
    run.py
