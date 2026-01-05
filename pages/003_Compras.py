import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================

st.title("OYKEN · Compras")
st.divider()

# =========================
# ARCHIVOS
# =========================
COMPRAS_FILE = Path("compras.csv")
PROVEEDORES_FILE = Path("proveedores.csv")

# =========================
# ESTADO: PROVEEDORES (MAESTRO)
# =========================
if "proveedores" not in st.session_state:
    if PROVEEDORES_FILE.exists():
        st.session_state.proveedores = (
            pd.read_csv(PROVEEDORES_FILE)["Proveedor"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
    else:
        st.session_state.proveedores = []

# Normalizar y ordenar siempre
st.session_state.proveedores = sorted(
    set(st.session_state.proveedores),
    key=lambda x: x.upper()
)

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

        if not nombre:
            st.stop()

        existentes_upper = [p.upper() for p in st.session_state.proveedores]

        if nombre.upper() in existentes_upper:
            st.warning("Este proveedor ya existe. No se ha guardado.")
            st.stop()

        st.session_state.proveedores.append(nombre)

        # Normalizar, ordenar y persistir
        st.session_state.proveedores = sorted(
            set(st.session_state.proveedores),
            key=lambda x: x.upper()
        )

        pd.DataFrame(
            {"Proveedor": st.session_state.proveedores}
        ).to_csv(PROVEEDORES_FILE, index=False)

        st.success("Proveedor guardado")

if st.session_state.proveedores:
    st.markdown("**Proveedores existentes**")

    proveedores = st.session_state.proveedores
    filas = [proveedores[i:i+3] for i in range(0, len(proveedores), 3)]

    for fila in filas:
        cols = st.columns(3)
        for i, proveedor in enumerate(fila):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        padding: 8px 12px;
                        text-align: center;
                        font-weight: 500;
                        background-color: #fafafa;
                        ">
                        {proveedor}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


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

# =========================================================
# COMPRAS MENSUALES · CONSOLIDADO (FASE 1)
# =========================================================

st.divider()
st.subheader("Compras mensuales")

from pathlib import Path
from datetime import datetime

COMPRAS_MENSUALES_FILE = Path("compras_mensuales.csv")

# -------------------------
# MAPA MESES ESPAÑOL
# -------------------------
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# -------------------------
# PREPARAR DATOS OPERATIVOS
# -------------------------
df_compras = st.session_state.compras.copy()

df_compras["Fecha"] = pd.to_datetime(
    df_compras["Fecha"],
    dayfirst=True,
    errors="coerce"
)

df_compras["Coste (€)"] = pd.to_numeric(
    df_compras["Coste (€)"],
    errors="coerce"
).fillna(0)

# -------------------------
# SELECTORES
# -------------------------
c1, c2 = st.columns(2)

with c1:
    anios_disponibles = sorted(
        df_compras["Fecha"].dt.year.dropna().unique()
    )
    anio_sel = st.selectbox(
        "Año",
        anios_disponibles,
        index=len(anios_disponibles) - 1,
        key="anio_compras_mensual"
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x],
        key="mes_compras_mensual"
    )

# -------------------------
# FILTRADO OPERATIVO
# -------------------------
df_filtrado = df_compras[
    df_compras["Fecha"].dt.year == anio_sel
]

if mes_sel != 0:
    df_filtrado = df_filtrado[
        df_filtrado["Fecha"].dt.month == mes_sel
    ]

# -------------------------
# CONSTRUCCIÓN TABLA MENSUAL (VISIBLE)
# -------------------------
datos_meses = []

for mes in range(1, 13):
    if mes_sel != 0 and mes != mes_sel:
        continue

    total_mes = df_filtrado[
        df_filtrado["Fecha"].dt.month == mes
    ]["Coste (€)"].sum()

    datos_meses.append({
        "Mes": MESES_ES[mes],
        "Compras del mes (€)": round(total_mes, 2)
    })

tabla_compras_mensuales = pd.DataFrame(datos_meses)

st.dataframe(
    tabla_compras_mensuales,
    hide_index=True,
    use_container_width=True
)

st.metric(
    "Total período seleccionado",
    f"{tabla_compras_mensuales['Compras del mes (€)'].sum():,.2f} €"
)

# -------------------------
# GUARDAR CSV MENSUAL (CANÓNICO)
# -------------------------

# Crear CSV si no existe
if not COMPRAS_MENSUALES_FILE.exists():
    pd.DataFrame(
        columns=["anio", "mes", "compras_total_eur", "fecha_actualizacion"]
    ).to_csv(COMPRAS_MENSUALES_FILE, index=False)

# Preparar datos a guardar (desde la tabla visible)
df_csv = tabla_compras_mensuales.copy()

df_csv["mes"] = df_csv["Mes"].map(
    {v: k for k, v in MESES_ES.items()}
)
df_csv["anio"] = anio_sel
df_csv["compras_total_eur"] = df_csv["Compras del mes (€)"]

df_csv = df_csv[["anio", "mes", "compras_total_eur"]]

# Cargar histórico
df_hist = pd.read_csv(COMPRAS_MENSUALES_FILE)

# Eliminar meses existentes del mismo año (overwrite limpio)
df_hist = df_hist[
    ~(
        (df_hist["anio"] == anio_sel) &
        (df_hist["mes"].isin(df_csv["mes"]))
    )
]

# Añadir timestamp
df_csv["fecha_actualizacion"] = datetime.now()

# Guardar final
df_final = pd.concat([df_hist, df_csv], ignore_index=True)
df_final = df_final.sort_values(["anio", "mes"])
df_final.to_csv(COMPRAS_MENSUALES_FILE, index=False)
