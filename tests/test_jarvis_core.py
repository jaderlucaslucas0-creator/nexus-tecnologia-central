from core.assistant import JarvisAssistant
from core.security import RiskLevel, SecurityCore

def test_core_returns_reply():
    assert JarvisAssistant().handle('Olá, JARVIS')

def test_high_risk_is_blocked():
    decision = SecurityCore().evaluate(RiskLevel.HIGH, 'formatar disco')
    assert not decision.allowed and decision.requires_confirmation