import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="OYKEN · EBITDA",
    layout="centered"
)

st.title("OYKEN · EBITDA")
st.caption("Rentabilidad operativa consolidada")

# =========================
# ARCHIVOS CANÓNICOS
# =========================
VENTAS_FILE = Path("ventas_mensuales.csv")
COMPRAS_FILE = Path("compras_mensuales.csv")
RRHH_FILE = Path("rrhh_mensual.csv")

if not VENTAS_FILE.exists() or not COMPRAS_FILE.exists() or not RRHH_FILE.exists():
    st.warning("Aún no existen cierres mensuales suficientes.")
    st.stop()

# =========================
# CARGA DE DATOS
# =========================
df_v = pd.read_csv(VENTAS_FILE)
df_c = pd.read_csv(COMPRAS_FILE)
df_r = pd.read_csv(RRHH_FILE)

# Normalizar tipos
for df in [df_v, df_c, df_r]:
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")

df_v["ventas_total_eur"] = pd.to_numeric(
    df_v["ventas_total_eur"], errors="coerce"
).fillna(0)

df_c["compras_total_eur"] = pd.to_numeric(
    df_c["compras_total_eur"], errors="coerce"
).fillna(0)

df_r["rrhh_total_eur"] = pd.to_numeric(
    df_r["rrhh_total_eur"], errors="coerce"
).fillna(0)

# =========================
# SELECTORES
# =========================
anios_disponibles = sorted(
    set(df_v["anio"].dropna().unique())
    | set(df_c["anio"].dropna().unique())
    | set(df_r["anio"].dropna().unique())
)

if not anios_disponibles:
    st.info("No hay datos suficientes para calcular EBITDA.")
    st.stop()

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        anios_disponibles,
        index=len(anios_disponibles) - 1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(range(1, 13)),
        format_func=lambda x: "Todos los meses" if x == 0 else [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

# =========================
# FILTRADO POR AÑO / MES
# =========================
df_v = df_v[df_v["anio"] == anio_sel]
df_c = df_c[df_c["anio"] == anio_sel]
df_r = df_r[df_r["anio"] == anio_sel]

if mes_sel != 0:
    df_v = df_v[df_v["mes"] == mes_sel]
    df_c = df_c[df_c["mes"] == mes_sel]
    df_r = df_r[df_r["mes"] == mes_sel]

# =========================
# CRUCE MENSUAL Y CÁLCULO
# =========================
df_base = pd.DataFrame({"mes": range(1, 13)})

df_base = df_base.merge(
    df_v[["mes", "ventas_total_eur"]],
    on="mes",
    how="left"
)

df_base = df_base.merge(
    df_c[["mes", "compras_total_eur"]],
    on="mes",
    how="left"
)

df_base = df_base.merge(
    df_r[["mes", "rrhh_total_eur"]],
    on="mes",
    how="left"
)

df_base = df_base.fillna(0)

df_base["ebitda_eur"] = (
    df_base["ventas_total_eur"]
    - df_base["compras_total_eur"]
    - df_base["rrhh_total_eur"]
)

# Aplicar filtro visual de mes
if mes_sel != 0:
    df_base = df_base[df_base["mes"] == mes_sel]

# Orden cronológico correcto
df_base = df_base.sort_values("mes")

# =========================
# PRESENTACIÓN TABLA
# =========================
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

df_base["Mes"] = df_base["mes"].map(MESES_ES)

tabla_ebitda = df_base[[
    "Mes",
    "ventas_total_eur",
    "compras_total_eur",
    "rrhh_total_eur",
    "ebitda_eur"
]].rename(columns={
    "ventas_total_eur": "Ventas (€)",
    "compras_total_eur": "Compras (€)",
    "rrhh_total_eur": "RRHH (€)",
    "ebitda_eur": "EBITDA (€)"
})

st.divider()
st.subheader("EBITDA · Detalle mensual")

st.dataframe(
    tabla_ebitda,
    hide_index=True,
    use_container_width=True
)
