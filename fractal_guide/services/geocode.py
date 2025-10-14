import time
from geopy.geocoders import Nominatim
from geopy.location import Location


_geolocator = Nominatim(user_agent="fractal_guide_mvp", timeout=5)


def reverse_geocode(lat: float, lon: float) -> str:
    location: Location | None = None
    for attempt in range(2):  # simple retry to handle transient timeouts
        try:
            location = _geolocator.reverse(
                (lat, lon), exactly_one=True, language="en"
            )
            break
        except Exception:
            if attempt == 0:
                time.sleep(0.5)
            continue

    if not location:
        return f"You're near {lat:.5f}, {lon:.5f}"
    # Prefer a named POI if available, else use address
    name = location.raw.get("name") if hasattr(location, "raw") else None
    if name:
        return f"You're in/near {name}"
    return f"You're in/near {location.address}"


