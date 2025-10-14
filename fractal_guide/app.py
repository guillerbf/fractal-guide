import base64
import io
import os
from typing import Optional

from dotenv import load_dotenv

import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from fractal_guide.services.geocode import reverse_geocode
from fractal_guide.services.llm import summarize_context


def get_image_bytes() -> Optional[bytes]:
    image = st.camera_input("Take a photo (optional)")
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

    with st.expander("Privacy", expanded=False):
        st.write("Images and location are sent to APIs to generate responses. No data is persisted.")

    # Location capture
    st.subheader("Share location")
    geo = streamlit_geolocation()
    lat = geo.get("latitude") if geo else None
    lon = geo.get("longitude") if geo else None

    place_text: Optional[str] = None
    if lat is not None and lon is not None:
        place_text = cached_reverse_geocode(lat, lon)
        st.success(place_text)
    else:
        st.info("Tap the button above to share your location.")

    # Photo + question input
    image_bytes = get_image_bytes()
    user_text = st.text_input("Ask a question (optional)", placeholder="What's around me?")

    col1, col2 = st.columns(2)
    with col1:
        consent = st.checkbox("I consent to sending my data to APIs", value=False)
    with col2:
        submit = st.button("Get guidance", type="primary", disabled=not consent)

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


if __name__ == "__main__":
    main()


