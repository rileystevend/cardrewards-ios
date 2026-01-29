from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Recommendation:
    card_nickname: str
    reason: str
    score: float
    reward_currency: str
    merchant_category: str
    place_name: Optional[str]
