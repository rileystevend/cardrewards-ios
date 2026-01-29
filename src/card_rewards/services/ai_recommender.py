from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests

@dataclass(frozen=True)
class AIRecommendation:
    recommended_card: str
    reason: str
    confidence: float

class AIRecommenderClient:
    """Calls YOUR backend (not OpenAI directly) to keep secrets out of iOS."""
    def __init__(self, base_url: str, timeout_s: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def recommend(
        self,
        place_name: Optional[str],
        place_types: List[str],
        merchant_category: str,
        wallet_payload: List[Dict[str, Any]],
    ) -> AIRecommendation:
        payload = {
            "place_name": place_name,
            "place_types": place_types,
            "merchant_category": merchant_category,
            "wallet": wallet_payload,
        }
        r = requests.post(f"{self.base_url}/recommend", json=payload, timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()
        return AIRecommendation(
            recommended_card=str(data["recommended_card"]),
            reason=str(data["reason"]),
            confidence=float(data.get("confidence", 0.5)),
        )
