from memory.database import Database

class LongTermMemory:
    def __init__(self, database: Database):
        self.database = database
    def save(self, content: str, category='long_term'):
        return self.database.add_memory(content, category)
    def recent(self, limit=20):
        return self.database.list_memories(limit)