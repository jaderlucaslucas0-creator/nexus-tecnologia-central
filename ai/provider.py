import os
from abc import ABC, abstractmethod
from urllib.request import Request, urlopen
import json

class AIProvider(ABC):
    @abstractmethod
    def respond(self, prompt: str, context: list[dict]) -> str:
        raise NotImplementedError

class LocalFallbackProvider(AIProvider):
    def respond(self, prompt: str, context: list[dict]) -> str:
        return "Recebi seu comando. Configure JARVIS_AI_API_URL e JARVIS_AI_API_KEY para conectar um provedor remoto."

class HTTPAIProvider(AIProvider):
    def __init__(self, endpoint: str, api_key: str = "", model: str = ""):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model

    def respond(self, prompt: str, context: list[dict]) -> str:
        payload = {"model": self.model, "messages": [{"role": "system", "content": prompt}, *context]}
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json", "User-Agent": "JARVIS-AI/0.2"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.endpoint, data=body, headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _extract_text(data)

def _extract_text(data: dict) -> str:
    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        if message.get("content"):
            return str(message["content"])
        if choices[0].get("text"):
            return str(choices[0]["text"])
    if data.get("response"):
        return str(data["response"])
    raise ValueError("Resposta de IA em formato não reconhecido.")

def configured_provider():
    endpoint = os.getenv("JARVIS_AI_API_URL", "").strip()
    key = os.getenv("JARVIS_AI_API_KEY", "").strip()
    model = os.getenv("JARVIS_AI_MODEL", "").strip()
    return HTTPAIProvider(endpoint, key, model) if endpoint else LocalFallbackProvider()
