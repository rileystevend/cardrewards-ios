import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from card_rewards.config import Config
from card_rewards.logging_setup import setup_logging

from card_rewards.db.database import Database
from card_rewards.db.wallet_repo import WalletRepository

from card_rewards.services.location_service_ios import IOSLocationService
from card_rewards.services.google_places import GooglePlacesClient
from card_rewards.services.category_mapper import types_to_category
from card_rewards.services.ai_recommender import AIRecommenderClient

from card_rewards.rewards.engine import recommend_card

LOGGER = setup_logging()

class CardRewardsApp(toga.App):
    def startup(self):
        self.db = Database()
        self.db.init()
        self.repo = WalletRepository(self.db)

        self.location = IOSLocationService()
        self.places = GooglePlacesClient(Config.GOOGLE_MAPS_API_KEY)
        self.ai = AIRecommenderClient(Config.RECOMMENDER_API_BASE_URL)

        self.status = toga.Label("Ready", style=Pack(padding=10))
        self.place_lbl = toga.Label("Place: (none)", style=Pack(padding=10))
        self.cat_lbl = toga.Label("Category: (none)", style=Pack(padding=10))
        self.rec_lbl = toga.MultilineTextInput(readonly=True, style=Pack(padding=10, height=140))

        btn_row = toga.Box(style=Pack(direction=ROW, padding=10, gap=10))
        btn_row.add(toga.Button("Seed Example Wallet", on_press=self.seed_example))
        btn_row.add(toga.Button("Detect Store + Recommend", on_press=self.detect_and_recommend))

        main_box = toga.Box(style=Pack(direction=COLUMN))
        main_box.add(self.status)
        main_box.add(btn_row)
        main_box.add(self.place_lbl)
        main_box.add(self.cat_lbl)
        main_box.add(self.rec_lbl)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def seed_example(self, widget):
        self.status.text = "Seeding example wallet..."

        gas_id = self.repo.add_card("Gas 2x Card", issuer="ExampleBank", last4="1234", reward_currency="points")
        self.repo.add_rule(gas_id, "gas", 2.0, "x", "2x at gas stations")
        self.repo.add_rule(gas_id, "other", 1.0, "x", "1x everything else")

        flat_id = self.repo.add_card("1% Everything Card", issuer="ExampleBank", last4="9876", reward_currency="cashback")
        self.repo.add_rule(flat_id, "other", 1.0, "percent", "1% back everywhere")

        self.status.text = "Seeded. Tap Detect Store + Recommend."

    def _wallet_to_payload(self):
        wallet = self.repo.list_wallet()
        payload = []
        for card, rules in wallet:
            payload.append({
                "nickname": card.nickname,
                "reward_currency": card.reward_currency,
                "rules": [{"category": r.category, "multiplier": r.multiplier, "unit": r.unit} for r in rules],
            })
        return payload, wallet

    def detect_and_recommend(self, widget):
        self.status.text = "Requesting location permission + GPS fix..."

        def on_fix(loc):
            try:
                self.location.stop()
                self.status.text = f"Got location: {loc.lat:.6f}, {loc.lng:.6f} (±{loc.accuracy_m:.0f}m)"

                place = self.places.search_nearby(loc.lat, loc.lng, radius_m=Config.PLACES_RADIUS_METERS)
                if not place:
                    self.place_lbl.text = "Place: (unknown)"
                    self.cat_lbl.text = "Category: other"
                    self.rec_lbl.value = "No nearby place found."
                    return

                category = types_to_category(place.types)
                self.place_lbl.text = f"Place: {place.name}"
                self.cat_lbl.text = f"Category: {category}"

                wallet_payload, wallet_local = self._wallet_to_payload()

                # Prefer AI recommendation (via your backend)
                try:
                    ai_rec = self.ai.recommend(
                        place_name=place.name,
                        place_types=place.types,
                        merchant_category=category,
                        wallet_payload=wallet_payload,
                    )
                    self.rec_lbl.value = (
                        f"Use: {ai_rec.recommended_card}\n"
                        f"Why: {ai_rec.reason}\n"
                        f"Confidence: {ai_rec.confidence:.2f}\n"
                        f"Detected: {place.name} ({category})"
                    )
                    self.status.text = "Done (AI)."
                    return
                except Exception as e:
                    LOGGER.exception("AI recommend failed; falling back to deterministic engine")
                    rec = recommend_card(wallet_local, merchant_category=category, place_name=place.name)
                    if not rec:
                        self.rec_lbl.value = "No cards/rules found in wallet."
                        self.status.text = f"Done (no rec). AI error: {e}"
                        return
                    self.rec_lbl.value = (
                        f"Use: {rec.card_nickname} (fallback)\n"
                        f"Why: {rec.reason}\n"
                        f"Detected: {rec.place_name} ({rec.merchant_category})\n"
                        f"AI error: {e}"
                    )
                    self.status.text = "Done (fallback)."

            except Exception as e:
                LOGGER.exception("Failed")
                self.status.text = f"Error: {e}"

        self.location.request_and_start(on_fix)

def main():
    return CardRewardsApp("Card Rewards", "com.yourcompany.cardrewards")
