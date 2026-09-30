from ai.prompts import SYSTEM_PROMPT
from ai.router import AIRouter
from core.context import ConversationContext
from core.security import RiskLevel, SecurityCore
from tools.applications import open_target
from tools.files import find_files
from tools.search import search_web
from tools.system import get_system_status

class JarvisAssistant:
    def __init__(self, provider=None):
        self.router = AIRouter(provider)
        self.context = ConversationContext()
        self.security = SecurityCore()

    def handle(self, command: str) -> str:
        text = command.strip()
        if not text:
            return "Diga ou escreva um comando para começar."

        self.context.add("user", text)
        lowered = text.lower()

        if lowered in {"/clear", "/limpar"}:
            self.context.clear()
            return "Conversa limpa."

        if lowered in {"/system", "/sistema"}:
            status = get_system_status()
            reply = (
                f"Sistema: {status['os']} | Python: {status['python']} | "
                f"CPU lógica: {status['cpu_count']} | Disco livre: "
                f"{status['disk_free_gb']} GB"
            )
        elif lowered.startswith(("abra ", "abrir ")):
            target = text.split(" ", 1)[1]
            decision = self.security.evaluate(RiskLevel.LOW, f"abrir {target}")
            try:
                reply = (
                    open_target(target)
                    if decision.allowed and not decision.requires_confirmation
                    else decision.message
                )
            except (OSError, RuntimeError, ValueError) as exc:
                reply = f"Não consegui concluir essa operação: {exc}"
        elif lowered.startswith(("pesquise ", "pesquisar ", "/search ")):
            query = text.split(" ", 1)[1]
            try:
                results = search_web(query)
                reply = self._format_search_results(query, results)
            except Exception:
                reply = "Não consegui realizar a pesquisa agora."
        elif lowered.startswith(("procure arquivo ", "buscar arquivo ")):
            name = text.split(" ", 2)[2]
            matches = find_files(name)
            reply = self._format_file_results(matches)
        else:
            context = [
                {"role": message.role, "content": message.content}
                for message in self.context.messages()
            ]
            enriched = f"{SYSTEM_PROMPT}\n\nComando do usuário: {text}"
            reply = self.router.respond(enriched, context)

        self.context.add("assistant", reply)
        return reply

    @staticmethod
    def _format_search_results(query: str, results: list[dict]) -> str:
        if not results:
            return f"Não encontrei resultados para: {query}"
        return "Resultados encontrados:\n" + "\n".join(
            f"- {item['title']}" for item in results
        )

    @staticmethod
    def _format_file_results(matches: list[str]) -> str:
        if not matches:
            return "Não encontrei arquivos correspondentes."
        return "Arquivos encontrados:\n" + "\n".join(f"- {item}" for item in matches[:10])
