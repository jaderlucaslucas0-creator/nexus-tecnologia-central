from core.assistant import JarvisAssistant
from core.security import RiskLevel, SecurityCore

def test_core_returns_reply():
    assert JarvisAssistant().handle("Olá, JARVIS")

def test_high_risk_is_blocked():
    decision = SecurityCore().evaluate(RiskLevel.HIGH, "formatar disco")
    assert not decision.allowed and decision.requires_confirmation

def test_system_command():
    assert "Sistema:" in JarvisAssistant().handle("/system")

def test_search_command_handles_empty_result():
    assistant = JarvisAssistant()
    assert "resultados" in assistant._format_search_results("teste", []).lower()

if __name__ == "__main__":
    test_core_returns_reply()
    test_high_risk_is_blocked()
    test_system_command()
    test_search_command_handles_empty_result()
    print("JARVIS AI: testes v0.2 OK")
