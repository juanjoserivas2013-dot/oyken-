import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.title("OYKEN · RRHH")
st.caption("Planificación estructural de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

SS_EMPRESA = 0.33
PUESTOS_FILE = Path("rrhh_puestos.csv")

# =====================================================
# UTILIDADES DE PERSISTENCIA
# =====================================================

def cargar_puestos():
    if PUESTOS_FILE.exists():
        return pd.read_csv(PUESTOS_FILE)
    return pd.DataFrame(columns=["Año", "Puesto", "Bruto anual (€)", *MESES])

def guardar_puesto(registro: dict):
    df = cargar_puestos()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(PUESTOS_FILE, index=False)

# =====================================================
# CONTEXTO DE PLANIFICACIÓN
# =====================================================

anio_activo = st.selectbox(
    "Año activo",
    list(range(2022, 2031)),
    index=list(range(2022, 2031)).index(2025)
)

df_puestos = cargar_puestos()
df_puestos_anio = df_puestos[df_puestos["Año"] == anio_activo]

st.divider()

# =====================================================
# BLOQUE 1 · ALTA DE PUESTOS
# =====================================================

st.subheader("Alta de puestos")

with st.form("alta_puesto", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Salario bruto anual por persona (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Necesidad mensual del puesto (personas)**")
    cols = st.columns(6)
    necesidad = {}

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            necesidad[mes] = st.number_input(
                mes,
                min_value=0,
                step=1,
                key=f"need_{mes}"
            )

    guardar = st.form_submit_button("Guardar puesto")

    if guardar and puesto.strip():
        registro = {
            "Año": anio_activo,
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual),
            **necesidad
        }
        guardar_puesto(registro)
        st.success(f"Puesto '{puesto}' guardado para {anio_activo}")
        st.rerun()

# =====================================================
# TABLA · ESTRUCTURA DE PUESTOS
# =====================================================

st.subheader(f"Estructura de puestos — {anio_activo}")

if not df_puestos_anio.empty:
    st.dataframe(
        df_puestos_anio.drop(columns=["Año"]),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No hay puestos definidos para este año.")

st.divider()

# =====================================================
# BLOQUE 2 · COSTE DE PERSONAL (NÓMINA)
# =====================================================

st.subheader("Coste de personal — Nómina (económico)")
st.caption("Cálculo económico aislado de la planificación.")

SS_EMPRESA = 0.33

# =====================================================
# BLOQUE 2B · MAPA DE MESES
# =====================================================

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# =====================================================
# BLOQUE 2C · SELECTORES ECONÓMICOS
# =====================================================

st.divider()
st.subheader("Selector temporal económico")

c1, c2 = st.columns(2)

with c1:
    anios_disponibles = sorted(df_puestos["Año"].unique())

    if not anios_disponibles:
        st.info("No hay estructura de RRHH disponible.")
        st.stop()

    anio_economico = st.selectbox(
        "Año económico",
        anios_disponibles,
        index=len(anios_disponibles) - 1,
        key="anio_rrhh_economico"
    )

with c2:
    mes_economico = st.selectbox(
        "Mes",
        options=[0] + list(range(1, 13)),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x - 1],
        key="mes_rrhh_economico"
    )

# =====================================================
# BLOQUE 2D · ORIGEN ECONÓMICO (AISLADO)
# =====================================================

df_puestos_econ = df_puestos[
    df_puestos["Año"] == anio_economico
]

if df_puestos_econ.empty:
    st.warning("No hay puestos definidos para este año económico.")
    st.stop()

# =====================================================
# BLOQUE 3 · CÁLCULO ROBUSTO MENSUAL
# =====================================================

datos_meses = []

for i, mes_nombre in enumerate(MESES_ES, start=1):

    if mes_economico != 0 and i != mes_economico:
        continue

    total_mes = 0.0

    for _, row in df_puestos_econ.iterrows():
        salario_mensual = row["Bruto anual (€)"] / 12
        personas = row[mes_nombre]

        nomina = salario_mensual * personas
        ss = nomina * SS_EMPRESA

        total_mes += nomina + ss

    datos_meses.append({
        "Mes": mes_nombre,
        "Coste RRHH (€)": round(total_mes, 2)
    })

df_totales = pd.DataFrame(datos_meses)

# =====================================================
# BLOQUE 4 · TABLA VISIBLE
# =====================================================

st.divider()
st.subheader("Totales mensuales RRHH (económico)")

st.dataframe(
    df_totales,
    hide_index=True,
    use_container_width=True
)

st.metric(
    "Coste RRHH período seleccionado",
    f"{df_totales['Coste RRHH (€)'].sum():,.2f} €"
)

# =====================================================
# BLOQUE 5 · CSV CANÓNICO MENSUAL
# =====================================================

from datetime import datetime

RRHH_MENSUAL_FILE = Path("rrhh_mensual.csv")

# Crear CSV si no existe
if not RRHH_MENSUAL_FILE.exists():
    pd.DataFrame(
        columns=["anio", "mes", "rrhh_total_eur", "fecha_actualizacion"]
    ).to_csv(RRHH_MENSUAL_FILE, index=False)

# Preparar datos a guardar
df_csv = df_totales.copy()
df_csv["mes"] = df_csv["Mes"].map(
    {v: i + 1 for i, v in enumerate(MESES_ES)}
)
df_csv["anio"] = anio_economico
df_csv["rrhh_total_eur"] = df_csv["Coste RRHH (€)"]
df_csv = df_csv[["anio", "mes", "rrhh_total_eur"]]

# Cargar histórico
df_hist = pd.read_csv(RRHH_MENSUAL_FILE)

# Overwrite limpio por (anio, mes)
df_hist = df_hist[
    ~(
        (df_hist["anio"] == anio_economico) &
        (df_hist["mes"].isin(df_csv["mes"]))
    )
]

df_csv["fecha_actualizacion"] = datetime.now()

df_final = pd.concat([df_hist, df_csv], ignore_index=True)
df_final = df_final.sort_values(["anio", "mes"])
df_final.to_csv(RRHH_MENSUAL_FILE, index=False)

st.success("RRHH económico consolidado correctamente.")
