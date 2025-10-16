import time
from geopy.geocoders import Nominatim
from geopy.location import Location
import requests


_geolocator = Nominatim(user_agent="fractal_guide_mvp", timeout=5)


def get_nearby_pois(lat, lon, radius=200):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["tourism"](around:{radius},{lat},{lon});
      node["historic"](around:{radius},{lat},{lon});
    );
    out body;
    """
    # node["amenity"~"restaurant|cafe|museum|theater"](around:{radius},{lat},{lon});
    # node["leisure"~"park|beach"](around:{radius},{lat},{lon}); 
    response = requests.get(overpass_url, params={'data': query})
    return [element["tags"].get("name", "") for element in response.json()["elements"] if element["tags"].get("name", "")]


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
    
    # Extract meaningful location context from the raw response
    raw = location.raw if hasattr(location, "raw") else {}
    address = raw.get("address", {})
    
    # Build context prioritizing street/city over generic businesses
    context_parts = []
    
    # Street and number (most specific)
    if address.get("road") and address.get("house_number"):
        context_parts.append(f"{address['house_number']} {address['road']}")
    elif address.get("road"):
        context_parts.append(address["road"])
    
    # Neighborhood or suburb
    if address.get("quarter") and address.get("quarter") not in context_parts:
        context_parts.append(address["quarter"])
    if address.get("suburb") and address.get("suburb") not in context_parts:
        context_parts.append(address["suburb"])
    elif address.get("neighbourhood") and address.get("neighbourhood") not in context_parts:
        context_parts.append(address["neighbourhood"])
    
    # City/town
    if address.get("city"):
        context_parts.append(address["city"])
    elif address.get("town"):
        context_parts.append(address["town"])
    elif address.get("village"):
        context_parts.append(address["village"])
    
    
    # Fallback to full address if no good context found
    if not context_parts:
        return f"You're in/near {location.address}"
    
    context = ", ".join(context_parts) 

    return f"You're in/near {context}" #. " # Nearby POIs: {nearby_pois}


