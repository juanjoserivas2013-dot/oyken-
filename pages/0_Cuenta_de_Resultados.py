import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# IDENTIDAD
# =========================
st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura económica real del negocio. Sin interpretación.")

# =========================
# SELECTOR DE PERIODO
# =========================
c1, c2 = st.columns(2)
with c1:
    mes = st.selectbox("Mes", list(range(1, 13)), index=11)
with c2:
    año = st.selectbox("Año", [2024, 2025, 2026], index=1)

# =========================
# ARCHIVOS DEL ECOSISTEMA
# =========================
VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
INVENTARIO_FILE = Path("inventario.csv")
MERMAS_FILE = Path("mermas.csv")
GASTOS_FILE = Path("gastos.csv")
RRHH_FILE = Path("rrhh.csv")

# =========================
# FUNCIÓN DE CARGA SEGURA
# =========================
def cargar_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# =========================
# CARGA DE DATOS
# =========================
df_ventas = cargar_csv(VENTAS_FILE)
df_compras = cargar_csv(COMPRAS_FILE)
df_inventario = cargar_csv(INVENTARIO_FILE)
df_mermas = cargar_csv(MERMAS_FILE)
df_gastos = cargar_csv(GASTOS_FILE)
df_rrhh = cargar_csv(RRHH_FILE)

# =========================
# INGRESOS · VENTAS
# =========================
ventas_totales = 0.0

if not df_ventas.empty and "ventas_total_eur" in df_ventas.columns:
    df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"])
    df_v = df_ventas[
        (df_ventas["fecha"].dt.month == mes) &
        (df_ventas["fecha"].dt.year == año)
    ]
    ventas_totales = df_v["ventas_total_eur"].sum()

# =========================
# COSTE DE VENTAS
# =========================

# Compras imputadas
compras_total = (
    df_compras["importe_eur"].sum()
    if not df_compras.empty and "importe_eur" in df_compras.columns
    else 0.0
)

# Variación de inventario
variacion_inventario = 0.0
if (
    not df_inventario.empty
    and "inventario_inicial_eur" in df_inventario.columns
    and "inventario_final_eur" in df_inventario.columns
):
    variacion_inventario = (
        df_inventario["inventario_final_eur"].sum()
        - df_inventario["inventario_inicial_eur"].sum()
    )

# Mermas (por ahora solo cuantía)
mermas_total = (
    df_mermas["cantidad"].sum()
    if not df_mermas.empty and "cantidad" in df_mermas.columns
    else 0.0
)

coste_ventas = compras_total + variacion_inventario + mermas_total

# =========================
# MARGEN BRUTO
# =========================
margen_bruto = ventas_totales - coste_ventas
margen_pct = (margen_bruto / ventas_totales * 100) if ventas_totales > 0 else 0.0

# =========================
# COSTES DE PERSONAL
# =========================
coste_personal = (
    df_rrhh["coste_total_eur"].sum()
    if not df_rrhh.empty and "coste_total_eur" in df_rrhh.columns
    else 0.0
)

# =========================
# GASTOS OPERATIVOS
# =========================
gastos_operativos = (
    df_gastos["importe_eur"].sum()
    if not df_gastos.empty and "importe_eur" in df_gastos.columns
    else 0.0
)

# =========================
# RESULTADO OPERATIVO
# =========================
resultado_operativo = margen_bruto - coste_personal - gastos_operativos

# =========================
# VISUALIZACIÓN PREMIUM
# =========================
st.divider()

st.subheader("INGRESOS")
st.metric("Ventas totales", f"{ventas_totales:,.2f} €")

st.subheader("COSTE DE VENTAS")
st.write(f"Compras imputadas: {compras_total:,.2f} €")
st.write(f"Variación de inventario: {variacion_inventario:,.2f} €")
st.write(f"Mermas: {mermas_total:,.2f}")
st.write(f"**Coste de ventas total: {coste_ventas:,.2f} €**")

st.subheader("MARGEN BRUTO")
st.metric("Margen bruto", f"{margen_bruto:,.2f} €", f"{margen_pct:.1f}%")

st.subheader("COSTES DE PERSONAL")
st.metric("Total personal", f"{coste_personal:,.2f} €")

st.subheader("GASTOS OPERATIVOS")
st.metric("Gastos varios", f"{gastos_operativos:,.2f} €")

st.divider()
st.subheader("RESULTADO OPERATIVO")
st.metric("Resultado operativo", f"{resultado_operativo:,.2f} €")
