import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")

DATA_FILE = Path("ventas.csv")

# =========================
# MAPEO DÍAS SEMANA (ROBUSTO)
# =========================
DOW_MAP = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=[
        "fecha",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
    ])

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input(
        "Fecha",
        value=date.today(),
        format="DD/MM/YYYY"
    )

    st.caption("Desglose por franja")
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f")
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f")
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f")

    guardar = st.form_submit_button("Guardar venta")

if guardar:
    total = vm + vt + vn

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Venta guardada correctamente")

st.divider()

# =========================
# VISTA MENSUAL
# =========================
st.subheader("Vista mensual")

if df.empty:
    st.info("No hay datos todavía.")
else:
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day

    # Día de la semana SIN locale
    df["dow_en"] = df["fecha"].dt.day_name()
    df["dow"] = df["dow_en"].map(DOW_MAP)

    c1, c2 = st.columns(2)
    with c1:
        años = sorted(df["año"].unique())
        año_sel = st.selectbox("Año", años, index=len(años) - 1)
    with c2:
        mes_sel = st.selectbox(
            "Mes",
            list(range(1, 13)),
            format_func=lambda m: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][m - 1]
        )

    mensual = (
        df[(df["año"] == año_sel) & (df["mes"] == mes_sel)]
        .sort_values("fecha")
    )

    st.dataframe(
        mensual[[
            "fecha",
            "dia",
            "dow",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur"
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================
    # RESUMEN MENSUAL · ACUMULADO VS MES ANTERIOR
    # =========================
    st.subheader("Resumen mensual · Acumulado vs mes anterior")

    total_actual = mensual["ventas_total_eur"].sum()
    dias_actual = mensual[mensual["ventas_total_eur"] > 0].shape[0]
    prom_actual = total_actual / dias_actual if dias_actual > 0 else 0

    if mes_sel == 1:
        mes_ant = 12
        año_ant = año_sel - 1
    else:
        mes_ant = mes_sel - 1
        año_ant = año_sel

    anterior = df[(df["año"] == año_ant) & (df["mes"] == mes_ant)]
    total_ant = anterior["ventas_total_eur"].sum()
    dias_ant = anterior[anterior["ventas_total_eur"] > 0].shape[0]
    prom_ant = total_ant / dias_ant if dias_ant > 0 else 0

    diff_eur = total_actual - total_ant
    diff_dias = dias_actual - dias_ant
    diff_pct = ((total_actual / total_ant) - 1) * 100 if total_ant > 0 else 0

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Mes actual**")
        st.metric("Total acumulado (€)", f"{total_actual:,.2f}")
        st.metric("Días con venta", dias_actual)
        st.metric("Promedio diario (€)", f"{prom_actual:,.2f}")

    with c2:
        st.markdown("**Mes anterior**")
        st.metric("Total mes (€)", f"{total_ant:,.2f}")
        st.metric("Días con venta", dias_ant)
        st.metric("Promedio diario (€)", f"{prom_ant:,.2f}")

    with c3:
        st.markdown("**Diferencia vs mes anterior**")
        st.metric("€ vs mes anterior", f"{diff_eur:+,.2f}")
        st.metric("Diferencia días", f"{diff_dias:+d}")
        st.metric("% variación", f"{diff_pct:+.1f}%")
