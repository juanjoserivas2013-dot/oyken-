import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CABECERA
# =====================================================

st.subheader("OYKEN · Breakeven Operativo")
st.caption("Punto de equilibrio estructural del negocio")
st.divider()

# =====================================================
# ARCHIVOS CANÓNICOS
# =====================================================

COSTE_PRODUCTO_FILE = Path("coste_producto.csv")
RRHH_FILE = Path("rrhh_mensual.csv")
GASTOS_FILE = Path("gastos.csv")

# =====================================================
# SELECTOR TEMPORAL (AUTÓNOMO)
# =====================================================

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.number_input(
        "Año",
        min_value=2020,
        max_value=2100,
        value=2026,
        step=1
    )

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

with c2:
    mes_sel = st.selectbox(
        "Mes",
        ["Todos los meses"] + MESES_ES
    )

st.divider()

# =====================================================
# MARGEN BRUTO (DESDE COMPRAS + VENTAS)
# =====================================================

COMPRAS_MENSUALES_FILE = Path("compras_mensuales.csv")
VENTAS_MENSUALES_FILE = Path("ventas_mensuales.csv")

# ---------- Validaciones ----------
if not COMPRAS_MENSUALES_FILE.exists():
    st.error("No existen datos de Compras mensuales.")
    st.stop()

if not VENTAS_MENSUALES_FILE.exists():
    st.error("No existen datos de Ventas mensuales.")
    st.stop()

# ---------- Cargar datos ----------
df_compras = pd.read_csv(COMPRAS_MENSUALES_FILE)
df_ventas = pd.read_csv(VENTAS_MENSUALES_FILE)

# ---------- Normalizar tipos (CRÍTICO) ----------
for df in (df_compras, df_ventas):
    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)

df_compras["compras_total_eur"] = pd.to_numeric(
    df_compras["compras_total_eur"], errors="coerce"
).fillna(0)

df_ventas["ventas_total_eur"] = pd.to_numeric(
    df_ventas["ventas_total_eur"], errors="coerce"
).fillna(0)

# ---------- Filtrar período ----------
row_compras = df_compras[
    (df_compras["anio"] == int(anio_sel)) &
    (df_compras["mes"] == int(mes_sel))
]

row_ventas = df_ventas[
    (df_ventas["anio"] == int(anio_sel)) &
    (df_ventas["mes"] == int(mes_sel))
]

# ---------- Validación semántica ----------
if row_compras.empty or row_ventas.empty:
    st.warning(
        "No hay datos suficientes de Compras o Ventas "
        "para el período seleccionado."
    )
    st.stop()

compras = float(row_compras.iloc[0]["compras_total_eur"])
ventas = float(row_ventas.iloc[0]["ventas_total_eur"])

if ventas <= 0:
    st.warning("Las ventas del período son 0 €. No se puede calcular margen.")
    st.stop()

# ---------- Cálculo estructural ----------
coste_producto_pct = compras / ventas
margen_bruto = 1 - coste_producto_pct

# ---------- Visualización ----------
st.markdown("### Margen bruto estructural")

st.metric("Margen bruto", f"{margen_bruto:.2%}")

st.caption(
    "Fuente: Compras y Ventas mensuales · "
    "Cálculo directo (sin CSV intermedio)"
)

st.divider()

# =====================================================
# COSTES FIJOS · RRHH
# =====================================================

if not RRHH_FILE.exists():
    st.error("No existen datos de Recursos Humanos.")
    st.stop()

df_rrhh = pd.read_csv(RRHH_FILE)

row_rrhh = df_rrhh[
    (df_rrhh["anio"] == anio_sel) &
    (df_rrhh["mes"] == mes_sel)
]

if row_rrhh.empty:
    st.warning("No hay costes de RRHH para el período seleccionado.")
    st.stop()

coste_rrhh = float(row_rrhh.iloc[0]["rrhh_total_eur"])

# =====================================================
# COSTES FIJOS · GASTOS ESTRUCTURALES
# =====================================================

if not GASTOS_FILE.exists():
    st.error("No existen gastos registrados.")
    st.stop()

df_gastos = pd.read_csv(GASTOS_FILE)

gastos_fijos = df_gastos[
    (df_gastos["Tipo_Gasto"] == "Fijo") &
    (df_gastos["Rol_Gasto"] == "Estructural")
]

gastos_por_categoria = (
    gastos_fijos
    .groupby("Categoria", as_index=False)["Coste (€)"]
    .sum()
)

total_gastos_fijos = gastos_por_categoria["Coste (€)"].sum()

# =====================================================
# COSTES FIJOS TOTALES
# =====================================================

costes_fijos_totales = coste_rrhh + total_gastos_fijos

st.markdown("### Costes fijos estructurales")
st.metric("Total costes fijos", f"{costes_fijos_totales:,.2f} €")
st.caption("Incluye RRHH + gastos fijos estructurales")

st.divider()

# =====================================================
# DESGLOSE AUDITABLE
# =====================================================

st.markdown("### Desglose de costes fijos")

df_desglose = pd.concat(
    [
        pd.DataFrame([{
            "Concepto": "Recursos Humanos",
            "Coste (€)": coste_rrhh
        }]),
        gastos_por_categoria.rename(
            columns={"Categoria": "Concepto"}
        )
    ],
    ignore_index=True
)

st.dataframe(df_desglose, hide_index=True, use_container_width=True)

st.divider()

# =====================================================
# BREAKEVEN
# =====================================================

breakeven = costes_fijos_totales / margen_bruto

st.markdown("### Punto de equilibrio")
st.metric("Breakeven (sin IVA)", f"{breakeven:,.2f} €")

st.caption(
    "Facturación mínima necesaria para cubrir la estructura fija del negocio."
)
