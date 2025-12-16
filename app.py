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

COLUMNAS = [
    "fecha",
    "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur", "ventas_total_eur",
    "comensales_manana", "comensales_tarde", "comensales_noche",
    "tickets_manana", "tickets_tarde", "tickets_noche",
    "observaciones"
]

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for c in COLUMNAS:
    if c not in df.columns:
        df[c] = 0 if c != "observaciones" else ""

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

    observaciones = st.text_area("Observaciones del día", height=80)
    guardar = st.form_submit_button("Guardar venta")

if guardar:
    total = vm + vt + vn
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm, "ventas_tarde_eur": vt, "ventas_noche_eur": vn,
        "ventas_total_eur": total,
        "comensales_manana": cm, "comensales_tarde": ct, "comensales_noche": cn,
        "tickets_manana": tm, "tickets_tarde": tt, "tickets_noche": tn,
        "observaciones": observaciones.strip()
    }])
    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)
    st.success("Venta guardada")
    st.rerun()

if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN
# =========================
df = df.sort_values("fecha")
df["año"] = df["fecha"].dt.year
df["dow"] = df["fecha"].dt.weekday.map(DOW_ES)

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

# =========================
# OBTENER HOY
# =========================
hoy = df[df["fecha"] == fecha_hoy]
if hoy.empty:
    h = {k: 0 for k in COLUMNAS}
else:
    h = hoy.iloc[0]

# =========================
# OBTENER DOW AÑO ANTERIOR
# =========================
fecha_ref = fecha_hoy.replace(year=fecha_hoy.year - 1)
cand = df[(df["año"] == fecha_ref.year) & (df["fecha"].dt.weekday == fecha_hoy.weekday())]

if cand.empty:
    a = {k: 0 for k in COLUMNAS}
    fecha_dow_txt = "Sin histórico comparable"
else:
    cand = cand.copy()
    cand["dist"] = (cand["fecha"] - fecha_ref).abs()
    a = cand.sort_values("dist").iloc[0]
    fecha_dow_txt = f"{DOW_ES[a['fecha'].weekday()]} · {a['fecha'].strftime('%d/%m/%Y')}"

# =========================
# FUNCIONES
# =========================
def diff(actual, base):
    d = actual - base
    p = (d / base * 100) if base > 0 else 0
    return d, p

def color(v):
    if v > 0: return "green"
    if v < 0: return "red"
    return "gray"

# =========================
# BLOQUE HOY
# =========================
st.divider()
st.subheader("HOY")

c1, c2, c3 = st.columns(3)

# --- HOY ---
with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")
    for t in ["manana","tarde","noche"]:
        st.markdown(f"**{t.capitalize()}**")
        st.write(f"Ventas: {h[f'ventas_{t}_eur']:.2f} €")
        st.write(f"Comensales: {h[f'comensales_{t}']}")
        st.write(f"Tickets: {h[f'tickets_{t}']}")
    st.markdown(f"### TOTAL {h['ventas_total_eur']:.2f} €")

# --- DOW ---
with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_dow_txt)
    for t in ["manana","tarde","noche"]:
        st.markdown(f"**{t.capitalize()}**")
        st.write(f"Ventas: {a[f'ventas_{t}_eur']:.2f} €")
        st.write(f"Comensales: {a[f'comensales_{t}']}")
        st.write(f"Tickets: {a[f'tickets_{t}']}")
    st.markdown(f"### TOTAL {a['ventas_total_eur']:.2f} €")

# --- VARIACIÓN ---
with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")
    for t in ["manana","tarde","noche"]:
        dv, pv = diff(h[f'ventas_{t}_eur'], a[f'ventas_{t}_eur'])
        dc, pc = diff(h[f'comensales_{t}'], a[f'comensales_{t}'])
        dt, pt = diff(h[f'tickets_{t}'], a[f'tickets_{t}'])
        st.markdown(f"**{t.capitalize()}**")
        st.markdown(f"<span style='color:{color(dv)}'>Ventas: {dv:+.2f} € ({pv:+.1f}%)</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{color(dc)}'>Comensales: {dc:+} ({pc:+.1f}%)</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{color(dt)}'>Tickets: {dt:+} ({pt:+.1f}%)</span>", unsafe_allow_html=True)

# =========================
# BITÁCORA
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[(df["fecha"].dt.month == fecha_hoy.month) & (df["fecha"].dt.year == fecha_hoy.year)].copy()
df_mes["fecha"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")

st.dataframe(
    df_mes[[
        "fecha","dow",
        "ventas_manana_eur","ventas_tarde_eur","ventas_noche_eur",
        "ventas_total_eur","observaciones"
    ]],
    hide_index=True,
    use_container_width=True
)
