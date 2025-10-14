from geopy.geocoders import Nominatim
from geopy.location import Location


_geolocator = Nominatim(user_agent="fractal_guide_mvp")


def reverse_geocode(lat: float, lon: float) -> str:
    location: Location | None = _geolocator.reverse((lat, lon), exactly_one=True, language="en")
    if not location:
        return f"You're near {lat:.5f}, {lon:.5f}"
    # Prefer a named POI if available, else use address
    name = location.raw.get("name") if hasattr(location, "raw") else None
    if name:
        return f"You're in/near {name}"
    return f"You're in/near {location.address}"


