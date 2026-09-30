from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def respond(self, prompt: str, context: list[dict]) -> str:
        raise NotImplementedError

class LocalFallbackProvider(AIProvider):
    def respond(self, prompt: str, context: list[dict]) -> str:
        return 'Recebi seu comando. O provedor de IA remoto ainda não está configurado.'