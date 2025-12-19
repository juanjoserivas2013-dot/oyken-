import streamlit as st
import pandas as pd
from pathlib import Path

# ===============================
# CONFIGURACIÓN 
# ===============================

st.title("OIKEN · Tendencias")
st.caption("Dirección, consistencia y estructura del negocio")

DATA_FILE = Path("ventas.csv")

# ===============================
# CARGA DE DATOS
# ===============================

if not DATA_FILE.exists():
    st.error("No se encuentra el archivo ventas.csv")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

df["dow"] = df["fecha"].dt.dayofweek
df["week"] = df["fecha"].dt.isocalendar().week
df["year"] = df["fecha"].dt.year

df["ventas_total"] = (
    df["ventas_manana_eur"]
    + df["ventas_tarde_eur"]
    + df["ventas_noche_eur"]
)

# ===============================
# BLOQUE 1 · DIRECCIÓN DEL NEGOCIO
# ===============================

st.subheader("Dirección del negocio")

media_7d = df.tail(7)["ventas_total"].mean()

prev_7d = df.iloc[-14:-7]["ventas_total"].mean()
var_7d = ((media_7d - prev_7d) / prev_7d * 100) if prev_7d > 0 else 0

col1, col2 = st.columns([1, 3])

with col1:
    st.metric(
        label="Media móvil 7 días",
        value=f"{media_7d:,.0f} €",
        delta=f"{var_7d:+.1f} %",
    )

with col2:
    trend_df = df.set_index("fecha")["ventas_total"].rolling(7).mean()
    st.line_chart(trend_df)

st.divider()

# ===============================
# BLOQUE 2 · CONSISTENCIA DEL RESULTADO
# ===============================

st.subheader("Consistencia del resultado")

weekly = df.groupby(["year", "week"])["ventas_total"].sum().reset_index()
cv = weekly["ventas_total"].std() / weekly["ventas_total"].mean() * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Coeficiente de variación semanal", f"{cv:.1f} %")

with col2:
    delta_week = (
        (weekly.iloc[-1]["ventas_total"] - weekly.iloc[-2]["ventas_total"])
        / weekly.iloc[-2]["ventas_total"] * 100
        if len(weekly) > 1
        else 0
    )
    st.metric("Variación semana vs semana", f"{delta_week:+.1f} %")

with col3:
    ticket = df["ventas_total"].sum() / df["tickets_total"].sum()
    st.metric("Ticket medio tendencial", f"{ticket:.2f} €")

st.divider()

# ===============================
# BLOQUE 3 · DÍAS FUERTES VS DÉBILES
# ===============================

st.subheader("Días fuertes vs días débiles")

dow_map = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

dow_stats = (
    df.groupby("dow")["ventas_total"]
    .mean()
    .reset_index()
    .assign(dia=lambda x: x["dow"].map(dow_map))
    .sort_values("ventas_total", ascending=False)
)

fuerte = dow_stats.iloc[0]
debil = dow_stats.iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Día más fuerte",
        fuerte["dia"],
        f"{fuerte['ventas_total']:.0f} €"
    )

with col2:
    st.metric(
        "Día más débil",
        debil["dia"],
        f"{debil['ventas_total']:.0f} €"
    )

st.bar_chart(
    dow_stats.set_index("dia")["ventas_total"],
    height=260
)

st.divider()

# ===============================
# BLOQUE 4 · ESTRUCTURA DE LA TENDENCIA
# ===============================

st.subheader("Estructura de la tendencia")

# Pendiente simple últimos 14 días
last_14 = df.tail(14)
x = range(len(last_14))
y = last_14["ventas_total"]

slope = pd.Series(y).diff().mean()

if slope > 5:
    estructura = "Tendencia estructuralmente creciente"
elif slope < -5:
    estructura = "Tendencia estructuralmente decreciente"
else:
    estructura = "Tendencia estable"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Pendiente media diaria", f"{slope:+.1f} €")

with col2:
    st.metric("Dirección", estructura)

with col3:
    peso_findesemana = (
        df[df["dow"] >= 4]["ventas_total"].sum()
        / df["ventas_total"].sum() * 100
    )
    st.metric("Peso viernes–domingo", f"{peso_findesemana:.1f} %")

# ===============================
# NOTA FINAL
# ===============================

st.caption(
    "Este bloque describe la dirección y estabilidad del negocio. "
    "No interpreta causas ni recomienda acciones."
)
