#!/usr/bin/env python3
"""
Simple script to test reverse geocoding.
Usage: python test_geo.py <lat> <lon>
Example: python test_geo.py 40.7589 -73.9851 <llm_flag>
"""

import sys
import os
from fractal_guide.services.geocode import reverse_geocode
from fractal_guide.services.llm import summarize_context

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("Usage: python test_geo.py <lat> <lon> <llm_flag>")
        print("Example: python test_geo.py 40.7589 -73.9851 <llm_flag>")
        sys.exit(1)
    
    try:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
        llm_flag = sys.argv[3]
        print(f"Coordinates: {lat}, {lon}")
        result = reverse_geocode(lat, lon)
        print(f"Result: {result}")
        if llm_flag:
            result = summarize_context(place_text=result, user_text="", image_bytes=None, history=None)
            print(f"Result: {result}")
    except ValueError:
        print("Error: Please provide valid latitude and longitude as numbers")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
