import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="OYKEN · RRHH",
    layout="centered"
)

st.title("OYKEN · RRHH")
st.caption("Gestión del coste de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

COLUMNAS_BASE = ["Puesto", "Bruto anual (€)"] + MESES
RUTA_EXPORT = Path("rrhh_coste_mensual.csv")
SS_EMPRESA = 0.33

# =====================================================
# ESTADO INICIAL
# =====================================================

if "rrhh_personal" not in st.session_state:
    st.session_state.rrhh_personal = pd.DataFrame(columns=COLUMNAS_BASE)

# =====================================================
# FASE 1 · ALTA DE PERSONAL
# =====================================================

st.subheader("Fase 1 · Alta de puestos")

with st.form("form_rrhh", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Bruto anual (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Número de personas por mes**")

    personas_mes = {}
    cols = st.columns(6)

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            personas_mes[mes] = st.number_input(
                mes,
                min_value=0,
                step=1,
                key=f"{mes}_personas"
            )

    guardar = st.form_submit_button("Añadir puesto")

    if guardar and puesto.strip() != "":
        fila = {
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual)
        }
        for mes in MESES:
            fila[mes] = int(personas_mes[mes])

        st.session_state.rrhh_personal = pd.concat(
            [st.session_state.rrhh_personal, pd.DataFrame([fila])],
            ignore_index=True
        )

# =====================================================
# VISUALIZACIÓN PERSONAL
# =====================================================

if not st.session_state.rrhh_personal.empty:
    st.dataframe(
        st.session_state.rrhh_personal,
        hide_index=True,
        use_container_width=True
    )

st.divider()

# =====================================================
# FASE 2 · COSTE DE NÓMINA
# =====================================================

st.subheader("Fase 2 · Coste de personal (nómina)")

tabla_nominas = []

for _, row in st.session_state.rrhh_personal.iterrows():
    bruto_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(bruto_mensual * row[mes], 2)

    tabla_nominas.append(fila)

df_nominas = pd.DataFrame(tabla_nominas)

if not df_nominas.empty:
    st.dataframe(df_nominas, hide_index=True, use_container_width=True)
else:
    st.info("No hay datos de nómina.")

st.divider()

# =====================================================
# FASE 3 · SEGURIDAD SOCIAL Y COSTE EMPRESA
# =====================================================

st.subheader("Fase 3 · Seguridad Social y coste empresa")

aplicar_ss = st.checkbox(
    "Aplicar Seguridad Social Empresa (33%)",
    value=True
)

tabla_coste = []

for _, row in df_nominas.iterrows():
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row.get(mes, 0.0)
        ss = nomina * SS_EMPRESA if aplicar_ss else 0.0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS Empresa"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    tabla_coste.append(fila)

df_coste = pd.DataFrame(tabla_coste)

# --- BLINDAJE: GARANTIZAR TODAS LAS COLUMNAS ---
for mes in MESES:
    for sufijo in ["Nómina", "SS Empresa", "Coste Empresa"]:
        col = f"{mes} · {sufijo}"
        if col not in df_coste.columns:
            df_coste[col] = 0.0

if not df_coste.empty:
    st.dataframe(df_coste, hide_index=True, use_container_width=True)
else:
    st.info("No hay datos de coste salarial.")

st.divider()

# =====================================================
# TOTALES MENSUALES
# =====================================================

st.subheader("Totales mensuales")

totales = []

for mes in MESES:
    nomina = df_coste[f"{mes} · Nómina"].sum()
    ss = df_coste[f"{mes} · SS Empresa"].sum()
    coste = df_coste[f"{mes} · Coste Empresa"].sum()

    totales.append({
        "Mes": mes,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)

st.dataframe(df_totales, hide_index=True, use_container_width=True)

# =====================================================
# EXPORTACIÓN PARA CUENTA DE RESULTADOS
# =====================================================

anio = st.selectbox(
    "Año de referencia",
    list(range(2022, 2031)),
    index=3
)

df_export = df_totales.copy()
df_export.insert(0, "Año", anio)

df_export.to_csv(RUTA_EXPORT, index=False)

st.success("Coste de RRHH mensual guardado correctamente")
st.caption("Este módulo construye y persiste el coste salarial completo.")
