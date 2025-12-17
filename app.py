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
# ESTADO · FECHA ACTIVA
# =========================
if "fecha_activa" not in st.session_state:
    st.session_state.fecha_activa = date.today()

# =========================
# MENÚ PRINCIPAL
# =========================
st.sidebar.title("OYKEN")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "📊 Control Diario",
        "👥 Comportamiento",
        "📈 Tendencia",
        "🧠 Oyken Core"
    ]
)

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

df["observaciones"] = df.get("observaciones", "").fillna("")

# =========================
# PREPARACIÓN ISO
# =========================
if not df.empty:
    df = df.sort_values("fecha")
    iso = df["fecha"].dt.isocalendar()
    df["iso_year"] = iso.year
    df["iso_week"] = iso.week
    df["weekday"] = df["fecha"].dt.weekday
    df["dow"] = df["weekday"].map(DOW_ES)

# ==========================================================
# 📊 CONTROL DIARIO
# ==========================================================
if seccion == "📊 Control Diario":

    # =========================
    # REGISTRO DIARIO
    # =========================
    st.subheader("Registro diario")

    with st.form("form_ventas", clear_on_submit=True):
        fecha = st.date_input(
            "Fecha",
            value=st.session_state.fecha_activa,
            format="DD/MM/YYYY"
        )
        st.session_state.fecha_activa = fecha

        st.markdown("**Ventas (€)**")
        v1, v2, v3 = st.columns(3)
        vm = v1.number_input("Mañana", min_value=0.0, step=10.0)
        vt = v2.number_input("Tarde", min_value=0.0, step=10.0)
        vn = v3.number_input("Noche", min_value=0.0, step=10.0)

        st.markdown("**Comensales**")
        c1, c2, c3 = st.columns(3)
        cm = c1.number_input("Mañana ", min_value=0, step=1)
        ct = c2.number_input("Tarde ", min_value=0, step=1)
        cn = c3.number_input("Noche ", min_value=0, step=1)

        st.markdown("**Tickets**")
        t1, t2, t3 = st.columns(3)
        tm = t1.number_input("Mañana  ", min_value=0, step=1)
        tt = t2.number_input("Tarde  ", min_value=0, step=1)
        tn = t3.number_input("Noche  ", min_value=0, step=1)

        observaciones = st.text_area(
            "Observaciones del día",
            placeholder="Clima, eventos, incidencias, promociones…",
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
    # BLOQUE HOY COMPLETO
    # =========================
    st.divider()
    st.subheader("HOY")

    fecha_ref = pd.to_datetime(st.session_state.fecha_activa)
    iso_ref = fecha_ref.isocalendar()

    fila_hoy = df[df["fecha"] == fecha_ref]
    if fila_hoy.empty:
        st.info("No hay datos para la fecha seleccionada.")
        st.stop()

    h = fila_hoy.iloc[0]

    # HOY
    vm_h, vt_h, vn_h = h["ventas_manana_eur"], h["ventas_tarde_eur"], h["ventas_noche_eur"]
    cm_h, ct_h, cn_h = h["comensales_manana"], h["comensales_tarde"], h["comensales_noche"]
    tm_h, tt_h, tn_h = h["tickets_manana"], h["tickets_tarde"], h["tickets_noche"]
    total_h = h["ventas_total_eur"]

    # Ticket medio HOY
    tmed_m_h = vm_h / tm_h if tm_h > 0 else 0
    tmed_t_h = vt_h / tt_h if tt_h > 0 else 0
    tmed_n_h = vn_h / tn_h if tn_h > 0 else 0
    tmed_tot_h = total_h / (tm_h + tt_h + tn_h) if (tm_h + tt_h + tn_h) > 0 else 0

    # DOW año anterior
    df_dow = df[
        (df["iso_year"] == iso_ref.year - 1) &
        (df["iso_week"] == iso_ref.week) &
        (df["weekday"] == fecha_ref.weekday())
    ]

    if df_dow.empty:
        vm_a = vt_a = vn_a = total_a = 0
        cm_a = ct_a = cn_a = 0
        tm_a = tt_a = tn_a = 0
        fecha_dow_txt = "Sin histórico comparable"
    else:
        a = df_dow.iloc[0]
        vm_a, vt_a, vn_a = a["ventas_manana_eur"], a["ventas_tarde_eur"], a["ventas_noche_eur"]
        cm_a, ct_a, cn_a = a["comensales_manana"], a["comensales_tarde"], a["comensales_noche"]
        tm_a, tt_a, tn_a = a["tickets_manana"], a["tickets_tarde"], a["tickets_noche"]
        total_a = a["ventas_total_eur"]
        fecha_dow_txt = f"{DOW_ES[a['weekday']]} · {a['fecha'].strftime('%d/%m/%Y')}"

    # Ticket medio DOW
    tmed_m_a = vm_a / tm_a if tm_a > 0 else 0
    tmed_t_a = vt_a / tt_a if tt_a > 0 else 0
    tmed_n_a = vn_a / tn_a if tn_a > 0 else 0
    tmed_tot_a = total_a / (tm_a + tt_a + tn_a) if (tm_a + tt_a + tn_a) > 0 else 0

    # Funciones
    def diff_pct(act, base):
        d = act - base
        p = (d / base * 100) if base > 0 else 0
        return d, p

    def color(v):
        return "green" if v > 0 else "red" if v < 0 else "gray"

    # Variaciones ventas
    d_vm, p_vm = diff_pct(vm_h, vm_a)
    d_vt, p_vt = diff_pct(vt_h, vt_a)
    d_vn, p_vn = diff_pct(vn_h, vn_a)
    d_tot, p_tot = diff_pct(total_h, total_a)

    c1, c2, c3 = st.columns(3)

    # HOY
    with c1:
        st.markdown("**HOY**")
        st.caption(f"{DOW_ES[fecha_ref.weekday()]} · {fecha_ref.strftime('%d/%m/%Y')}")
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
        st.markdown(f"<span style='color:{color(d_vm)}'>{d_vm:+,.2f} € ({p_vm:+.1f}%)</span>", unsafe_allow_html=True)

        st.write("**Tarde**")
        st.markdown(f"<span style='color:{color(d_vt)}'>{d_vt:+,.2f} € ({p_vt:+.1f}%)</span>", unsafe_allow_html=True)

        st.write("**Noche**")
        st.markdown(f"<span style='color:{color(d_vn)}'>{d_vn:+,.2f} € ({p_vn:+.1f}%)</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"<span style='color:{color(d_tot)}'>### TOTAL {d_tot:+,.2f} € ({p_tot:+.1f}%)</span>", unsafe_allow_html=True)

# ==========================================================
# 👥 COMPORTAMIENTO
# ==========================================================
elif seccion == "👥 Comportamiento":

    st.subheader("Comportamiento del cliente")
    st.caption("Valores agregados · Comparativa vs mismo DOW año anterior")

    fecha_ref = pd.to_datetime(st.session_state.fecha_activa)
    iso_ref = fecha_ref.isocalendar()

    h = df[df["fecha"] == fecha_ref].iloc[0]

    ventas_h = h["ventas_total_eur"]
    com_h = h["comensales_manana"] + h["comensales_tarde"] + h["comensales_noche"]
    tic_h = h["tickets_manana"] + h["tickets_tarde"] + h["tickets_noche"]

    tpc_h = tic_h / com_h if com_h > 0 else 0
    epc_h = ventas_h / com_h if com_h > 0 else 0

    a = df[
        (df["iso_year"] == iso_ref.year - 1) &
        (df["iso_week"] == iso_ref.week) &
        (df["weekday"] == fecha_ref.weekday())
    ].iloc[0]

    ventas_a = a["ventas_total_eur"]
    com_a = a["comensales_manana"] + a["comensales_tarde"] + a["comensales_noche"]
    tic_a = a["tickets_manana"] + a["tickets_tarde"] + a["tickets_noche"]

    tpc_a = tic_a / com_a if com_a > 0 else 0
    epc_a = ventas_a / com_a if com_a > 0 else 0

    d_tpc, p_tpc = diff_pct(tpc_h, tpc_a)
    d_epc, p_epc = diff_pct(epc_h, epc_a)

    st.markdown("### Tickets por comensal")
    st.write(f"HOY: **{tpc_h:.2f}**")
    st.write(f"DOW: **{tpc_a:.2f}**")
    st.write(f"VARIACIÓN: **{d_tpc:+.2f} ({p_tpc:+.1f}%)**")

    st.divider()

    st.markdown("### € por comensal")
    st.write(f"HOY: **{epc_h:,.2f} €**")
    st.write(f"DOW: **{epc_a:,.2f} €**")
    st.write(f"VARIACIÓN: **{d_epc:+.2f} € ({p_epc:+.1f}%)**")

# ==========================================================
# 📈 TENDENCIA
# ==========================================================
elif seccion == "📈 Tendencia":
    st.subheader("Tendencia")
    st.info("Módulo en construcción")

# ==========================================================
# 🧠 OYKEN CORE
# ==========================================================
elif seccion == "🧠 Oyken Core":
    st.subheader("Oyken Core")
    st.info("Análisis inteligente en desarrollo")
