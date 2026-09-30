from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget
from core.assistant import JarvisAssistant
from memory.long_term import LongTermMemory

class MainWindow(QMainWindow):
    def __init__(self, assistant: JarvisAssistant, memory: LongTermMemory):
        super().__init__(); self.assistant = assistant; self.memory = memory; self.setWindowTitle('JARVIS AI'); self.resize(1200, 760); self._build_ui()
    def _build_ui(self):
        central = QWidget(); layout = QVBoxLayout(central)
        title = QLabel('J A R V I S  A I'); title.setObjectName('title')
        status = QLabel('● SYSTEM ONLINE  |  CORE ACTIVE'); status.setObjectName('status')
        self.chat = QTextEdit(); self.chat.setReadOnly(True)
        self.input = QLineEdit(); self.input.setPlaceholderText('Digite um comando para o JARVIS...'); self.input.returnPressed.connect(self.send_message)
        send = QPushButton('ENVIAR'); send.clicked.connect(self.send_message)
        controls = QHBoxLayout(); controls.addWidget(self.input); controls.addWidget(send)
        layout.addWidget(title); layout.addWidget(status); layout.addWidget(self.chat, 1); layout.addLayout(controls); self.setCentralWidget(central)
    def send_message(self):
        command = self.input.text().strip()
        if not command: return
        self.chat.append(f'<b>VOCÊ</b><br>{command}<br>'); self.input.clear()
        reply = self.assistant.handle(command); self.chat.append(f'<b>JARVIS</b><br>{reply}<br>')
        if command.lower().startswith(('memorize ', 'guarde ')): self.memory.save(command.split(' ', 1)[1].strip())