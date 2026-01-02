import streamlit as st
from datetime import date

# =========================
# CONTEXTO TEMPORAL
# =========================

st.subheader("Contexto temporal")
st.caption("Selecciona el periodo de análisis")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

anio_actual = date.today().year
mes_actual = date.today().month

col1, col2 = st.columns(2)

with col1:
    mes_sel = st.selectbox(
        "Mes",
        options=MESES,
        index=mes_actual - 1
    )

with col2:
    anio_sel = st.selectbox(
        "Año",
        options=list(range(anio_actual - 5, anio_actual + 6)),
        index=5
    )

st.caption(f"Periodo activo: {mes_sel} {anio_sel}")
