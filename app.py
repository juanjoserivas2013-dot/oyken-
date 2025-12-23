import streamlit as st

st.set_page_config(
    page_title="OYKEN",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("OYKEN")
st.caption("Sistema operativo de gestión")

st.markdown(
    """
Selecciona un módulo en el menú lateral.

---

### Ventas  
Análisis operativo, comportamiento y comparables.  
Incluye control diario, lectura de tendencias y análisis comparativo.

---

### Próximamente  
Compras · Costes · Resultados  
Cuenta de explotación, eficiencia operativa y rentabilidad real.
"""
)
