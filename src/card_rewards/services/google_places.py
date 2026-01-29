from dataclasses import dataclass
from typing import List, Optional
import requests

@dataclass(frozen=True)
class PlaceResult:
    name: str
    formatted_address: Optional[str]
    types: List[str]
    place_id: Optional[str]

class GooglePlacesClient:
    def __init__(self, api_key: str, timeout_s: int = 8):
        self.api_key = api_key
        self.timeout_s = timeout_s

    def search_nearby(self, lat: float, lng: float, radius_m: int = 35) -> Optional[PlaceResult]:
        if not self.api_key:
            raise RuntimeError("Missing GOOGLE_MAPS_API_KEY")

        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.types",
        }
        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(radius_m),
                }
            },
            "rankPreference": "DISTANCE",
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        data = resp.json()

        places = data.get("places", [])
        if not places:
            return None

        p0 = places[0]
        display = (p0.get("displayName") or {}).get("text") or "Unknown place"
        return PlaceResult(
            name=display,
            formatted_address=p0.get("formattedAddress"),
            types=p0.get("types", []) or [],
            place_id=p0.get("id"),
        )
