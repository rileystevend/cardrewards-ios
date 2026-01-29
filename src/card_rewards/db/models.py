from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Card:
    id: int
    nickname: str
    issuer: Optional[str]
    last4: Optional[str]
    reward_currency: str  # points|cashback|miles

@dataclass(frozen=True)
class RewardRule:
    id: int
    card_id: int
    category: str         # gas|grocery|restaurant|travel|drugstore|other
    multiplier: float
    unit: str             # x|percent
    notes: Optional[str]
