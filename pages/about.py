import streamlit as st
from src.locale import init_locale, render_branding

_ = init_locale()
render_footer = render_branding()
render_footer()


reset_container = st.container(key="reset_container")

col_image, col_text = st.columns([1, 4])

with col_image:
    st.image("img/oiseau-orcidee.png")

with col_text:
    st.header(_("À propos"))

    st.markdown(_("about_text"))