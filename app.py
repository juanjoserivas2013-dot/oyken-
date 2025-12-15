import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN GENERAL
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

COLUMNAS_BASE = [
    "fecha",
    "ventas_manana_eur",
    "ventas_tarde_eur",
    "ventas_noche_eur",
    "ventas_total_eur",
    "observaciones"
]

# =========================
# CARGA DE DATOS (FUENTE ÚNICA)
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS_BASE)

# Blindaje por CSV antiguos
for col in COLUMNAS_BASE:
    if col not in df.columns:
        df[col] = ""

df["observaciones"] = df["observaciones"].fillna("")

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

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Climatología, eventos, incidencias, promociones, obras, festivos…",
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
        "observaciones": observaciones.strip()
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Venta y observaciones guardadas correctamente")
    st.rerun()

# =========================
# SI NO HAY DATOS
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
# BLOQUE 1 — HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

# --- Venta HOY ---
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

# --- Funciones ---
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

# --- Diferencias ---
d_vm, p_vm = diff_and_pct(vm_h, vm_a)
d_vt, p_vt = diff_and_pct(vt_h, vt_a)
d_vn, p_vn = diff_and_pct(vn_h, vn_a)
d_tot, p_tot = diff_and_pct(total_h, total_a)

# =========================
# DISPOSICIÓN VISUAL (3 COLUMNAS)
# =========================
c1, c2, c3 = st.columns(3)

# --- HOY ---
with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")
    st.write(f"Mañana: {vm_h:.2f} €")
    st.write(f"Tarde: {vt_h:.2f} €")
    st.write(f"Noche: {vn_h:.2f} €")
    st.markdown(f"### TOTAL HOY: {total_h:.2f} €")

# --- DOW ---
with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)
    st.write(f"Mañana: {vm_a:.2f} €")
    st.write(f"Tarde: {vt_a:.2f} €")
    st.write(f"Noche: {vn_a:.2f} €")
    st.markdown(f"### TOTAL DOW: {total_a:.2f} €")

# --- VARIACIÓN ---
with c3:
    st.markdown("**Variación**")
    st.caption("Vs. DOW año anterior")

    st.markdown(
        f"Mañana: <span style='color:{color(d_vm)}'>{d_vm:+.2f} € ({p_vm:+.1f}%)</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Tarde: <span style='color:{color(d_vt)}'>{d_vt:+.2f} € ({p_vt:+.1f}%)</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Noche: <span style='color:{color(d_vn)}'>{d_vn:+.2f} € ({p_vn:+.1f}%)</span>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        f"### TOTAL: <span style='color:{color(d_tot)}'>{d_tot:+.2f} € ({p_tot:+.1f}%)</span>",
        unsafe_allow_html=True
    )

# =========================
# OBSERVACIONES DEL DÍA (LECTURA)
# =========================
st.divider()
st.subheader("OBSERVACIONES OPERATIVAS — BITÁCORA DEL DÍA")

st.text_area(
    "Observaciones del día",
    value=obs_hoy if obs_hoy else "",
    height=120
)

# =========================
# BLOQUE 3 — BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

# Filtrar mes y año actual
df_mes = df[
    (df["mes"] == fecha_hoy.month) &
    (df["año"] == fecha_hoy.year)
].copy()

# Formato visual de fecha + icono 👁️ si hay observaciones
df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️"
    if str(r["observaciones"]).strip()
    else r["fecha_display"],
    axis=1
)

# Mostrar tabla
st.dataframe(
    df_mes[[
        "fecha_display",
        "dow",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
        "observaciones"
    ]].rename(columns={
        "fecha_display": "fecha"
    }),
    hide_index=True,
    use_container_width=True
)
