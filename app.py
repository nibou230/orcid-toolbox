import streamlit as st
import gettext

st.markdown(f"""
<div class="BUL-header">
    <a href="https://www.ulaval.ca/" target="_blank">
        <svg aria-hidden="true" viewBox="0 0 102.6 129.8" style="display:block; width:19px; margin-right:0.625em;">
            <path fill="#E30513" d="M0 0v101.4c0 8.7 6.7 15.6 15.3 15.6h24.1c3.2 0 7.4 2.2 9.5 8.3l1.2 3.4c.3.7.7 1.1 1.2 1.1s.9-.4 1.2-1.1l1.2-3.4c2.1-6.1 6.3-8.3 9.5-8.3h24.1c8.6 0 15.3-6.8 15.3-15.6V0H0z"></path>
        </svg>
        <span>Université Laval</span>
    </a>
    &nbsp;|&nbsp;
	<a href="https://bibl.ulaval.ca/" target="_blank">
		<span>Bibliothèque</span>
	</a>
</div>
""", unsafe_allow_html=True)

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

# Set up gettext translations
_ = gettext.translation('messages', localedir='loc', languages=[st.session_state.locale], fallback=True).gettext

pg = st.navigation([st.Page("pages/main.py", title=_("app-title")), st.Page("pages/about.py", title=_("À propos"))], position="top")
pg.run()