import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="OYKEN · EBITDA",
    layout="centered"
)

st.title("OYKEN · EBITDA")

# =========================
# ARCHIVOS CANÓNICOS
# =========================
VENTAS_FILE      = Path("ventas_mensuales.csv")
COMPRAS_FILE     = Path("compras_mensuales.csv")
RRHH_FILE        = Path("rrhh_mensual.csv")
GASTOS_FILE      = Path("gastos_mensuales.csv")
INVENTARIO_FILE  = Path("inventario_mensual.csv")

if not all(p.exists() for p in [
    VENTAS_FILE, COMPRAS_FILE, RRHH_FILE, GASTOS_FILE
]):
    st.warning("Aún no existen cierres mensuales suficientes para calcular EBITDA.")
    st.stop()

# =========================
# CARGA DE DATOS
# =========================
df_v = pd.read_csv(VENTAS_FILE)
df_c = pd.read_csv(COMPRAS_FILE)
df_r = pd.read_csv(RRHH_FILE)
df_g = pd.read_csv(GASTOS_FILE)

if INVENTARIO_FILE.exists():
    df_i = pd.read_csv(INVENTARIO_FILE)
else:
    df_i = pd.DataFrame(columns=["anio", "mes", "variacion_inventario_eur"])

# Normalizar tipos
for df in [df_v, df_c, df_r, df_g, df_i]:
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")

df_v["ventas_total_eur"] = pd.to_numeric(df_v["ventas_total_eur"], errors="coerce").fillna(0)
df_c["compras_total_eur"] = pd.to_numeric(df_c["compras_total_eur"], errors="coerce").fillna(0)
df_r["rrhh_total_eur"] = pd.to_numeric(df_r["rrhh_total_eur"], errors="coerce").fillna(0)
df_g["gastos_total_eur"] = pd.to_numeric(df_g["gastos_total_eur"], errors="coerce").fillna(0)
df_i["variacion_inventario_eur"] = pd.to_numeric(
    df_i.get("variacion_inventario_eur", 0),
    errors="coerce"
).fillna(0)

# =========================
# SELECTORES
# =========================
anios_disponibles = sorted(
    set(df_v["anio"].dropna())
    | set(df_c["anio"].dropna())
    | set(df_r["anio"].dropna())
    | set(df_g["anio"].dropna())
)

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox("Año", anios_disponibles, index=len(anios_disponibles) - 1)

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(range(1, 13)),
        format_func=lambda x: "Todos los meses" if x == 0 else [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

# =========================
# BREAKEVEN · LECTURA CANÓNICA
# =========================

BREAKEVEN_RESUMEN_FILE = Path("breakeven_resumen.csv")

if not BREAKEVEN_RESUMEN_FILE.exists():
    st.warning("No existe resumen de Breakeven. Ejecuta primero la página de Breakeven.")
    st.stop()

df_be = pd.read_csv(BREAKEVEN_RESUMEN_FILE)

df_be["anio"] = pd.to_numeric(df_be["anio"], errors="coerce")
df_be["mes"] = pd.to_numeric(df_be["mes"], errors="coerce")

df_be_sel = df_be[
    (df_be["anio"] == anio_sel) &
    (df_be["mes"] == mes_sel)
]

if df_be_sel.empty:
    st.warning("No hay datos de Breakeven para el período seleccionado.")
    st.stop()

be = df_be_sel.iloc[0]

# =========================
# FILTRADO
# =========================
for name in ["df_v", "df_c", "df_r", "df_g", "df_i"]:
    locals()[name] = locals()[name][locals()[name]["anio"] == anio_sel]
    if mes_sel != 0:
        locals()[name] = locals()[name][locals()[name]["mes"] == mes_sel]

# =========================
# BASE MENSUAL
# =========================
base = pd.DataFrame({"mes": range(1, 13)})

base = base.merge(df_v[["mes", "ventas_total_eur"]], on="mes", how="left")
base = base.merge(df_c[["mes", "compras_total_eur"]], on="mes", how="left")
base = base.merge(df_r[["mes", "rrhh_total_eur"]], on="mes", how="left")
base = base.merge(df_g[["mes", "gastos_total_eur"]], on="mes", how="left")
base = base.merge(df_i[["mes", "variacion_inventario_eur"]], on="mes", how="left")

base = base.fillna(0)

if mes_sel != 0:
    base = base[base["mes"] == mes_sel]

base = base.sort_values("mes")

# =========================
# CÁLCULOS
# =========================
base["ebitda_base_eur"] = (
    base["ventas_total_eur"]
    - base["compras_total_eur"]
    - base["rrhh_total_eur"]
    - base["gastos_total_eur"]
)

base["ebitda_ajustado_eur"] = (
    base["ebitda_base_eur"]
    - base["variacion_inventario_eur"]
)

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

base["Mes"] = base["mes"].map(MESES_ES)

# =====================================================
# BLOQUE 1 — EBITDA OPERATIVO
# =====================================================
st.divider()
st.subheader("EBITDA operativo (sin inventario)")

st.dataframe(
    base[[
        "Mes",
        "ventas_total_eur",
        "compras_total_eur",
        "rrhh_total_eur",
        "gastos_total_eur",
        "ebitda_base_eur"
    ]].rename(columns={
        "ventas_total_eur": "Ventas (€)",
        "compras_total_eur": "Compras (€)",
        "rrhh_total_eur": "RRHH (€)",
        "gastos_total_eur": "Gastos (€)",
        "ebitda_base_eur": "EBITDA operativo (€)"
    }),
    hide_index=True,
    use_container_width=True
)

# =====================================================
# BLOQUE 2 — AJUSTE POR VARIACIÓN DE INVENTARIO
# =====================================================
st.divider()
st.subheader("Ajuste por variación de inventario")

st.dataframe(
    base[[
        "Mes",
        "variacion_inventario_eur"
    ]].rename(columns={
        "variacion_inventario_eur": "Variación inventario (€)"
    }),
    hide_index=True,
    use_container_width=True
)

# =====================================================
# BLOQUE 3 — EBITDA AJUSTADO
# =====================================================
st.divider()
st.subheader("EBITDA ajustado (consumo real)")

st.dataframe(
    base[[
        "Mes",
        "ebitda_base_eur",
        "variacion_inventario_eur",
        "ebitda_ajustado_eur"
    ]].rename(columns={
        "ebitda_base_eur": "EBITDA operativo (€)",
        "variacion_inventario_eur": "Variación inventario (€)",
        "ebitda_ajustado_eur": "EBITDA ajustado (€)"
    }),
    hide_index=True,
    use_container_width=True
)

st.divider()
st.subheader("Referencias económicas del período")

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Ventas mínimas sostenibles",
        f"{be['breakeven_real_eur']:,.2f} €"
    )
    st.metric(
        "Brecha operativa",
        f"{be['brecha_operativa_eur']:,.2f} €"
    )

with c2:
    st.metric(
        "Costes fijos estructurales",
        f"{be['costes_fijos_totales_eur']:,.2f} €"
    )
    st.metric(
        "Margen de contribución real",
        f"{be['margen_contribucion_real_pct']:.2%}"
    )

# =====================================================
# SIMULADOR DE ESCENARIO · ABSORCIÓN DE BRECHA
# =====================================================

st.divider()
st.subheader("Simulador de escenario operativo")

st.caption(
    "Explora qué ocurre al absorber progresivamente la brecha operativa real. "
    "Las ventas y el EBITDA se calculan automáticamente según tu estructura."
)

absorcion = st.slider(
    "Nivel de absorción de brecha operativa",
    min_value=0,
    max_value=120,
    value=50,
    step=5,
    format="%d %%"
)

ratio = absorcion / 100

# Cálculos estructurales
ventas_objetivo = be_real + (brecha * ratio)
ebitda_esperado = brecha * ratio

# Clasificación de zona
if ratio < 0.5:
    zona = "🟢 Sostenible"
    riesgo = "Bajo"
    mensaje = (
        "El negocio opera con colchón limitado. "
        "No absorbe toda la brecha, pero mantiene estabilidad."
    )
elif ratio < 0.7:
    zona = "🟡 Eficiente"
    riesgo = "Controlado"
    mensaje = (
        "Zona óptima. Se absorbe gran parte de la brecha "
        "con equilibrio entre resultado y riesgo."
    )
elif ratio <= 1:
    zona = "🔴 Exigente"
    riesgo = "Alto"
    mensaje = (
        "Se absorbe prácticamente toda la brecha operativa. "
        "Requiere disciplina total y control diario."
    )
else:
    zona = "⚠️ Forzado"
    riesgo = "Muy alto"
    mensaje = (
        "El escenario exige más resultado del que la estructura permite. "
        "Riesgo elevado de ruptura operativa."
    )

# Visual
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Ventas objetivo", f"{ventas_objetivo:,.0f} €")

with c2:
    st.metric("EBITDA esperado", f"{ebitda_esperado:,.0f} €")

with c3:
    st.metric("Zona operativa", zona)

st.caption(f"Riesgo estructural: **{riesgo}**")
st.info(mensaje)

# =====================================================
# LECTURA DEL OBJETIVO · REFERENCIAS ESTRUCTURALES
# =====================================================

st.divider()
st.subheader("Lectura del objetivo según tu estructura actual")

# Variables base
be_real = float(be["breakeven_real_eur"])
brecha = float(be["brecha_operativa_eur"])
mc = float(be["margen_contribucion_real_pct"])

# Escenarios
ventas_sostenible = be_real

ventas_eficiente_min = be_real + (brecha * 0.5)
ventas_eficiente_max = be_real + (brecha * 0.7)

ventas_exigente = be_real + brecha

ebitda_eficiente_min = (ventas_eficiente_min - be_real) * mc
ebitda_eficiente_max = (ventas_eficiente_max - be_real) * mc

ebitda_exigente = brecha  # interpretación directa OYKEN

# ---------- MENSAJE 1 · SOSTENIBLE ----------
st.markdown(
    f"""
<small>
<strong>🟢 Objetivo sostenible · Equilibrio real</strong><br>
Ventas ≈ <strong>{ventas_sostenible:,.0f} €</strong><br>
EBITDA esperado ≈ <strong>0 €</strong><br>
Mantiene el negocio en equilibrio real, sin margen para absorber desviaciones.
</small>
""",
    unsafe_allow_html=True
)

# ---------- MENSAJE 2 · EFICIENTE ----------
st.markdown(
    f"""
<small>
<strong>🟡 Objetivo eficiente · Zona óptima</strong><br>
Ventas ≈ <strong>{ventas_eficiente_min:,.0f} €</strong> – <strong>{ventas_eficiente_max:,.0f} €</strong><br>
EBITDA estimado ≈ <strong>{ebitda_eficiente_min:,.0f} €</strong> – <strong>{ebitda_eficiente_max:,.0f} €</strong><br>
Absorbe parte de la brecha operativa y genera beneficio de forma estable.
</small>
""",
    unsafe_allow_html=True
)

# ---------- MENSAJE 3 · EXIGENTE ----------
st.markdown(
    f"""
<small>
<strong>🔴 Objetivo exigente · Techo operativo</strong><br>
Ventas ≥ <strong>{ventas_exigente:,.0f} €</strong><br>
EBITDA potencial ≈ <strong>{ebitda_exigente:,.0f} €</strong><br>
Requiere disciplina operativa total; cualquier desviación impacta directamente.
</small>
""",
    unsafe_allow_html=True
)


