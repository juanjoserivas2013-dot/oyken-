import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="OYKEN",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR · SEGMENTACIÓN
# =========================
with st.sidebar:
    st.markdown("### Ventas")
    st.markdown(
        "<span style='color:#666;'>"
        "Análisis operativo, comportamiento y comparables"
        "</span>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### Próximamente")
    st.markdown(
        "<span style='color:#999;'>"
        "Compras · Costes · Resultados"
        "</span>",
        unsafe_allow_html=True
    )

# =========================
# CUERPO PRINCIPAL
# =========================
st.title("OYKEN")
st.caption("Sistema operativo de gestión")

st.markdown(
    "Selecciona un módulo en el menú lateral."
)
