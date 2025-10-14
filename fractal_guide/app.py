import base64
import io
import os
from typing import Optional

from dotenv import load_dotenv

import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import get_geolocation

from fractal_guide.services.geocode import reverse_geocode
from fractal_guide.services.llm import summarize_context


def get_image_bytes() -> Optional[bytes]:
    # Only render camera when the user opted in via the UI toggle
    if not st.session_state.get("show_camera", False):
        return None
    image = st.camera_input("Take a photo (optional)", key="camera")
    if image is None:
        return None
    return image.getvalue()


@st.cache_data(ttl=3600)
def cached_reverse_geocode(lat: float, lon: float) -> str:
    return reverse_geocode(lat, lon)


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="Fractal Guide", page_icon="🧭", layout="centered")
    st.title("Fractal Guide")
    st.caption("A lightweight local guide using your location and photo")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False

    # Location capture

    # Try live geolocation first; fallback to streamlit_geolocation
    lat = None
    lon = None
    try:
        loc = get_geolocation()
        if loc and "coords" in loc:
            lat = loc["coords"].get("latitude")
            lon = loc["coords"].get("longitude")
    except Exception:
        pass

    if lat is None or lon is None:
        geo = streamlit_geolocation()
        lat = geo.get("latitude") if geo else None
        lon = geo.get("longitude") if geo else None

    place_text: Optional[str] = None
    if lat is not None and lon is not None:
        place_text = cached_reverse_geocode(lat, lon)
        st.success(place_text)
    else:
        st.info("Tap the button above to share your location.")

    st.subheader("What are you interested in?")

    # Photo capture toggled by user action
    colp1, colp2 = st.columns(2)
    with colp1:
        if not st.session_state.show_camera:
            if st.button("Add photo"):
                st.session_state.show_camera = True
                st.rerun()
        else:
            if st.button("Hide photo"):
                st.session_state.show_camera = False
                st.rerun()
    with colp2:
        pass

    image_bytes = get_image_bytes()
    user_text = st.text_input("Ask a question (optional)", placeholder="What's around me?")

    submit = st.button("Ask your AI guide", type="primary")

    # Render history
    for role, content in st.session_state.messages:
        st.chat_message(role).write(content)

    if submit:
        if place_text is None:
            st.warning("Please allow location first.")
            return

        with st.spinner("Thinking..."):
            try:
                reply, need_clarifier, options = summarize_context(
                    place_text=place_text,
                    user_text=user_text or "",
                    image_bytes=image_bytes,
                )
            except Exception as e:
                st.error("There was an issue generating guidance. Please try again.")
                reply, need_clarifier, options = (
                    "I had trouble contacting services. You can retry in a moment.",
                    False,
                    [],
                )

        st.session_state.messages.append(("assistant", reply))
        st.chat_message("assistant").write(reply)

        if need_clarifier and options:
            st.info("Help me disambiguate:")
            bcols = st.columns(len(options))
            for i, opt in enumerate(options):
                if bcols[i].button(opt):
                    st.session_state.messages.append(("user", opt))
                    st.rerun()
    
    # with st.expander("Privacy", expanded=False):
    #     st.write("Images and location are sent to APIs to generate responses. No data is persisted. By using this app, I consent to sending my data to APIs")

if __name__ == "__main__":
    main()


