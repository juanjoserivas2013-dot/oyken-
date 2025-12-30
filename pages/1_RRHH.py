import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.title("OYKEN · RRHH")
st.caption("Gestión estructural de costes de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

SS_EMPRESA = 0.33
EXPORT_FILE = Path("rrhh_coste_mensual.csv")

# =====================================================
# ESTADO GLOBAL (AÑO ACTIVO + PUESTOS)
# =====================================================

if "anio_rrhh" not in st.session_state:
    st.session_state.anio_rrhh = 2025

if "puestos" not in st.session_state:
    st.session_state.puestos = []

# =====================================================
# BLOQUE 1 · ALTA DE PUESTOS (AÑO AQUÍ)
# =====================================================

st.subheader("Alta de puestos")

st.session_state.anio_rrhh = st.selectbox(
    "Año de planificación",
    list(range(2022, 2031)),
    index=list(range(2022, 2031)).index(st.session_state.anio_rrhh)
)

with st.form("alta_puesto", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Salario bruto anual (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Necesidad mensual (personas)**")
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
        st.session_state.puestos.append({
            "Año": st.session_state.anio_rrhh,
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual),
            **necesidad
        })

# =====================================================
# TABLA · ESTRUCTURA DE PUESTOS (AÑO ACTIVO)
# =====================================================

df_puestos = pd.DataFrame(st.session_state.puestos)

df_puestos_anio = df_puestos[
    df_puestos["Año"] == st.session_state.anio_rrhh
] if not df_puestos.empty else pd.DataFrame()

st.subheader("Estructura de puestos")

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

st.subheader("Coste de personal — Nómina")

nominas = []

for _, row in df_puestos_anio.iterrows():
    salario_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(salario_mensual * row[mes], 2)

    nominas.append(fila)

df_nominas = pd.DataFrame(nominas)

if not df_nominas.empty:
    st.dataframe(df_nominas, hide_index=True, use_container_width=True)
else:
    st.info("Sin datos de nómina.")

st.divider()

# =====================================================
# BLOQUE 3 · SEGURIDAD SOCIAL Y COSTE EMPRESA
# =====================================================

st.subheader("Seguridad Social y coste empresarial")

aplicar_ss = st.checkbox(
    "Aplicar Seguridad Social Empresa (33%)",
    value=True
)

costes = []

for _, row in df_nominas.iterrows():
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss = nomina * SS_EMPRESA if aplicar_ss else 0.0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    costes.append(fila)

df_costes = pd.DataFrame(costes)

if not df_costes.empty:
    st.dataframe(df_costes, hide_index=True, use_container_width=True)
else:
    st.info("Sin datos de coste empresarial.")

st.divider()

# =====================================================
# BLOQUE 4 · TOTALES MENSUALES RRHH
# =====================================================

st.subheader("Totales mensuales RRHH")

totales = []

for mes in MESES:
    nomina = df_costes.get(f"{mes} · Nómina", pd.Series()).sum()
    ss = df_costes.get(f"{mes} · SS", pd.Series()).sum()
    coste = df_costes.get(f"{mes} · Coste Empresa", pd.Series()).sum()

    totales.append({
        "Mes": mes,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)

st.dataframe(df_totales, hide_index=True, use_container_width=True)

st.divider()

# =====================================================
# BLOQUE 5 · PERSISTENCIA (HEREDA AÑO ACTIVO)
# =====================================================

st.subheader("Guardar RRHH")

df_export = df_totales.copy()
df_export.insert(0, "Año", st.session_state.anio_rrhh)

df_export.to_csv(EXPORT_FILE, index=False)

st.success(
    f"Coste de RRHH del año {st.session_state.anio_rrhh} guardado correctamente"
)

st.caption("Este coste se integra directamente en la Cuenta de Resultados.")
