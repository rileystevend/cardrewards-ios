# Card Rewards (iOS, Python) + AI Recommender Backend

This repo contains:
- **iOS app** written in Python using BeeWare/Toga (client)
- **Backend recommender API** (FastAPI) that calls OpenAI safely (server-side)

## Why a backend?
Do **not** embed OpenAI API keys in a mobile app. The iOS client calls your backend, and the backend calls OpenAI.

## Structure
```
card_rewards_ios/
  pyproject.toml
  src/card_rewards/...
  server/...
```

## Quick start (backend)
1) Create a virtualenv and install deps:
```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Set env vars and run:
```bash
export OPENAI_API_KEY="YOUR_KEY"
export OPENAI_MODEL="gpt-5"
uvicorn main:app --host 0.0.0.0 --port 8000
```

3) Health check:
```bash
curl http://localhost:8000/healthz
```

## iOS app config
The app reads these environment variables at runtime:
- `GOOGLE_MAPS_API_KEY`
- `RECOMMENDER_API_BASE_URL` (e.g., `http://YOUR_LAN_IP:8000`)
- `PLACES_RADIUS_METERS` (optional)

## Build iOS with Briefcase
On macOS with Xcode installed:
```bash
python -m pip install briefcase
briefcase create iOS
briefcase build iOS
briefcase run iOS
```

### iOS permissions
In the generated Xcode project Info.plist, set:
- `NSLocationWhenInUseUsageDescription`

Example:
> "We use your location to identify the store you're in and recommend the best card."

## Notes
- The iOS app will prefer the AI recommendation. If the backend fails, it falls back to a deterministic local engine.
- Wallet data is stored locally in SQLite (`wallet.db`) inside the app sandbox.
- By Steven Riley
