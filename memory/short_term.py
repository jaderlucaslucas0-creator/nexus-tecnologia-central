from core.context import ConversationContext

class ShortTermMemory:
    def __init__(self, max_messages=20): self.context=ConversationContext(max_messages)
    def remember(self, role, content): self.context.add(role, content)
    def messages(self): return self.context.messages()
    def clear(self): self.context.clear()
