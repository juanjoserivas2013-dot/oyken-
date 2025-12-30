import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CABECERA
# =====================================================
st.subheader("OYKEN · Gastos")
st.markdown("**Registro de gastos operativos no ligados a compras de producto.**")
st.caption("Aquí se captura la estructura fija y variable del negocio.")

# =====================================================
# ARCHIVO DE DATOS
# =====================================================
DATA_FILE = Path("gastos.csv")

# =====================================================
# ESTADO
# =====================================================
if "gastos" not in st.session_state:
    if DATA_FILE.exists():
        st.session_state.gastos = pd.read_csv(DATA_FILE)
    else:
        st.session_state.gastos = pd.DataFrame(
            columns=["Fecha", "Mes", "Concepto", "Categoria", "Coste (€)"]
        )

# =====================================================
# CATEGORÍAS BASE OYKEN
# =====================================================
CATEGORIAS = [
    "Alquiler",
    "Suministros",
    "Mantenimiento",
    "Servicios profesionales",
    "Bancos y Medios de pago",
    "Tecnología y Plataformas",
    "Marqueting y Comunicación",
    "Limpieza y Lavandería",
    "Uniformes y utensilios",
    "Vigilancia y Seguridad",
    "otros Gastos operativos"
    
]

# =====================================================
# FORMULARIO
# =====================================================
with st.form("registro_gastos", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            format="DD/MM/YYYY"
        )

    with col2:
        categoria = st.selectbox("Categoría", CATEGORIAS)

    concepto = st.text_input(
        "Concepto / Descripción",
        placeholder="Ej: Alquiler local, gestoría, electricidad..."
    )

    coste = st.number_input(
        "Coste (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f"
    )

    submitted = st.form_submit_button("Registrar gasto")

    if submitted:

        if not concepto:
            st.warning("Debes introducir un concepto.")
            st.stop()

        if coste <= 0:
            st.warning("El coste debe ser mayor que cero.")
            st.stop()

        nuevo = {
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Mes": fecha.strftime("%Y-%m"),
            "Concepto": concepto,
            "Categoria": categoria,
            "Coste (€)": round(coste, 2)
        }

        st.session_state.gastos = pd.concat(
            [st.session_state.gastos, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        st.session_state.gastos.to_csv(DATA_FILE, index=False)
        st.success("Gasto registrado correctamente.")

# =====================================================
# VISUALIZACIÓN
# =====================================================
st.divider()

if st.session_state.gastos.empty:
    st.info("No hay gastos registrados todavía.")
else:
    st.dataframe(
        st.session_state.gastos,
        hide_index=True,
        use_container_width=True
    )

    total = st.session_state.gastos["Coste (€)"].sum()
    st.markdown(f"### Total acumulado: **{total:.2f} €**")

# =====================================================
# ELIMINAR REGISTRO
# =====================================================
st.subheader("Eliminar gasto")

idx = st.selectbox(
    "Selecciona un registro",
    st.session_state.gastos.index,
    format_func=lambda i: (
        f'{st.session_state.gastos.loc[i,"Fecha"]} | '
        f'{st.session_state.gastos.loc[i,"Concepto"]} | '
        f'{st.session_state.gastos.loc[i,"Coste (€)"]:.2f} €'
    )
)

if st.button("Eliminar gasto"):
    st.session_state.gastos = (
        st.session_state.gastos
        .drop(idx)
        .reset_index(drop=True)
    )
    st.session_state.gastos.to_csv(DATA_FILE, index=False)
    st.success("Gasto eliminado correctamente.")
    
# ===============================
# BASE CUENTA DE RESULTADOS
# Resumen mensual de gastos
# ===============================

st.markdown("---")
st.subheader("Base Cuenta de Resultados — Gastos mensuales")

# Año base (se deduce de los datos si existen)
if not st.session_state.gastos.empty:
    anio_base = (
        st.session_state.gastos["Mes"]
        .astype(str)
        .str[:4]
        .mode()
        .iloc[0]
    )
else:
    anio_base = pd.Timestamp.today().year

st.caption(f"Año base para Cuenta de Resultados: {anio_base}")

# Crear estructura enero–diciembre
MESES_TEXTO = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

base_meses = pd.DataFrame({
    "Mes": MESES_TEXTO
})

# Agrupar gastos reales
if not st.session_state.gastos.empty:
    gastos_mensuales = (
        st.session_state.gastos
        .groupby("Mes", as_index=False)["Coste (€)"]
        .sum()
    )
else:
    gastos_mensuales = pd.DataFrame(columns=["Mes", "Coste (€)"])

# Unir estructura base con datos reales
df_base = base_meses.merge(
    gastos_mensuales,
    on="Mes",
    how="left"
).fillna(0)

# Mostrar tabla
st.dataframe(
    df_base.rename(columns={"Coste (€)": "Gastos (€)"}),
    use_container_width=True
)

# Total anual
total_anual = df_base["Coste (€)"].sum()
st.markdown(f"**Total anual de gastos:** {total_anual:,.2f} €")
