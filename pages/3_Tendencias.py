import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

# =========================
# CABECERA
# =========================
st.title("OIKEN · Tendencias")
st.caption("Estructura, estabilidad y robustez del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

hoy = pd.to_datetime(date.today())

# =========================
# VARIABLES BASE
# =========================
df["tickets_total"] = (
    df["tickets_manana"] +
    df["tickets_tarde"] +
    df["tickets_noche"]
)

df["ticket_medio"] = np.where(
    df["tickets_total"] > 0,
    df["ventas_total_eur"] / df["tickets_total"],
    np.nan
)

# =========================
# SEMANA ISO EN CURSO (LUNES → HOY)
# =========================
lunes_semana = hoy - pd.Timedelta(days=hoy.weekday())
df_semana = df[(df["fecha"] >= lunes_semana) & (df["fecha"] <= hoy)]

# =========================
# VENTANAS AMPLIADAS
# =========================
df_7 = df[df["fecha"] <= hoy].tail(7)
df_10 = df[df["fecha"] <= hoy].tail(10)
df_14 = df[df["fecha"] <= hoy].tail(14)
df_15 = df[df["fecha"] <= hoy].tail(15)

# =========================
# 1. DIRECCIÓN DEL NEGOCIO
# =========================
st.subheader("Dirección del negocio")

if len(df_semana) >= 5:
    mm_actual = df_semana["ventas_total_eur"].mean()
    prev = df[(df["fecha"] < lunes_semana)].tail(len(df_semana))

    if len(prev) >= len(df_semana):
        mm_prev = prev["ventas_total_eur"].mean()
        var_mm = ((mm_actual - mm_prev) / mm_prev * 100) if mm_prev > 0 else 0
    else:
        var_mm = 0

    st.metric(
        "Media diaria semana en curso",
        f"{mm_actual:,.0f} €",
        f"{var_mm:+.1f} %"
    )
else:
    st.info("Semana en curso aún sin datos suficientes.")

st.divider()

# =========================
# 2. CONSISTENCIA DEL RESULTADO
# =========================
st.subheader("Consistencia del resultado")

if len(df_7) >= 7:
    cv_ventas = df_7["ventas_total_eur"].std() / df_7["ventas_total_eur"].mean()
    st.metric(
        "Coeficiente de variación de ventas (7 días)",
        f"{cv_ventas*100:.1f} %"
    )
else:
    cv_ventas = np.nan
    st.info("Consistencia requiere al menos 7 días.")

st.divider()

# =========================
# 3. DÍAS FUERTES Y DÉBILES
# =========================
st.subheader("Días fuertes y días débiles")

if len(df_15) >= 15:
    df_15["weekday"] = df_15["fecha"].dt.day_name()
    media_dia = df_15.groupby("weekday")["ventas_total_eur"].mean()
    media_global = df_15["ventas_total_eur"].mean()

    dia_fuerte = media_dia.idxmax()
    dia_debil = media_dia.idxmin()

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            "Día más fuerte",
            dia_fuerte,
            f"{(media_dia.max()/media_global - 1)*100:+.0f} %"
        )
    with c2:
        st.metric(
            "Día más débil",
            dia_debil,
            f"{(media_dia.min()/media_global - 1)*100:+.0f} %"
        )
else:
    st.info("Se requieren al menos 15 días para identificar días fuertes y débiles.")

st.divider()

# =========================
# 4. ESTABILIDAD DEL TICKET MEDIO
# =========================
st.subheader("Estabilidad del ticket medio")

if len(df_7) >= 7:
    cv_ticket = df_7["ticket_medio"].std() / df_7["ticket_medio"].mean()
    st.metric(
        "Coeficiente de variación del ticket medio (7 días)",
        f"{cv_ticket*100:.1f} %"
    )
else:
    cv_ticket = np.nan
    st.info("Estabilidad del ticket requiere al menos 7 días.")

st.divider()

# =========================
# 5. VOLATILIDAD POR TURNOS
# =========================
st.subheader("Volatilidad por turnos")

def cv_turno(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm) / np.nanmean(tm)

if len(df_7) >= 7:
    tabla_turnos = pd.DataFrame({
        "Turno": ["Mañana", "Tarde", "Noche"],
        "CV Ticket (%)": [
            round(cv_turno(df_7["ventas_manana_eur"], df_7["tickets_manana"]) * 100, 1),
            round(cv_turno(df_7["ventas_tarde_eur"], df_7["tickets_tarde"]) * 100, 1),
            round(cv_turno(df_7["ventas_noche_eur"], df_7["tickets_noche"]) * 100, 1)
        ]
    })
    st.table(tabla_turnos)
else:
    tabla_turnos = None
    st.info("Volatilidad por turnos requiere al menos 7 días.")

st.divider()

# =========================
# 6. DEPENDENCIA DE PICOS
# =========================
st.subheader("Dependencia de picos")

if len(df_10) >= 10:
    media = df_10["ventas_total_eur"].mean()
    desv = df_10["ventas_total_eur"].std()

    picos = df_10[df_10["ventas_total_eur"] > media + 2 * desv]
    pct_picos = (
        picos["ventas_total_eur"].sum()
        / df_10["ventas_total_eur"].sum()
        * 100
    )

    st.metric(
        "Ventas concentradas en días excepcionalmente altos",
        f"{pct_picos:.1f} %"
    )
else:
    pct_picos = np.nan
    st.info("Dependencia de picos requiere al menos 10 días.")

st.divider()

# =========================
# 7. SEÑALES DE CALIDAD OPERATIVA
# =========================
st.subheader("Señales de calidad operativa")

if not np.isnan(cv_ticket):
    if cv_ticket > 0.25:
        st.write("⚠️ Variabilidad elevada en el ticket medio")
    else:
        st.write("🟢 Ticket medio estable")

if not np.isnan(pct_picos):
    if pct_picos > 45:
        st.write("🔴 Alta dependencia de picos de venta")
    elif pct_picos > 30:
        st.write("⚠️ Dependencia moderada de picos")
    else:
        st.write("🟢 Dependencia de picos baja")

if tabla_turnos is not None:
    tarde_cv = tabla_turnos.loc[
        tabla_turnos["Turno"] == "Tarde", "CV Ticket (%)"
    ].values[0]

    if tarde_cv > 30:
        st.write("⚠️ Variabilidad elevada en turno tarde")
    else:
        st.write("🟢 Turnos bajo control")

# =========================
# NOTA DE SISTEMA
# =========================
st.caption(
    "Este bloque analiza tendencias estructurales. "
    "Las decisiones se priorizan en Calidad Operativa."
)
