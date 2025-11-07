import plotly.express as px
import plotly.graph_objs as go
# Colores globales
CONTRAST_COLOR = "#1fbad6"
TEXT_COLOR = "#c0c0c8"

# Estilo Plotly minimalista, fondo transparente, template tipo dark
plotly_style = {
    "template": "plotly_dark",
    "margin": dict(t=50, l=25, r=25, b=25),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "color": TEXT_COLOR,
        "family": "Inter, Roboto, 'Segoe UI', Arial, sans-serif",
        "size": 12,
    },
    "colorway": [CONTRAST_COLOR, "#6c757d", "#9ad0f5", "#f1c40f", "#e74c3c"],
    "legend": {"bgcolor": "rgba(0,0,0,0)", "borderwidth": 0, "orientation": "h"},
    "xaxis": {
        "showgrid": False,
        "zeroline": False,
        "showline": False,
        "tickfont": {"color": TEXT_COLOR},
        "titlefont": {"color": TEXT_COLOR},
    },
    "yaxis": {
        "showgrid": False,
        "zeroline": False,
        "showline": False,
        "tickfont": {"color": TEXT_COLOR},
        "titlefont": {"color": TEXT_COLOR},
    },
    "hoverlabel": {
        "font": {
            "color": TEXT_COLOR,
            "family": "Inter, Roboto, 'Segoe UI', Arial, sans-serif",
        },
        "bgcolor": "rgba(0,0,0,0.6)",
    },
}

# Tab 1
# Graficos a la izquierda del mapa
def tab1_violin_plot(filtered_data, num_trips):
    fig = px.violin(
                    filtered_data,
                    y="trip_minutes",
                    box=True,
                    points="all",
                    title=f"Distribución del Tiempo de Viaje ({num_trips} viajes)",
                    color_discrete_sequence=["#42f2f5"],
                )
    fig.update_layout(yaxis_title="Minutos de Viaje", **plotly_style)
    return fig

def tab1_treemap_pasajeros(passenger_counts, num_trips):
    """
    Genera un treemap con la frecuencia de viajes por número de pasajeros.

    Args:
        passenger_counts (pd.DataFrame): DataFrame con columnas:
            - 'passenger_count_str'
            - 'frequency'
        num_trips (int): Total de viajes para el título.

    Returns:
        plotly.graph_objects.Figure: Figura lista para renderizar.
    """

    # Construcción del treemap
    fig = px.treemap(
        passenger_counts,
        path=[px.Constant(f"{num_trips} Viajes"), "passenger_count_str"],
        values="frequency",
        title=f"Frecuencia por Nº de Pasajeros ({num_trips} viajes)",
        color="frequency",
        color_continuous_scale="Blues",
    )

    # Aplicar estilos globales
    fig.update_layout(**plotly_style)

    return fig
def tab1_violin_distancia(filtered_data, num_trips):
    """Violin de distancias."""
    fig = px.violin(
        filtered_data,
        y="trip_distance_km",
        box=True,
        points="all",
        title=f"Distribución de la Distancia de Viaje ({num_trips} viajes)",
        color_discrete_sequence=["#ffc107"],
    )
    fig.update_layout(yaxis_title="Distancia (km)", **plotly_style)
    return fig

# Tab 2
def tab1_heatmap_distritos(df_pivot, text_format, color_scale, header_text, metric_col):
    """Heatmap de promedios por distrito."""
    fig = px.imshow(
        df_pivot,
        text_auto=text_format,
        aspect="auto",
        color_continuous_scale=color_scale,
        title=header_text,
        labels=dict(
            x="Distrito de Llegada",
            y="Distrito de Salida",
            color=f"Promedio de {metric_col}",
        ),
    )
    fig.update_xaxes(side="top")
    fig.update_layout(**plotly_style)
    return fig
from plotly.subplots import make_subplots

def tab2_barras_tiempo_distancia(df_pickup, df_dropoff, borough_order, header_text):
    """Comparativa pickup/dropoff tiempo/distancia."""
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Distritos de Salida (Pickup)", "Distritos de Llegada (Dropoff)"),
        horizontal_spacing=0.05,
    )

    # Rango simétrico global
    max_val_pickup = max(df_pickup["avg_time"].max(), df_pickup["avg_distance"].max())
    max_val_dropoff = max(df_dropoff["avg_time"].max(), df_dropoff["avg_distance"].max())
    max_global = max(max_val_pickup, max_val_dropoff) * 1.1

    # Pickup
    fig.add_trace(
        go.Bar(
            y=df_pickup["borough"],
            x=-df_pickup["avg_time"],
            name="Tiempo Salida (min)",
            orientation="h",
            marker_color="#20C997"
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(
            y=df_pickup["borough"],
            x=df_pickup["avg_distance"],
            name="Distancia Salida (km)",
            orientation="h",
            marker_color="#F1C40F"
        ),
        row=1, col=1,
    )

    # Dropoff
    fig.add_trace(
        go.Bar(
            y=df_dropoff["borough"],
            x=-df_dropoff["avg_time"],
            name="Tiempo Llegada (min)",
            orientation="h",
            marker_color="#20C997"
        ),
        row=1, col=2,
    )
    fig.add_trace(
        go.Bar(
            y=df_dropoff["borough"],
            x=df_dropoff["avg_distance"],
            name="Distancia Llegada (km)",
            orientation="h",
            marker_color="#F1C40F"
        ),
        row=1, col=2,
    )

    # Layout
    fig.update_layout(
        barmode="overlay",
        title=header_text,
        # legend=dict(
        #     x=0.5, y=1.1, xanchor="center",
        #     orientation="h", bgcolor="rgba(255,255,255,0)"
        # ),
        **plotly_style,
    )

    # Ejes X simétricos
    tickvals = [i for i in range(-int(max_global), int(max_global) + 1) if i != 0]
    ticktext = [str(abs(i)) for i in tickvals]

    for col in (1, 2):
        fig.update_xaxes(
            row=1, col=col,
            range=[-max_global, max_global],
            title_text="Tiempo Medio (min) <---- | ----> Distancia Media (km)",
            tickvals=tickvals, ticktext=ticktext,
        )

    # Ejes Y
    fig.update_yaxes(
        row=1, col=1,
        title_text="Distrito",
        tickvals=borough_order,
        ticktext=borough_order,
        categoryorder="category ascending",
    )
    fig.update_yaxes(row=1, col=2, showticklabels=False)

    # Línea central
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#AAAAAA", row=1, col=1)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#AAAAAA", row=1, col=2)

    return fig

# Tab 3
def tab3_sankey_flujo(labels, sources, targets, values):
    
    """Sankey flujo financiero."""
    link_colors = [
            "green",  # fare
            "yellow",  # extra
            "yellow",  # tip
            "red",  # tolls
            "red",  # surcharge
            "green",  # profit
    ]
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=25,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="#343a40",
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                hovertemplate="Flujo: %{value:,.2f} $<extra></extra>",
            ),
        )
    )

    fig.update_layout(
        title_text="Flujo de Dinero: Desde Cobros hasta Ganancia Neta",
        font_color="white",
        **plotly_style,
    )
    return fig

# Tab 4
def tab4_co2_horario(hourly, y_vals, y_label, metric_col, title_map):
    """Barra por hora."""
    total = hourly["count"].sum()
    fig = px.bar(
        hourly,
        x="pickup_hour",
        y=y_vals,
        labels={"pickup_hour": "Hora (0-23)", y_vals: y_label},
        title=f"{title_map.get(metric_col, metric_col)} ({total} viajes en el filtro)",
        hover_data={"pickup_hour": True, y_vals: True, "count": True},
    )
    fig.update_layout(**plotly_style)
    return fig

def tab4_co2_treemap(treemap_df):
    """Treemap CO₂ por borough."""
    fig = px.treemap(
        treemap_df,
        path=["pickup_borough"],
        values="co2_kg_sum",
        title="Contribución de CO₂ por Borough (kg total)",
        hover_data={"co2_kg_sum": True},
    )
    fig.update_layout(**plotly_style)
    return fig

# Tab 5
def tab5_stem_pop(x_values, y_values, y_label, chart_title):
    """Stem & pop por hora."""
    fig = go.Figure()

    # Palos
    fig.add_trace(go.Bar(
        x=x_values,
        y=y_values,
        width=0.05,
        name="Volumen",
        marker=dict(
            color=y_values,
            colorscale="Cividis",
            showscale=True,
            colorbar_title=y_label,
        ),
    ))

    # Pops
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode="markers",
        name="Punto",
        marker=dict(
            size=10,
            color=y_values,
            colorscale="Cividis",
            showscale=False,
        ),
    ))

    # Layout
    fig.update_layout(
        title=chart_title,
        xaxis_title="Hora del Día (0-23)",
        yaxis_title=y_label,
        **plotly_style,
    )

    return fig

