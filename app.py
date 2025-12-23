import streamlit as st

st.set_page_config(
    page_title="OYKEN",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR – SEGMENTACIÓN PREMIUM
# =========================
with st.sidebar:
    st.markdown("### Ventas")
    st.caption("Análisis operativo, comportamiento y comparables")
    st.divider()

    # Nota: aquí Streamlit inyecta automáticamente las páginas
    # No se tocan, solo se guían visualmente

    st.markdown("---")
    st.markdown("### Próximamente")
    st.caption("Compras · Costes · Resultados")

# =========================
# CONTENIDO PRINCIPAL
# =========================
st.title("OYKEN")
st.caption("Sistema operativo de gestión")
st.markdown("Selecciona un módulo en el menú lateral")
