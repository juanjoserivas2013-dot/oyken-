import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================

st.title("OYKEN · Costes de Personal")
st.caption("Estructura económica del capital humano")

# =========================
# DATOS
# =========================
DATA_FILE = Path("costes_personal.csv")

if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(
        columns=[
            "Mes", "Año",
            "Coste total (€)",
            "Incluye SS",
            "Incluye variables",
            "Observaciones"
        ]
    )

# =========================
# SELECCIÓN DE PERIODO
# =========================
st.divider()
st.subheader("Periodo de registro")

col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Mes",
        [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
    )

with col2:
    año = st.selectbox(
        "Año",
        list(range(2022, 2031)),
        index=3
    )

st.caption("El registro es mensual. OYKEN no impone fechas.")

# =========================
# REGISTRO DE COSTE
# =========================
st.divider()
st.subheader("Registro de coste mensual")

with st.form("form_coste_personal", clear_on_submit=True):

    coste = st.number_input(
        "Coste total de personal (€)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    col3, col4 = st.columns(2)
    with col3:
        incluye_ss = st.checkbox("Incluye Seguridad Social")
    with col4:
        incluye_var = st.checkbox("Incluye variables / extras")

    observaciones = st.text_input(
        "Observaciones internas (opcional)"
    )

    guardar = st.form_submit_button("Registrar coste del mes")

    if guardar:

        if coste <= 0:
            st.warning("El coste debe ser mayor que 0 €")
            st.stop()

        # Si ya existe el mes, se sustituye
        df = df[~((df["Mes"] == mes) & (df["Año"] == año))]

        nuevo = {
            "Mes": mes,
            "Año": año,
            "Coste total (€)": round(coste, 2),
            "Incluye SS": incluye_ss,
            "Incluye variables": incluye_var,
            "Observaciones": observaciones
        }

        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Coste mensual registrado correctamente.")

# =========================
# RESUMEN DEL MES
# =========================
st.divider()
st.subheader(f"Resumen · {mes} {año}")

registro = df[(df["Mes"] == mes) & (df["Año"] == año)]

if registro.empty:
    st.info("No hay coste registrado para este periodo.")
else:
    coste_mes = registro.iloc[0]["Coste total (€)"]
    coste_diario = coste_mes / 30

    st.markdown(f"""
    - **Coste total de personal:** **{coste_mes:,.2f} €**
    - **Días operativos considerados:** 30
    - **Coste medio diario:** **{coste_diario:,.2f} € / día**
    """)

    st.caption("El coste diario es una referencia estructural.")

# =========================
# CONTEXTO SECTOR HORECA
# =========================
st.divider()
st.subheader("Contexto sector Horeca")

tabla_contexto = pd.DataFrame({
    "Tipo de negocio": [
        "Cafetería / Bar",
        "Restaurante informal",
        "Restaurante servicio completo",
        "Restaurante premium",
        "Dark kitchen / delivery"
    ],
    "Rango estructural": [
        "25% – 32%",
        "28% – 35%",
        "30% – 38%",
        "35% – 45%",
        "20% – 28%"
    ]
})

st.table(tabla_contexto)
st.caption("Referencias estructurales. No son objetivos ni evaluaciones.")

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("Histórico de costes de personal")

if df.empty:
    st.info("No hay registros históricos.")
else:
    df_hist = df.sort_values(["Año", "Mes"])
    df_hist["Coste diario (€)"] = df_hist["Coste total (€)"] / 30

    st.dataframe(
        df_hist[[
            "Mes", "Año",
            "Coste total (€)",
            "Coste diario (€)"
        ]],
        hide_index=True,
        use_container_width=True
    )

    idx = st.selectbox(
        "Eliminar registro",
        df_hist.index,
        format_func=lambda i: f'{df_hist.loc[i,"Mes"]} {df_hist.loc[i,"Año"]}'
    )

    if st.button("Eliminar"):
        df = df.drop(idx).reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Registro eliminado correctamente.")

# =========================
# NOTA OYKEN
# =========================
st.caption(
    "OYKEN no evalúa personas. "
    "Analiza estructuras para proteger la rentabilidad y la sostenibilidad."
)
