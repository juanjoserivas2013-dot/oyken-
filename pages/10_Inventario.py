import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================

st.title("OYKEN · Inventario")
st.caption("Registro mensual del valor real del stock")

# =========================
# DATOS
# =========================
DATA_FILE = Path("inventario.csv")

if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(
        columns=["Mes", "Año", "Inventario (€)", "Fecha registro"]
    )

# =========================
# REGISTRO INVENTARIO
# =========================
st.subheader("Registro de inventario mensual")

with st.form("form_inventario", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox(
            "Mes inventario",
            [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ],
            index=date.today().month - 1
        )

    with col2:
        año = st.selectbox(
            "Año",
            list(range(date.today().year - 3, date.today().year + 2)),
            index=3
        )

    inventario = st.number_input(
        "Valor total del inventario (€)",
        min_value=0.00,
        step=100.00,
        format="%.2f"
    )

    submitted = st.form_submit_button("Guardar inventario del mes")

    if submitted:

        if inventario <= 0:
            st.warning("El valor del inventario debe ser mayor que cero.")
            st.stop()

        # Eliminar inventario previo del mismo mes/año (si existe)
        df = df[
            ~((df["Mes"] == mes) & (df["Año"] == año))
        ]

        nuevo = {
            "Mes": mes,
            "Año": año,
            "Inventario (€)": round(inventario, 2),
            "Fecha registro": date.today().strftime("%d/%m/%Y")
        }

        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        df = df.sort_values(["Año", "Mes"])

        df.to_csv(DATA_FILE, index=False)

        st.success("Inventario mensual registrado correctamente.")

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("Histórico de inventarios mensuales")

if df.empty:
    st.info("Todavía no hay inventarios registrados.")
else:
    st.dataframe(
        df.sort_values(["Año", "Mes"], ascending=False),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Solo existe un inventario válido por mes. "
        "Si se registra de nuevo, el valor anterior se sustituye."
    )
# =====================================================
# INVENTARIO MENSUAL · LECTURA REAL
# =====================================================

st.divider()
st.subheader("Inventario mensual")

# Copia segura
df_inv = df.copy()

# Forzar tipos
df_inv["Año"] = pd.to_numeric(df_inv["Año"], errors="coerce")
df_inv["Inventario (€)"] = pd.to_numeric(df_inv["Inventario (€)"], errors="coerce")

# -------------------------
# SELECTORES
# -------------------------
c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        sorted(df_inv["Año"].dropna().unique()),
        index=len(sorted(df_inv["Año"].dropna().unique())) - 1,
        key="anio_inventario"
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=["Todos"] + sorted(df_inv["Mes"].dropna().unique()),
        key="mes_inventario"
    )

# -------------------------
# FILTRADO REAL (SIN RECONSTRUIR)
# -------------------------
df_filtrado = df_inv[df_inv["Año"] == anio_sel]

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_sel]

# -------------------------
# TABLA
# -------------------------
st.dataframe(
    df_filtrado.sort_values("Fecha registro"),
    hide_index=True,
    use_container_width=True
)

# -------------------------
# MÉTRICA CORRECTA
# -------------------------
if not df_filtrado.empty:
    valor_actual = df_filtrado.iloc[-1]["Inventario (€)"]
    st.metric(
        "Inventario vigente (€)",
        f"{valor_actual:,.2f} €"
    )
