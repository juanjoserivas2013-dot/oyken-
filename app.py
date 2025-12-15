import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")
st.title("OYKEN · Control Operativo")
st.caption("Sistema automático basado en criterio operativo")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

MESES_ES = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
]

# =========================
# CARGA DE DATOS (ÚNICA FUENTE DE VERDAD)
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
# REGISTRO DIARIO (ÚNICA ACCIÓN HUMANA)
# =========================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input(
        "Fecha",
        value=date.today(),
        format="DD/MM/YYYY"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0)
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0)
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0)

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
    st.rerun()

# =========================
# SI NO HAY DATOS, PARAMOS
# =========================
if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN AUTOMÁTICA
# =========================
df = df.sort_values("fecha")
df["año"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia"] = df["fecha"].dt.day
df["dow"] = df["fecha"].dt.weekday.map(DOW_ES)

# =========================
# BLOQUE 1 — HOY (DEFINITIVO)
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

venta_hoy = df[df["fecha"] == fecha_hoy]

if venta_hoy.empty:
    vm_h = vt_h = vn_h = total_h = 0.0
else:
    fila_h = venta_hoy.iloc[0]
    vm_h = fila_h["ventas_manana_eur"]
    vt_h = fila_h["ventas_tarde_eur"]
    vn_h = fila_h["ventas_noche_eur"]
    total_h = fila_h["ventas_total_eur"]

# --- Buscar DOW año anterior ---
fecha_obj = fecha_hoy.replace(year=fecha_hoy.year - 1)

candidatos = df[
    (df["año"] == fecha_obj.year) &
    (df["fecha"].dt.weekday == fecha_hoy.weekday())
]

if candidatos.empty:
    fecha_a_txt = "Sin histórico comparable"
    vm_a = vt_a = vn_a = total_a = 0.0
else:
    candidatos = candidatos.copy()
    candidatos["dist"] = (candidatos["fecha"] - fecha_obj).abs()
    comp = candidatos.sort_values("dist").iloc[0]

    fecha_a_txt = f"{DOW_ES[comp['fecha'].weekday()]} · {comp['fecha'].strftime('%d/%m/%Y')}"
    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

def diff_and_pct(actual, base):
    diff = actual - base
    pct = (diff / base * 100) if base > 0 else 0
    return diff, pct

def color_from_value(v):
    if v > 0:
        return "green"
    if v < 0:
        return "red"
    return "gray"

d_vm, p_vm = diff_and_pct(vm_h, vm_a)
d_vt, p_vt = diff_and_pct(vt_h, vt_a)
d_vn, p_vn = diff_and_pct(vn_h, vn_a)
d_tot, p_tot = diff_and_pct(total_h, total_a)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")
    st.write(f"Mañana: {vm_h:.2f} €")
    st.write(f"Tarde: {vt_h:.2f} €")
    st.write(f"Noche: {vn_h:.2f} €")
    st.markdown(f"### TOTAL HOY: {total_h:.2f} €")

with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)
    st.write(f"Mañana: {vm_a:.2f} €")
    st.write(f"Tarde: {vt_a:.2f} €")
    st.write(f"Noche: {vn_a:.2f} €")
    st.markdown(f"### TOTAL DOW: {total_a:.2f} €")

with c3:
    st.markdown("**Variación**")
    st.caption("Lectura orientativa basada en histórico disponible")

    st.markdown(
        f"Mañana: <span style='color:{color_from_value(d_vm)}'>{d_vm:+.2f} € ({p_vm:+.1f}%)</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Tarde: <span style='color:{color_from_value(d_vt)}'>{d_vt:+.2f} € ({p_vt:+.1f}%)</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Noche: <span style='color:{color_from_value(d_vn)}'>{d_vn:+.2f} € ({p_vn:+.1f}%)</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"### TOTAL: <span style='color:{color_from_value(d_tot)}'>{d_tot:+.2f} € ({p_tot:+.1f}%)</span>",
        unsafe_allow_html=True
    )

# =========================
# BLOQUE 2 — RESUMEN MENSUAL AUTOMÁTICO
# =========================
st.divider()
st.subheader("Resumen mensual automático")

mes_actual = fecha_hoy.month
año_actual = fecha_hoy.year

df_mes = df[(df["mes"] == mes_actual) & (df["año"] == año_actual)]

total_mes = df_mes["ventas_total_eur"].sum()
dias_mes = df_mes["ventas_total_eur"].gt(0).sum()
prom_mes = total_mes / dias_mes if dias_mes else 0

if mes_actual == 1:
    mes_ant = 12
    año_ant = año_actual - 1
else:
    mes_ant = mes_actual - 1
    año_ant = año_actual

df_ant = df[(df["mes"] == mes_ant) & (df["año"] == año_ant)]

total_ant = df_ant["ventas_total_eur"].sum()
dias_ant = df_ant["ventas_total_eur"].gt(0).sum()
prom_ant = total_ant / dias_ant if dias_ant else 0

dif_total = total_mes - total_ant
dif_dias = dias_mes - dias_ant
dif_pct = ((prom_mes / prom_ant) - 1) * 100 if prom_ant > 0 else 0

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"**Mes actual · {MESES_ES[mes_actual-1]} {año_actual}**")
    st.metric("Total acumulado (€)", f"{total_mes:,.2f}")
    st.metric("Días con venta", dias_mes)
    st.metric("Promedio diario (€)", f"{prom_mes:,.2f}")

with c2:
    st.markdown(f"**Mes anterior · {MESES_ES[mes_ant-1]} {año_ant}**")
    st.metric("Total mes (€)", f"{total_ant:,.2f}")
    st.metric("Días con venta", dias_ant)
    st.metric("Promedio diario (€)", f"{prom_ant:,.2f}")

with c3:
    st.markdown(f"**Diferencia · {MESES_ES[mes_actual-1]} vs {MESES_ES[mes_ant-1]}**")
    st.metric("€ vs mes anterior", f"{dif_total:+,.2f}")
    st.metric("Δ días", f"{dif_dias:+d}")
    st.metric("Δ promedio", f"{dif_pct:+.1f} %")

# =========================
# BLOQUE 3 — BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

st.dataframe(
    df_mes[[
        "fecha","dow",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur"
    ]],
    hide_index=True,
    use_container_width=True
)
