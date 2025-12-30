import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="OYKEN · RRHH",
    layout="centered"
)

st.title("OYKEN · RRHH")
st.caption("Estructura salarial y coste de personal")

# =========================
# CONSTANTES
# =========================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

RRHH_FILE = Path("rrhh_coste_mensual.csv")

# =========================
# FASE 1 · PERSONAL
# =========================

st.subheader("Fase 1 · Personal necesario")

if "rrhh_personal" not in st.session_state:
    st.session_state.rrhh_personal = pd.DataFrame(
        columns=["Puesto", "Bruto anual (€)"] + MESES
    )

with st.form("form_personal", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input("Bruto anual (€)", min_value=0.0, step=500.0)

    cols = st.columns(6)
    necesidades = {}

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            necesidades[mes] = st.number_input(
                mes, min_value=0, step=1, key=f"n_{mes}"
            )

    submit = st.form_submit_button("Añadir puesto")

    if submit and puesto:
        fila = {"Puesto": puesto, "Bruto anual (€)": bruto_anual}
        fila.update(necesidades)

        st.session_state.rrhh_personal = pd.concat(
            [st.session_state.rrhh_personal, pd.DataFrame([fila])],
            ignore_index=True
        )

if not st.session_state.rrhh_personal.empty:
    st.dataframe(st.session_state.rrhh_personal, hide_index=True)

st.divider()

# =========================
# FASE 2 · COSTE NÓMINA
# =========================

st.subheader("Fase 2 · Coste de personal (nómina)")

if st.session_state.rrhh_personal.empty:
    st.info("Introduce personal para calcular el coste.")
    st.stop()

tabla_coste = []

for _, row in st.session_state.rrhh_personal.iterrows():
    bruto_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(bruto_mensual * row[mes], 2)

    tabla_coste.append(fila)

df_coste = pd.DataFrame(tabla_coste)
st.dataframe(df_coste, hide_index=True, use_container_width=True)

st.divider()

# =========================
# FASE 3 · SS Y COSTE EMPRESA
# =========================

st.subheader("Fase 3 · Seguridad Social y coste salarial")

aplicar_ss = st.checkbox("Aplicar Seguridad Social Empresa (33%)", value=True)

SS_EMPRESA = 0.33

tabla_final = []

for _, row in df_coste.iterrows():
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss = nomina * SS_EMPRESA if aplicar_ss else 0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS Empresa"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    tabla_final.append(fila)

df_final = pd.DataFrame(tabla_final)
st.dataframe(df_final, hide_index=True, use_container_width=True)

st.divider()

# =========================
# TOTALES MENSUALES + EXPORT
# =========================

st.subheader("Totales mensuales")

totales = []

for mes in MESES:
    nomina = df_final[f"{mes} · Nómina"].sum()
    ss = df_final[f"{mes} · SS Empresa"].sum()
    coste = df_final[f"{mes} · Coste Empresa"].sum()

    totales.append({
        "Mes": mes,
        "Nomina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)
st.dataframe(df_totales, hide_index=True, use_container_width=True)

# =========================
# EXPORT CSV (CLAVE OYKEN)
# =========================

anio = st.selectbox(
    "Año de referencia",
    list(range(2022, 2031)),
    index=3
)

export = []

for _, row in df_totales.iterrows():
    export.append({
        "Año": anio,
        "Mes": row["Mes"],
        "Nomina (€)": row["Nomina (€)"],
        "Seguridad Social (€)": row["Seguridad Social (€)"],
        "Coste Empresa (€)": row["Coste Empresa (€)"]
    })

df_export = pd.DataFrame(export)
df_export.to_csv(RRHH_FILE, index=False)

st.success("Coste de RRHH mensual guardado correctamente")

st.caption(
    "Este módulo construye y persiste el coste salarial completo."
)
