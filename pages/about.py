import streamlit as st
import os
import gettext

# Set up gettext translations
_ = gettext.translation('messages', localedir='loc', languages=[st.session_state.locale], fallback=True).gettext

# Set locale from Streamlit context if available, otherwise default to fr
default_locale = "fr"
if hasattr(st.context, "locale"):
    browser_locale = st.context.locale
    if isinstance(browser_locale, str) and browser_locale.startswith("fr"):
        default_locale = "fr"
    elif isinstance(browser_locale, str) and browser_locale.startswith("en"):
        default_locale = "en"

if "locale" not in st.session_state:
    st.session_state.locale = default_locale

# Keep locale in sync with sidebar selector without forcing manual reruns.
if "locale_picker" in st.session_state and st.session_state.locale != st.session_state.locale_picker:
    st.session_state.locale = st.session_state.locale_picker

# ULaval branding
with open(os.path.join("css", "bibl-ulaval.css"), encoding="utf-8") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Set locale from Streamlit context if available, otherwise default to fr
default_locale = "fr"
if hasattr(st.context, "locale"):
    browser_locale = st.context.locale
    if isinstance(browser_locale, str) and browser_locale.startswith("fr"):
        default_locale = "fr"
    elif isinstance(browser_locale, str) and browser_locale.startswith("en"):
        default_locale = "en"

if "locale" not in st.session_state:
    st.session_state.locale = default_locale

# Keep locale in sync with sidebar selector without forcing manual reruns.
if "locale_picker" in st.session_state and st.session_state.locale != st.session_state.locale_picker:
    st.session_state.locale = st.session_state.locale_picker

# Compact language chooser
if "locale_picker" not in st.session_state:
    st.session_state.locale_picker = st.session_state.locale

st.segmented_control(
    "lang",
    options=["fr", "en"],
    format_func=lambda option: "FR" if option == "fr" else "EN",
    key="locale_picker",
    label_visibility="collapsed",
)

reset_container = st.container(key="reset_container")

with st.bottom:
    st.markdown("""
                © 2026 Université Laval | [Licence libre MIT](https://github.com/timtomch/orcid-toolbox)
                | [Avis légal](https://www.bibl.ulaval.ca/avis-legal)
                | [Conditions générales d'utilisation](https://www.bibl.ulaval.ca/conditions-generales-dutilisation)
                | [Fraude en ligne](https://www.ulaval.ca/cybersecurite)
""")

col_image, col_text = st.columns([1, 4])

with col_image:
    st.image("img/oiseau-orcidee.png")

with col_text:
    st.header(_("À propos"))

    st.markdown(_("about_text"))