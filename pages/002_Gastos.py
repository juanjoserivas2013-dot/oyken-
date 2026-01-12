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
                "Tipo_Gasto",   # ⬅ OYKEN
                "Rol_Gasto",    # ⬅ OYKEN
                "Coste (€)"
            ]
        )

# =====================================================
# CATEGORÍAS BASE OYKEN
# =====================================================
CATEGORIAS = [
    # 1. Estructurales fijos
    "Alquiler",
    "Hipoteca / Leasing inmueble",
    "IBI",
    "Comunidad",
    "Licencia de actividad",
    "Licencia de terraza",
    "SGAE / Música",
    "Seguros obligatorios",
    "Asesoría fiscal",
    "Asesoría laboral",
    "Asesoría autonómica",
    "PRL",
    "RGPD / LOPD",

    # 2. Estructurales variables
    "Electricidad",
    "Agua",
    "Gas",
    "Internet",
    "Telefonía",
    "Extintores",
    "Sistemas contra incendios",
    "Control de plagas",
    "Análisis sanitarios",
    "Mantenimiento cocina",
    "Reparaciones",
    "Climatización",

    # 3. Recursos Humanos
    "Salarios base",
    "Seguridad Social empresa",
    "Turnos mínimos",
    "Horas extra",
    "Eventuales",
    "Sustituciones",

    # 4. Costes variables directos
    "Materia prima",
    "Bebidas",
    "Packaging",
    "Consumibles de servicio",
    "Mermas",
    "Desperdicio",

    # 5. Plataformas y cobro
    "Comisiones datáfonos",
    "Comisiones bancarias",
    "Plataformas delivery",
    "Pasarelas de pago",

    # 6. Operativos no estructurales
    "Limpieza externa",
    "Lavandería",
    "Uniformes",
    "Utensilios",
    "Papelería",

    # 7. Discrecionales / tácticos
    "Marketing",
    "Redes sociales",
    "Eventos",
    "Formación no obligatoria",
    "Consultoría estratégica",
    "Innovación / pruebas"
]

# =====================================================
# MATRIZ OYKEN · CLASIFICACIÓN EXPERTA
# =====================================================
MATRIZ_CATEGORIAS_OYKEN = {
    # 1. Estructurales fijos
    "Alquiler": ("Fijo", "Estructural", "Ancla del modelo operativo."),
    "Hipoteca / Leasing inmueble": ("Fijo", "Estructural", "Financiación del espacio."),
    "IBI": ("Fijo", "Estructural", "Coste país no controlable."),
    "Comunidad": ("Fijo", "Estructural", "Obligación del inmueble."),
    "Licencia de actividad": ("Fijo", "Estructural", "Permiso legal."),
    "Licencia de terraza": ("Fijo", "Estructural", "Uso de vía pública."),
    "SGAE / Música": ("Fijo", "Estructural", "Derechos obligatorios."),
    "Seguros obligatorios": ("Fijo", "Estructural", "Blindaje legal."),
    "Asesoría fiscal": ("Fijo", "Estructural", "Cumplimiento fiscal."),
    "Asesoría laboral": ("Fijo", "Estructural", "Cumplimiento laboral."),
    "Asesoría autonómica": ("Fijo", "Estructural", "Sanidad y normativa."),
    "PRL": ("Fijo", "Estructural", "Prevención obligatoria."),
    "RGPD / LOPD": ("Fijo", "Estructural", "Protección de datos."),

    # 2. Estructurales variables
    "Electricidad": ("Variable", "Estructural", "Consumo mínimo operativo."),
    "Agua": ("Variable", "Estructural", "Consumo sanitario."),
    "Gas": ("Variable", "Estructural", "Producción térmica."),
    "Internet": ("Mixto", "Estructural", "Infraestructura digital."),
    "Telefonía": ("Mixto", "Estructural", "Comunicación operativa."),
    "Extintores": ("Variable", "Estructural", "Prevención incendios."),
    "Sistemas contra incendios": ("Variable", "Estructural", "Seguridad."),
    "Control de plagas": ("Variable", "Estructural", "Higiene obligatoria."),
    "Análisis sanitarios": ("Variable", "Estructural", "Cumplimiento sanitario."),
    "Mantenimiento cocina": ("Variable", "Estructural", "Continuidad productiva."),
    "Reparaciones": ("Variable", "Estructural", "Fragilidad operativa."),
    "Climatización": ("Variable", "Estructural", "Confort mínimo."),

    # 3. RRHH
    "Salarios base": ("Fijo", "Estructural", "Suelo humano."),
    "Seguridad Social empresa": ("Fijo", "Estructural", "Coste país."),
    "Turnos mínimos": ("Fijo", "Estructural", "Cobertura mínima."),
    "Horas extra": ("Variable", "Operativo", "Picos de carga."),
    "Eventuales": ("Variable", "Operativo", "Elasticidad."),
    "Sustituciones": ("Variable", "Estructural", "Riesgo oculto."),

    # 4. Directos
    "Materia prima": ("Variable", "Directo", "Margen."),
    "Bebidas": ("Variable", "Directo", "Cash generator."),
    "Packaging": ("Variable", "Directo", "Delivery tax."),
    "Consumibles de servicio": ("Variable", "Directo", "Microcostes."),
    "Mermas": ("Variable", "Directo", "Ineficiencia."),
    "Desperdicio": ("Variable", "Directo", "Fuga de margen."),

    # 5. Cobros
    "Comisiones datáfonos": ("Variable", "Directo", "Impuesto invisible."),
    "Comisiones bancarias": ("Variable", "Operativo", "Fricción financiera."),
    "Plataformas delivery": ("Variable", "Directo", "Erosión de margen."),
    "Pasarelas de pago": ("Variable", "Directo", "Escalabilidad."),

    # 6. Operativos no estructurales
    "Limpieza externa": ("Variable", "Operativo", "Externalización."),
    "Lavandería": ("Variable", "Operativo", "Servicio."),
    "Uniformes": ("Variable", "Operativo", "Imagen."),
    "Utensilios": ("Variable", "Operativo", "Desgaste."),
    "Papelería": ("Variable", "Operativo", "Residual."),

    # 7. Discrecionales
    "Marketing": ("Variable", "No estructural", "Acelerador."),
    "Redes sociales": ("Variable", "No estructural", "Marca."),
    "Eventos": ("Variable", "No estructural", "Volatilidad."),
    "Formación no obligatoria": ("Variable", "No estructural", "Upside."),
    "Consultoría estratégica": ("Variable", "No estructural", "Retorno esperado."),
    "Innovación / pruebas": ("Variable", "No estructural", "Riesgo controlado.")
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
    # CLASIFICACIÓN ESTRUCTURAL SEGÚN MATRIZ OYKEN
    # =================================================
    tipo_rec, rol_rec, justificacion = MATRIZ_CATEGORIAS_OYKEN[categoria]

    st.markdown("**Clasificación estructural del gasto (OYKEN)**")

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
            f"Según OYKEN esta categoría es **{tipo_rec} / {rol_rec}**.\n\n"
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
            "Tipo_Gasto": tipo_gasto,   # ⬅ OYKEN
            "Rol_Gasto": rol_gasto,     # ⬅ OYKEN
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
    datos_meses.append({
        "Mes": MESES_ES[mes],
        "Gastos del mes (€)": round(gasto_mes, 2)
    })

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
