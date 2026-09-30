from ai.provider import AIProvider, LocalFallbackProvider, configured_provider

class AIRouter:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or configured_provider()

    def respond(self, prompt: str, context: list[dict]) -> str:
        try:
            return self.provider.respond(prompt, context)
        except Exception:
            if not isinstance(self.provider, LocalFallbackProvider):
                return LocalFallbackProvider().respond(prompt, context)
            raise
