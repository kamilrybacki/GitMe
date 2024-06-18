import abc
import dataclasses

import gitme.llm.base


@dataclasses.dataclass
class LocalK8sLLMProvider(gitme.llm.base.LLMProvider, abc.ABC):
    """
        Base class for Local Kubernetes models, that does not utilize any external services.

        These services are to be managed by the user, with the
        connection details provided in the configuration.

        The _cluster_info field should contain the connection details for the Kubernetes cluster, if needed.
    """
    _cluster_info: dict[str, str] = dataclasses.field(init=False)

# Implement the concrete class for the Kubernetes provider of choice
