import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================
st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura automática desde bases mensuales")

DATA = Path("data")

# =========================
# SELECTOR DE PERIODO
# =========================
hoy = datetime.today()

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

mes_num = st.selectbox(
    "Mes",
    list(MESES.keys()),
    index=hoy.month - 1,
    format_func=lambda x: MESES[x]
)

anio = st.selectbox(
    "Año",
    [hoy.year - 1, hoy.year],
    index=1
)

mes = MESES[mes_num]

st.divider()

# =========================
# FUNCIÓN LECTURA BASE
# =========================
def leer_total(path, anio, mes):
    if not path.exists():
        return 0.0

    df = pd.read_csv(path)

    fila = df[(df["anio"] == anio) & (df["mes"] == mes)]
    if not fila.empty:
        return float(fila["total"].sum())

    return 0.0

def euro(valor):
    return f"{valor:,.2f} €"

# =========================
# LECTURA DE TOTALES
# =========================
ventas = leer_total(DATA / "ventas_mensuales.csv", anio, mes)
compras = leer_total(DATA / "compras_mensuales.csv", anio, mes)
inventario = leer_total(DATA / "inventario_mensual.csv", anio, mes)
mermas = leer_total(DATA / "mermas_mensual.csv", anio, mes)
rrhh = leer_total(DATA / "rrhh_mensual.csv", anio, mes)
gastos = leer_total(DATA / "gastos_mensuales.csv", anio, mes)

# =========================
# CUENTA DE RESULTADOS
# =========================
st.subheader(f"Resultado {mes} {anio}")
st.divider()

# INGRESOS
st.subheader("INGRESOS")
st.write("Ventas netas:", euro(ventas))
st.divider()

# COSTE DE VENTAS
st.subheader("COSTE DE VENTAS")
st.write("Compras:", euro(compras))
st.write("Variación de inventario:", euro(inventario))
st.write("Mermas:", euro(mermas))

coste_ventas = compras + inventario + mermas
st.write("Coste de ventas total:", euro(coste_ventas))
st.divider()

# MARGEN BRUTO
margen_bruto = ventas - coste_ventas
margen_pct = (margen_bruto / ventas * 100) if ventas > 0 else 0

st.subheader("MARGEN BRUTO")
st.write("Margen bruto €:", euro(margen_bruto))
st.write("Margen bruto %:", f"{margen_pct:.2f} %")
st.divider()

# COSTE DE PERSONAL
st.subheader("COSTE DE PERSONAL")
st.write("RRHH:", euro(rrhh))
st.divider()

# GASTOS OPERATIVOS
st.subheader("GASTOS OPERATIVOS")
st.write("Gastos generales:", euro(gastos))
st.divider()

# RESULTADO OPERATIVO
resultado_operativo = margen_bruto - rrhh - gastos
resultado_pct = (resultado_operativo / ventas * 100) if ventas > 0 else 0

st.subheader("RESULTADO OPERATIVO")
st.write("Resultado operativo €:", euro(resultado_operativo))
st.write("Resultado operativo %:", f"{resultado_pct:.2f} %")
