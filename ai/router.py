from ai.provider import AIProvider, LocalFallbackProvider

class AIRouter:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or LocalFallbackProvider()
    def respond(self, prompt: str, context: list[dict]) -> str:
        try:
            return self.provider.respond(prompt, context)
        except Exception:
            return LocalFallbackProvider().respond(prompt, context)
