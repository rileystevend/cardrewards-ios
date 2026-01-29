from typing import List, Tuple
from .database import Database
from .models import Card, RewardRule

class WalletRepository:
    def __init__(self, db: Database):
        self.db = db

    def add_card(self, nickname: str, issuer: str = "", last4: str = "", reward_currency: str = "points") -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO cards (nickname, issuer, last4, reward_currency) VALUES (?, ?, ?, ?)",
                (nickname.strip(), issuer.strip() or None, last4.strip() or None, reward_currency.strip()),
            )
            conn.commit()
            return int(cur.lastrowid)

    def delete_card(self, card_id: int) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            conn.commit()

    def list_cards(self) -> List[Card]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM cards ORDER BY created_at DESC").fetchall()
        return [Card(int(r["id"]), r["nickname"], r["issuer"], r["last4"], r["reward_currency"]) for r in rows]

    def add_rule(self, card_id: int, category: str, multiplier: float, unit: str, notes: str = "") -> int:
        category = category.strip().lower()
        unit = unit.strip().lower()
        if unit not in ("x", "percent"):
            raise ValueError("unit must be 'x' or 'percent'")

        with self.db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO reward_rules (card_id, category, multiplier, unit, notes) VALUES (?, ?, ?, ?, ?)",
                (card_id, category, float(multiplier), unit, notes.strip() or None),
            )
            conn.commit()
            return int(cur.lastrowid)

    def delete_rule(self, rule_id: int) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM reward_rules WHERE id = ?", (rule_id,))
            conn.commit()

    def get_rules_for_card(self, card_id: int) -> List[RewardRule]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM reward_rules WHERE card_id = ? ORDER BY category",
                (card_id,),
            ).fetchall()
        return [
            RewardRule(int(r["id"]), int(r["card_id"]), r["category"], float(r["multiplier"]), r["unit"], r["notes"])
            for r in rows
        ]

    def list_wallet(self) -> List[Tuple[Card, List[RewardRule]]]:
        cards = self.list_cards()
        return [(c, self.get_rules_for_card(c.id)) for c in cards]
