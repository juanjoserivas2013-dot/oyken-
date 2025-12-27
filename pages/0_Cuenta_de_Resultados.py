import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# CONFIGURACIÓN BÁSICA
# =========================

st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura económica real del negocio. Sin interpretación.")

# =========================
# ARCHIVOS DE DATOS
# =========================
VENTAS_FILE = Path("ventas.csv")

# =========================
# CONTRATO DE DATOS (VENTAS)
# =========================
COLUMNAS_VENTAS = [
    "fecha",
    "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur", "ventas_total_eur",
    "comensales_manana", "comensales_tarde", "comensales_noche",
    "tickets_manana", "tickets_tarde", "tickets_noche",
    "observaciones"
]

# =========================
# CARGA DEFENSIVA DE VENTAS
# =========================
if VENTAS_FILE.exists():
    df_ventas = pd.read_csv(VENTAS_FILE, parse_dates=["fecha"])
else:
    df_ventas = pd.DataFrame(columns=COLUMNAS_VENTAS)

for col in COLUMNAS_VENTAS:
    if col not in df_ventas.columns:
        df_ventas[col] = 0

if df_ventas.empty:
    st.info("No hay ventas registradas todavía.")
    st.stop()

# =========================
# SELECCIÓN DE PERIODO
# =========================
st.divider()

col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Mes",
        options=list(range(1, 13)),
        format_func=lambda x: datetime(2000, x, 1).strftime("%B")
    )

with col2:
    anio = st.selectbox(
        "Año",
        options=sorted(df_ventas["fecha"].dt.year.unique())
    )

# =========================
# FILTRO DE PERIODO
# =========================
df_periodo = df_ventas[
    (df_ventas["fecha"].dt.month == mes) &
    (df_ventas["fecha"].dt.year == anio)
].copy()

if df_periodo.empty:
    st.warning("No hay datos para el periodo seleccionado.")
    st.stop()

# =========================
# INGRESOS
# =========================
ventas_totales = df_periodo["ventas_total_eur"].sum()

# =========================
# BLOQUES PLACEHOLDER (HASTA CRUCE REAL)
# =========================
compras_imputadas = 0.0
variacion_inventario = 0.0
mermas = 0.0

coste_ventas_total = compras_imputadas + variacion_inventario + mermas
margen_bruto = ventas_totales - coste_ventas_total
margen_bruto_pct = (margen_bruto / ventas_totales * 100) if ventas_totales > 0 else 0

coste_salarial = 0.0
seguridad_social = 0.0
total_personal = coste_salarial + seguridad_social

gastos_operativos = 0.0

resultado_operativo = margen_bruto - total_personal - gastos_operativos

# =========================
# VISUAL CUENTA DE RESULTADOS
# =========================
st.divider()
st.subheader(f"Periodo: {datetime(anio, mes, 1).strftime('%B %Y')}")

def fila(label, value, bold=False):
    if bold:
        st.markdown(f"**{label}**  {value:,.2f} €")
    else:
        st.write(f"{label}  {value:,.2f} €")

st.markdown("### INGRESOS")
fila("Ventas totales", ventas_totales, bold=True)

st.markdown("---")
st.markdown("### COSTE DE VENTAS")
fila("Compras imputadas", compras_imputadas)
fila("Variación de inventario", variacion_inventario)
fila("Mermas", mermas)
fila("→ Coste de ventas total", coste_ventas_total, bold=True)

st.markdown("---")
st.markdown("### MARGEN BRUTO")
fila("Margen bruto", margen_bruto, bold=True)
st.caption(f"Margen bruto %: {margen_bruto_pct:.1f} %")

st.markdown("---")
st.markdown("### COSTES DE PERSONAL")
fila("Coste salarial", coste_salarial)
fila("Seguridad social", seguridad_social)
fila("→ Total personal", total_personal, bold=True)

st.markdown("---")
st.markdown("### GASTOS OPERATIVOS")
fila("Gastos varios", gastos_operativos)

st.markdown("---")
st.markdown("### RESULTADO OPERATIVO")
fila("Resultado operativo", resultado_operativo, bold=True)

st.divider()
st.caption("OYKEN no interpreta todavía. Solo muestra la verdad económica.")
