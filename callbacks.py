# callbacks.py
# Contiene toda la lógica de callbacks de la aplicación.

from dash import Input, Output, State, callback_context, ALL, no_update
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from dash import html, dcc
import json

# Importar variables de datos y layout
from data import data, pickup_markers, dropoff_markers, green_icon, red_icon, ICON_MAP
from layout import viajes_content, distritos_content, pagos_content, evolucion_content

DEFAULT_PAYMENT_TYPE = "Otros"

# def create_markers(df, marker_type, icon):
#     """
#     Genera una lista de dl.Marker desde un DataFrame, usando el 
#     índice del DataFrame como 'index' en el ID del marcador.
#     """
#     markers = []
#     lat_col = 'pickup_latitude' if marker_type == 'pickup' else 'dropoff_latitude'
#     lon_col = 'pickup_longitude' if marker_type == 'pickup' else 'dropoff_longitude'
#     tooltip = "Salida" if marker_type == 'pickup' else "Llegada"
    
#     for idx, row in df.iterrows():
#         marker = dl.Marker(
#             position=(row[lat_col], row[lon_col]),
#             icon=icon,
#             children=[dl.Tooltip(tooltip)],
#             # ID de coincidencia de patrones. El 'index' es el índice
#             # original del DataFrame 'data', no la posición (iloc).
#             id={'type': f'{marker_type}_marker', 'index': idx}
#         )
#         markers.append(marker)
#     return markers
# SAMPLE_LIMIT = 500


def register_callbacks(app):

    # --------------- RENDER DE PESTAÑAS ----------------
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
            return pagos_content
        elif active_tab == "tab-evolucion":
            return evolucion_content
        return dash.html.Div(dash.html.P("Selecciona una pestaña."))
    # --- CALLBACK: Toggle botón (ahora guarda 'pickups'/'dropoffs') ---
    @app.callback(
        Output('filter-applied-flag', 'data'),
        Output('toggle-view-btn', 'children'),
        Input('toggle-view-btn', 'n_clicks'),
        State('filter-applied-flag', 'data'),
        prevent_initial_call=False
    )
    def toggle_view(n_clicks, current_mode):
        # Normalizamos el valor por defecto
        if current_mode not in ('pickups', 'dropoffs'):
            current_mode = 'pickups'
        # Si no se ha hecho click aún, devolvemos el estado actual (inicio)
        if n_clicks is None:
            label = "Mostrando salidas" if current_mode == 'pickups' else "Mostrando llegadas"
            return current_mode, label
        # Toggle por cada click
        new_mode = 'dropoffs' if current_mode == 'pickups' else 'pickups'
        label = "Mostrando salidas" if new_mode == 'pickups' else "Mostrando llegadas"
        return new_mode, label

    # --- CALLBACK UNIFICADO: fechas, modo, clicks en marcadores y movimiento del mapa ---
    @app.callback(
        Output('map', 'children'),         # reconstruir marcadores (solo cuando toca)
        Output('map', 'bounds'),           # ajustar bounds cuando se selecciona un viaje
        Output('map', 'center'),           # ajustar center al seleccionar
        Output('filtered-data-store', 'data'),  # almacenar SOLO los viajes visibles (para gráficos)
        Output('map-info', 'children'),    # texto de info resumida
        Input('start-time-input', 'value'),      
        Input('end-time-input', 'value'),         
        Input('fixed-date-store', 'data'),        # fecha fija (YYYY-MM-DD)
        Input('filter-applied-flag', 'data'),     # 'pickups' o 'dropoffs'
        Input('map', 'bounds'),                   # pan/zoom -> actualizar visibles
        Input({'type': 'pickup-marker', 'index': ALL}, 'n_clicks'),
        Input({'type': 'dropoff-marker', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=False
    )
    def map_master(start_time, end_time, fixed_date, mode, current_bounds, pickup_clicks, dropoff_clicks):
        """
        start_time, end_time : "HH:MM" (strings) desde los Inputs type=time
        fixed_date : "YYYY-MM-DD" desde el store
        mode : 'pickups' o 'dropoffs'
        current_bounds : [[lat_min, lon_min], [lat_max, lon_max]] (o None)
        """
        ctx = callback_context

        # Detectar qué disparó el callback de forma robusta
        triggered = None
        if ctx.triggered:
            trig = ctx.triggered[0]  # primer trigger (normalmente el único)
            prop_id = trig.get('prop_id', '')
            # prop_id puede ser: 'start-time-input.value' o '{"type":"pickup-marker","index":123}.n_clicks'
            comp_id = prop_id.split('.')[0] if prop_id else ''
            # Si comp_id es JSON (pattern-matching), convertir a dict
            try:
                triggered = json.loads(comp_id) if comp_id.startswith('{') else comp_id
            except Exception:
                triggered = comp_id
        else:
            triggered = None

        # --- Normalizaciones / validaciones ---
        if not fixed_date:
            # No tenemos fecha fija: no procesamos
            raise dash.exceptions.PreventUpdate

        # Si faltan horas, pongo defaults basados en dataset
        min_dt = pd.to_datetime(data['tpep_pickup_datetime'].min())
        if start_time is None:
            start_time = min_dt.strftime('%H:%M')
        if end_time is None:
            end_time = (min_dt + pd.Timedelta(hours=1)).strftime('%H:%M')

        # Construir timestamps completos y asegurar end > start
        try:
            start_ts = pd.to_datetime(f"{fixed_date} {start_time}")
            end_ts = pd.to_datetime(f"{fixed_date} {end_time}")
        except Exception:
            start_ts = min_dt
            end_ts = min_dt + pd.Timedelta(hours=1)

        if end_ts <= start_ts:
            end_ts = start_ts + pd.Timedelta(hours=1)

        # Filtrar por intervalo horario
        df = data.copy()
        # df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        filtered_df = df[(df['tpep_pickup_datetime'] >= start_ts) & (df['tpep_pickup_datetime'] <= end_ts)].reset_index(drop=False)
        total_after_date = len(filtered_df)

        # Si no hay datos en el intervalo
        if total_after_date == 0:
            info = html.Div([
                html.P(f"Viajes tras hora: {total_after_date}", className="mb-0 small"),
                html.P("No hay viajes en el intervalo horario seleccionado.", className="mb-0 small")
            ])
            return [dl.TileLayer()], no_update, no_update, [], info

        # Serializar viajes filtrados en una lista
        store_all = []
        for _, row in filtered_df.iterrows():
            idx = int(row['index'])
            store_all.append({
                'index': idx,
                'pickup_latitude': float(row['pickup_latitude']),
                'pickup_longitude': float(row['pickup_longitude']),
                'dropoff_latitude': float(row['dropoff_latitude']),
                'dropoff_longitude': float(row['dropoff_longitude']),
                'passenger_count': row.get('passenger_count', None),
                'total_amount': float(row.get('total_amount', 0)) if pd.notna(row.get('total_amount', None)) else None,
                'trip_minutes': float(row.get('trip_minutes', 0)) if pd.notna(row.get('trip_minutes', None)) else None,
                'trip_distance_km': float(row.get('trip_distance_km', 0)) if pd.notna(row.get('trip_distance_km', None)) else None,
                'tpep_pickup_datetime': str(row['tpep_pickup_datetime'])
            })

        # Helper para comprobar si un punto está en bounds
        def in_bounds(lat, lon, bounds):
            if bounds is None:
                return True
            try:
                (lat_min, lon_min), (lat_max, lon_max) = bounds[0], bounds[1]
                return (lat >= min(lat_min, lat_max)) and (lat <= max(lat_min, lat_max)) and \
                    (lon >= min(lon_min, lon_max)) and (lon <= max(lon_min, lon_max))
            except Exception:
                return True

        # --- Caso 1: click en marcador (pattern-matching -> triggered es dict) ---
        if isinstance(triggered, dict) and 'type' in triggered and 'index' in triggered:
            clicked_index = int(triggered['index'])
            sel = next((r for r in store_all if int(r['index']) == clicked_index), None)
            if sel is None:
                # click en marcador que no está en current interval -> no update
                pass
            else:
                # Construir pickup + dropoff y ajustar bounds/center
                idx = int(sel['index'])
                pickup_marker = dl.Marker(
                    id={'type': 'pickup-marker', 'index': idx},
                    position=(float(sel['pickup_latitude']), float(sel['pickup_longitude'])),
                    icon=green_icon if 'green_icon' in globals() else None,
                    children=[
                        dl.Tooltip("Salida"),
                        dl.Popup(
                            html.Div([
                                html.H5("🚖 Información del viaje", className="text-dark"),
                                html.P(f"👤 Pasajeros: {sel.get('passenger_count', 'N/A')}"),
                                html.P(f"💰 Total: ${float(sel.get('total_amount', 0)):.2f}"),
                                html.P(f"⏱️ Duración: {float(sel.get('trip_minutes', 0)):.1f} min"),
                                html.P(f"🛣️ Distancia: {float(sel.get('trip_distance_km', 0)):.2f} km"),
                            ], className="text-secondary", style={'color': 'black'})
                        )
                    ]
                )
                dropoff_marker = dl.Marker(
                    id={'type': 'dropoff-marker', 'index': idx},
                    position=(float(sel['dropoff_latitude']), float(sel['dropoff_longitude'])),
                    icon=red_icon if 'red_icon' in globals() else None,
                    children=[dl.Tooltip("Llegada")]
                )
                children = [dl.TileLayer(), pickup_marker, dropoff_marker]
            

                lat1, lon1 = float(sel['pickup_latitude']), float(sel['pickup_longitude'])
                lat2, lon2 = float(sel['dropoff_latitude']), float(sel['dropoff_longitude'])
                lat_min, lat_max = min(lat1, lat2), max(lat1, lat2)
                lon_min, lon_max = min(lon1, lon2), max(lon1, lon2)
                lat_pad = (lat_max - lat_min) * 0.2 if (lat_max - lat_min) != 0 else 0.001
                lon_pad = (lon_max - lon_min) * 0.2 if (lon_max - lon_min) != 0 else 0.001
                bounds = [[lat_min - lat_pad, lon_min - lon_pad], [lat_max + lat_pad, lon_max + lon_pad]]
                center = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]

                new_filtered = [sel]
                info = html.Div([
                    html.P(f"Viajes tras hora: 1", className="mb-0 small"),
                    html.P(f"Viajes visibles (por bounds): 1", className="mb-0 small"),
                    html.P(f"Lat range: {lat_min:.4f} — {lat_max:.4f}", className="mb-0 small"),
                    html.P(f"Lon range: {lon_min:.4f} — {lon_max:.4f}", className="mb-0 small"),
                ])

                return children, bounds, center, new_filtered, info

        # --- Caso 2: movimiento del mapa (prop_id = 'map.bounds') ---
        if triggered == 'map' or (isinstance(triggered, str) and triggered == 'map'):
            visible = []
            for r in store_all:
                lat = r['pickup_latitude'] if mode != 'dropoffs' else r['dropoff_latitude']
                lon = r['pickup_longitude'] if mode != 'dropoffs' else r['dropoff_longitude']
                if in_bounds(lat, lon, current_bounds):
                    visible.append(r)
            if len(visible) == 0:
                info = html.Div([
                    html.P(f"Viajes tras hora: {total_after_date}", className="mb-0 small"),
                    html.P("No hay viajes visibles en el área actual.", className="mb-0 small")
                ])
                return no_update, no_update, no_update, [], info

            lat_min = min([ (v['pickup_latitude'] if mode != 'dropoffs' else v['dropoff_latitude']) for v in visible ])
            lat_max = max([ (v['pickup_latitude'] if mode != 'dropoffs' else v['dropoff_latitude']) for v in visible ])
            lon_min = min([ (v['pickup_longitude'] if mode != 'dropoffs' else v['dropoff_longitude']) for v in visible ])
            lon_max = max([ (v['pickup_longitude'] if mode != 'dropoffs' else v['dropoff_longitude']) for v in visible ])

            info = html.Div([
                html.P(f"Viajes tras hora: {total_after_date}", className="mb-0 small"),
                html.P(f"Viajes visibles (por bounds): {len(visible)}", className="mb-0 small"),
                html.P(f"Lat range: {lat_min:.4f} — {lat_max:.4f}", className="mb-0 small"),
                html.P(f"Lon range: {lon_min:.4f} — {lon_max:.4f}", className="mb-0 small"),
            ])
            return no_update, no_update, no_update, visible, info

        # --- Flujo por cambio de horas o cambio de modo (pickups/dropoffs): reconstruir marcadores ---
        limited_points = store_all[:300]
        
        children = [dl.TileLayer()]
        
        for r in limited_points:
            idx = int(r['index'])
            if mode == 'dropoffs':
                marker = dl.Marker(
                    id={'type': 'dropoff-marker', 'index': idx},
                    position=(float(r['dropoff_latitude']), float(r['dropoff_longitude'])),
                    icon=red_icon if 'red_icon' in globals() else None,
                    children=[dl.Tooltip("Llegada")]
                )
            else:
                marker = dl.Marker(
                    id={'type': 'pickup-marker', 'index': idx},
                    position=(float(r['pickup_latitude']), float(r['pickup_longitude'])),
                    icon=green_icon if 'green_icon' in globals() else None,
                    children=[
                        dl.Tooltip("Salida"),
                        dl.Popup(
                            html.Div([
                                html.H5("🚖 Información del viaje", className="text-dark"),
                                html.P(f"👤 Pasajeros: {r.get('passenger_count', 'N/A')}"),
                                html.P(f"💰 Total: ${float(r.get('total_amount', 0)):.2f}"),
                                html.P(f"⏱️ Duración: {float(r.get('trip_minutes', 0)):.1f} min"),
                                html.P(f"🛣️ Distancia: {float(r.get('trip_distance_km', 0)):.2f} km"),
                            ], className="text-secondary", style={'color': 'black'})
                        )
                    ]
                )
            children.append(marker)

        # Guardar solo los puntos visibles según current_bounds (si existe)
        visible = []
        for r in store_all:
            lat = r['pickup_latitude'] if mode != 'dropoffs' else r['dropoff_latitude']
            lon = r['pickup_longitude'] if mode != 'dropoffs' else r['dropoff_longitude']
            if in_bounds(lat, lon, current_bounds):
                visible.append(r)

        saved = visible if current_bounds is not None else store_all

        lat_min = min([ (v['pickup_latitude'] if mode != 'dropoffs' else v['dropoff_latitude']) for v in saved ]) if saved else 0
        lat_max = max([ (v['pickup_latitude'] if mode != 'dropoffs' else v['dropoff_latitude']) for v in saved ]) if saved else 0
        lon_min = min([ (v['pickup_longitude'] if mode != 'dropoffs' else v['dropoff_longitude']) for v in saved ]) if saved else 0
        lon_max = max([ (v['pickup_longitude'] if mode != 'dropoffs' else v['dropoff_longitude']) for v in saved ]) if saved else 0

        info = html.Div([
            html.P(f"Viajes tras hora: {total_after_date}", className="mb-0 small"),
            html.P(f"Viajes visibles (por bounds): {len(saved)}", className="mb-0 small"),
            html.P(f"Lat range: {lat_min:.4f} — {lat_max:.4f}", className="mb-0 small"),
            html.P(f"Lon range: {lon_min:.4f} — {lon_max:.4f}", className="mb-0 small"),
        ])

        return children, no_update, no_update, saved, info
    # ---------------------------------------------------------------------
    # 4) CALLBACK: GRAFICOS -> ya lo proporcionaste; lo integro aquí con el mismo ID
    #    - Input: analysis-dropdown, filtered-data-store
    #    - Output: analysis-graph.figure
    # ---------------------------------------------------------------------
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

        # Treemap - pasajeros
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

        # Violin - tiempo
        elif selected_value == 'trip_time':
            fig = px.violin(filtered_data,
                            y="trip_minutes",
                            box=True,
                            points="all",
                            title=f'Distribución del Tiempo de Viaje ({num_trips} viajes)',
                            color_discrete_sequence=['#42f2f5'])
            fig.update_layout(yaxis_title="Minutos de Viaje", **plotly_style)
            return fig

        # Violin - distancia
        elif selected_value == 'trip_distance':
            fig = px.violin(filtered_data,
                            y="trip_distance_km",
                            box=True,
                            points="all",
                            title=f'Distribución de la Distancia de Viaje ({num_trips} viajes)',
                            color_discrete_sequence=['#ffc107'])
            fig.update_layout(yaxis_title="Distancia (km)", **plotly_style)
            return fig

        # Default vacío
        fig = go.Figure()
        fig.update_layout(**plotly_style)
        return fig

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