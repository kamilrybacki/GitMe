import llm.config
import llm.providers.google
from llm.base import LLMProvider


AVAILABLE_PROVIDERS = {
    "G1P": llm.providers.google.GeminiOnePro,
    "G1HF": llm.providers.google.GeminiOneHalfFlash
}


def get_provider(configuration: llm.config.LLMConfigDictionary) -> LLMProvider:
    if target_provider := AVAILABLE_PROVIDERS.get(configuration["name"]):
        return target_provider.initialize(configuration)
    raise ValueError(f"Provider {configuration['name']} is not supported")
