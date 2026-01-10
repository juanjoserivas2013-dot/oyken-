import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.title("OYKEN · RRHH")
st.caption("Planificación estructural de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

SS_EMPRESA = 0.33
PUESTOS_FILE = Path("rrhh_puestos.csv")

# =====================================================
# UTILIDADES DE PERSISTENCIA
# =====================================================

def cargar_puestos():
    if PUESTOS_FILE.exists():
        return pd.read_csv(PUESTOS_FILE)
    return pd.DataFrame(columns=["Año", "Puesto", "Bruto anual (€)", *MESES])

def guardar_puesto(registro: dict):
    df = cargar_puestos()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(PUESTOS_FILE, index=False)

# =====================================================
# CONTEXTO DE PLANIFICACIÓN
# =====================================================

anio_activo = st.selectbox(
    "Año activo",
    list(range(2022, 2031)),
    index=list(range(2022, 2031)).index(2025),
    key="rrhh_anio_activo"
)

df_puestos = cargar_puestos()
df_puestos_anio = df_puestos[df_puestos["Año"] == anio_activo]

st.divider()

# =====================================================
# BLOQUE 1 · ALTA DE PUESTOS
# =====================================================

st.subheader("Alta de puestos")

with st.form("alta_puesto", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Salario bruto anual por persona (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Necesidad mensual del puesto (personas)**")
    cols = st.columns(6)
    necesidad = {}

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            necesidad[mes] = st.number_input(
                mes,
                min_value=0,
                step=1,
                key=f"need_{mes}"
            )

    guardar = st.form_submit_button("Guardar puesto")

    if guardar and puesto.strip():
        registro = {
            "Año": anio_activo,
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual),
            **necesidad
        }
        guardar_puesto(registro)
        st.success(f"Puesto '{puesto}' guardado para {anio_activo}")
        st.rerun()

# =====================================================
# TABLA · ESTRUCTURA DE PUESTOS
# =====================================================

st.subheader(f"Estructura de puestos — {anio_activo}")

if not df_puestos_anio.empty:
    st.dataframe(
        df_puestos_anio.drop(columns=["Año"]),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No hay puestos definidos para este año.")

st.divider()

# =====================================================
# BLOQUE 2 · COSTE DE PERSONAL (NÓMINA)
# =====================================================

st.subheader("Coste de personal — Nómina")

nominas = []

for _, row in df_puestos_anio.iterrows():
    salario_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(salario_mensual * row[mes], 2)

    nominas.append(fila)

df_nominas = pd.DataFrame(nominas)

if not df_nominas.empty:
    st.dataframe(df_nominas, hide_index=True, use_container_width=True)
else:
    st.info("Sin datos de nómina.")

st.divider()

# =====================================================
# BLOQUE 3 · SEGURIDAD SOCIAL Y COSTE EMPRESA
# =====================================================

st.subheader("Seguridad Social y coste empresarial")

aplicar_ss = st.checkbox("Aplicar Seguridad Social Empresa (33%)", value=True)

costes = []

for _, row in df_nominas.iterrows():
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss = nomina * SS_EMPRESA if aplicar_ss else 0.0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    costes.append(fila)

df_costes = pd.DataFrame(costes)

if not df_costes.empty:
    st.dataframe(df_costes, hide_index=True, use_container_width=True)
else:
    st.info("Sin datos de coste empresarial.")

st.divider()

# =====================================================
# BLOQUE 4 · TOTALES MENSUALES RRHH
# =====================================================

st.subheader("Totales mensuales RRHH")

totales = []

for mes in MESES:
    nomina = df_costes.get(f"{mes} · Nómina", pd.Series()).sum()
    ss = df_costes.get(f"{mes} · SS", pd.Series()).sum()
    coste = df_costes.get(f"{mes} · Coste Empresa", pd.Series()).sum()

    totales.append({
        "Mes": mes,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)

st.dataframe(df_totales, hide_index=True, use_container_width=True)

st.caption(
    "Este consolidado alimenta directamente la Cuenta de Resultados."
)
# =====================================================
# TOTALES MENSUALES RRHH · CONSOLIDADO (FASE 1)
# =====================================================

st.divider()
st.subheader("Totales mensuales RRHH")

from pathlib import Path
from datetime import datetime

RRHH_MENSUAL_FILE = Path("rrhh_mensual.csv")

# -------------------------
# MAPA MESES ESPAÑOL
# -------------------------
MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# -------------------------
# SELECTORES
# -------------------------
c1, c2 = st.columns(2)

with c1:
    anios_disponibles = sorted(df_puestos["Año"].unique())
    anio_sel = st.selectbox(
        "Año",
        anios_disponibles,
        index=len(anios_disponibles) - 1,
        key="anio_rrhh_mensual"
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(range(1, 13)),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x - 1],
        key="mes_rrhh_mensual"
    )

# -------------------------
# PREPARAR COSTES (ROBUSTO)
# -------------------------
df_costes_filtrado = df_costes.copy()

for col in df_costes_filtrado.columns:
    if "€" in col:
        df_costes_filtrado[col] = pd.to_numeric(
            df_costes_filtrado[col],
            errors="coerce"
        ).fillna(0)

# -------------------------
# CONSTRUCCIÓN TABLA VISIBLE
# -------------------------
totales = []

for i, mes_nombre in enumerate(MESES_ES, start=1):
    if mes_sel != 0 and i != mes_sel:
        continue

    nomina = df_costes_filtrado.get(
        f"{mes_nombre} · Nómina",
        pd.Series(dtype=float)
    ).sum()

    ss = df_costes_filtrado.get(
        f"{mes_nombre} · SS",
        pd.Series(dtype=float)
    ).sum()

    coste = df_costes_filtrado.get(
        f"{mes_nombre} · Coste Empresa",
        pd.Series(dtype=float)
    ).sum()

    totales.append({
        "Mes": mes_nombre,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)

st.dataframe(
    df_totales,
    hide_index=True,
    use_container_width=True
)

st.metric(
    "Coste RRHH período seleccionado",
    f"{df_totales['Coste Empresa (€)'].sum():,.2f} €"
)

# -------------------------
# GUARDAR CSV MENSUAL (CANÓNICO)
# -------------------------

# Crear CSV si no existe
if not RRHH_MENSUAL_FILE.exists():
    pd.DataFrame(
        columns=["anio", "mes", "rrhh_total_eur", "fecha_actualizacion"]
    ).to_csv(RRHH_MENSUAL_FILE, index=False)

# Preparar datos desde la tabla visible
df_csv = df_totales.copy()
df_csv["mes"] = df_csv["Mes"].map(
    {v: i + 1 for i, v in enumerate(MESES_ES)}
)
df_csv["anio"] = anio_sel
df_csv["rrhh_total_eur"] = df_csv["Coste Empresa (€)"]
df_csv = df_csv[["anio", "mes", "rrhh_total_eur"]]

# Cargar histórico
df_hist = pd.read_csv(RRHH_MENSUAL_FILE)

# Overwrite limpio por año + mes
# Upsert por (anio, mes): actualizar si existe, insertar si no
df_hist = df_hist.merge(
    df_csv,
    on=["anio", "mes"],
    how="outer",
    suffixes=("_old", "")
)

df_hist["rrhh_total_eur"] = df_hist["rrhh_total_eur"].fillna(
    df_hist["rrhh_total_eur_old"]
)

df_hist = df_hist[["anio", "mes", "rrhh_total_eur", "fecha_actualizacion"]]

df_csv["fecha_actualizacion"] = datetime.now()

df_final = pd.concat([df_hist, df_csv], ignore_index=True)
df_final = df_final.sort_values(["anio", "mes"])
df_final.to_csv(RRHH_MENSUAL_FILE, index=False)

