import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# CONFIGURACIÓN BÁSICA
# =========================
st.title("OYKEN · Cuenta de Resultados")
st.caption("Estado financiero operativo")

# =========================
# ARCHIVOS DE DATOS
# =========================
VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
INVENTARIO_FILE = Path("inventario.csv")
MERMAS_FILE = Path("mermas.csv")
GASTOS_FILE = Path("gastos.csv")
RRHH_FILE = Path("rrhh.csv")

# =========================
# SELECTOR DE PERIODO
# =========================
hoy = datetime.today()
mes = st.selectbox(
    "Periodo",
    list(range(1, 13)),
    index=hoy.month - 1,
    format_func=lambda x: datetime(2000, x, 1).strftime("%B")
)
anio = st.selectbox("Año", [hoy.year - 1, hoy.year], index=1)

st.divider()

# =========================
# FUNCIONES AUXILIARES
# =========================
def cargar_df(path, fecha_col=None):
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if fecha_col and fecha_col in df.columns:
        df[fecha_col] = pd.to_datetime(df[fecha_col])
    return df

def filtrar_periodo(df, fecha_col):
    return df[
        (df[fecha_col].dt.month == mes) &
        (df[fecha_col].dt.year == anio)
    ]

def euro(valor):
    return f"{valor:,.2f} €"

# =========================
# CARGA DE DATOS
# =========================
ventas = filtrar_periodo(
    cargar_df(VENTAS_FILE, "fecha"),
    "fecha"
)

compras = filtrar_periodo(
    cargar_df(COMPRAS_FILE, "Fecha"),
    "Fecha"
)

inventario = cargar_df(INVENTARIO_FILE)
mermas = filtrar_periodo(
    cargar_df(MERMAS_FILE, "Fecha"),
    "Fecha"
)

gastos = filtrar_periodo(
    cargar_df(GASTOS_FILE, "Fecha"),
    "Fecha"
)

rrhh = filtrar_periodo(
    cargar_df(RRHH_FILE, "Fecha"),
    "Fecha"
)

# =========================
# INGRESOS
# =========================
ventas_totales = ventas["ventas_total_eur"].sum() if not ventas.empty else 0

st.subheader("INGRESOS")
st.write("Ventas totales:", euro(ventas_totales))
st.divider()

# =========================
# COSTE DE VENTAS
# =========================
compras_total = compras["Coste (€)"].sum() if not compras.empty else 0
mermas_total = mermas["Cantidad"].sum() if not mermas.empty else 0

inv_inicial = inventario.loc[
    (inventario["Mes"] == mes) & (inventario["Tipo"] == "Inicial"),
    "Valor"
].sum() if not inventario.empty else 0

inv_final = inventario.loc[
    (inventario["Mes"] == mes) & (inventario["Tipo"] == "Final"),
    "Valor"
].sum() if not inventario.empty else 0

variacion_inventario = inv_final - inv_inicial
coste_ventas = compras_total + variacion_inventario + mermas_total

st.subheader("COSTE DE VENTAS")
st.write("Compras imputadas:", euro(compras_total))
st.write("Variación de inventario:", euro(variacion_inventario))
st.write("Mermas:", euro(mermas_total))
st.write("Coste de ventas total:", euro(coste_ventas))
st.divider()

# =========================
# MARGEN BRUTO
# =========================
margen_bruto = ventas_totales - coste_ventas
margen_pct = (margen_bruto / ventas_totales * 100) if ventas_totales > 0 else 0

st.subheader("MARGEN BRUTO")
st.write("Margen bruto €:", euro(margen_bruto))
st.write("Margen bruto %:", f"{margen_pct:.2f} %")
st.divider()

# =========================
# COSTE DE PERSONAL
# =========================
coste_salarial = rrhh["Coste Salarial"].sum() if not rrhh.empty else 0
seg_social = rrhh["Seguridad Social"].sum() if not rrhh.empty else 0
total_personal = coste_salarial + seg_social

st.subheader("COSTE DE PERSONAL")
st.write("Coste salarial:", euro(coste_salarial))
st.write("Seguridad social empresa:", euro(seg_social))
st.write("Total personal:", euro(total_personal))
st.divider()

# =========================
# GASTOS POR BLOQUES
# =========================
def gastos_por_familia(nombre):
    return gastos.loc[gastos["Familia"] == nombre, "Coste (€)"].sum()

alquiler = gastos_por_familia("Alquiler")
suministros = gastos_por_familia("Suministros")
operativos = gastos_por_familia("Operativos")
mantenimiento = gastos_por_familia("Mantenimiento")
seguros = gastos_por_familia("Seguros")
financieros = gastos_por_familia("Financieros")
marketing = gastos_por_familia("Marketing")
servicios = gastos_por_familia("Servicios")
otros = gastos_por_familia("Otros")

st.subheader("GASTOS OPERATIVOS")
st.write("Alquiler:", euro(alquiler))
st.write("Suministros:", euro(suministros))
st.write("Gastos operativos:", euro(operativos))
st.write("Mantenimiento:", euro(mantenimiento))
st.write("Seguros:", euro(seguros))
st.write("Financieros:", euro(financieros))
st.write("Marketing:", euro(marketing))
st.write("Servicios profesionales:", euro(servicios))
st.write("Otros gastos:", euro(otros))
st.divider()

# =========================
# RESULTADO OPERATIVO
# =========================
total_gastos = (
    total_personal + alquiler + suministros + operativos +
    mantenimiento + seguros + financieros + marketing +
    servicios + otros
)

resultado_operativo = margen_bruto - total_gastos
resultado_pct = (resultado_operativo / ventas_totales * 100) if ventas_totales > 0 else 0

st.subheader("RESULTADO OPERATIVO")
st.write("Resultado operativo €:", euro(resultado_operativo))
st.write("Resultado operativo %:", f"{resultado_pct:.2f} %")
