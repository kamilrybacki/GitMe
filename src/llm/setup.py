import llm.config
import llm.providers.gemini
from llm.base import LLMProvider


def get_provider(configuration: llm.config.LLMConfigDictionary) -> LLMProvider:
    if target_provider := {
        "G1P": llm.providers.gemini.GeminiOnePro
    }.get(configuration["name"]):
        return target_provider.initialize(configuration)
    raise ValueError(f"Provider {configuration['name']} is not supported")
