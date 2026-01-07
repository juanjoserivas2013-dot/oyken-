import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OIKEN · Tendencias", layout="centered")

st.title("OIKEN · Tendencias")
st.caption("Estructura, estabilidad y robustez del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"]).sort_values("fecha")
hoy = df["fecha"].max()

# =========================
# UTILIDADES
# =========================
def rango_fechas(df):
    return f"{df['fecha'].min().strftime('%d/%m')} – {df['fecha'].max().strftime('%d/%m')}"

def cv_turno_seguro(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm)

def render_bloque(titulo, metrica_label, metrica_valor, periodo, texto):
    st.subheader(titulo.upper())
    st.markdown(f"**{metrica_label.upper()}**")
    st.markdown(f"### {metrica_valor}")
    st.caption(f"Periodo analizado: {periodo}")
    st.markdown(texto)
    st.divider()

def render_bloque_no_disponible(titulo, motivo):
    st.subheader(titulo.upper())
    st.caption("Bloque no disponible")
    st.markdown(motivo)
    st.divider()

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
# VENTANAS TEMPORALES
# =========================
lunes_semana = hoy - pd.Timedelta(days=hoy.weekday())
df_semana = df[(df["fecha"] >= lunes_semana) & (df["fecha"] <= hoy)]

df_7  = df.tail(7)
df_10 = df.tail(10)
df_15 = df.tail(15)

# =========================
# 1 · DIRECCIÓN DEL NEGOCIO
# =========================
if len(df_semana) >= 5:
    media_actual = df_semana["ventas_total_eur"].mean()
    prev = df[df["fecha"] < lunes_semana].tail(len(df_semana))

    if len(prev) >= len(df_semana) and prev["ventas_total_eur"].mean() > 0:
        variacion = (
            (media_actual - prev["ventas_total_eur"].mean())
            / prev["ventas_total_eur"].mean()
            * 100
        )
    else:
        variacion = 0

    texto = f"""
Este bloque analiza la dirección inmediata del sistema comercial,
evaluando la evolución del ritmo medio de generación de ingresos
en el corto plazo.

La media diaria observada se sitúa en {media_actual:,.0f} €, con una
variación del {variacion:+.1f} %, lo que refleja un cambio efectivo
en el comportamiento reciente del sistema.
"""

    render_bloque(
        "Dirección del negocio",
        "Media diaria",
        f"{media_actual:,.0f} €",
        rango_fechas(df_semana),
        texto
    )
else:
    render_bloque_no_disponible(
        "Dirección del negocio",
        "Este bloque analiza la dirección del negocio a partir de la semana en curso. "
        "Actualmente no hay suficientes días operados dentro de la semana para una lectura estructural fiable."
    )

# =========================
# 2 · CONSISTENCIA DEL RESULTADO
# =========================
if len(df_7) >= 7 and df_7["ventas_total_eur"].mean() > 0:
    cv_ventas = (
        df_7["ventas_total_eur"].std()
        / df_7["ventas_total_eur"].mean()
        * 100
    )

    texto = f"""
Este bloque evalúa la consistencia del resultado diario, entendida
como la capacidad del sistema para generar ventas de forma regular
y predecible.

El coeficiente de variación observado se sitúa en {cv_ventas:.1f} %,
describiendo el nivel de estabilidad interna del sistema operativo.
"""

    render_bloque(
        "Consistencia del resultado",
        "Coeficiente de variación",
        f"{cv_ventas:.1f} %",
        rango_fechas(df_7),
        texto
    )
else:
    render_bloque_no_disponible(
        "Consistencia del resultado",
        "Este bloque requiere un mínimo de 7 días consecutivos de operación para evaluar estabilidad y consistencia. "
        "La base actual aún no alcanza ese umbral."
    )

# =========================
# 3 · DÍAS FUERTES Y DÉBILES
# =========================
if len(df_15) >= 15:
    df_15 = df_15.copy()
    df_15["weekday"] = df_15["fecha"].dt.day_name()

    media_dia = df_15.groupby("weekday")["ventas_total_eur"].mean()
    dia_fuerte = media_dia.idxmax()
    dia_debil = media_dia.idxmin()

    texto = f"""
El análisis por día de la semana muestra una estructura asimétrica
del rendimiento.

El día más fuerte es {dia_fuerte} y el más débil {dia_debil}, lo que
condiciona la distribución temporal del esfuerzo y del retorno
operativo.
"""

    render_bloque(
        "Días fuertes y días débiles",
        "Semana",
        f"{dia_fuerte} / {dia_debil}",
        rango_fechas(df_15),
        texto
    )
else:
    render_bloque_no_disponible(
        "Días fuertes y días débiles",
        "Este bloque identifica patrones recurrentes por día de la semana. "
        "El análisis requiere al menos 15 días operados para evitar conclusiones espurias."
    )

# =========================
# 4 · ESTABILIDAD DEL TICKET MEDIO
# =========================
if len(df_7) >= 7 and df_7["ticket_medio"].mean() > 0:
    cv_ticket = (
        df_7["ticket_medio"].std()
        / df_7["ticket_medio"].mean()
        * 100
    )

    texto = f"""
Este bloque evalúa la regularidad del ingreso por operación,
integrando el comportamiento del cliente y la ejecución comercial.

El coeficiente de variación del ticket medio se sitúa en {cv_ticket:.1f} %,
reflejando el grado de estabilidad del comportamiento de venta.
"""

    render_bloque(
        "Estabilidad del ticket medio",
        "Coeficiente de variación",
        f"{cv_ticket:.1f} %",
        rango_fechas(df_7),
        texto
    )
else:
    render_bloque_no_disponible(
        "Estabilidad del ticket medio",
        "Este bloque requiere al menos 7 días de operación para evaluar la regularidad del ingreso por operación."
    )

# =========================
# 5 · VOLATILIDAD POR TURNOS
# =========================
if len(df_7) >= 7:
    tabla_turnos = [
        {"Turno": "Mañana", "CV": cv_turno_seguro(df_7["ventas_manana_eur"], df_7["tickets_manana"])},
        {"Turno": "Tarde",  "CV": cv_turno_seguro(df_7["ventas_tarde_eur"], df_7["tickets_tarde"])},
        {"Turno": "Noche",  "CV": cv_turno_seguro(df_7["ventas_noche_eur"], df_7["tickets_noche"])},
    ]

    turno_mas_volatil = max(tabla_turnos, key=lambda x: x["CV"])["Turno"]

    texto = f"""
El análisis por franjas horarias muestra una ejecución no homogénea
entre turnos.

El turno con mayor volatilidad es {turno_mas_volatil}, lo que introduce
fricción en la previsibilidad del resultado diario.
"""

    render_bloque(
        "Volatilidad por turnos",
        "Turno más volátil",
        turno_mas_volatil,
        rango_fechas(df_7),
        texto
    )
else:
    render_bloque_no_disponible(
        "Volatilidad por turnos",
        "Este bloque evalúa la estabilidad por franja horaria y requiere un mínimo de 7 días operados."
    )

# =========================
# 6 · DEPENDENCIA DE PICOS
# =========================
if len(df_10) >= 10:
    media = df_10["ventas_total_eur"].mean()
    desv = df_10["ventas_total_eur"].std()

    if media > 0 and desv > 0:
        pct_picos = (
            df_10[df_10["ventas_total_eur"] > media + 2 * desv]["ventas_total_eur"].sum()
            / df_10["ventas_total_eur"].sum()
            * 100
        )
    else:
        pct_picos = 0

    texto = f"""
Este bloque evalúa la dependencia del negocio respecto a días de
ventas excepcionalmente altas.

Los picos concentran el {pct_picos:.1f} % del volumen total, lo que
describe el grado de robustez estructural del sistema.
"""

    render_bloque(
        "Dependencia de picos",
        "Ventas en días excepcionales",
        f"{pct_picos:.1f} %",
        rango_fechas(df_10),
        texto
    )
else:
    render_bloque_no_disponible(
        "Dependencia de picos",
        "Este bloque analiza concentración de ventas excepcionales y requiere al menos 10 días de operación."
    )

# =========================
# NOTA FINAL
# =========================
st.caption(
    "Este módulo analiza tendencias estructurales del negocio. "
    "La lectura se prioriza sobre criterios de calidad operativa."
)
