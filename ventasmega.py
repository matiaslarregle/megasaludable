import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns

# --- Cargar datos ---
df = pd.read_csv("megasaludableventas.csv")
df['Fecha'] = pd.to_datetime(df['Fecha'])

st.title("Dashboard de Ventas Megasaludable")

# --- Selección de mes o rango de meses ---
st.sidebar.header("Filtros")
opcion_filtro = st.sidebar.radio("Selecciona tipo de filtro:", ["Mes", "Rango de meses"])

if opcion_filtro == "Mes":
    mes_seleccionado = st.sidebar.text_input("Mes (YYYY-MM)", "2025-06")
    df_mes = df[df['Fecha'].dt.to_period('M') == mes_seleccionado]
else:
    rango_meses = st.sidebar.date_input("Rango de fechas", [])
    if len(rango_meses) == 2:
        inicio, fin = rango_meses
        df_mes = df[(df['Fecha'] >= pd.to_datetime(inicio)) & (df['Fecha'] <= pd.to_datetime(fin))]
    else:
        st.warning("Selecciona un rango de dos fechas")
        st.stop()

if df_mes.empty:
    st.warning("No hay datos para el mes o rango seleccionado")
    st.stop()

# ---- AGRUPAR Y TOMAR TOP 10 ----
top_cantidad = (
    df_mes.groupby('Descripcion')['Cantidad']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# Calcular top ingresos filtrado
top_ingresos = (
    df_mes.groupby('Descripcion')['Total']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

ventas_diarias = df_mes.groupby('Fecha')['Total'].sum().reset_index()

fig = plt.figure(figsize=(16,9),constrained_layout=True)
gs = fig.add_gridspec(nrows=5,ncols=7)
fig.set_facecolor('white')

ax1 = fig.add_subplot(gs[:2,:2])
ax1.set_title('[:2,:2]')
ax1.clear()
ax1.set_title(f'Top 10 Productos por Cantidad Vendida', fontsize=14, fontweight='bold')

top_cantidad_sorted = top_cantidad.sort_values(by='Cantidad', ascending=True)

ax1.barh(
    top_cantidad_sorted['Descripcion'],
    top_cantidad_sorted['Cantidad'],
    color='#34995c'
)

for i, (cantidad, producto) in enumerate(zip(top_cantidad_sorted['Cantidad'], top_cantidad_sorted['Descripcion'])):
    ax1.text(cantidad * 1.02, i, f"{cantidad:,.0f}", va='center', fontsize=9)

ax1.tick_params(axis='y', labelsize=9)
ax1.grid(axis='x', linestyle='--', alpha=0.3)

ax2 = fig.add_subplot(gs[0,2:3])
ax2.set_title('[0,2:3]')

ax4 = fig.add_subplot(gs[0,4:5])
ax4.set_title('[0,4:5]')

ax5 = fig.add_subplot(gs[:2,5:])
ax5.clear()

# Usar el DataFrame filtrado por mes
df_dia = df_mes.groupby('Fecha').agg({'Total': 'sum'}).reset_index()
df_dia['Día'] = df_dia['Fecha'].dt.day

dias_ingles_espanol_abrev = {
    'Monday': 'Lun',
    'Tuesday': 'Mar',
    'Wednesday': 'Mié',
    'Thursday': 'Jue',
    'Friday': 'Vie',
    'Saturday': 'Sáb',
    'Sunday': 'Dom'
}
df_dia['Día_semana'] = df_dia['Fecha'].dt.day_name().map(dias_ingles_espanol_abrev)
df_dia = df_dia[df_dia['Día_semana'] != 'Dom']

df_dia['Tramo_Mes'] = pd.cut(df_dia['Día'], bins=[0,10,20,31], labels=['1-10', '11-20', '21-fin'])

pivot = df_dia.pivot_table(index='Día_semana', columns='Tramo_Mes', values='Total', aggfunc='mean')
orden_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
pivot = pivot.reindex(orden_dias)

sns.heatmap(
    pivot,
    cmap='Oranges',
    annot=True,
    fmt='.0f',
    ax=ax5,
    cbar=False
)

# Quitar etiquetas de los ejes
ax5.set_xlabel("")
ax5.set_ylabel("")
ax5.set_title(f"Promedio por Día y Tramo del Mes", fontsize=12, fontweight='bold')

ax7 = fig.add_subplot(gs[1:4,2:5])

ventas_por_fecha = df_mes.groupby('Fecha')['Total'].sum().sort_index()

dias_semana_en = [fecha.strftime('%a') for fecha in ventas_por_fecha.index]
mapa_dias = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié', 'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'}
dias_semana = [mapa_dias[d] for d in dias_semana_en]

color_map = {
    'Lun': '#1f77b4', 'Mar': '#2ca02c', 'Mié': '#ff7f0e',
    'Jue': '#d62728', 'Vie': '#9467bd', 'Sáb': '#8c564b', 'Dom': '#e377c2'
}
colors = [color_map[dia] for dia in dias_semana]

ax7.clear()
ax7.set_title(f'Ventas diarias', fontsize=16, fontweight='bold')

# Línea de ventas general
ax7.plot(ventas_por_fecha.index, ventas_por_fecha.values, color='lightgray', alpha=0.6, zorder=1)

# Puntos de ventas
ax7.scatter(ventas_por_fecha.index, ventas_por_fecha.values, color=colors, s=80, zorder=3)

# Media móvil 7 días
ventas_suavizadas = ventas_por_fecha.rolling(window=7, center=True, min_periods=1).mean()
mm_line, = ax7.plot(
    ventas_suavizadas.index,
    ventas_suavizadas.values,
    color='red',
    linewidth=3,
    zorder=2,
    label='Media móvil (7 días)'
)

# Etiquetas de días
for x, y, dia in zip(ventas_por_fecha.index, ventas_por_fecha.values, dias_semana):
    ax7.text(x, y + max(ventas_por_fecha.values)*0.05, dia, fontsize=8, ha='center', va='bottom', color='black')

# Feriados
feriados = pd.to_datetime([
    '2025-03-03', '2025-03-04', '2025-03-24',
    '2025-04-02', '2025-04-18', '2025-05-01', '2025-05-25',
    '2025-06-20', '2025-07-09'
])
feriados_mes = [fecha for fecha in feriados if fecha in ventas_por_fecha.index]

feriado_line = None
if feriados_mes:
    for fecha in feriados_mes:
        feriado_line = ax7.axvline(
            fecha, color='darkblue', linestyle='--', alpha=0.3, zorder=0, label='Feriado'
        )

# Puntos de ventas muy bajas
umbral_bajo = ventas_por_fecha.mean() * 0.5
puntos_bajos = ventas_por_fecha[ventas_por_fecha < umbral_bajo]
for x, y in puntos_bajos.items():
    dia_semana = x.strftime('%a')
    color = color_map[mapa_dias[dia_semana]]
    ax7.scatter(x, y, color=color, edgecolor='white', linewidth=1.5, s=110, zorder=4)
    ax7.text(x, y - max(ventas_por_fecha.values)*0.06, f"${int(y):,}",
            fontsize=8, ha='center', va='top', color='darkred', fontweight='bold')

# Quitar ejes y ticks
ax7.set_xlabel("")
ax7.set_ylabel("")
ax7.set_xticks([])
ax7.set_yticks([])

# Leyenda dinámica
if feriado_line:
    ax7.legend([mm_line, feriado_line], ['Media móvil (7 días)', 'Feriado'], fontsize=6, loc='lower left')
else:
    ax7.legend([mm_line], ['Media móvil (7 días)'], fontsize=6, loc='lower left')


ax11 = fig.add_subplot(gs[2:4,0:2])
ax11.set_title('[2:4,0:2]')
ax11.clear()
ax11.set_title(f'Top 10 Productos por Ingresos', fontsize=14, fontweight='bold')

top_ingresos_sorted = top_ingresos.sort_values(by='Total', ascending=True)

ax11.barh(
    top_ingresos_sorted['Descripcion'],
    top_ingresos_sorted['Total'],
    color='#34995c'
)

for i, (total, producto) in enumerate(zip(top_ingresos_sorted['Total'], top_ingresos_sorted['Descripcion'])):
    ax11.text(total * 1.02, i, f"${total:,.0f}", va='center', fontsize=9)

ax11.tick_params(axis='y', labelsize=9)
ax11.grid(axis='x', linestyle='--', alpha=0.3)

ax12 = fig.add_subplot(gs[2:4,5:])
ax12.clear()
ax12.set_title('Promedio Ventas por Día', fontsize=14, fontweight='bold')

dias_map = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}
ventas_diarias['DiaSemana'] = ventas_diarias['Fecha'].dt.dayofweek.map(dias_map)

promedio_por_dia = (
    ventas_diarias.groupby('DiaSemana')['Total']
    .mean()
    .reindex(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
    .reset_index()
)

norm = plt.Normalize(promedio_por_dia['Total'].min(), promedio_por_dia['Total'].max())
cmap = plt.cm.Oranges

bars = ax12.bar(
    promedio_por_dia['DiaSemana'],
    promedio_por_dia['Total'],
    color=cmap(norm(promedio_por_dia['Total']))
)

for bar in bars:
    height = bar.get_height()
    ax12.text(
        bar.get_x() + bar.get_width() / 2,
        height * 1.01,
        f"${height:,.0f}",
        ha='center',
        va='bottom',
        fontsize=7,
        color='black'
    )

ax12.tick_params(axis='x', rotation=30)

for ax in [ax1, ax2, ax4, ax5, ax7, ax11, ax12]:
    for spine in ax.spines.values():
        spine.set_visible(False)

for ax in [ax1, ax11]:
    ax.set_xticks([])
    ax.set_xlabel("")
    ax.tick_params(left=False, bottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

for ax in [ax12]:
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.tick_params(left=False, bottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

total_mes = df_mes['Total'].sum()
ax2.clear()
ax2.axis('off')
ax2.text(
    0.5, 0.5,
    f"Total Vendido\n${total_mes:,.0f}",
    ha='center', va='center',
    fontsize=16, fontweight='bold', color='black'
)

total_boletas = df_mes['Factura'].nunique()
ax4.clear()
ax4.axis('off')
ax4.text(
    0.5, 0.5,
    f"Total Facturas\n{total_boletas:,}",
    ha='center', va='center',
    fontsize=16, fontweight='bold', color='black'
)

ax20 = fig.add_subplot(gs[0,3:4])
ax20.clear()
ax20.axis('off')
logo_path = "megasaludble.jpg"
logo_img = mpimg.imread(logo_path)
ax20.imshow(logo_img)

plt.tight_layout()
st.pyplot(fig)
