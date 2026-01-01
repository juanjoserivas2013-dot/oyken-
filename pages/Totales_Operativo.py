import streamlit as st
import pandas as pd
from pathlib import Path

st.markdown("""
<style>
/* Chips de multiselect */
div[data-baseweb="tag"] {
    background-color: #f3f3f3 !important;
    color: #333333 !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 6px !important;
    font-weight: 500;
}

/* Icono de cerrar (x) */
div[data-baseweb="tag"] svg {
    color: #777777 !important;
}

/* Hover */
div[data-baseweb="tag"]:hover {
    background-color: #eaeaea !important;
    border-color: #c0c0c0 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================

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

# =========================
# LECTURA COMPRAS MENSUALES
# =========================

COMPRAS_FILE = Path("compras.csv")

if COMPRAS_FILE.exists():
    df_compras = pd.read_csv(COMPRAS_FILE)

    # Normalizar fecha
    df_compras["Fecha"] = pd.to_datetime(
        df_compras["Fecha"],
        dayfirst=True,
        errors="coerce"
    )

    # Agregación mensual
    compras_mensuales = (
        df_compras
        .assign(
            anio=df_compras["Fecha"].dt.year,
            mes=df_compras["Fecha"].dt.month
        )
        .groupby(["anio", "mes"], as_index=False)
        .agg(importe_eur=("Coste (€)", "sum"))
    )

    compras_mensuales["origen"] = "Compras"
    compras_mensuales["concepto"] = "Compras Totales"

    # Unir a Totales Operativos
    df = pd.concat([df, compras_mensuales], ignore_index=True)

# =========================
# LECTURA GASTOS MENSUALES
# =========================
GASTOS_FILE = Path("gastos.csv")

if GASTOS_FILE.exists():
    df_gastos = pd.read_csv(GASTOS_FILE)
    df_gastos["Fecha"] = pd.to_datetime(df_gastos["Fecha"], dayfirst=True)

    gastos_mensuales = (
        df_gastos
        .assign(
            anio=df_gastos["Fecha"].dt.year,
            mes=df_gastos["Fecha"].dt.month
        )
        .groupby(["anio", "mes"], as_index=False)
        .agg(importe_eur=("Coste (€)", "sum"))
    )

    gastos_mensuales["origen"] = "Gastos"
    gastos_mensuales["concepto"] = "Gastos Totales"

    df = pd.concat([df, gastos_mensuales], ignore_index=True)

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
from datetime import date

MESES_TXT = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

mes_actual = date.today().month
meses_disponibles = sorted(df_anio["mes"].unique())

with c3:
    mes_sel = st.selectbox(
        "Mes",
        options=meses_disponibles,
        index=meses_disponibles.index(mes_actual)
        if mes_actual in meses_disponibles else 0,
        format_func=lambda m: MESES_TXT[m]
    )

df_filtro = df_anio[
    (df_anio["origen"].isin(origen_sel)) &
    (df_anio["concepto"].isin(concepto_sel)) &
    (df_anio["mes"] == mes_sel)
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
