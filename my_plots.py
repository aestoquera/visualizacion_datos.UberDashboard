import plotly.express as px
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
        "size": 14,  # un poco más grande que antes
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
            line=dict(width=0)  # sin bordes para look más moderno
        ),
        root_color="rgba(0,0,0,0)"  # fondo transparente para el root
    )

    # Layout global (usando tu style dict)
    fig.update_layout(
        **plotly_style,
        showlegend=False,
        title=dict(
            font=dict(size=20, family="Inter, Roboto", color=TEXT_COLOR),
            x=0.18,  # centrado relativo (moderno)
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

