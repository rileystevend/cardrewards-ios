from typing import List

TYPE_TO_CATEGORY = {
    "gas_station": "gas",
    "supermarket": "grocery",
    "grocery_store": "grocery",
    "restaurant": "restaurant",
    "cafe": "restaurant",
    "bar": "restaurant",
    "pharmacy": "drugstore",
    "drugstore": "drugstore",
    "airport": "travel",
    "lodging": "travel",
    "hotel": "travel",
}

def types_to_category(place_types: List[str]) -> str:
    for t in place_types or []:
        t = t.lower()
        if t in TYPE_TO_CATEGORY:
            return TYPE_TO_CATEGORY[t]
    return "other"
