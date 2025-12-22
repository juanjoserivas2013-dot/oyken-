import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.title("OIKEN · Comparables")
st.caption("Pulso diario, proyección y estructura temporal del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para mostrar comparables.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

if df.empty:
    st.stop()

# =========================
# VARIABLES BASE
# =========================
df["year"] = df["fecha"].dt.year
df["weekday"] = df["fecha"].dt.weekday
df["day"] = df["fecha"].dt.day

df["tickets_total"] = (
    df["tickets_manana"] +
    df["tickets_tarde"] +
    df["tickets_noche"]
)

# =========================
# FECHA ACTUAL
# =========================
hoy = pd.to_datetime(date.today())
df_mes = df[
    (df["fecha"].dt.year == hoy.year) &
    (df["fecha"].dt.month == hoy.month) &
    (df["fecha"] <= hoy)
].copy()

dias_operativos = hoy.day

if df_mes.empty:
    st.warning("No hay datos del mes en curso.")
    st.stop()

ventas_acumuladas = df_mes["ventas_total_eur"].sum()
ritmo_diario = ventas_acumuladas / dias_operativos
estimacion_cierre = ritmo_diario * 30

# =========================
# 1. PULSO DIARIO (DOW)
# =========================
st.subheader("Pulso diario (comparativa DOW)")

df_prev = df[
    (df["fecha"].dt.year == hoy.year - 1) &
    (df["fecha"].dt.month == hoy.month)
].copy()

registros = []

for _, row in df_mes.iterrows():
    dow_eq = df_prev[df_prev["weekday"] == row["weekday"]]
    if dow_eq.empty:
        continue

    ref = dow_eq.iloc[0]
    if ref["ventas_total_eur"] <= 0:
        continue

    pct = (
        (row["ventas_total_eur"] - ref["ventas_total_eur"])
        / ref["ventas_total_eur"] * 100
    )

    registros.append({
        "fecha": row["fecha"].strftime("%a %d"),
        "variacion_pct": pct,
        "ventas": row["ventas_total_eur"]
    })

df_pulso = pd.DataFrame(registros)

if not df_pulso.empty:
    max_venta = df_pulso["ventas"].max()
    df_pulso["barra"] = df_pulso["ventas"] / max_venta * 100

    st.dataframe(
        df_pulso[["fecha", "variacion_pct", "barra"]]
        .rename(columns={
            "fecha": "Día",
            "variacion_pct": "% vs año anterior",
            "barra": "Volumen relativo"
        }),
        hide_index=True,
        use_container_width=True
    )

# =========================
# 2. ESTIMACIÓN DE CIERRE
# =========================
st.divider()
st.subheader("Estimación de cierre de mes")

st.metric(
    "Estimación cierre de mes",
    f"{estimacion_cierre:,.0f} €",
    help=f"Basado en {dias_operativos} días operativos · multiplicador 30"
)

st.caption(
    f"Ventas acumuladas (1 → {dias_operativos}): {ventas_acumuladas:,.0f} € · "
    f"Ritmo medio diario: {ritmo_diario:,.0f} €"
)

# =========================
# 3. EVOLUCIÓN MENSUAL DOW
# =========================
st.divider()
st.subheader("Evolución mensual ajustada a DOW")

ventas_prev = df_prev.head(len(df_mes))["ventas_total_eur"].sum()

if ventas_prev > 0:
    diff = ventas_acumuladas - ventas_prev
    pct = diff / ventas_prev * 100

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Este año", f"{ventas_acumuladas:,.0f} €")
    with c2:
        st.metric("Año anterior (DOW)", f"{ventas_prev:,.0f} €")

    st.caption(
        f"Diferencia: {diff:,.0f} € · Variación: {pct:+.1f} %"
    )

# =========================
# 4. RITMO MEDIO DIARIO
# =========================
st.divider()
st.subheader("Ritmo medio diario")

ritmo_prev = ventas_prev / dias_operativos if dias_operativos > 0 else 0

st.metric(
    "Ritmo medio diario",
    f"{ritmo_diario:,.0f} € / día",
    f"{(ritmo_diario - ritmo_prev) / ritmo_prev * 100:+.1f} %" if ritmo_prev > 0 else None
)

# =========================
# 5. PESO DEL AÑO POR CUATRIMESTRES
# =========================
st.divider()
st.subheader("Peso del año por cuatrimestres")

df_year = df[df["year"] == hoy.year].copy()
df_year["cuatrimestre"] = pd.cut(
    df_year["fecha"].dt.month,
    bins=[0, 4, 8, 12],
    labels=["Ene–Abr", "May–Ago", "Sep–Dic"]
)

tabla_cuatri = (
    df_year.groupby("cuatrimestre")["ventas_total_eur"]
    .sum()
    .reset_index()
)

total_anual = tabla_cuatri["ventas_total_eur"].sum()
tabla_cuatri["Peso %"] = (
    tabla_cuatri["ventas_total_eur"] / total_anual * 100
).round(1)

st.table(
    tabla_cuatri.rename(columns={
        "cuatrimestre": "Cuatrimestre",
        "ventas_total_eur": "Ventas (€)"
    })
)

# =========================
# NOTA DE SISTEMA
# =========================
st.caption(
    "Comparables estructurales basados en calendario, DOW y ritmo operativo."
)
