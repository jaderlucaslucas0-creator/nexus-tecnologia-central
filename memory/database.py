import sqlite3
from pathlib import Path

class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection
    def _initialize(self):
        with self.connect() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, category TEXT NOT NULL DEFAULT \'long_term\', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    def add_memory(self, content: str, category='long_term'):
        with self.connect() as connection:
            cursor = connection.execute('INSERT INTO memories(content, category) VALUES(?, ?)', (content, category))
            return int(cursor.lastrowid)
    def list_memories(self, limit=50):
        with self.connect() as connection:
            rows = connection.execute('SELECT id, content, category, created_at FROM memories ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [dict(row) for row in rows]