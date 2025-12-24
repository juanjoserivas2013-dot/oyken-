import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="OYKEN · Compras",
    layout="centered"
)

st.title("OYKEN · Compras")
st.markdown("**Registro operativo diario del coste real del negocio.**")
st.caption("Este módulo no analiza. Captura la verdad económica.")

# =========================
# ESTADO Y DATOS
# =========================
DATA_FILE = Path("compras.csv")

if "compras" not in st.session_state:
    if DATA_FILE.exists():
        st.session_state.compras = pd.read_csv(DATA_FILE)
    else:
        st.session_state.compras = pd.DataFrame(
            columns=["Fecha", "Proveedor", "Familia", "Coste (€)"]
        )

if "proveedores" not in st.session_state:
    st.session_state.proveedores = sorted(
        st.session_state.compras["Proveedor"].dropna().unique().tolist()
        if not st.session_state.compras.empty else []
    )

FAMILIAS = ["Materia prima", "Bebidas", "Limpieza", "Otros"]

# =========================
# FORMULARIO DE REGISTRO
# =========================
with st.form("registro_compras", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            format="DD/MM/YYYY"
        )

    with col2:
        proveedor = st.selectbox(
            "Proveedor",
            st.session_state.proveedores + ["+ Añadir proveedor"]
        )

    if proveedor == "+ Añadir proveedor":
        nuevo_proveedor = st.text_input("Nuevo proveedor")
    else:
        nuevo_proveedor = None

    familia = st.selectbox("Familia / Apartado", FAMILIAS)

    coste = st.number_input(
        "Coste total (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f"
    )

    submitted = st.form_submit_button("Registrar compra")

    if submitted:

        if proveedor == "+ Añadir proveedor":
            if not nuevo_proveedor:
                st.warning("Debes introducir el nombre del proveedor.")
                st.stop()
            proveedor = nuevo_proveedor
            if proveedor not in st.session_state.proveedores:
                st.session_state.proveedores.append(proveedor)

        if coste <= 0:
            st.warning("El coste debe ser mayor que cero.")
            st.stop()

        nueva_compra = {
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Proveedor": proveedor,
            "Familia": familia,
            "Coste (€)": round(coste, 2)
        }

        st.session_state.compras = pd.concat(
            [st.session_state.compras, pd.DataFrame([nueva_compra])],
            ignore_index=True
        )

        st.session_state.compras.to_csv(DATA_FILE, index=False)
        st.success("Compra registrada correctamente.")

# =========================
# VISUALIZACIÓN Y CONTROL
# =========================
st.divider()

if st.session_state.compras.empty:
    st.info("No hay compras registradas todavía.")
else:
    st.subheader("Compras registradas")

    st.dataframe(
        st.session_state.compras,
        hide_index=True,
        use_container_width=True
    )

    total = st.session_state.compras["Coste (€)"].sum()
    st.markdown(f"### Total acumulado: **{total:.2f} €**")

    st.subheader("Eliminar compra")

    idx = st.selectbox(
        "Selecciona un registro",
        st.session_state.compras.index,
        format_func=lambda i: (
            f'{st.session_state.compras.loc[i,"Fecha"]} | '
            f'{st.session_state.compras.loc[i,"Proveedor"]} | '
            f'{st.session_state.compras.loc[i,"Coste (€)"]:.2f} €'
        )
    )

    if st.button("Eliminar compra"):
        st.session_state.compras = (
            st.session_state.compras
            .drop(idx)
            .reset_index(drop=True)
        )
        st.session_state.compras.to_csv(DATA_FILE, index=False)
        st.success("Compra eliminada correctamente.")
