# =========================
# BLOQUE 3 — BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

# Formato de fecha para visualización
df_mes_view = df_mes.copy()
df_mes_view["fecha"] = df_mes_view["fecha"].dt.strftime("%d-%m-%Y")

st.dataframe(
    df_mes_view[[
        "fecha",
        "dow",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur"
    ]],
    hide_index=True,
    use_container_width=True
)
