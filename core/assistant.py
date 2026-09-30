from ai.provider import AIProvider, LocalFallbackProvider
from core.context import ConversationContext
from core.security import RiskLevel, SecurityCore
from tools.applications import open_target
from tools.system import get_system_status

class JarvisAssistant:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or LocalFallbackProvider()
        self.context = ConversationContext()
        self.security = SecurityCore()
    def handle(self, command: str):
        text = command.strip()
        if not text: return 'Diga ou escreva um comando para começar.'
        self.context.add('user', text)
        lowered = text.lower()
        if lowered in {'/clear', '/limpar'}:
            self.context.clear(); return 'Conversa limpa.'
        if lowered in {'/system', '/sistema'}:
            status = get_system_status()
            reply = f"Sistema: {status['os']} | Python: {status['python']} | CPU lógica: {status['cpu_count']} | Disco livre: {status['disk_free_gb']} GB"
        elif lowered.startswith(('abra ', 'abrir ')):
            target = text.split(' ', 1)[1]
            decision = self.security.evaluate(RiskLevel.LOW, f'abrir {target}')
            try: reply = open_target(target) if decision.allowed and not decision.requires_confirmation else decision.message
            except (OSError, RuntimeError, ValueError) as exc: reply = f'Não consegui concluir essa operação: {exc}'
        else:
            context = [{'role': m.role, 'content': m.content} for m in self.context.messages()]
            reply = self.provider.respond(text, context)
        self.context.add('assistant', reply)
        return reply