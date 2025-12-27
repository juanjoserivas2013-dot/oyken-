import streamlit as st
import pandas as pd
from pathlib import Path

st.title("OYKEN · Gastos")
st.markdown("**Estructura económica mensual del negocio**")
st.caption("Registro de gastos estructurales no vinculados a producto ni personal")

# =========================
# ARCHIVO DE DATOS
# =========================
DATA_FILE = Path("gastos.csv")

if DATA_FILE.exists():
    gastos_df = pd.read_csv(DATA_FILE)
else:
    gastos_df = pd.DataFrame(
        columns=["Mes", "Familia", "Concepto", "Tipo", "Importe (€)"]
    )

# =========================
# SELECTOR DE MES
# =========================
st.divider()

mes = st.selectbox(
    "📅 Mes de imputación",
    [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ],
    index=0
)

st.divider()

# =========================
# FORMULARIO DE REGISTRO
# =========================
st.subheader("Registrar nuevo gasto")

FAMILIAS = [
    "Alquiler y arrendamientos",
    "Suministros",
    "Servicios externos",
    "Marketing y ventas",
    "Financieros",
    "Impuestos y tasas",
    "Otros estructurales"
]

TIPOS = ["Fijo", "Semifijo", "Variable estructural"]

with st.form("form_gastos", clear_on_submit=True):

    familia = st.selectbox("Familia de gasto", FAMILIAS)
    concepto = st.text_input("Concepto")
    tipo = st.radio("Tipo de gasto", TIPOS, horizontal=True)
    importe = st.number_input(
        "Importe mensual (€)",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )

    submitted = st.form_submit_button("Registrar gasto")

    if submitted:
        if not concepto:
            st.warning("El concepto no puede estar vacío.")
            st.stop()

        if importe <= 0:
            st.warning("El importe debe ser mayor que cero.")
            st.stop()

        nuevo = {
            "Mes": mes,
            "Familia": familia,
            "Concepto": concepto,
            "Tipo": tipo,
            "Importe (€)": round(importe, 2)
        }

        gastos_df = pd.concat(
            [gastos_df, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        gastos_df.to_csv(DATA_FILE, index=False)
        st.success("Gasto registrado correctamente.")

# =========================
# VISUALIZACIÓN DEL MES
# =========================
st.divider()
st.subheader(f"Gastos imputados · {mes}")

gastos_mes = gastos_df[gastos_df["Mes"] == mes]

if gastos_mes.empty:
    st.info("No hay gastos registrados para este mes.")
else:
    st.dataframe(
        gastos_mes,
        hide_index=True,
        use_container_width=True
    )

    total = gastos_mes["Importe (€)"].sum()
    st.markdown(f"### Total gastos estructurales · **{total:,.2f} €**")

# =========================
# ELIMINAR GASTO
# =========================
if not gastos_mes.empty:
    st.divider()
    st.subheader("Eliminar gasto")

    idx = st.selectbox(
        "Selecciona un registro",
        gastos_mes.index,
        format_func=lambda i: (
            f'{gastos_df.loc[i,"Familia"]} | '
            f'{gastos_df.loc[i,"Concepto"]} | '
            f'{gastos_df.loc[i,"Importe (€)"]:.2f} €'
        )
    )

    if st.button("Eliminar gasto"):
        gastos_df = gastos_df.drop(idx).reset_index(drop=True)
        gastos_df.to_csv(DATA_FILE, index=False)
        st.success("Gasto eliminado correctamente.")
