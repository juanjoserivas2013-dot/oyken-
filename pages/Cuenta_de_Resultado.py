import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Cuenta de Resultados")

DATA = Path("data")

# =========================
# SELECTORES
# =========================
col1, col2 = st.columns(2)

with col1:
    anio = st.selectbox("Año", [2024, 2025, 2026], index=1)

with col2:
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    mes = st.selectbox("Mes", list(meses.keys()), format_func=lambda x: meses[x])

# =========================
# FUNCIÓN LECTURA MENSUAL
# =========================
def leer_total(path, anio, mes):
    if not path.exists():
        return 0.0

    df = pd.read_csv(path)

    if {"anio", "mes", "total"}.issubset(df.columns):
        fila = df[(df["anio"] == anio) & (df["mes"] == mes)]
        if not fila.empty:
            return float(fila["total"].sum())

    return 0.0

# =========================
# LECTURA DE TOTALES
# =========================
ventas = leer_total(DATA / "ventas_mensuales.csv", anio, mes)
compras = leer_total(DATA / "compras_mensuales.csv", anio, mes)
inventario = leer_total(DATA / "inventario_mensual.csv", anio, mes)
mermas = leer_total(DATA / "mermas_mensual.csv", anio, mes)
rrhh = leer_total(DATA / "rrhh_mensual.csv", anio, mes)
gastos = leer_total(DATA / "gastos_mensuales.csv", anio, mes)

# =========================
# CUENTA DE RESULTADOS
# =========================
st.divider()
st.subheader(f"Resultado {meses[mes]} {anio}")

st.write("Ventas netas", f"{ventas:,.2f} €")
st.write("Compras", f"-{compras:,.2f} €")
st.write("Variación inventario", f"{inventario:,.2f} €")
st.write("Mermas", f"-{mermas:,.2f} €")

margen_bruto = ventas - compras + inventario - mermas

st.markdown(f"### **MARGEN BRUTO**  \n**{margen_bruto:,.2f} €**")

st.divider()
st.write("RRHH", f"-{rrhh:,.2f} €")
st.write("Gastos operativos", f"-{gastos:,.2f} €")

ebitda = margen_bruto - rrhh - gastos

st.divider()
st.markdown(f"### **EBITDA**  \n**{ebitda:,.2f} €**")
