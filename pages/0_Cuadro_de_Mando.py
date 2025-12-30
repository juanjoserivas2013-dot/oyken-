import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIG
# =========================

st.title("Cuadro de Mandos")

DATA = Path("data")

# =========================
# SELECTORES
# =========================
anio = st.selectbox(
    "Año",
    options=list(range(2023, 2031)),
    index=2  # 2025 por defecto si empieza en 2023
)

# =========================
# CARGA DE VENTAS
# =========================
ventas_path = DATA / "ventas_mensuales.csv"

if ventas_path.exists():
    df_ventas = pd.read_csv(ventas_path)

    # Asegurar tipos
    df_ventas["anio"] = df_ventas["anio"].astype(int)
    df_ventas["mes"] = df_ventas["mes"].astype(int)
    df_ventas["total"] = df_ventas["total"].astype(float)

    # Filtrar año
    df_ventas_anio = df_ventas[df_ventas["anio"] == anio]

else:
    df_ventas_anio = pd.DataFrame(
        {
            "anio": [anio] * 12,
            "mes": list(range(1, 13)),
            "total": [0.0] * 12
        }
    )

# =========================
# TABLA BASE CUADRO DE MANDOS (SOLO VENTAS)
# =========================
meses_nombre = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

base = pd.DataFrame({
    "Mes": [meses_nombre[m] for m in range(1, 13)],
    "Ventas (€)": [
        df_ventas_anio[df_ventas_anio["mes"] == m]["total"].sum()
        for m in range(1, 13)
    ]
})

# =========================
# VISUALIZACIÓN
# =========================
st.subheader(f"Ventas mensuales – {anio}")
st.dataframe(base, use_container_width=True)

st.metric(
    "Total anual ventas",
    f"{base['Ventas (€)'].sum():,.2f} €"
)
