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

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = 0 if col not in ["fecha", "observaciones"] else ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    st.markdown("**Ventas (€)**")
    v1, v2, v3 = st.columns(3)
    with v1:
        vm = st.number_input("Mañana", min_value=0.0, step=10.0)
    with v2:
        vt = st.number_input("Tarde", min_value=0.0, step=10.0)
    with v3:
        vn = st.number_input("Noche", min_value=0.0, step=10.0)

    st.markdown("**Comensales**")
    c1, c2, c3 = st.columns(3)
    with c1:
        cm = st.number_input("Mañana ", min_value=0, step=1)
    with c2:
        ct = st.number_input("Tarde ", min_value=0, step=1)
    with c3:
        cn = st.number_input("Noche ", min_value=0, step=1)

    st.markdown("**Tickets**")
    t1, t2, t3 = st.columns(3)
    with t1:
        tm = st.number_input("Mañana  ", min_value=0, step=1)
    with t2:
        tt = st.number_input("Tarde  ", min_value=0, step=1)
    with t3:
        tn = st.number_input("Noche  ", min_value=0, step=1)

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
    st.success("Venta guardada correctamente")
    st.rerun()

if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN ISO (REGLA CORRECTA GRANDES CADENAS)
# =========================
df = df.sort_values("fecha")
iso = df["fecha"].dt.isocalendar()
df["iso_year"] = iso.year
df["iso_week"] = iso.week
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

# =========================
# BLOQUE HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
iso_hoy = fecha_hoy.isocalendar()

inicio_dia = fecha_hoy.normalize()
fin_dia = inicio_dia + pd.Timedelta(days=1)

venta_hoy = df[
    (df["fecha"] >= inicio_dia) &
    (df["fecha"] < fin_dia)
]

def fila_o_cero(col):
    return fila[col] if not venta_hoy.empty else 0

if not venta_hoy.empty:
    fila = venta_hoy.iloc[0]

# --- HOY ---
vm_h = fila_o_cero("ventas_manana_eur")
vt_h = fila_o_cero("ventas_tarde_eur")
vn_h = fila_o_cero("ventas_noche_eur")
total_h = fila_o_cero("ventas_total_eur")

cm_h = fila_o_cero("comensales_manana")
ct_h = fila_o_cero("comensales_tarde")
cn_h = fila_o_cero("comensales_noche")

tm_h = fila_o_cero("tickets_manana")
tt_h = fila_o_cero("tickets_tarde")
tn_h = fila_o_cero("tickets_noche")

# Ticket medio HOY
tmed_m_h = vm_h / tm_h if tm_h > 0 else 0
tmed_t_h = vt_h / tt_h if tt_h > 0 else 0
tmed_n_h = vn_h / tn_h if tn_h > 0 else 0
tmed_tot_h = total_h / (tm_h + tt_h + tn_h) if (tm_h + tt_h + tn_h) > 0 else 0

# =========================
# DOW AÑO ANTERIOR (MISMA SEMANA ISO)
# =========================
dow_ant = df[
    (df["iso_year"] == iso_hoy.year - 1) &
    (df["iso_week"] == iso_hoy.week) &
    (df["weekday"] == fecha_hoy.weekday())
]

if dow_ant.empty:
    fecha_dow_txt = "Sin histórico comparable"

    vm_a = vt_a = vn_a = total_a = 0.0
    cm_a = ct_a = cn_a = 0
    tm_a = tt_a = tn_a = 0
else:
    comp = dow_ant.iloc[0]
    fecha_dow_txt = f"{DOW_ES[comp['weekday']]} · {comp['fecha'].strftime('%d/%m/%Y')}"

    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

    cm_a = comp["comensales_manana"]
    ct_a = comp["comensales_tarde"]
    cn_a = comp["comensales_noche"]

    tm_a = comp["tickets_manana"]
    tt_a = comp["tickets_tarde"]
    tn_a = comp["tickets_noche"]

# Ticket medio DOW
tmed_m_a = vm_a / tm_a if tm_a > 0 else 0
tmed_t_a = vt_a / tt_a if tt_a > 0 else 0
tmed_n_a = vn_a / tn_a if tn_a > 0 else 0
tmed_tot_a = total_a / (tm_a + tt_a + tn_a) if (tm_a + tt_a + tn_a) > 0 else 0

# =========================
# FUNCIONES VARIACIÓN
# =========================
def diff_pct(actual, base):
    d = actual - base
    p = (d / base * 100) if base > 0 else (100.0 if actual > 0 else 0.0)
    return d, p

def color(v):
    return "green" if v > 0 else "red" if v < 0 else "gray"

def icono(p):
    if p > 25:
        return "👁️"
    elif 1 <= p <= 25:
        return "↑"
    elif -25 <= p <= -1:
        return "↓"
    elif p < -25:
        return "⚠️"
    else:
        return ""


# =========================
# CÁLCULOS VARIACIÓN
# =========================
# Ventas
d_vm, p_vm = diff_pct(vm_h, vm_a)
d_vt, p_vt = diff_pct(vt_h, vt_a)
d_vn, p_vn = diff_pct(vn_h, vn_a)
d_tot, p_tot = diff_pct(total_h, total_a)

# Comensales
d_cm = cm_h - cm_a
d_ct = ct_h - ct_a
d_cn = cn_h - cn_a

# Tickets
d_tm = tm_h - tm_a
d_tt = tt_h - tt_a
d_tn = tn_h - tn_a

# Ticket medio
d_tmed_m, p_tmed_m = diff_pct(tmed_m_h, tmed_m_a)
d_tmed_t, p_tmed_t = diff_pct(tmed_t_h, tmed_t_a)
d_tmed_n, p_tmed_n = diff_pct(tmed_n_h, tmed_n_a)
d_tmed_tot, p_tmed_tot = diff_pct(tmed_tot_h, tmed_tot_a)

# =========================
# DISPOSICIÓN VISUAL
# =========================
c1, c2, c3 = st.columns(3)

# HOY
with c1:
    st.markdown("**HOY**")
    st.caption(f"{DOW_ES[fecha_hoy.weekday()]} · {fecha_hoy.strftime('%d/%m/%Y')}")

    st.write("**Mañana**")
    st.write(f"{vm_h:,.2f} €")
    st.caption(f"{cm_h} comensales · {tm_h} tickets")
    st.caption(f"Ticket medio: {tmed_m_h:,.2f} €")

    st.write("**Tarde**")
    st.write(f"{vt_h:,.2f} €")
    st.caption(f"{ct_h} comensales · {tt_h} tickets")
    st.caption(f"Ticket medio: {tmed_t_h:,.2f} €")

    st.write("**Noche**")
    st.write(f"{vn_h:,.2f} €")
    st.caption(f"{cn_h} comensales · {tn_h} tickets")
    st.caption(f"Ticket medio: {tmed_n_h:,.2f} €")

    st.markdown("---")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")
    st.caption(f"Ticket medio: {tmed_tot_h:,.2f} €")

# DOW
with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_dow_txt)

    st.write("**Mañana**")
    st.write(f"{vm_a:,.2f} €")
    st.caption(f"{cm_a} comensales · {tm_a} tickets")
    st.caption(f"Ticket medio: {tmed_m_a:,.2f} €")

    st.write("**Tarde**")
    st.write(f"{vt_a:,.2f} €")
    st.caption(f"{ct_a} comensales · {tt_a} tickets")
    st.caption(f"Ticket medio: {tmed_t_a:,.2f} €")

    st.write("**Noche**")
    st.write(f"{vn_a:,.2f} €")
    st.caption(f"{cn_a} comensales · {tn_a} tickets")
    st.caption(f"Ticket medio: {tmed_n_a:,.2f} €")

    st.markdown("---")
    st.markdown(f"### TOTAL DOW\n{total_a:,.2f} €")
    st.caption(f"Ticket medio: {tmed_tot_a:,.2f} €")

# VARIACIÓN
with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")

    st.write("**Mañana**")
    st.markdown(
        f"<span style='color:{color(d_vm)}'>{d_vm:+,.2f} € ({p_vm:+.1f}%) {icono(p_vm)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{d_cm:+} comensales · {d_tm:+} tickets")
    st.caption(
        f"Ticket medio: {d_tmed_m:+.2f} € ({p_tmed_m:+.1f}%) {icono(p_tmed_m)}"
    )

    st.write("**Tarde**")
    st.markdown(
        f"<span style='color:{color(d_vt)}'>{d_vt:+,.2f} € ({p_vt:+.1f}%) {icono(p_vt)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{d_ct:+} comensales · {d_tt:+} tickets")
    st.caption(
        f"Ticket medio: {d_tmed_t:+.2f} € ({p_tmed_t:+.1f}%) {icono(p_tmed_t)}"
    )

    st.write("**Noche**")
    st.markdown(
        f"<span style='color:{color(d_vn)}'>{d_vn:+,.2f} € ({p_vn:+.1f}%) {icono(p_vn)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"{d_cn:+} comensales · {d_tn:+} tickets")
    st.caption(
        f"Ticket medio: {d_tmed_n:+.2f} € ({p_tmed_n:+.1f}%) {icono(p_tmed_n)}"
    )

    st.markdown("---")
    st.markdown(
        f"<span style='color:{color(d_tot)}'>"
        f" TOTAL {d_tot:+,.2f} € ({p_tot:+.1f}%)"
        f"</span>",
        unsafe_allow_html=True
    )
    st.caption(
        f"Ticket medio: {d_tmed_tot:+.2f} € ({p_tmed_tot:+.1f}%) {icono(p_tmed_tot)}"
    )

# =========================
# BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[
    (df["fecha"].dt.month == fecha_hoy.month) &
    (df["fecha"].dt.year == fecha_hoy.year)
].copy()

df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️" if r["observaciones"].strip() else r["fecha_display"],
    axis=1
)

st.dataframe(
    df_mes[[
        "fecha_display", "dow",
        "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur",
        "ventas_total_eur",
        "comensales_manana", "comensales_tarde", "comensales_noche",
        "tickets_manana", "tickets_tarde", "tickets_noche",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
)
# =========================
# CIERRE MENSUAL · VENTAS
# =========================
st.divider()
st.subheader("Cierre mensual · Ventas")

c_mes, c_ano = st.columns(2)

with c_mes:
    mes_sel = st.selectbox(
        "Mes",
        options=list(range(1, 13)),
        index=fecha_hoy.month - 1,
        format_func=lambda x: date(1900, x, 1).strftime("%B")
    )

with c_ano:
    ano_sel = st.selectbox(
        "Año",
        options=sorted(df["fecha"].dt.year.unique()),
        index=len(sorted(df["fecha"].dt.year.unique())) - 1
    )

df_cierre = df[
    (df["fecha"].dt.month == mes_sel) &
    (df["fecha"].dt.year == ano_sel)
]

ventas_mes = df_cierre["ventas_total_eur"].sum()
dias_operados = df_cierre["fecha"].nunique()
ticket_medio_mes = (
    ventas_mes / df_cierre[["tickets_manana", "tickets_tarde", "tickets_noche"]].sum().sum()
    if df_cierre[["tickets_manana", "tickets_tarde", "tickets_noche"]].sum().sum() > 0
    else 0
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Ventas del mes", f"{ventas_mes:,.2f} €")

with c2:
    st.metric("Días operados", dias_operados)

with c3:
    st.metric("Ticket medio mes", f"{ticket_medio_mes:,.2f} €")

