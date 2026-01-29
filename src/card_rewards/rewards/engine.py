from typing import List, Tuple, Optional
from card_rewards.db.models import Card, RewardRule
from .types import Recommendation

DEFAULT_BASE_CATEGORY = "other"

def _score_for_rule(rule: RewardRule) -> float:
    # Simple scoring: compare multipliers within same unit. For better rigor,
    # add currency preference & unit normalization.
    return float(rule.multiplier)

def recommend_card(
    wallet: List[Tuple[Card, List[RewardRule]]],
    merchant_category: str,
    place_name: Optional[str] = None
) -> Optional[Recommendation]:
    best: Optional[Recommendation] = None

    for card, rules in wallet:
        matching = [r for r in rules if r.category == merchant_category]
        fallback = [r for r in rules if r.category == DEFAULT_BASE_CATEGORY]
        candidate_rule = matching[0] if matching else (fallback[0] if fallback else None)
        if not candidate_rule:
            continue

        score = _score_for_rule(candidate_rule)
        suffix = "x" if candidate_rule.unit == "x" else "%"
        reason = f"{candidate_rule.multiplier:g}{suffix} on {candidate_rule.category}"

        rec = Recommendation(
            card_nickname=card.nickname,
            reason=reason,
            score=score,
            reward_currency=card.reward_currency,
            merchant_category=merchant_category,
            place_name=place_name,
        )
        if best is None or rec.score > best.score:
            best = rec

    return best
