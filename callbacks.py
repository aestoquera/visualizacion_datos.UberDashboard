# callbacks.py
# Contiene toda la lógica de callbacks de la aplicación.

import pandas as pd
import dash
from dash import Input, Output, State, ALL, ctx, html
import dash_leaflet as dl
import plotly.express as px
import plotly.graph_objects as go
import random

# Importar variables de datos y layout
from data import data, pickup_markers, dropoff_markers, green_icon, red_icon, ICON_MAP
from layout import viajes_content, distritos_content, pagos_content, evolucion_content

DEFAULT_PAYMENT_TYPE = "Otros"

def register_callbacks(app):
    
    # CALLBACK para RENDERIZAR el contenido de la pestaña
    @app.callback(
        Output('content-div', 'children'),
        Input('tabs', 'active_tab')
    )
    def render_tab_content(active_tab):
        if active_tab == "tab-viajes":
            return viajes_content
        elif active_tab == "tab-distritos":
            return distritos_content
        elif active_tab == "tab-pagos":
            # --- AÑADIDO ---
            return pagos_content 
        elif active_tab == "tab-evolucion":
            return evolucion_content
        return html.Div(html.P("Selecciona una pestaña."))


    # CALLBACK 1: Alternar vistas del mapa
    @app.callback(
        Output("map", "children"),
        Output("toggle-view-btn", "children"),
        Output("map", "center"),
        Output("map", "zoom"),
        Output("map-memory", "data"), 
        Input("toggle-view-btn", "n_clicks"),
        # **QUITAR: prevent_initial_call=True**
        # AL NO USAR prevent_initial_call=True, SE EJECUTA AL INICIO (n_clicks=None)
    )
    def toggle_view(n_clicks):
        if data.empty:
            raise dash.exceptions.PreventUpdate

        # Si n_clicks es None (carga inicial), se interpreta como 0, lo que significa mostrar pickups.
        # Si n_clicks existe, se alterna el módulo.
        show_pickups = (n_clicks or 0) % 2 == 0
        
        if show_pickups:
            visible_markers = pickup_markers
            button_text = "Mostrando salidas"
        else:
            visible_markers = dropoff_markers
            button_text = "Mostrando llegadas"
            
        # Usar las coordenadas pre-calculadas para la vista global
        # Esto es crucial para restablecer el mapa
        lat_center = data['pickup_latitude'].median()
        lon_center = data['pickup_longitude'].median()
        default_center = [lat_center, lon_center]
        default_zoom = 13
        
        # **Asegurar que siempre retorna la vista GLOBAL y el estado 'global_view'**
        return [dl.TileLayer()] + visible_markers, button_text, default_center, default_zoom, 'global_view'

    # CALLBACK 2: Enfocar en un viaje
    @app.callback(
        Output("map", "children", allow_duplicate=True),
        Output("map", "center", allow_duplicate=True),
        Output("map", "zoom", allow_duplicate=True),
        Output("map-memory", "data", allow_duplicate=True), 
        Input({"type": "pickup_marker", "index": ALL}, "n_clicks"),
        Input({"type": "dropoff_marker", "index": ALL}, "n_clicks"),
        State("map-memory", "data"), 
        prevent_initial_call=True
    )
    def focus_on_trip(pickup_clicks, dropoff_clicks, current_map_state):
        triggered = ctx.triggered_id
        if not triggered or data.empty:
            raise dash.exceptions.PreventUpdate
        if current_map_state == 'global_view':
            return dash.no_update, dash.no_update, dash.no_update, 'idle'
        
        idx = triggered["index"]
        row = data.iloc[idx]
        
        popup_content = html.Div([
            html.H5("🚖 Información del viaje", className="text-dark"),
            html.P(f"👤 Pasajeros: {row['passenger_count']}"),
            html.P(f"💰 Total: ${row['total_amount']:.2f}"),
            html.P(f"⏱️ Duración: {row['trip_minutes']:.1f} min"),
            html.P(f"🛣️ Distancia: {row['trip_distance_km']:.2f} km")
        ], className="text-secondary")

        pickup = dl.Marker(
            position=(row['pickup_latitude'], row['pickup_longitude']),
            icon=green_icon,
            children=[dl.Tooltip("Salida"), dl.Popup(popup_content)],
        )
        dropoff = dl.Marker(
            position=(row['dropoff_latitude'], row['dropoff_longitude']),
            icon=red_icon,
            children=[dl.Tooltip("Llegada"), dl.Popup(popup_content)],
        )
        lat_center = pd.Series([row['pickup_latitude'], row['dropoff_latitude']]).median()
        lon_center = pd.Series([row['pickup_longitude'], row['dropoff_longitude']]).median()
        new_children = [dl.TileLayer()] + [pickup, dropoff]
        new_center = [lat_center, lon_center]
        new_zoom = 13 
        return new_children, new_center, new_zoom, 'isolated_view'


    # CALLBACK 3: FILTRAR DATOS POR ZOOM Y ACTUALIZAR INFORMACIÓN DE ÁREA
    @app.callback(
        Output('map-info', 'children'),
        Output('filtered-data-store', 'data'),
        Input('map', 'bounds'),
        State('toggle-view-btn', 'children'),
    )
    def filter_data_by_bounds(bounds, current_view):
        if data.empty:
            info_text = html.Div([html.P("No hay datos cargados.", className="mb-0 small")])
            return info_text, []
            
        df = data.copy() 
        
        if not bounds:
            info_text = html.Div([
                html.P(f"Viajes visibles: {len(df)} / {len(df)} (Global)", className="mb-0 small"),
            ])
            return info_text, df.to_dict('records')

        lat_min, lon_min = bounds[0]
        lat_max, lon_max = bounds[1]
        
        if "salidas" in current_view.lower():
            lat_col = 'pickup_latitude'
            lon_col = 'pickup_longitude'
        else:
            lat_col = 'dropoff_latitude'
            lon_col = 'dropoff_longitude'

        filtered_data = df[
            (df[lat_col] >= lat_min) & (df[lat_col] <= lat_max) &
            (df[lon_col] >= lon_min) & (df[lon_col] <= lon_max)
        ]
        
        num_trips = len(filtered_data)
        
        info_text = html.Div([
            html.P(f"Viajes visibles: {num_trips} / {len(df)}", className="mb-0 small"),
            html.P(f"Sup. Izda: Lat {lat_max:.4f}, Lon {lon_min:.4f}", className="mb-0 small"),
            html.P(f"Inf. Dcha: Lat {lat_min:.4f}, Lon {lon_max:.4f}", className="mb-0 small"),
        ])
        
        return info_text, filtered_data.to_dict('records')

    # CALLBACK 4: GENERAR GRÁFICOS USANDO LOS DATOS FILTRADOS
    @app.callback(
        Output('analysis-graph', 'figure'),
        Input('analysis-dropdown', 'value'),
        Input('filtered-data-store', 'data')
    )
    def update_analysis_graph(selected_value, filtered_data_dict):
        
        plotly_style = {
            'template': 'plotly_dark',
            'margin': dict(t=50, l=25, r=25, b=25)
        }
        
        if not filtered_data_dict or len(filtered_data_dict) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos visibles en el área del mapa.",
                                xref="paper", yref="paper",
                                x=0.5, y=0.5, showarrow=False,
                                font=dict(size=16, color="#AAAAAA"))
            fig.update_layout(title="Ajuste el Zoom", **plotly_style)
            return fig
        
        filtered_data = pd.DataFrame(filtered_data_dict)
        num_trips = len(filtered_data)
        
        # 1. Gráfico de Pasajeros (Treemap)
        if selected_value == 'passengers':
            passenger_counts = filtered_data['passenger_count'].value_counts().reset_index()
            passenger_counts.columns = ['passenger_count', 'frequency']
            passenger_counts['passenger_count_str'] = passenger_counts['passenger_count'].astype(str) + ' Pasajeros'
            
            fig = px.treemap(passenger_counts, 
                             path=[px.Constant(f"{num_trips} Viajes"), 'passenger_count_str'], 
                             values='frequency',
                             title=f'Frecuencia por Nº de Pasajeros ({num_trips} viajes)',
                             color='frequency',
                             color_continuous_scale='Blues')
            fig.update_layout(**plotly_style)
            return fig

        # 2. Distribución de Tiempo (Violin Plot)
        elif selected_value == 'trip_time':
            fig = px.violin(filtered_data, 
                            y="trip_minutes", 
                            box=True,
                            points="all",
                            title=f'Distribución del Tiempo de Viaje ({num_trips} viajes)',
                            color_discrete_sequence=['#42f2f5'])
            fig.update_layout(yaxis_title="Minutos de Viaje", **plotly_style)
            return fig

        # 3. Distribución de Distancia (Violin Plot)
        elif selected_value == 'trip_distance':
            fig = px.violin(filtered_data, 
                            y="trip_distance_km", 
                            box=True, 
                            points="all",
                            title=f'Distribución de la Distancia de Viaje ({num_trips} viajes)',
                            color_discrete_sequence=['#ffc107'])
            fig.update_layout(yaxis_title="Distancia (km)", **plotly_style)
            return fig

        return go.Figure(**plotly_style)

    # ----------------------------------------------------------------------
    # --- CALLBACK 5: ACTUALIZAR GRÁFICO DE DISTRITOS ---
    # ----------------------------------------------------------------------

    @app.callback(
        Output('distritos-graph', 'figure'),
        Output('distritos-graph-header', 'children'),
        Input('distritos-dropdown', 'value')
    )
    def update_distritos_graph(selected_metric):
        
        plotly_style = {
            'template': 'plotly_dark',
            'margin': dict(t=50, l=25, r=25, b=25)
        }

        # Comprobar datos
        if data.empty or 'pickup_borough' not in data.columns or 'dropoff_borough' not in data.columns:
            fig = go.Figure()
            fig.add_annotation(text="Datos de distrito ('pickup_borough'/'dropoff_borough') no encontrados.",
                               xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=16, color="#AAAAAA"))
            fig.update_layout(title="Error: Datos Incompletos", **plotly_style)
            return fig, "Error en la Carga de Datos"

        df_trips = data.copy()

        # ---------------------------------------
        # --- OPCIONES DE MAPA DE CALOR ---
        # ---------------------------------------
        if selected_metric in ['distance', 'time']:
            
            if selected_metric == 'distance':
                metric_col = 'trip_distance_km'
                header_text = 'Matriz de Distancia Promedio (km) entre Distritos'
                color_scale = 'Blues' 
                text_format = ".2f"    
            else:
                metric_col = 'trip_minutes'
                header_text = 'Matriz de Tiempo Promedio (min) entre Distritos'
                color_scale = 'Greens'
                text_format = ".1f"   
            
            # Agrupar y pivotar para el Heatmap (Origen x Destino)
            df_agg = df_trips.groupby(['pickup_borough', 'dropoff_borough'])[metric_col].mean().reset_index()
            df_pivot = df_agg.pivot(
                index='pickup_borough',      # Origen (Eje Y)
                columns='dropoff_borough',   # Destino (Eje X)
                values=metric_col
            )
            df_pivot = df_pivot.fillna(0) # Rellenar NaNs con 0 (viajes que no ocurren)

            fig = px.imshow(
                df_pivot,
                text_auto=text_format, 
                aspect="auto",
                color_continuous_scale=color_scale,
                title=header_text,
                labels=dict(x="Distrito de Llegada", y="Distrito de Salida", color=f"Promedio de {metric_col}")
            )
            
            fig.update_xaxes(side="top")
            fig.update_layout(**plotly_style)
            return fig, header_text

        # ---------------------------------------
        # --- OPCIÓN DE PIRÁMIDE (TIME vs DISTANCE) ---
        # ---------------------------------------
        elif selected_metric == 'pyramid':
      
            header_text = 'Doble Pirámide de Flujo: Métrica Promedio por Distrito (Salida vs. Llegada)'

            # --- 1. Agregar datos por Origen (Salida) ---
            df_pickup = df_trips.groupby('pickup_borough').agg(
                avg_time=('trip_minutes', 'mean'),
                avg_distance=('trip_distance_km', 'mean')
            ).reset_index().rename(columns={'pickup_borough': 'borough'})
            
            # --- 2. Agregar datos por Destino (Llegada) ---
            df_dropoff = df_trips.groupby('dropoff_borough').agg(
                avg_time=('trip_minutes', 'mean'),
                avg_distance=('trip_distance_km', 'mean')
            ).reset_index().rename(columns={'dropoff_borough': 'borough'})

            # Aseguramos que el orden de los distritos (eje Y) es consistente
            borough_order = sorted(df_pickup['borough'].unique())
            df_pickup['borough'] = pd.Categorical(df_pickup['borough'], categories=borough_order, ordered=True)
            df_dropoff['borough'] = pd.Categorical(df_dropoff['borough'], categories=borough_order, ordered=True)
            df_pickup = df_pickup.sort_values('borough')
            df_dropoff = df_dropoff.sort_values('borough')

            # --- 3. Crear Sub-plots ---
            # Es necesario importar make_subplots al principio del archivo: from plotly.subplots import make_subplots
            from plotly.subplots import make_subplots 
                    
            fig = make_subplots(
                rows=1, 
                cols=2, 
                subplot_titles=("Distritos de Salida (Pickup)", "Distritos de Llegada (Dropoff)"),
                        horizontal_spacing=0.05
            )

            # Definir el rango máximo para que ambos subplots tengan el mismo eje X simétrico
            max_val_pickup = max(df_pickup['avg_time'].max(), df_pickup['avg_distance'].max())
            max_val_dropoff = max(df_dropoff['avg_time'].max(), df_dropoff['avg_distance'].max())
            max_global = max(max_val_pickup, max_val_dropoff) * 1.1

            # --- SUBPLOT 1: SALIDAS (Pickup) ---
            # Tiempo Medio (Izquierda, barras negativas)
            fig.add_trace(go.Bar(
                y=df_pickup['borough'],
                x=-df_pickup['avg_time'],
                name='Tiempo Salida (min)',
                orientation='h',
                marker_color='#20C997', 
                        showlegend=True
            ), row=1, col=1)

            # Distancia Media (Derecha, barras positivas)
            fig.add_trace(go.Bar(
                y=df_pickup['borough'],
                x=df_pickup['avg_distance'],
                name='Distancia Salida (km)',
                orientation='h',
                marker_color='#F1C40F', 
                        showlegend=True
            ), row=1, col=1)


            # --- SUBPLOT 2: LLEGADAS (Dropoff) ---
            # Tiempo Medio (Izquierda, barras negativas)
            fig.add_trace(go.Bar(
                y=df_dropoff['borough'],
                x=-df_dropoff['avg_time'],
                name='Tiempo Llegada (min)',
                orientation='h',
                marker_color='#20C997', 
                        showlegend=False # La leyenda es compartida
            ), row=1, col=2)

            # Distancia Media (Derecha, barras positivas)
            fig.add_trace(go.Bar(
                y=df_dropoff['borough'],
                x=df_dropoff['avg_distance'],
                name='Distancia Llegada (km)',
                orientation='h',
                marker_color='#F1C40F',
                        showlegend=False # La leyenda es compartida
            ), row=1, col=2)

            # --- 4. Configuración del Layout ---
            # Configuración general
            fig.update_layout(
                barmode='overlay',
                title=header_text,
                legend=dict(x=0.5, y=1.1, xanchor='center', orientation='h', bgcolor='rgba(255, 255, 255, 0)'),
                **plotly_style
            )

            # Configuración Eje X (Subplot 1 - Salida)
            fig.update_xaxes(
                row=1, col=1,
                range=[-max_global, max_global], 
                title_text="Tiempo Medio (min) <---- | ----> Distancia Media (km)",
                tickvals=[i for i in range(-int(max_global), int(max_global) + 1) if i != 0],
                ticktext=[str(abs(i)) for i in range(-int(max_global), int(max_global) + 1) if i != 0]
            )
            # Configuración Eje X (Subplot 2 - Llegada)
            fig.update_xaxes(
                row=1, col=2,
                range=[-max_global, max_global], 
                title_text="Tiempo Medio (min) <---- | ----> Distancia Media (km)",
                tickvals=[i for i in range(-int(max_global), int(max_global) + 1) if i != 0],
                ticktext=[str(abs(i)) for i in range(-int(max_global), int(max_global) + 1) if i != 0]
            )

            # Configuración Eje Y (Compartido)
            # Solo mostrar los labels del Eje Y en el sub-plot de Salida (izquierda)
            fig.update_yaxes(
                row=1, col=1,
                title_text="Distrito",
                tickvals=borough_order,
                ticktext=borough_order,
                categoryorder='category ascending' 
            )
            fig.update_yaxes(
                row=1, col=2,
                showticklabels=False # Ocultar labels para el segundo sub-plot
            )
            
            # Agregar línea central para ambas pirámides
            fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#AAAAAA", row=1, col=1)
            fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#AAAAAA", row=1, col=2)
            
            return fig, header_text

        # En caso de que se seleccione un valor no manejado
        fig = go.Figure()
        fig.update_layout(title="Selecciona una opción válida", **plotly_style)
        return fig, "Selección Inválida"
    
    # ----------------------------------------------------------------------
    # --- CALLBACK 6: GENERAR GRÁFICO SANKEY (PESTAÑA PAGOS) ---
    # ----------------------------------------------------------------------
    @app.callback(
        Output('sankey-graph', 'figure'),
        Input('tabs', 'active_tab')
    )
    def update_sankey_graph(active_tab):
        # Solo calcular si la pestaña de pagos está activa
        if active_tab != "tab-pagos" or data.empty:
            raise dash.exceptions.PreventUpdate

        # --- Lógica de Datos Sankey ---
        
        # 1. Calcular sumas de los flujos de entrada
        s_fare = data['fare_amount'].sum()
        s_extra = data['extra'].sum()
        s_tip = data['tip_amount'].sum()
        
        # El "Total Bruto" es la suma de los componentes que fluyen a él
        s_total_bruto = s_fare + s_extra + s_tip 
        # (Nota: Omitimos mta_tax según la especificación)

        # 2. Calcular sumas de los flujos de salida (Deducciones)
        s_tolls = data['tolls_amount'].sum()
        s_surcharge = data['improvement_surcharge'].sum()
        
        # 3. Calcular Ganancia Neta (PROFIT)
        # Usamos total_amount (que incluye TODO) menos las deducciones especificadas
        s_profit = data['total_amount'].sum() - s_tolls - s_surcharge
        
        # Definición de Nodos y Flujos
        labels = [
            # Nodos de Origen (Col 1)
            "Tarifa (fare_amount)",  # 0
            "Extras (extra)",        # 1
            "Propina (tip_amount)",  # 2
            
            # Nodo Intermedio (Col 2)
            "Total Bruto",           # 3
            
            # Nodos de Destino (Col 3 y 4)
            "Peajes (tolls)",        # 4
            "Recargo (surcharge)",   # 5
            "GANANCIA NETA (Profit)" # 6
        ]
        
        sources = [0, 1, 2, 3, 3, 3] # Índices de 'labels'
        targets = [3, 3, 3, 4, 5, 6] # Índices de 'labels'
        values = [
            s_fare, 
            s_extra, 
            s_tip, 
            s_tolls, 
            s_surcharge, 
            s_profit
        ]
        
        # Colores de los flujos
        link_colors = [
            "green",  # fare
            "green",  # extra
            "yellow", # tip
            "gray",   # tolls
            "gray",   # surcharge
            "green"   # profit
        ]

        # --- Creación de la Figura ---
        fig = go.Figure(go.Sankey(
            arrangement="snap", # Alinea los nodos verticalmente
            node=dict(
                pad=25,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="#343a40" # Color oscuro para los nodos
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                hovertemplate='Flujo: %{value:,.2f} $<extra></extra>'
            )
        ))

        fig.update_layout(
            title_text="Flujo de Dinero: Desde Cobros hasta Ganancia Neta",
            font_color="white",
            paper_bgcolor="#222222", # Color de fondo oscuro
            plot_bgcolor="#222222",
            margin=dict(l=20, r=20, b=20, t=50)
        )
        
        return fig

    # ----------------------------------------------------------------------
    # --- CALLBACK 7: GENERAR WAFFLE PLOT (GRÁFICO INVERTIDO) ---
    # ----------------------------------------------------------------------
    @app.callback(
        Output('waffle-plot-container', 'children'),
        Input('tabs', 'active_tab')
    )
    def update_waffle_plot(active_tab):
        if active_tab != "tab-pagos" or data.empty:
            raise dash.exceptions.PreventUpdate
        
        # ... (Pasos 1, 2, 3a, 3b, 3c, 3d - sin cambios) ...
        df_waffle = data.copy()
        # q1 = df_waffle['total_amount'].quantile(0.25)
        # q2 = df_waffle['total_amount'].quantile(0.50)
        # q3 = df_waffle['total_amount'].quantile(0.75)
        q1 = 10
        q2 = 15
        q3 = 20
        q_max = df_waffle['total_amount'].max()
        bin_labels = [
            f"$0.00 - ${q1:.2f}",
            f"${q1 + 0.01:.2f} - ${q2:.2f}",
            f"${q2 + 0.01:.2f} - ${q3:.2f}",
            f"${q3 + 0.01:.2f} - ${q_max:.2f}"
        ]
        bins = [0, q1, q2, q3, q_max]
        df_waffle['price_bin'] = pd.cut(
            df_waffle['total_amount'], 
            bins=bins, 
            labels=bin_labels, 
            include_lowest=True
        )
        tipos_conocidos = set(ICON_MAP.keys())
        df_waffle['payment_type_str'] = df_waffle['payment_type'].apply(
            lambda x: x if x in tipos_conocidos else DEFAULT_PAYMENT_TYPE
        )
        df_grouped = df_waffle.groupby(
            ['price_bin', 'payment_type_str'], 
            observed=False
        ).size().unstack(fill_value=0)
        df_norm = df_grouped.div(df_grouped.sum(axis=1), axis=0).fillna(0) 

        bin_counts = df_grouped.sum(axis=1)
        max_count = bin_counts.max()
        proportional_heights = (bin_counts / max_count * 100).round().astype(int)

        # Orden de apilamiento: Más frecuente abajo.
        # PERO, como el gráfico se invierte, para que el MÁS FRECUENTE esté ABAJO VISUALMENTE
        # (aunque la barra se llene de arriba abajo), seguiremos el mismo orden
        # de sorted_types_by_volume para los bloques coloreados, y la inversión 
        # visual se hará al colocar los empty blocks.
        overall_frequency = df_waffle['payment_type_str'].value_counts()
        sorted_types_by_volume = overall_frequency.sort_values(ascending=False).index.tolist() 

        # --- 4. Generación de HTML ---
        
        # Leyenda (Sin cambios)
        legend_items = []
        legend_order = sorted(ICON_MAP.keys()) 
        for payment_type in legend_order:
            if payment_type in ICON_MAP:
                legend_items.append(
                    html.Div([
                        html.Img(src=ICON_MAP[payment_type], className="waffle-icon"),
                        html.Span(payment_type, className="ms-2")
                    ], className="d-flex align-items-center me-3")
                )
        legend_div = html.Div(legend_items, className="d-flex flex-wrap mb-4 justify-content-center")

        
        waffle_bars_container = html.Div(
            children=[],
            className="waffle-bars-container"
        )
        
        # Iterar sobre cada bin (barra)
        for bin_label in df_norm.index:
            
            # --- LÓGICA DE REDONDEO ---
            total_icons_for_this_bin = proportional_heights.loc[bin_label]
            row_data_pct = df_norm.loc[bin_label]
            
            counts = (row_data_pct * total_icons_for_this_bin).fillna(0)
            num_blocks_floor = counts.apply(lambda x: int(x))
            remainders = counts - num_blocks_floor
            diff = total_icons_for_this_bin - num_blocks_floor.sum()
            indices_to_adjust = remainders.nlargest(diff).index
            final_counts = num_blocks_floor.copy()
            for idx in indices_to_adjust:
                final_counts[idx] += 1
            # --- FIN REDONDEO ---

            
            # --- 4. Generación de Bloques (Coloreados + Vacíos) ---
            
            # Generar los bloques COLOREADOS
            colored_blocks = []
            for payment_type in sorted_types_by_volume:
                if payment_type in final_counts.index:
                    num_blocks = final_counts[payment_type] 
                    if num_blocks > 0:
                        percentage = row_data_pct[payment_type]
                        icon_src = ICON_MAP.get(payment_type, ICON_MAP[DEFAULT_PAYMENT_TYPE])
                        
                        for _ in range(int(num_blocks)):
                            colored_blocks.append(
                                html.Img(
                                    src=icon_src, 
                                    className="waffle-icon",
                                    title=f"{payment_type}: {percentage:.1%}"
                                )
                            )
            
            # Generar los bloques VACÍOS
            empty_blocks = []
            num_empty_blocks = 100 - total_icons_for_this_bin
            for _ in range(num_empty_blocks):
                empty_blocks.append(html.Div(className="waffle-icon-empty"))

            # CORRECCIÓN: Invertir el orden de concatenación
            # Los bloques vacíos van PRIMERO en la lista para que se muestren ABAJO.
            # Los bloques coloreados van DESPUÉS para que se muestren ARRIBA.
            blocks = empty_blocks + colored_blocks
            
            # 5. Crear la barra Waffle
            waffle_bar = html.Div([
                html.Div(blocks, className="waffle-grid-bar"), 
                html.P(html.B(bin_label), className="waffle-label-bottom") 
            ], className="waffle-column") 
            
            waffle_bars_container.children.append(waffle_bar)

        return html.Div([legend_div, waffle_bars_container])