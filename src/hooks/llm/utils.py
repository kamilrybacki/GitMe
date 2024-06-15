import hooks.llm.config
import hooks.llm.gemini
from hooks.llm.base import LLMProvider


def get_provider(configuration: hooks.llm.config.LLMConfigDictionary) -> LLMProvider:
    if target_provider := {
        "G1P": hooks.llm.gemini.GeminiOnePro
    }.get(configuration["name"]):
        return target_provider.initialize(configuration)
    raise ValueError(f"Provider {configuration['name']} is not supported")
