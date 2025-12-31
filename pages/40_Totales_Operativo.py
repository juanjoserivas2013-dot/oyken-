import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(page_title="OYKEN · Totales Operativos", layout="centered")

st.title("OYKEN · Totales Operativos")
st.caption("Consolidado mensual de magnitudes económicas operativas")

# =========================
# FUENTES DE DATOS
# =========================
DATA_FILE = Path("totales_operativos.csv")                 # Compras, Gastos, RRHH, Inventario
VENTAS_FILE = Path("ventas_mensuales_consolidadas.csv")   # Ventas desde Control Operativo

dfs = []

if DATA_FILE.exists():
    dfs.append(pd.read_csv(DATA_FILE))

if VENTAS_FILE.exists():
    dfs.append(pd.read_csv(VENTAS_FILE))

if not dfs:
    st.warning("No existen datos en Totales Operativos.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

if df.empty:
    st.info("Totales Operativos no contiene registros.")
    st.stop()

# =========================
# NORMALIZAR TIPOS
# =========================
df["anio"] = df["anio"].astype(int)
df["mes"] = df["mes"].astype(int)
df["importe_eur"] = df["importe_eur"].astype(float)

# =========================
# SELECTOR DE AÑO
# =========================
anios = sorted(df["anio"].unique())
anio_sel = st.selectbox("Año", anios, index=len(anios) - 1)

df_anio = df[df["anio"] == anio_sel].copy()

# =========================
# ESTADO DE COBERTURA
# =========================
st.divider()
st.markdown("**Estado de cobertura**")

MODULOS = [
    "Control Operativo",
    "Compras",
    "Gastos",
    "RRHH",
    "Inventario"
]

cobertura = []
for m in MODULOS:
    if (df_anio["origen"] == m).any():
        cobertura.append(f"{m}: OK")
    else:
        cobertura.append(f"{m}: Sin datos")

st.write(" · ".join(cobertura))

# =========================
# FILTROS DISCRETOS
# =========================
st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    origen_sel = st.multiselect(
        "Origen",
        sorted(df_anio["origen"].unique()),
        default=sorted(df_anio["origen"].unique())
    )

with c2:
    concepto_sel = st.multiselect(
        "Concepto",
        sorted(df_anio["concepto"].unique()),
        default=sorted(df_anio["concepto"].unique())
    )

MESES_TXT = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

with c3:
    meses_disponibles = sorted(df_anio["mes"].unique())

    mes_sel_txt = st.multiselect(
        "Mes",
        options=[MESES_TXT[m] for m in meses_disponibles],
        default=[MESES_TXT[m] for m in meses_disponibles]
    )

    # Volvemos a mes numérico para el filtro
    mes_sel = [k for k, v in MESES_TXT.items() if v in mes_sel_txt]


df_filtro = df_anio[
    (df_anio["origen"].isin(origen_sel)) &
    (df_anio["concepto"].isin(concepto_sel)) &
    (df_anio["mes"].isin(mes_sel))
].copy()

# =========================
# PRESENTACIÓN TABULAR
# =========================
st.divider()

MESES_TXT = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

df_filtro["Mes"] = df_filtro["mes"].map(MESES_TXT)

tabla = (
    df_filtro
    .sort_values(["anio", "mes", "origen"])
    .rename(columns={
        "anio": "Año",
        "origen": "Origen",
        "concepto": "Concepto",
        "importe_eur": "Importe (€)"
    })
    [["Año", "Mes", "Origen", "Concepto", "Importe (€)"]]
)

st.dataframe(
    tabla,
    hide_index=True,
    use_container_width=True
)
