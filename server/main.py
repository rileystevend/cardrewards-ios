import json
import os
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

# Server-side only:
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

Category = Literal["gas", "grocery", "restaurant", "travel", "drugstore", "other"]
Unit = Literal["x", "percent"]

class CardRule(BaseModel):
    category: Category
    multiplier: float = Field(..., gt=0)
    unit: Unit

class WalletCard(BaseModel):
    nickname: str
    reward_currency: str
    rules: List[CardRule]

class RecommendRequest(BaseModel):
    place_name: Optional[str] = None
    place_types: List[str] = []
    merchant_category: Category
    wallet: List[WalletCard]

class RecommendResponse(BaseModel):
    recommended_card: str
    reason: str
    confidence: float

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")

    context = {
        "place": {"name": req.place_name, "types": req.place_types, "category": req.merchant_category},
        "wallet": [c.model_dump() for c in req.wallet],
        "instructions": (
            "Pick the single best card to maximize rewards for the given purchase category. "
            "Use ONLY the rules provided. If multiple cards tie, choose the simplest justification. "
            "Return JSON that matches the schema exactly."
        ),
    }

    resp = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-5"),
        input=[
            {"role": "system", "content": "You are a rewards optimizer. Output ONLY valid JSON."},
            {"role": "user", "content": json.dumps(context)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "card_recommendation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "recommended_card": {"type": "string"},
                        "reason": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": ["recommended_card", "reason", "confidence"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )

    out_text = getattr(resp, "output_text", None)
    if not out_text:
        raise HTTPException(status_code=500, detail="No output_text from model response")

    data = json.loads(out_text)

    # Sanity check: only allow recommending an existing card nickname
    valid_cards = {c.nickname for c in req.wallet}
    if data.get("recommended_card") not in valid_cards:
        raise HTTPException(status_code=400, detail="Model returned card not in wallet")

    return RecommendResponse(**data)
