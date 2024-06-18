import gitme.config
import gitme.llm.providers.google
from gitme.llm.base import LLMProvider


__AVAILABLE_PROVIDERS = {
    "G1P": gitme.llm.providers.google.GeminiOnePro,
    "G1HF": gitme.llm.providers.google.GeminiOneHalfFlash
}
AVAILABLE_PROVIDERS = __AVAILABLE_PROVIDERS.keys()


def get_provider(configuration: gitme.config.LLMProviderConfig) -> LLMProvider:
    if target_provider := __AVAILABLE_PROVIDERS.get(configuration.name):
        return target_provider.initialize(configuration)
    raise ValueError(f"Provider {configuration['name']} is not supported")
