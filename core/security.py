from dataclasses import dataclass
from enum import Enum

class RiskLevel(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    requires_confirmation: bool
    message: str

class SecurityCore:
    def evaluate(self, risk: RiskLevel, action: str) -> SecurityDecision:
        if risk is RiskLevel.HIGH:
            return SecurityDecision(False, True, f'Ação de alto risco bloqueada: {action}')
        if risk is RiskLevel.MEDIUM:
            return SecurityDecision(True, True, f'Confirmação necessária: {action}')
        return SecurityDecision(True, False, f'Ação autorizada: {action}')