import gitme.llm.config
import gitme.llm.providers.google
from gitme.llm.base import LLMProvider


AVAILABLE_PROVIDERS = {
    "G1P": gitme.llm.providers.google.GeminiOnePro,
    "G1HF": gitme.llm.providers.google.GeminiOneHalfFlash
}


def get_provider(configuration: gitme.llm.config.LLMConfigDictionary) -> LLMProvider:
    if target_provider := AVAILABLE_PROVIDERS.get(configuration["name"]):
        return target_provider.initialize(configuration)
    raise ValueError(f"Provider {configuration['name']} is not supported")
