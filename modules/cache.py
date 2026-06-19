import json
import os
from datetime import datetime, timedelta


CACHE_DIR = "cache"


def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(name):
    ensure_cache_dir()
    return os.path.join(CACHE_DIR, f"{name}.json")


def load_cache(name, max_age_minutes=60):
    path = get_cache_path(name)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        created_at = datetime.fromisoformat(payload.get("created_at"))
        age = datetime.now() - created_at

        if age > timedelta(minutes=max_age_minutes):
            return None

        return payload.get("data")

    except Exception as exc:
        print(f"[cache] load failed for {name}: {exc}")
        return None


def save_cache(name, data):
    path = get_cache_path(name)

    try:
        payload = {
            "created_at": datetime.now().isoformat(),
            "data": data,
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    except Exception as exc:
        print(f"[cache] save failed for {name}: {exc}")


def get_or_set_cache(name, builder, max_age_minutes=60):
    cached = load_cache(name, max_age_minutes=max_age_minutes)

    if cached is not None:
        print(f"[cache] using cached {name}")
        return cached

    print(f"[cache] rebuilding {name}")
    data = builder()
    save_cache(name, data)
    return data
