import streamlit as st
import pandas as pd
from pathlib import Path

st.subheader("OYKEN · Breakeven Operativo")
st.caption("Punto de equilibrio estructural del negocio")

st.divider()

# =====================================================
# ARCHIVOS
# =====================================================
COSTE_PRODUCTO_FILE = Path("coste_producto.csv")
RRHH_FILE = Path("rrhh_mensual.csv")
GASTOS_FILE = Path("gastos.csv")

# =====================================================
# SELECTOR TEMPORAL
# =====================================================
c1, c2 = st.columns(2)

with c1:
    anio_sel = st.number_input(
        "Año",
        min_value=2020,
        max_value=2100,
        value=2026
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=list(range(1, 13)),
        format_func=lambda x: [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

st.divider()

# =====================================================
# MARGEN BRUTO (DESDE COMPRAS)
# =====================================================
if not COSTE_PRODUCTO_FILE.exists():
    st.error("No existe el coste de producto definido en Compras.")
    st.stop()

df_cp = pd.read_csv(COSTE_PRODUCTO_FILE)

row_cp = df_cp[
    (df_cp["anio"] == anio_sel) &
    (df_cp["mes"] == mes_sel)
]

if row_cp.empty:
    st.warning("No hay coste de producto para el período seleccionado.")
    st.stop()

coste_producto_pct = row_cp.iloc[0]["coste_producto_pct"]
margen_bruto = 1 - coste_producto_pct

st.markdown("### Margen bruto estructural")
st.metric(
    "Margen bruto",
    f"{margen_bruto:.2%}"
)

st.caption("Fuente: Compras · Coste de producto sobre ventas")

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

coste_rrhh = row_rrhh.iloc[0]["coste_rrhh_total"]

# =====================================================
# COSTES FIJOS · GASTOS
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
    .groupby("Categoria")["Coste (€)"]
    .sum()
    .reset_index()
)

total_gastos_fijos = gastos_por_categoria["Coste (€)"].sum()

# =====================================================
# COSTES FIJOS TOTALES
# =====================================================
costes_fijos_totales = coste_rrhh + total_gastos_fijos

st.markdown("### Costes fijos estructurales")

st.metric(
    "Total costes fijos",
    f"{costes_fijos_totales:,.2f} €"
)

st.caption("Incluye RRHH + gastos fijos estructurales")

st.divider()

# =====================================================
# DESGLOSE AUDITABLE
# =====================================================
st.markdown("### Desglose de costes fijos")

st.dataframe(
    pd.concat([
        pd.DataFrame([{
            "Concepto": "Recursos Humanos",
            "Coste (€)": coste_rrhh
        }]),
        gastos_por_categoria.rename(
            columns={
                "Categoria": "Concepto",
                "Coste (€)": "Coste (€)"
            }
        )
    ]),
    hide_index=True,
    use_container_width=True
)

st.divider()

# =====================================================
# BREAKEVEN
# =====================================================
breakeven = costes_fijos_totales / margen_bruto

st.markdown("### Punto de equilibrio")

st.metric(
    "Breakeven (sin IVA)",
    f"{breakeven:,.2f} €"
)

st.caption(
    "Facturación mínima necesaria para cubrir la estructura fija del negocio."
)
