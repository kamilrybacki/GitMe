# GitMe - Contextualize info about Your GitHub profile

<img
    src='.github/assets/gitme.svg'
    alt='GitMe logo'
    width='200'
    style='display: block; margin: 0 auto;'
/>

## Overview

GitMe is a Python library designed to summarize and analyze data about your GitHub repositories using various generative AI service options.

This information may be helpful for developers, data scientists, or anyone interested in showcasing their GitHub profile better e.g. for a job application
or creating that legendary `README.md` file You've always wanted to have. 🗒️✨

## Features

- **Repository Analysis**: Generate detailed summaries of your GitHub repositories,
based on their readme, description and language metadata.
- **AI Integration**: Utilizes generative AI services to provide intelligent insights.
- **Extensible**: Easily integrate with other tools or extend functionalities
by implementing adapters to various LLM providers.

## Installation

Clone the repository and install dependencies:

```bash
pip install git+https://github.com/kamilrybacki/GitMe.git
```

## Usage

To use GitMe, import the library and initialize the `GitMeRunner` class with appropiate configuration:

```python
import gitme

# Initialize GitMeRunner
runner = gitme.GitMeRunner(...)  # Add configuration here

# Run the inferrence models on desired repositories
summaries = runner.run()

# Dump the summaries to a file in CSV format
runner.dump(summaries)

```

An example of the runner script [`run.py`](./example/run.py) and the Bash script
that sets up necessary environment variables [`run.sh`](./example/run.sh) can be found in the `example` directory.

Simply **edit** and run the Bash script to generate summaries for your repositories:

```bash
bash example/run.sh
```

## Configuration

The configuration of the `GitMeRunner` class is done through the dictionary which
schema is defined in the [`config.py`](./gitme/config.py) file and can be passed as a parameter to the class constructor.

### Schema details

For full details on the configuration schema, please refer to the [`config.schema.json`](./config.schema.json) file.

Below is a brief overview of the configuration options:

#### Required Parts

- **`llm` (object)**: Configuration for the LLM provider.
  - **`name` (string)**: The name of the LLM provider.
  - **`connection` (object)**: Connection details specific to the LLM provider.
    - **Example**:

        **NOTE**: The connection details depend on the LLM provider. For example, for the Google AI, the connection details are the API key.

      ```json
      {
        "api_key": "your_api_key",
      }
      ```

  - **`retry` (object)**: Retry settings for the LLM provider.
    - **`delay` (integer)**: Delay between retry attempts in seconds.
    - **`attempts` (integer)**: Number of retry attempts before failing.
    - **Example**:

      ```json
      {
        "delay": 2,
        "attempts": 3
      }
      ```

- **`github` (object)**: Configuration for the GitHub profile.
  - **`username` (string)**: The GitHub username.
  - **`token` (string)**: The GitHub read-only token.
  - **Example**:

    ```json
    {
      "username": "your_github_username",
      "token": "your_github_token"
    }
    ```

- **`output` (string)**: The name of the output file where results will be saved.
  - **Example**:

    ```json
    "output": "results/output.csv"
    ```

#### Optional Parts

- **`github.only` (string, nullable)**: Comma-separated list of exclusive repositories to analyze.
  - **Example**:

    ```json
    "only": "repo1,repo2"
    ```

- **`github.add` (string, nullable)**: Comma-separated list of additional repositories to analyze.
  - **Example**:

    ```json
    "add": "repo3,repo4"
    ```

## Available LLM Providers

The following LLM providers are currently supported:

- **Google AI**: Utilizes the Google AI models to generate summaries:

  Models:

  - `G1P`: Google Gemini 1.0 Pro model
  - `G1HF`: Google Gemini 1.5 Flash model

  Configuration:

  ```json
  {
      "llm": {
        "name": "G1P",
        "connection": {
            "api_key": "your_api_key"
        },
        "retry": {
            ... // Retry settings
        }
      }
  }
  ```

To use a chosen model, set the `name` field in the `llm` configuration to the desired model tag e.g. `G1P`.

## Contributing

We welcome contributions! If you want to contribute to GitMe, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Please ensure your code adheres to the project's coding standards and passes all tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please open an issue on GitHub or contact the maintainer:

- [Kamil Rybacki](https://kamilrybacki.gda.pl)
