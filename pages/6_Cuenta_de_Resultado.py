import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Cuenta de Resultados", layout="centered")
st.title("Cuenta de Resultados")

DATA_PATH = Path("data")
YEAR = st.session_state.get("year_rrhh", 2025)

# =========================
# Función segura de carga
# =========================
def load_csv_safe(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

def filter_year(df, year):
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df[df["fecha"].dt.year == year]
    return df

# =========================
# INGRESOS
# =========================
st.subheader("Ingresos")

df_ventas = load_csv_safe(DATA_PATH / "ventas.csv")
df_ventas = filter_year(df_ventas, YEAR)

ventas_total = df_ventas["importe"].sum() if "importe" in df_ventas.columns else 0

st.metric("Ventas netas", f"{ventas_total:,.2f} €")

# =========================
# COSTE DE VENTAS (COGS)
# =========================
st.divider()
st.subheader("Coste de ventas (COGS)")

df_compras = load_csv_safe(DATA_PATH / "compras.csv")
df_compras = filter_year(df_compras, YEAR)

compras_total = df_compras["importe"].sum() if "importe" in df_compras.columns else 0

st.write("Compras de producto", f"-{compras_total:,.2f} €")

margen_bruto = ventas_total - compras_total

st.markdown(
    f"### **MARGEN BRUTO**\n**{margen_bruto:,.2f} €**"
)

# =========================
# GASTOS DE PERSONAL (RRHH)
# =========================
st.divider()
st.subheader("Gastos de personal")

df_rrhh = load_csv_safe(DATA_PATH / f"rrhh_{YEAR}.csv")

coste_personal = (
    df_rrhh["coste_empresa"].sum()
    if "coste_empresa" in df_rrhh.columns
    else 0
)

st.write("Coste de personal", f"-{coste_personal:,.2f} €")

# =========================
# GASTOS OPERATIVOS
# =========================
st.divider()
st.subheader("Gastos operativos")

df_gastos = load_csv_safe(DATA_PATH / "gastos.csv")
df_gastos = filter_year(df_gastos, YEAR)

gastos_operativos = (
    df_gastos["importe"].sum()
    if "importe" in df_gastos.columns
    else 0
)

st.write("Otros gastos operativos", f"-{gastos_operativos:,.2f} €")

# =========================
# EBITDA
# =========================
st.divider()
st.subheader("Resultado del periodo")

ebitda = margen_bruto - coste_personal - gastos_operativos

st.markdown(
    f"""
    ### **EBITDA**
    **{ebitda:,.2f} €**
    """
)
