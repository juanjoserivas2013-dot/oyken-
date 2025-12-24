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
st.divider()

# =========================
# ARCHIVOS
# =========================
COMPRAS_FILE = Path("compras.csv")
PROVEEDORES_FILE = Path("proveedores.csv")

# =========================
# ESTADO: COMPRAS
# =========================
if "compras" not in st.session_state:
    if COMPRAS_FILE.exists():
        st.session_state.compras = pd.read_csv(COMPRAS_FILE)
    else:
        st.session_state.compras = pd.DataFrame(
            columns=["Fecha", "Proveedor", "Familia", "Coste (€)"]
        )

# =========================
# ESTADO: PROVEEDORES (MAESTRO)
# =========================
if "proveedores" not in st.session_state:
    if PROVEEDORES_FILE.exists():
        st.session_state.proveedores = (
            pd.read_csv(PROVEEDORES_FILE)["Proveedor"]
            .dropna()
            .unique()
            .tolist()
        )
    else:
        st.session_state.proveedores = []

FAMILIAS = ["Materia prima", "Bebidas", "Limpieza", "Otros"]

# =========================================================
# REGISTRAR COMPRA
# =========================================================
st.subheader("Registrar compra")

with st.container(border=True):
    with st.form("form_compras", clear_on_submit=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            fecha = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with c2:
            proveedor = st.selectbox(
                "Proveedor",
                st.session_state.proveedores,
                placeholder="Seleccionar proveedor"
            )

        with c3:
            familia = st.selectbox("Familia", FAMILIAS)

        coste = st.number_input(
            "Coste total (€)",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )

        registrar = st.form_submit_button(
            "Registrar compra",
            use_container_width=True
        )

        if registrar:

            if not proveedor or coste <= 0:
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

            st.session_state.compras.to_csv(COMPRAS_FILE, index=False)
            st.success("Compra registrada")

# =========================================================
# GESTIÓN DE PROVEEDORES
# =========================================================
st.divider()
st.subheader("Gestión de proveedores")

with st.container(border=True):

    nuevo_proveedor = st.text_input(
        "Nuevo proveedor",
        placeholder="Escribir nombre del proveedor"
    )

    if st.button("Guardar proveedor", use_container_width=True):

        nombre = nuevo_proveedor.strip()

        if nombre and nombre not in st.session_state.proveedores:
            st.session_state.proveedores.append(nombre)

            pd.DataFrame(
                {"Proveedor": st.session_state.proveedores}
            ).to_csv(PROVEEDORES_FILE, index=False)

            st.success("Proveedor guardado")

    if st.session_state.proveedores:
        st.markdown("**Proveedores existentes**")
        for p in sorted(st.session_state.proveedores):
            st.write(f"• {p}")

# =========================================================
# RESUMEN
# =========================================================
st.divider()
st.subheader("Resumen")

total = (
    st.session_state.compras["Coste (€)"].sum()
    if not st.session_state.compras.empty else 0
)
num_compras = len(st.session_state.compras)

c1, c2 = st.columns(2)
c1.metric("Total registrado (€)", f"{total:.2f}")
c2.metric("Nº de compras", num_compras)

# =========================================================
# HISTÓRICO
# =========================================================
st.divider()
st.subheader("Histórico de compras")

if not st.session_state.compras.empty:
    st.dataframe(
        st.session_state.compras,
        hide_index=True,
        use_container_width=True
    )

# =========================================================
# CORRECCIÓN DE ERRORES
# =========================================================
st.divider()
st.subheader("Corrección de errores")

with st.container(border=True):

    if not st.session_state.compras.empty:

        idx = st.selectbox(
            "Selecciona una compra",
            st.session_state.compras.index,
            format_func=lambda i: (
                f'{st.session_state.compras.loc[i,"Fecha"]} · '
                f'{st.session_state.compras.loc[i,"Proveedor"]} · '
                f'{st.session_state.compras.loc[i,"Coste (€)"]:.2f} €'
            )
        )

        if st.button("Eliminar compra", use_container_width=True):

            st.session_state.compras = (
                st.session_state.compras
                .drop(idx)
                .reset_index(drop=True)
            )

            st.session_state.compras.to_csv(COMPRAS_FILE, index=False)
            st.success("Compra eliminada")
