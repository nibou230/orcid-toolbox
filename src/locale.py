import gettext
import os
import streamlit as st

def init_locale() -> callable:
    # 1. Detect browser locale on first load
    default_locale = "fr"
    if hasattr(st.context, "locale"):
        browser_locale = st.context.locale
        if isinstance(browser_locale, str) and browser_locale.startswith("en"):
            default_locale = "en"

    # 2. Initialise session_state on first run
    if "locale" not in st.session_state:
        st.session_state.locale = default_locale

    # 3. Sync from picker widget (handles None gracefully)
    picked = st.session_state.get("locale_picker")
    if picked is not None:
        st.session_state.locale = picked

    # 4. Final defensive fallback — gettext never sees None
    active_locale = st.session_state.get("locale") or default_locale
    st.session_state.locale = active_locale

    return gettext.translation(
        "messages",
        localedir="loc",
        languages=[active_locale],
        fallback=True,
    ).gettext


def render_branding() -> callable:
    with open(os.path.join("css", "bibl-ulaval.css"), encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

    # Language picker widget — must be rendered on every page so
    # session_state.locale_picker stays alive across navigation
    if "locale_picker" not in st.session_state:
        st.session_state.locale_picker = st.session_state.locale

    st.segmented_control(
        "lang",
        options=["fr", "en"],
        format_func=lambda option: "FR" if option == "fr" else "EN",
        key="locale_picker",
        label_visibility="collapsed",
    )

    # Render footer with legal links and copyright notice
    def render_footer():
        with st.bottom:
            st.markdown("\n".join(line.strip() for line in """
                © 2026 Université Laval | [Licence libre MIT](https://github.com/timtomch/orcid-toolbox)
                | [Avis légal](https://www.bibl.ulaval.ca/avis-legal)
                | [Conditions générales d'utilisation](https://www.bibl.ulaval.ca/conditions-generales-dutilisation)
                | [Fraude en ligne](https://www.ulaval.ca/cybersecurite)
            """.splitlines()))

    return render_footer