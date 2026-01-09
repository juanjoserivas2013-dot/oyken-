import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime

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
            columns=[
                "Fecha",
                "Mes",
                "Concepto",
                "Categoria",
                "Tipo_Gasto",      # ⬅ ICANN
                "Rol_Gasto",       # ⬅ ICANN
                "Coste (€)"
            ]
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
# MATRIZ ICANN / OYKEN · CLASIFICACIÓN EXPERTA  ⬅ ICANN
# =====================================================
MATRIZ_CATEGORIAS_ICANN = {
    "Alquiler": ("Fijo", "Estructural", "El alquiler existe independientemente de la venta."),
    "Suministros": ("Fijo", "Estructural", "Existe un consumo base imprescindible para operar."),
    "Mantenimiento": ("Fijo", "Estructural", "Mantiene la operatividad mínima del negocio."),
    "Servicios profesionales": ("Fijo", "Estructural", "Servicios obligatorios para operar."),
    "Bancos y Medios de pago": ("Variable", "Estructural", "Escala con la venta, pero es imprescindible."),
    "Tecnología y Plataformas": ("Fijo", "Estructural", "Infraestructura mínima operativa."),
    "Marqueting y Comunicación": ("Variable", "No estructural", "Acelera ventas, no sostiene estructura."),
    "Limpieza y Lavandería": ("Fijo", "Estructural", "Higiene mínima obligatoria."),
    "Uniformes y utensilios": ("Variable", "No estructural", "Reposición por desgaste."),
    "Vigilancia y Seguridad": ("Fijo", "Estructural", "Prevención y obligación normativa."),
    "otros Gastos operativos": ("Variable", "No estructural", "Gasto no crítico estructuralmente.")
}

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

    # =================================================
    # CLASIFICACIÓN ESTRUCTURAL SEGÚN MATRIZ ICANN ⬅ ICANN
    # =================================================
    tipo_rec, rol_rec, justificacion = MATRIZ_CATEGORIAS_ICANN[categoria]

    st.markdown("**Clasificación estructural del gasto (ICANN / OYKEN)**")

    c_tipo, c_rol = st.columns(2)

    with c_tipo:
        tipo_gasto = st.selectbox(
            "Tipo de gasto",
            ["Fijo", "Variable"],
            index=["Fijo", "Variable"].index(tipo_rec)
        )

    with c_rol:
        rol_gasto = st.selectbox(
            "Rol del gasto",
            ["Estructural", "No estructural"],
            index=["Estructural", "No estructural"].index(rol_rec)
        )

    if tipo_gasto != tipo_rec or rol_gasto != rol_rec:
        st.warning(
            f"Según ICANN/OYKEN esta categoría es **{tipo_rec} / {rol_rec}**.\n\n"
            f"Motivo: {justificacion}\n\n"
            f"Has decidido clasificarla como **{tipo_gasto} / {rol_gasto}**."
        )

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
            "Tipo_Gasto": tipo_gasto,   # ⬅ ICANN
            "Rol_Gasto": rol_gasto,     # ⬅ ICANN
            "Coste (€)": round(coste, 2)
        }

        st.session_state.gastos = pd.concat(
            [st.session_state.gastos, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        st.session_state.gastos.to_csv(DATA_FILE, index=False)
        st.success("Gasto registrado correctamente.")

# =====================================================
# VISUALIZACIÓN (SIN CAMBIOS)
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
# ELIMINAR REGISTRO (SIN CAMBIOS)
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
        st.session_state.gastos.drop(idx).reset_index(drop=True)
    )
    st.session_state.gastos.to_csv(DATA_FILE, index=False)
    st.success("Gasto eliminado correctamente.")

# =====================================================
# GASTOS MENSUALES · CONSOLIDADO (SIN CAMBIOS)
# =====================================================
st.divider()
st.subheader("Gastos mensuales")

GASTOS_MENSUALES_FILE = Path("gastos_mensuales.csv")

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

df_gastos = st.session_state.gastos.copy()
df_gastos["Fecha"] = pd.to_datetime(df_gastos["Fecha"], dayfirst=True, errors="coerce")
df_gastos["Coste (€)"] = pd.to_numeric(df_gastos["Coste (€)"], errors="coerce").fillna(0)

c1, c2 = st.columns(2)

anios_disponibles = sorted(df_gastos["Fecha"].dt.year.dropna().unique())
if not anios_disponibles:
    st.stop()

with c1:
    anio_sel = st.selectbox("Año", anios_disponibles, index=len(anios_disponibles) - 1)

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x]
    )

df_filtrado = df_gastos[df_gastos["Fecha"].dt.year == anio_sel]
if mes_sel != 0:
    df_filtrado = df_filtrado[df_gastos["Fecha"].dt.month == mes_sel]

datos_meses = []
for mes in range(1, 13):
    if mes_sel != 0 and mes != mes_sel:
        continue

    gasto_mes = df_filtrado[df_filtrado["Fecha"].dt.month == mes]["Coste (€)"].sum()
    datos_meses.append({"Mes": MESES_ES[mes], "Gastos del mes (€)": round(gasto_mes, 2)})

tabla_gastos = pd.DataFrame(datos_meses)

st.dataframe(tabla_gastos, hide_index=True, use_container_width=True)
st.metric("Total período seleccionado", f"{tabla_gastos['Gastos del mes (€)'].sum():,.2f} €")

# =====================================================
# CSV MENSUAL CANÓNICO (SIN CAMBIOS)
# =====================================================
if not GASTOS_MENSUALES_FILE.exists():
    pd.DataFrame(
        columns=["anio", "mes", "gastos_total_eur", "fecha_actualizacion"]
    ).to_csv(GASTOS_MENSUALES_FILE, index=False)

df_csv = tabla_gastos.copy()
df_csv["mes"] = df_csv["Mes"].map({v: k for k, v in MESES_ES.items()})
df_csv["anio"] = anio_sel
df_csv["gastos_total_eur"] = df_csv["Gastos del mes (€)"]
df_csv["fecha_actualizacion"] = datetime.now()
df_csv = df_csv[["anio", "mes", "gastos_total_eur", "fecha_actualizacion"]]

df_hist = pd.read_csv(GASTOS_MENSUALES_FILE)
df_hist = df_hist[
    ~((df_hist["anio"] == anio_sel) & (df_hist["mes"].isin(df_csv["mes"])))
]

df_final = pd.concat([df_hist, df_csv], ignore_index=True)
df_final = df_final.sort_values(["anio", "mes"])
df_final.to_csv(GASTOS_MENSUALES_FILE, index=False)
