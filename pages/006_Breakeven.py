import streamlit as st
import pandas as pd
from pathlib import Path
import calendar

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
RRHH_PUESTOS_FILE = Path("rrhh_puestos.csv")
GASTOS_FILE = Path("gastos.csv")

# =====================================================
# SELECTOR TEMPORAL (AUTÓNOMO)
# =====================================================

MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.number_input(
        "Año",
        min_value=2020,
        max_value=2100,
        value=2026,
        step=1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x]
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
if mes_sel == 0:
    row_compras = df_compras[
        df_compras["anio"] == int(anio_sel)
    ]
    row_ventas = df_ventas[
        df_ventas["anio"] == int(anio_sel)
    ]
else:
    row_compras = df_compras[
        (df_compras["anio"] == int(anio_sel)) &
        (df_compras["mes"] == mes_sel)
    ]
    row_ventas = df_ventas[
        (df_ventas["anio"] == int(anio_sel)) &
        (df_ventas["mes"] == mes_sel)
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
    "Cálculo directo (sin CSV intermedio) · "
    "1 - (C.Producto/Ventas)"
)

st.divider()

# =====================================================
# COSTES FIJOS ESTRUCTURALES
# =====================================================

st.markdown("### Costes fijos estructurales")


# ---------- RRHH ESTRUCTURAL MÍNIMO ----------
if not RRHH_PUESTOS_FILE.exists():
    st.error("No existe la estructura de RRHH.")
    st.stop()

df_rrhh = pd.read_csv(RRHH_PUESTOS_FILE)

# Filtrar año
df_rrhh = df_rrhh[df_rrhh["Año"] == int(anio_sel)]

# Filtrar solo estructura mínima
df_rrhh = df_rrhh[
    df_rrhh["Rol_RRHH"] == "Estructural mínimo"
]

if df_rrhh.empty:
    coste_rrhh = 0.0
else:
    coste_rrhh = 0.0

    for _, row in df_rrhh.iterrows():
        salario_mensual = row["Bruto anual (€)"] / 12

        if mes_sel == 0:
            personas = sum(row[mes] for mes in MESES_ES.values())
        else:
            personas = row[MESES_ES[mes_sel]]

        nomina = salario_mensual * personas
        ss = nomina * 0.33

        coste_rrhh += nomina + ss

# ---------- GASTOS FIJOS ----------
if not GASTOS_FILE.exists():
    st.error("No existen gastos registrados.")
    st.stop()

df_gastos = pd.read_csv(GASTOS_FILE)

df_gastos["Coste (€)"] = pd.to_numeric(
    df_gastos["Coste (€)"], errors="coerce"
).fillna(0)

# Solo gastos fijos estructurales
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

# ---------- TOTAL COSTES FIJOS ----------
costes_fijos_totales = coste_rrhh + total_gastos_fijos

# ---------- VISUAL RESUMEN ----------

st.metric(
    "Costes fijos totales (€)",
    f"{costes_fijos_totales:,.2f}"
)

st.caption(
    "Incluye RRHH + gastos fijos estructurales. "
    "No incluye costes variables ni coste de producto."
)

# ---------- DESGLOSE AUDITABLE ----------
st.markdown("#### Desglose de costes fijos")

st.dataframe(
    pd.concat([
        pd.DataFrame([{
            "Concepto": "Recursos Humanos",
            "Coste (€)": coste_rrhh
        }]),
        gastos_por_categoria.rename(
            columns={"Categoria": "Concepto"}
        )
    ]),
    hide_index=True,
    use_container_width=True
)

st.divider()

# =====================================================
# BREAKEVEN OPERATIVO
# =====================================================

st.subheader("Breakeven operativo")
st.caption(
    "Nivel de ventas necesario para cubrir los costes fijos estructurales "
    "con el margen bruto actual."
)

if margen_bruto <= 0:
    st.error("El margen bruto es ≤ 0. No se puede calcular el breakeven.")
else:
    breakeven_eur = costes_fijos_totales / margen_bruto

    st.metric(
        "Ventas necesarias para cubrir estructura",
        f"{breakeven_eur:,.2f} €"
    )

    st.caption(
        "Fórmula: Costes fijos estructurales / Margen bruto estructural"
    )

# =====================================================
# BREAKEVEN OPERATIVO DIARIO
# =====================================================

st.divider()
st.subheader("Breakeven operativo diario")

if mes_sel == 0:
    st.info(
        "El breakeven diario se muestra solo cuando se selecciona "
        "un mes concreto."
    )
else:
    dias_mes = calendar.monthrange(int(anio_sel), int(mes_sel))[1]

    breakeven_diario = breakeven_eur / dias_mes

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            "Breakeven diario",
            f"{breakeven_diario:,.2f} € / día"
        )
    with c2:
        st.metric(
            "Días del mes",
            dias_mes
        )

    st.caption(
        "Distribución homogénea del breakeven mensual "
        "en los días naturales del mes seleccionado."
    )

# =====================================================
# MARGEN DE CONTRIBUCIÓN REAL (OYKEN)
# =====================================================

import pandas as pd

st.divider()
st.subheader("Margen de contribución real")
st.caption(
    "Capacidad real del negocio para cubrir la estructura fija mínima, "
    "una vez descontados todos los costes variables reales "
    "(producto, gastos variables y RRHH variables)."
)

# =====================================================
# CONSTANTES RRHH (MISMAS QUE EN EL MÓDULO RRHH)
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

SS_EMPRESA = 0.33
RRHH_PUESTOS_FILE = Path("rrhh_puestos.csv")

# =====================================================
# GASTOS VARIABLES ESTRUCTURALES
# =====================================================

gastos_variables = df_gastos[
    (df_gastos["Tipo_Gasto"] == "Variable") &
    (df_gastos["Rol_Gasto"] == "Estructural")
]

if mes_sel == 0:
    gastos_variables_total = gastos_variables[
        gastos_variables["anio"] == anio_sel
    ]["Coste (€)"].sum()
else:
    gastos_variables_total = gastos_variables[
        (gastos_variables["anio"] == anio_sel) &
        (gastos_variables["mes"] == mes_sel)
    ]["Coste (€)"].sum()

# =====================================================
# RRHH VARIABLES (ESTRUCTURAL AMPLIABLE + REFUERZO OPERATIVO)
# =====================================================

if not RRHH_PUESTOS_FILE.exists():
    rrhh_variables_total = 0.0
else:
    df_rrhh = pd.read_csv(RRHH_PUESTOS_FILE)
    df_rrhh = df_rrhh[df_rrhh["Año"] == anio_sel]

    df_rrhh_variables = df_rrhh[
        df_rrhh["Rol_RRHH"].isin([
            "Estructural ampliable",
            "Refuerzo operativo"
        ])
    ]

    rrhh_variables_total = 0.0

    for _, row in df_rrhh_variables.iterrows():
        salario_mensual = row["Bruto anual (€)"] / 12

        if mes_sel == 0:
            personas = sum(row[mes] for mes in MESES)
        else:
            personas = row[MESES[mes_sel - 1]]

        coste = salario_mensual * personas * (1 + SS_EMPRESA)
        rrhh_variables_total += coste

# =====================================================
# COSTES VARIABLES REALES
# =====================================================

costes_variables_reales = (
    compras
    + gastos_variables_total
    + rrhh_variables_total
)

# =====================================================
# CONTRIBUCIÓN Y MARGEN
# =====================================================

contribucion_eur = ventas - costes_variables_reales

if ventas > 0:
    margen_contribucion = contribucion_eur / ventas
else:
    margen_contribucion = 0.0

st.metric(
    "Margen de contribución real",
    f"{margen_contribucion:.2%}"
)

st.caption(
    f"Contribución absoluta del período: {contribucion_eur:,.2f} € · "
    "Fórmula: Ventas − (Producto + Gastos variables + RRHH variables)"
)
