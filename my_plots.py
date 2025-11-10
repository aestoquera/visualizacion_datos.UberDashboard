import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
# Colores globales
CONTRAST_COLOR = "#5a9ce7"
TEXT_COLOR = "#c0c0c8"

# Estilo Plotly minimalista, fondo transparente, template tipo dark
plotly_style = {
    "template": "plotly_dark",
    "margin": dict(t=50, l=25, r=25, b=25),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "color": TEXT_COLOR,
        "family": "Montserrat, 'Fira Sans', Poppins, 'Fira Sans', Montserrat, sans-serif",
        "size": 14, 
    },
    "colorway": [CONTRAST_COLOR, "#6c757d", "#9ad0f5", "#f1c40f", "#e74c3c"],
    #"legend": {"bgcolor": "rgba(0,0,0,0)", "borderwidth": 0, "orientation": "h"},
    "coloraxis_showscale":False,
    "xaxis": {
        "showgrid": True,
        "zeroline": False,
        "showline": True,
        "tickfont": {"color": TEXT_COLOR},
        "titlefont": {"color": TEXT_COLOR},
    },
    "yaxis": {
        "showgrid": True,
        "zeroline": False,
        "showline": True,
        "tickfont": {"color": TEXT_COLOR},
        "titlefont": {"color": TEXT_COLOR},
    },
    # "hoverlabel": {
    #     "font": {
    #         "color": TEXT_COLOR,
    #         "family": "Inter, Roboto, 'Segoe UI', Arial, sans-serif",
    #     },
    #     "bgcolor": "rgba(0,0,0,0.6)",
    # },
    "hoverlabel":{
        
            "bgcolor":"rgba(0,0,0,0.7)",
            "font_size":12,
            "font_family":"Inter"
    }
    
}

# Tab 1
# Graficos a la izquierda del mapa
def stylize_violin(fig, data, column_name, ylabel):
    import numpy as np

    vals = data[column_name].dropna().values
    q1, q2, q3 = np.percentile(vals, [25, 50, 75])
    vmin, vmax = vals.min(), vals.max()
    median = np.median(vals)

    # Hover limpio modern UI
    fig.update_traces(
        hovertemplate="<span style='font-size:13px'><b>%{y:.2f}</b> " + ylabel + "</span><extra></extra>",
        line=dict(width=1.2, color=CONTRAST_COLOR),
        hoveron="violins",
        opacity=0.92
    )


    # Layout global brand-driven
    fig.update_layout(
        **plotly_style,
        title=dict(
            font=dict(size=20, family="Inter, Roboto", color=TEXT_COLOR),
            x=0.18,
            y=0.95,
        ),
        yaxis_title=ylabel,
        transition=dict(duration=250, easing="cubic-in-out"),
        violinmode="overlay",
    )

    # Caja flotante UI-chip style
    x_pos = -0.25
    spacing = (vmax - vmin) * 0.055

    def add_box(label, y):
        fig.add_annotation(
            x=x_pos,
            y=y,
            text=label,
            showarrow=False,
            xanchor="right",
            font=dict(color=TEXT_COLOR, size=11, family="Inter"),
            align="center",
            bgcolor="rgba(31,186,214,0.11)",
            bordercolor=CONTRAST_COLOR,
            borderwidth=1,
            borderpad=6,
            opacity=0.95,
            yanchor="middle"
        )
    fig.update_layout(hovermode=False)

    add_box(f"Min: {vmin:.1f}", vmin)
    add_box(f"Q1: {q1:.1f}", q1 + spacing)
    add_box(f"Mediana: {median:.1f}", median + spacing * 2)
    add_box(f"Q3: {q3:.1f}", q3 + spacing * 3)
    add_box(f"Max: {vmax:.1f}", vmax + spacing)

    # Etiqueta responsiva
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")

    return fig
def tab1_violin_plot(filtered_data, num_trips):
    fig = px.violin(
        filtered_data,
        y="trip_minutes",
        box=True,
        points=None,
        title=f"<b>Distribución del Tiempo de Viaje</b><br><sup>{num_trips:,} viajes analizados</sup>",
        color_discrete_sequence=[CONTRAST_COLOR],
    )
    fig = stylize_violin(fig, filtered_data, "trip_minutes", "Minutos de Viaje")
    return fig
def tab1_violin_distancia(filtered_data, num_trips):
    fig = px.violin(
        filtered_data,
        y="trip_distance_km",
        box=True,
        points=None,
        title=f"<b>Distribución de la Distancia de Viaje</b><br><sup>{num_trips:,} viajes analizados</sup>",
        color_discrete_sequence=[CONTRAST_COLOR],
    )
    fig = stylize_violin(fig, filtered_data, "trip_distance_km", "Distancia (km)")
    return fig


def tab1_treemap_pasajeros(passenger_counts, num_trips):
    """
    Genera un treemap con estética moderna y minimalista (brand-driven)
    """

    # Construcción del treemap
    fig = px.treemap(
        passenger_counts,
        path=[
            px.Constant(f"Total: {num_trips:,} Viajes"),
            "passenger_count_str",
        ],
        values="frequency",
        color="frequency",
        color_continuous_scale=[
            "#00123a",  # fondo bajo (dark matte)
            "#7bb9ff",  # contraste/acento
        ],
        title=f"<b>Frecuencia por Nº de Pasajeros</b><br><sup>{num_trips:,} viajes analizados</sup>",
    )

    # Estilo visual minimalista
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,}",
        hovertemplate="<b>%{label}</b><br>Viajes: %{value:,}<extra></extra>",
        marker=dict(
            line=dict(width=0)  
        ),
        root_color="rgba(0,0,0,0)"  # fondo transparente para el root
    )

    # Layout global (usando tu style dict)
    fig.update_layout(
        **plotly_style,
        showlegend=False,
        title=dict(
            font=dict(size=20, family="Inter, Roboto", color=TEXT_COLOR),
            x=0.18,  # centrado relativo 
            y=0.95,
        ),
        coloraxis_colorbar=dict(
            thickness=14,
            outlinewidth=0,
            tickfont=dict(size=12, color=TEXT_COLOR),
        ),
        transition=dict(duration=250, easing="cubic-in-out"),
    )

    # Responsividad
    fig.update_layout(
        autosize=True,
        uniformtext_minsize=12,
        uniformtext_mode="hide"
    )

    return fig

# Tab 2
def tab1_heatmap_distritos(df_pivot, df_count, text_format, color_scale, metric_col):

    fig = px.imshow(
        df_pivot,
        text_auto=text_format,
        aspect="auto",
        color_continuous_scale=color_scale,
        labels=dict(
            x="Distrito de Llegada",
            y="Distrito de Salida",
            color=f"Promedio de {metric_col}",
        ),
        title=None,
    )

    # Hacemos una copia de plotly_style y aumentamos font general
    updated_plotly_style = plotly_style.copy()
    updated_plotly_style["font"] = dict(
        size=14,  # fuente más grande para todo el gráfico
        family="Inter, Roboto",
        color=TEXT_COLOR
    )

    fig.update_layout(
        **updated_plotly_style,
        showlegend=False,
        coloraxis_colorbar=dict(
            thickness=12,
            outlinewidth=0,
            tickfont=dict(size=11, color=TEXT_COLOR),
        ),
        transition=dict(duration=250, easing="cubic-in-out"),
    )

    # Texto dentro de celdas + hover + borde de celdas
    fig.update_traces(
        hovertemplate="<b>%{x} → %{y}</b><br>Promedio: %{z:.2f}<br>Viajes: %{customdata}<extra></extra>",
        showscale=True,
        selector=dict(type="heatmap"),
        customdata=df_count.values,  # Número de viajes
        xgap=3,  # grosor de la división entre celdas
        ygap=3,
    )

    return fig


from plotly.subplots import make_subplots
def tab2_radar_tiempo_distancia(df_pickup, df_dropoff, borough_order, header_text):
    """
    Comparativa en telaraña:
    Gráfico 1: Distancias (Salida vs Llegada)
    Gráfico 2: Tiempos (Salida vs Llegada)
    """

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "polar"}, {"type": "polar"}]],
        # --- Nuevos Títulos ---
        subplot_titles=("Comparativa de Distancias (km)", "Comparativa de Tiempos (min)"),
        horizontal_spacing=0.1,
    )

    # --- 1. Calcular Rangos Separados ---
    max_dist = max(df_pickup["avg_distance"].max(), df_dropoff["avg_distance"].max()) * 1.15
    max_time = max(df_pickup["avg_time"].max(), df_dropoff["avg_time"].max()) * 1.15

    # --- 2. Preparar Datos para Radar ---
    df_pickup = df_pickup.set_index('borough').loc[borough_order].reset_index()
    df_dropoff = df_dropoff.set_index('borough').loc[borough_order].reset_index()

    # Cerrar el bucle del radar
    theta_labels = borough_order + [borough_order[0]]

    # Listas de datos
    r_pickup_time = df_pickup["avg_time"].tolist() + [df_pickup["avg_time"].iloc[0]]
    r_pickup_dist = df_pickup["avg_distance"].tolist() + [df_pickup["avg_distance"].iloc[0]]
    r_dropoff_time = df_dropoff["avg_time"].tolist() + [df_dropoff["avg_time"].iloc[0]]
    r_dropoff_dist = df_dropoff["avg_distance"].tolist() + [df_dropoff["avg_distance"].iloc[0]]

    # --- 3. Definir Colores y Rellenos ---
    COLOR_SALIDA = "#5DADE2"  # Azul
    COLOR_LLEGADA = "#8E44AD" # Morado
    
    FILL_SALIDA = "rgba(93, 173, 226, 0.4)"  # Azul 40%
    FILL_LLEGADA = "rgba(142, 68, 173, 0.4)" # Morado 40%

    # --- 4. Añadir Trazados (Traces) ---
    # --- Gráfico 1: Distancias ---
    
    # Salida (Distancia)
    fig.add_trace(go.Scatterpolar(
        r=r_pickup_dist,
        theta=theta_labels,
        name="Salida",             # Para la leyenda
        legendgroup="salida",     # Para agrupar leyendas
        fill='toself',
        fillcolor=FILL_SALIDA,
        line=dict(color=COLOR_SALIDA, width=2.5),
        hovertemplate='<b>Salida (Dist)</b><br>%{theta}: %{r:.1f} km<extra></extra>'
    ), row=1, col=1)

    # Llegada (Distancia)
    fig.add_trace(go.Scatterpolar(
        r=r_dropoff_dist,
        theta=theta_labels,
        name="Llegada",            # Para la leyenda
        legendgroup="llegada",    # Para agrupar leyendas
        fill='toself',
        fillcolor=FILL_LLEGADA,
        line=dict(color=COLOR_LLEGADA, width=2.5),
        hovertemplate='<b>Llegada (Dist)</b><br>%{theta}: %{r:.1f} km<extra></extra>'
    ), row=1, col=1)

    # --- Gráfico 2: Tiempos ---

    # Salida (Tiempo)
    fig.add_trace(go.Scatterpolar(
        r=r_pickup_time,
        theta=theta_labels,
        name="Salida",
        legendgroup="salida",
        showlegend=False,         # Ocultar leyenda duplicada
        fill='toself',
        fillcolor=FILL_SALIDA,
        line=dict(color=COLOR_SALIDA, width=2.5),
        hovertemplate='<b>Salida (Tiempo)</b><br>%{theta}: %{r:.1f} min<extra></extra>'
    ), row=1, col=2)

    # Llegada (Tiempo)
    fig.add_trace(go.Scatterpolar(
        r=r_dropoff_time,
        theta=theta_labels,
        name="Llegada",
        legendgroup="llegada",
        showlegend=False,         # Ocultar leyenda duplicada
        fill='toself',
        fillcolor=FILL_LLEGADA,
        line=dict(color=COLOR_LLEGADA, width=2.5),
        hovertemplate='<b>Llegada (Tiempo)</b><br>%{theta}: %{r:.1f} min<extra></extra>'
    ), row=1, col=2)

    # --- 5. Aplicar Layout y Estilo ---
    fig.update_layout(
        title="",
        **plotly_style,  # Aplicar el estilo modificado
        
        # Asignar los rangos radiales separados
        polar1_radialaxis_range=[0, max_dist],
        polar2_radialaxis_range=[0, max_time],
    )

    # Ajustar la fuente de los títulos de los subplots
    fig.update_annotations(font_size=16, y=1.05)

    return fig
# Tab 3
import copy
def tab3_sankey_flujo(labels, sources, targets, values):
    """Sankey flujo financiero."""
    
    # Asumiendo el orden: fare, extra, tip, tolls, surcharge, profit
    link_colors_rgba = [
        "#0b4d19",   # Ingreso principal (Verde)
        "#7e7500",  # Ingreso secundario (Dorado)
        "#7e7500",  # Ingreso secundario (Dorado)
        "#700000",   # Costo (Rojo suave)
        "#700000",   # Costo (Rojo suave)
        "#0b4d19",   # Ganancia (Verde más sólido)
    ]
    
    # Colores para los nodos y sus bordes
    node_color = "#5D6D7E"
    node_line_color = "#BDC3C7"

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=25,
                thickness=20,
                line=dict(color=node_line_color, width=0.5),
                label=labels,
                color=node_color,
                # Hovertemplate mejorado para nodos
                hovertemplate="<b>Nodo:</b> %{label}<br><b>Total Acumulado:</b> $%{value:,.2f}<extra></extra>"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors_rgba,
                # Hovertemplate mejorado para flujos
                hovertemplate="<b>De:</b> %{source.label}<br><b>A:</b> %{target.label}<br><b>Monto:</b> $%{value:,.2f}<extra></extra>"
            ),
        )
    )
    plotly_style_2 = copy.deepcopy(plotly_style)
    plotly_style_2["font"]["color"] = "#ffffff"
    fig.update_layout(
        title_text="",
        font_color="white",
        **plotly_style_2,
        # Anotaciones para dar contexto a las columnas
        annotations=[
            dict(
                text="INGRESOS",
                x=0.05,
                y=1.05,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#cccccc"),
                xanchor="left"
            ),
            dict(
                text="COSTOS Y CARGOS",
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#cccccc"),
                xanchor="center"
            ),
            dict(
                text="RESULTADO NETO",
                x=0.95,
                y=1.05,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#cccccc"),
                xanchor="right"
            )
        ]
    )
    return fig

# Tab 4
def tab4_co2_horario(hourly, y_vals, y_label, metric_col, title_map):
    """
    Barra por hora con preatención monocromática, transparencia y anotación.
    """
    
    # Asegurarse de que hourly es un DataFrame
    if not isinstance(hourly, pd.DataFrame):
        hourly = pd.DataFrame(hourly)

    # --- 1. Preparación de Preatención Monocromática ---
    
    # Definición de colores
    try:
        highlight_color = CONTRAST_COLOR
        base_color = "#434268" 
    except NameError:
        highlight_color = '#5a9ce7' # Default
        base_color = "#4274a0"     # Default

    # Encontrar el valor máximo de la métrica y su índice
    max_val = hourly[y_vals].max()

    # Crear la columna de color: asigna el color base a todas las filas
    hourly['color_category'] = base_color
    
    # Asigna el color de contraste a la fila con el valor máximo
    hourly.loc[hourly[y_vals] == max_val, 'color_category'] = highlight_color
    
    # --- 2. Creación del Gráfico (con Plotly Express) ---

    total = hourly["count"].sum()
    
    # Usamos 'color_category' para asignar los colores individuales
    fig = px.bar(
        hourly,
        x="pickup_hour",
        y=y_vals,
        color='color_category', # Usamos la columna calculada para el color
        color_discrete_map={base_color: base_color, highlight_color: highlight_color}, # Mapeo para asegurar los colores
        labels={"pickup_hour": "Hora (0-23)", y_vals: y_label},
        title=f"<b>{title_map.get(metric_col, metric_col)}</b> por Hora ({total:,.0f} viajes en el filtro)",
        hover_data={"pickup_hour": True, y_vals: ':.2f', "count": True},
    )

    # --- 3. Aplicación de Conceptos de Visualización Avanzada (go.Figure) ---

    # Aplicar transparencia (Opacidad) a todas las barras
    fig.update_traces(opacity=0.7)
    
    # Mejorar la estética del hover (se hereda de plotly_style, pero lo aseguramos)
    fig.update_traces(hovertemplate=f"<b>Hora:</b> %{{x}}<br><b>{y_label}:</b> %{{y:,.0f}}<extra></extra>")
    
    # Ocultar la leyenda de colores, ya que es redundante (solo tenemos dos colores: base y max)
    fig.update_layout(showlegend=False)

    # --- 4. Anotación de Etiqueta de Datos (Refuerzo Preatentivo) ---

    # Encontrar la hora correspondiente al máximo
    max_hour = hourly.loc[hourly[y_vals] == max_val, "pickup_hour"].iloc[0]
    
    # Añadir una anotación de texto encima de la barra máxima
    fig.add_annotation(
        x=max_hour,
        y=max_val,
        text=f"<b>Pico:</b><br>{max_val:,.0f}",
        showarrow=True,
        arrowhead=7, # Estilo de flecha simple y limpio
        arrowcolor=highlight_color,
        arrowwidth=1.5,
        ax=0,   # Posición horizontal de la cola (centrado)
        ay=-30, # Desplazamiento vertical del texto (30px sobre la punta de la flecha)
        font=dict(size=14, color=highlight_color),
        bordercolor=highlight_color,
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(0,0,0,0.8)" # Fondo oscuro para resaltar
    )

    # --- 5. Layout Final ---
    fig.update_layout(
        xaxis_title="Hora del Día (0-23)",
        yaxis_title=y_label,
        **plotly_style,
    )
    
    # Asegurar el color del título del gráfico
    fig.update_layout(title=dict(text=fig.layout.title.text, font=dict(color=TEXT_COLOR)))

    return fig

def tab4_co2_treemap(treemap_df):
    """
    Treemap CO₂ por borough con estética moderna, minimalista y legible.
    """
    
    # 1. Cálculo de métricas y ruta jerárquica
    total_co2_kg = treemap_df["co2_kg_sum"].sum()

    # Definición de la escala de color moderna y de contraste
    color_scale = [
        "#00123a",  # Fondo bajo (dark matte)
        "#7bb9ff",  # Contraste/acento
    ]

    # 2. Construcción del treemap
    fig = px.treemap(
        treemap_df,
        # Añadimos la raíz con el total para un contexto jerárquico claro
        path=[
            px.Constant(f"Total CO₂: {total_co2_kg:,.0f} kg"),
            "pickup_borough",
        ],
        values="co2_kg_sum",
        color="co2_kg_sum",  # Colorear por la misma métrica (CO2)
        color_continuous_scale=color_scale,
        title=f"<b>Emisiones de CO₂ por Borough</b><br><sup>Total: {total_co2_kg:,.0f} kg de CO₂</sup>",
        hover_data={"co2_kg_sum": True},
    )

    # 3. Estilo visual minimalista y legible
    fig.update_traces(
        # Formato de texto: Etiqueta (Borough) y valor (CO2), con formato de miles
        texttemplate="<b>%{label}</b><br>%{value:,.0f} kg",
        hovertemplate="<b>%{label}</b><br>CO₂ emitido: %{value:,.0f} kg<extra></extra>",
        marker=dict(
            line=dict(width=0)  # Sin bordes (look moderno y limpio)
        ),
        root_color="rgba(0,0,0,0)"  # Fondo transparente para el root
    )

    # 4. Layout global (usando tu style dict)
    fig.update_layout(
        **plotly_style,
        showlegend=False,
        # Ajuste del título para centrado relativo y fuente
        title=dict(
            font=dict(size=20, family=plotly_style.get("font", {}).get("family", "Inter, Roboto"), color=TEXT_COLOR),
            x=0.18,  # Ajuste para centrado visual en el dashboard
            y=0.95,
        ),
        # Ajuste de la barra de color
        coloraxis_colorbar=dict(
            title="CO₂ (kg)",
            thickness=14,
            outlinewidth=0,
            tickfont=dict(size=12, color=TEXT_COLOR),
        ),
        transition=dict(duration=250, easing="cubic-in-out"),
        autosize=True,
        uniformtext_minsize=12,
        uniformtext_mode="hide"
    )

    return fig

# Tab 5
def tab5_stem_pop(x_values, y_values, y_label, chart_title):
    """
    Stem & pop por hora con paleta monocromática, 
    preatención en el máximo y anotación de flecha.
    """

    # --- 1. Preparación de Preatención ---
    
    # Asegurarnos de que trabajamos con Series de Pandas para usar idxmax
    if not isinstance(y_values, pd.Series):
         y_values = pd.Series(y_values)
    if not isinstance(x_values, pd.Series):
         # Alinear índices es crucial si y_values fue re-indexado
         x_values = pd.Series(x_values, index=y_values.index) 

    # Encontrar el valor máximo y su índice
    max_val = y_values.max()
    max_idx = y_values.idxmax()
    max_x = x_values[max_idx]

    # Crear listas de colores y tamaños para destacar el máximo
    base_color = "#4a006d"  # Tu color base
    highlight_color = CONTRAST_COLOR # El color de contraste principal

    # Lista de colores: todos base menos el máximo
    colors_list = [base_color] * len(x_values)
    # CORRECCIÓN: Aplicar directamente el color al índice máximo
    colors_list[max_idx] = highlight_color

    # Lista de tamaños: el máximo será más grande
    sizes_list = [10] * len(x_values)
    # CORRECCIÓN: Aplicar directamente el tamaño al índice máximo
    sizes_list[max_idx] = 16
        
    # Lista de anchos de línea: el máximo será más grueso
    stem_width_list = [0.03] * len(x_values)
    # CORRECCIÓN: Aplicar directamente el grosor al índice máximo
    stem_width_list[max_idx] = 0.06


    fig = go.Figure()

    # --- 2. Trazado de Palos (Stems) ---
    fig.add_trace(go.Bar(
        x=x_values,
        y=y_values,
        width=stem_width_list, # Anchos variables
        name="Volumen",
        marker=dict(
            color=colors_list, # Aplicamos la lista de colores
        ),
        hoverinfo="none" # Desactivamos hover para los palos
    ))

    # --- 3. Trazado de Pops (Markers) ---
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode="markers",
        name="Punto",
        marker=dict(
            size=sizes_list,  # Aplicamos lista de tamaños
            color=colors_list,  # Aplicamos lista de colores
            line=dict(color='white', width=1) # Borde blanco para definir el círculo
        ),
        # Hovertemplate mejorado para dar formato
        hovertemplate=f"<b>Hora:</b> %{{x}}:00<br><b>{y_label}:</b> %{{y:,.0f}}<extra></extra>"
    ))

    # --- 4. Anotación de Flecha Curva ---
    
    # Lógica para la posición del texto (evitar que se salga de la pantalla)
    if max_x > 18: # Si el pico está al final del eje X
        ax_offset = -40 # Mover el texto a la izquierda
        align = "right"
    elif max_x < 4: # Si el pico está al principio
        ax_offset = 40 # Mover el texto a la derecha
        align = "left"
    else: # Centrado
        ax_offset = 40 # Mover el texto a la derecha por defecto
        align = "left"

    fig.add_annotation(
        x=max_x,
        y=max_val,
        text=f"<b>Pico máximo:</b><br>{max_val:,.0f}", # Texto de la anotación
        showarrow=True,
        arrowhead=2,           # Estilo de flecha
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor=highlight_color, # Color de la flecha
        
        ax=ax_offset,          # Desplazamiento X de la *cola* de la flecha (controla curvatura)
        ay=-50,                # Desplazamiento Y de la *cola* (negativo = arriba)
        
        font=dict(size=13, color=highlight_color),
        align=align,
        bordercolor=highlight_color,
        borderwidth=1.5,
        borderpad=4,
        bgcolor=plotly_style.get("plot_bgcolor", "rgba(0,0,0,0.7)"), # Fondo del plot
        opacity=0.9
    )
    plotly_style_2 = copy.deepcopy(plotly_style)
    plotly_style_2.pop("xaxis", None)
    plotly_style_2.pop("yaxis", None)
    # --- 5. Layout Final ---
    fig.update_layout(
        title=chart_title,
        xaxis_title="Hora del Día (0-23)",
        yaxis_title=y_label,
        showlegend=False, # La leyenda "Volumen" y "Punto" no aporta valor
        
        # --- Ejes mejorados ---
        xaxis=dict(
            tickmode='linear', # Forzar ticks para cada hora
            dtick=1
        ),
        yaxis=dict(
            rangemode="tozero" # Asegurar que el eje Y empiece en 0
        ),
        # --- Fin ejes ---
        
        **plotly_style_2,
    )
    
    # Asegurar que los estilos de hover se apliquen correctamente
    fig.update_layout(hoverlabel=plotly_style.get('hoverlabel'))

    return fig
