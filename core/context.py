from collections import deque
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class ConversationContext:
    def __init__(self, max_messages: int = 20):
        self._messages = deque(maxlen=max_messages)
    def add(self, role: str, content: str):
        self._messages.append(Message(role, content))
    def clear(self):
        self._messages.clear()
    def messages(self):
        return list(self._messages)