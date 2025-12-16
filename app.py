import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")

st.title("OYKEN · Control Operativo")
st.markdown("**Entra en Oyken. En 30 segundos entiendes mejor tu negocio.**")
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

COLUMNAS = [
    "fecha",
    "ventas_manana_eur",
    "ventas_tarde_eur",
    "ventas_noche_eur",
    "ventas_total_eur",
    "comensales_manana",
    "comensales_tarde",
    "comensales_noche",
    "tickets_manana",
    "tickets_tarde",
    "tickets_noche",
    "observaciones"
]

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = 0 if col != "observaciones" else ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):

    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    st.markdown("### Mañana")
    vm = st.number_input("Ventas mañana (€)", min_value=0.0, step=10.0)
    cm = st.number_input("Comensales mañana", min_value=0, step=1)
    tm = st.number_input("Tickets mañana", min_value=0, step=1)

    st.markdown("### Tarde")
    vt = st.number_input("Ventas tarde (€)", min_value=0.0, step=10.0)
    ct = st.number_input("Comensales tarde", min_value=0, step=1)
    tt = st.number_input("Tickets tarde", min_value=0, step=1)

    st.markdown("### Noche")
    vn = st.number_input("Ventas noche (€)", min_value=0.0, step=10.0)
    cn = st.number_input("Comensales noche", min_value=0, step=1)
    tn = st.number_input("Tickets noche", min_value=0, step=1)

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Clima, eventos, incidencias, promociones, obras, festivos…",
        height=100
    )

    guardar = st.form_submit_button("Guardar venta")

if guardar:
    total = vm + vt + vn

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total,
        "comensales_manana": cm,
        "comensales_tarde": ct,
        "comensales_noche": cn,
        "tickets_manana": tm,
        "tickets_tarde": tt,
        "tickets_noche": tn,
        "observaciones": observaciones.strip()
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Registro guardado correctamente")
    st.rerun()

# =========================
# SI NO HAY DATOS
# =========================
if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN
# =========================
df = df.sort_values("fecha")
df["año"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia"] = df["fecha"].dt.day
df["dow"] = df["fecha"].dt.weekday.map(DOW_ES)

# =========================
# BLOQUE HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

venta_hoy = df[df["fecha"] == fecha_hoy]

if venta_hoy.empty:
    vm_h = vt_h = vn_h = total_h = 0.0
else:
    fila = venta_hoy.iloc[0]
    vm_h = fila["ventas_manana_eur"]
    vt_h = fila["ventas_tarde_eur"]
    vn_h = fila["ventas_noche_eur"]
    total_h = fila["ventas_total_eur"]

# --- DOW año anterior ---
fecha_obj = fecha_hoy.replace(year=fecha_hoy.year - 1)

cand = df[
    (df["año"] == fecha_obj.year) &
    (df["fecha"].dt.weekday == fecha_hoy.weekday())
]

if cand.empty:
    fecha_a_txt = "Sin histórico comparable"
    vm_a = vt_a = vn_a = total_a = 0.0
else:
    cand = cand.copy()
    cand["dist"] = (cand["fecha"] - fecha_obj).abs()
    comp = cand.sort_values("dist").iloc[0]

    fecha_a_txt = f"{DOW_ES[comp['fecha'].weekday()]} · {comp['fecha'].strftime('%d/%m/%Y')}"
    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

def diff_and_pct(actual, base):
    diff = actual - base
    pct = (diff / base * 100) if base > 0 else 0
    return diff, pct

def color(v):
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
    st.write(f"Mañana: {vm_h:,.2f} €")
    st.write(f"Tarde: {vt_h:,.2f} €")
    st.write(f"Noche: {vn_h:,.2f} €")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")

with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)
    st.write(f"Mañana: {vm_a:,.2f} €")
    st.write(f"Tarde: {vt_a:,.2f} €")
    st.write(f"Noche: {vn_a:,.2f} €")
    st.markdown(f"### TOTAL DOW\n{total_a:,.2f} €")

with c3:
    st.markdown("**VARIACIÓN**")
    st.markdown(
        f"<span style='color:{color(d_tot)}'>"
        f"{d_tot:+,.2f} € ({p_tot:+.1f}%)"
        f"</span>",
        unsafe_allow_html=True
    )

# =========================
# BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[(df["mes"] == fecha_hoy.month) & (df["año"] == fecha_hoy.year)].copy()
df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️" if str(r["observaciones"]).strip() else r["fecha_display"],
    axis=1
)

st.dataframe(
    df_mes[[
        "fecha_display",
        "dow",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
)
