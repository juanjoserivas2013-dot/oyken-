import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")
st.caption("Control operativo diario · Visibilidad · Contexto")

DATA_FILE = Path("ventas.csv")

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
        "Fecha (dd/mm/aaaa)",
        value=date.today(),
        min_value=date(2015, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY"
    )

    st.caption("Ventas por franja (€)")
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana", min_value=0.0, step=10.0, format="%.2f")
    with c2:
        vt = st.number_input("Tarde", min_value=0.0, step=10.0, format="%.2f")
    with c3:
        vn = st.number_input("Noche", min_value=0.0, step=10.0, format="%.2f")

    total = vm + vt + vn
    st.metric("Total del día (€)", f"{total:,.2f}")

    guardar = st.form_submit_button("Guardar")

if guardar:
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df = df.sort_values("fecha", ascending=False)
    df.to_csv(DATA_FILE, index=False)

    st.success(f"Venta guardada ({fecha.strftime('%d/%m/%Y')})")
    st.rerun()

st.divider()

# =========================
# LISTADO DE VENTAS (HISTÓRICO VISIBLE)
# =========================
st.subheader("Listado de ventas")

if df.empty:
    st.info("Aún no hay ventas registradas.")
else:
    df_listado = df.copy()
    df_listado["Fecha"] = df_listado["fecha"].dt.strftime("%d/%m/%Y")
    df_listado["Día"] = df_listado["fecha"].dt.day_name()

    st.dataframe(
        df_listado[[
            "Fecha",
            "Día",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur"
        ]].rename(columns={
            "ventas_manana_eur": "Mañana (€)",
            "ventas_tarde_eur": "Tarde (€)",
            "ventas_noche_eur": "Noche (€)",
            "ventas_total_eur": "Total (€)"
        }),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# =========================
# COMPARABLE AUTOMÁTICO POR DOW
# =========================
st.subheader("Lectura automática · Comparativa por día de la semana")

if df.empty:
    st.info("Aún no hay datos suficientes.")
else:
    fecha_actual = df["fecha"].max()
    dow_actual = fecha_actual.weekday()

    actual = df[df["fecha"] == fecha_actual].iloc[0]

    fecha_objetivo = fecha_actual.replace(year=fecha_actual.year - 1)

    candidatos = df[
        (df["fecha"].dt.year == fecha_objetivo.year) &
        (df["fecha"].dt.weekday == dow_actual)
    ].copy()

    if not candidatos.empty:
        candidatos["dist"] = (candidatos["fecha"] - fecha_objetivo).abs()
        comparable = candidatos.sort_values("dist").iloc[0]
    else:
        comparable = None

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Día actual**")
        st.write(f"Fecha: {fecha_actual.strftime('%d/%m/%Y')}")
        st.write(f"Mañana: {actual['ventas_manana_eur']:.2f} €")
        st.write(f"Tarde: {actual['ventas_tarde_eur']:.2f} €")
        st.write(f"Noche: {actual['ventas_noche_eur']:.2f} €")
        st.write(f"**Total: {actual['ventas_total_eur']:.2f} €**")

    with c2:
        st.markdown("**Mismo día de la semana · Año anterior**")
        if comparable is None:
            st.warning("No existe histórico comparable.")
        else:
            st.write(f"Fecha: {comparable['fecha'].strftime('%d/%m/%Y')}")
            st.write(f"Mañana: {comparable['ventas_manana_eur']:.2f} €")
            st.write(f"Tarde: {comparable['ventas_tarde_eur']:.2f} €")
            st.write(f"Noche: {comparable['ventas_noche_eur']:.2f} €")
            st.write(f"**Total: {comparable['ventas_total_eur']:.2f} €**")

    with c3:
        st.markdown("**Variación**")
        if comparable is None:
            st.info("Sin base histórica suficiente.")
        else:
            dif = actual["ventas_total_eur"] - comparable["ventas_total_eur"]
            pct = (dif / comparable["ventas_total_eur"] * 100) if comparable["ventas_total_eur"] > 0 else 0

            st.metric("Total", f"{dif:+.2f} €", f"{pct:+.1f} %")

            for franja in ["manana", "tarde", "noche"]:
                act = actual[f"ventas_{franja}_eur"]
                prev = comparable[f"ventas_{franja}_eur"]
                d = act - prev
                p = (d / prev * 100) if prev > 0 else 0
                st.write(f"{franja.capitalize()}: {d:+.2f} € ({p:+.1f} %)")
