# layout.py
# Define el layout completo de la aplicación y el contenido de las pestañas.

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd

# Importar variables pre-calculadas del módulo de datos
from data import data, pickup_markers, center_lat, center_lon


def render_tag(tag, value):
    """
    Convierte una entrada de diccionario en componente Dash HTML.
    """
    if tag.lower() == "br":
        return html.Br()

    if tag.lower() == "b":
        return html.B(value)

    if tag.lower() == "p":
        return html.P(value)

    if tag.lower() == "ul":
        # Value debe ser lista
        return html.Ul([html.Li(item) for item in value])

    if tag.lower() == "li":
        return html.Li(value)

    # fallback genérico
    return html.Div(value)


def InfoIcon(id_prefix, content_dict):
    """
    Recibe un diccionario { "tag": valor } y construye el tooltip.
    """
    children = []

    for tag, val in content_dict.items():
        # Si es lista (por ejemplo ul con ítems),
        # ya se procesa dentro de render_tag
        children.append(render_tag(tag, val))

    return html.Span(
        [
            html.Span("ℹ️", id=f"{id_prefix}-icon", style={"cursor": "pointer"}),
            dbc.Tooltip(
                children=html.Div(children),
                target=f"{id_prefix}-icon",
                id=f"{id_prefix}-tooltip",
                placement="top",
                className="tooltip-multiline",
            ),
        ],
        style={"fontSize": "28px"}
    )

# ----------------------------------------------------------------------
# --- CONTENIDO DE LAS PESTAÑAS ---
# ----------------------------------------------------------------------

# El contenido del mapa y los gráficos para la pestaña "Viajes"
min_dt = pd.to_datetime(data["tpep_pickup_datetime"].min())
min_date_str = min_dt.strftime("%Y-%m-%d")
default_start_time = min_dt.strftime("%H:%M")
default_end_time = (min_dt + pd.Timedelta(hours=1)).strftime("%H:%M")

viajes_content = html.Div(
    [
        dcc.Store(id="time-filtered-store", data=[]),
        dcc.Store(id="filtered-data-store", data=[]),
        dcc.Store(id="fixed-date-store", data=min_date_str),
        dcc.Store(id="filter-applied-flag", data="pickups"),
        
        dbc.Row(
            [
                # Columna Izquierda (Controles + Mapa)
                dbc.Col(
                    [
                        # Fila de Controles Superiores
                        dbc.Card(
                            dbc.CardBody(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            InfoIcon(
                                                id_prefix="tab1-info",
                                                content_dict={
                                                    "b": "🗺️ Información geográfica de los viajes",
                                                    "ul": [
                                                        "Usa el botón para ver las salidas o llegadas de los viajes.",
                                                        "Haz clic sobre un coche para ver un viaje individual.",
                                                        "Una vez has aislado un viaje, vuelve a hacer click en cualquier coche para ver información detallada del viaje",
                                                        "Haz click en el boton de ver salidas/llegadas para volver a ver todos los coches",
                                                        "Elige una hora de inicio y final para ver todos los viajes hechos en esa hora y hacer que los gráficos reaccionen",
                                                        "Muévete por el mapa para que los gráficos de la derecha reaccionen a lo que se ve en el mapa."
                                                    ]
                                                }
                                            ),
                                            width=1,
                                            className="d-flex align-items-center"
                                        ),
                                        dbc.Col(
                                            dbc.Button("Mostrando salidas", id="toggle-view-btn", color="light", className="w-100"),
                                            xs=12, sm=4, className="mb-2 mb-sm-0"
                                        ),
                                        dbc.Col(
                                            html.Div([
                                                html.H6("Filtro por Hora de Recogida", className="text-secondary mb-1 small"),
                                                dbc.Row([
                                                    dbc.Col(dbc.Input(id="start-time-input", type="time", value=default_start_time), width=6),
                                                    dbc.Col(dbc.Input(id="end-time-input", type="time", value=default_end_time), width=6),
                                                ], className="g-2")
                                            ]),
                                            xs=12, sm=7
                                        ),
                                    ],
                                    className="align-items-center",
                                )
                            ),
                            className="shadow-sm mb-3 border-light",
                            color="dark",
                        ),
                        
                        # Bloque del Mapa
                        dbc.Card(
                            [
                                dbc.CardHeader("Mapa Interactivo de Viajes", className="fw-bold bg-dark text-light"),
                                dbc.CardBody(
                                    dl.Map(
                                        id="map",
                                        center=[center_lat, center_lon],
                                        zoom=13,
                                        children=[html.Div(id="map-tiles")],
                                        # IMPORTANTE: Altura fija mínima para robustez
                                        style={"width": "100%", "height": "550px"} 
                                    ),
                                    className="p-0"
                                )
                            ],
                            className="shadow-lg border-light flex-grow-1",
                            color="dark",
                        ),
                    ],
                    # Responsividad: Full width en móvil, 8/12 en escritorio
                    xs=12, lg=8,
                    className="d-flex flex-column mb-4 mb-lg-0"
                ),

                # Columna Derecha (Análisis)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Análisis de Viajes Seleccionados", className="fw-bold bg-dark text-light"),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(
                                            id="analysis-dropdown",
                                            options=[
                                                {"label": "Número de pasajeros", "value": "passengers"},
                                                {"label": "Distribución del tiempo", "value": "trip_time"},
                                                {"label": "Distribución de la distancia", "value": "trip_distance"},
                                            ],
                                            value="passengers",
                                            clearable=False,
                                            className="mb-3",
                                        ),
                                        html.Div(id="map-info", className="mb-3 p-2 border rounded border-light bg-secondary"),
                                        dcc.Loading(
                                            id="loading-graph",
                                            children=dcc.Graph(
                                                id="analysis-graph",
                                                # Altura mínima para que el gráfico no sea un "fideo"
                                                style={"width": "100%", "height": "500px"},
                                                responsive=True
                                            )
                                        )
                                    ],
                                    className="d-flex flex-column",
                                ),
                            ],
                            className="shadow-lg border-light h-100",
                            color="dark",
                        )
                    ],
                    xs=12, lg=4,
                ),
            ],
            className="g-4" # Gutter (espaciado) entre columnas
        ),
    ],
    className="p-4",
    style={
        "minHeight": "100vh", # Forzamos a que ocupe al menos la pantalla completa
        "overflowY": "auto",  # Si el contenido (550px + 500px + controles) excede la pantalla, sale scroll
        "overflowX": "hidden"
    }
)

# Contenido para la pestaña Distritos
distritos_content = html.Div(
    [
        dbc.Row(
            [
                # Columna del Gráfico
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    id="distritos-graph-header",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(
                                            id="distritos-graph",
                                            responsive=True,
                                            # Establecemos una altura mínima para que el gráfico no se colapse
                                            style={"minHeight": "500px", "height": "100%"}
                                        )
                                    ],
                                    className="d-flex flex-column",
                                ),
                            ],
                            className="shadow-lg border-light h-100",
                            color="dark",
                        )
                    ],
                    # Responsividad: 12 columnas en móvil (xs), 9 en escritorio (lg)
                    xs=12, lg=9,
                    className="mb-4 mb-lg-0" # Margen inferior solo en móvil
                ),
                # Columna de Controles
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Control de Métrica",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    [
                                        html.P("Seleccione la visualización:", className="text-light"),
                                        dcc.Dropdown(
                                            id="distritos-dropdown",
                                            options=[
                                                {"label": "Distancia Promedio", "value": "distance"},
                                                {"label": "Tiempo Promedio", "value": "time"},
                                                {"label": "Comparar Tiempo vs Distancia", "value": "pyramid"},
                                            ],
                                            value="distance",
                                            clearable=False,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-lg border-light",
                            color="dark",
                            style={"minHeight": "200px"} # Robustez para los controles
                        )
                    ],
                    xs=12, lg=3,
                ),
            ],
            className="g-4", # Añade espacio (gutter) entre columnas de forma limpia
        )
    ],
    className="p-4",
    style={
        "height": "auto",       # Permite que crezca si es necesario
        "minHeight": "90vh",    # Mantiene una presencia visual importante
        "overflowY": "auto",    # Habilita el scroll vertical si el contenido es muy grande
        "overflowX": "hidden"   # Evita el scroll horizontal molesto
    }
)

# ----------------------------------------------------------------------
# --- CONTENIDO DE LA PESTAÑA PAGOS ---
# ----------------------------------------------------------------------
pagos_content = html.Div(
    [
        dbc.Row(
            [
                # --- Columna Izquierda: Waffle Plot (8/12 en escritorio, Full en móvil)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Distribución de Tipos de Pago por Costo (Waffle)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    html.Div(
                                        id="waffle-plot-container",
                                        # Establecemos un mínimo de 450px para que el waffle no se vuelva ilegible
                                        style={"minHeight": "450px", "width": "100%"} 
                                    ),
                                    className="p-3 d-flex flex-column",
                                ),
                            ],
                            color="dark",
                            className="shadow-lg border-light h-100 d-flex flex-column",
                        )
                    ],
                    xs=12, lg=8,
                    className="mb-4 mb-lg-0" # Espacio inferior cuando se apilan
                ),
                
                # --- Columna Derecha: Gráfico Sankey (4/12 en escritorio, Full en móvil)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Flujo de Ingresos y Deducciones (Sankey)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="sankey-graph", 
                                        responsive=True,
                                        # El Sankey necesita altura para separar los nodos
                                        style={"minHeight": "500px", "height": "100%"}
                                    ),
                                    className="p-3 d-flex flex-column",
                                ),
                            ],
                            className="shadow-lg border-light h-100 d-flex flex-column",
                        )
                    ],
                    xs=12, lg=4,
                ),
            ],
            # Eliminamos flex-grow-1 para dejar que el contenido defina su altura natural o mínima
            className="mt-4 g-4",
        )
    ],
    className="p-4",
    style={
        "minHeight": "100vh", # Ocupa toda la pantalla disponible
        "overflowY": "auto",   # Habilita scroll si los minHeight sumados superan la pantalla
        "overflowX": "hidden"
    }
)

# --- LAYOUT DE LA PESTAÑA DE EVOLUCIÓN ---

evolucion_content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Evolución Temporal de Métricas por Hora",
                                className="fw-bold bg-dark text-light",
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Label("Seleccionar Métrica:", className="fw-bold"),
                                    dbc.RadioItems(
                                        id="metric-selector",
                                        options=[
                                            {'label': 'Nº Pasajeros', 'value': 'passenger_count'},
                                            {'label': 'Ingresos Totales ($)', 'value': 'total_amount'},
                                            {'label': 'Minutos Totales (viaje)', 'value': 'trip_minutes'},
                                            {'label': 'Distancia Total (km)', 'value': 'trip_distance_km'},
                                        ],
                                        value='passenger_count',
                                        inline=True,
                                        className="mb-4", # <-- Esto toma su altura natural (flex-shrink: 0)
                                    ),
                                    dcc.Graph(
                                        id="lollipop-chart",
                                        style={"flex": "1"}, # El gráfico "crece" para llenar el espacio restante
                                        responsive=True # Asegura que Plotly se redibuje al cambiar el tamaño
                                    ),
                                ],
                                className="d-flex flex-column flex-grow-1" # El CardBody crece y apila a sus hijos
                            ),
                        ],
                        color="dark",
                        className="shadow-lg border-light h-100 d-flex flex-column", # La Card llena la Columna y es un contenedor flex
                    ),
                    width=12,
                    className="h-100" # La Columna debe llenar la altura de la Fila
                )
            ],
            className="mt-4 flex-grow-1", # La Fila "crece" para llenar el Div principal
        )
    ],
    className="p-4 d-flex flex-column", # El Div principal es un contenedor flex vertical
    style={"height": "85vh"} 
)
# ----------------------------------------------------------------------
# --- LAYOUT EMISIONES CARBONO ---
# ----------------------------------------------------------------------

emisiones_de_carbono_content = html.Div(
    [
        dbc.Row(
            [
                # COLUMNA DE CONTROLES (width=4 en LG, 12 en XS)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Filtros y Métricas",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Distrito", className="fw-bold"),
                                                dcc.Dropdown(
                                                    id="borough-dropdown",
                                                    options=[{"label": "Todos", "value": "ALL"}],
                                                    value=["ALL"],
                                                    multi=True,
                                                    placeholder="Selecciona distrito(s)...",
                                                    className="mb-3"
                                                ),
                                                html.Label("Rango de horas (pickup)", className="fw-bold"),
                                                html.Div(
                                                    dcc.RangeSlider(
                                                        id="hour-range-slider",
                                                        min=0, max=23, step=1, value=[0, 23],
                                                        marks={i: str(i) for i in range(0, 24, 6)},
                                                        tooltip={"placement": "bottom", "always_visible": False},
                                                    ),
                                                    className="px-2 mb-4"
                                                ),
                                                html.Label("Métrica de CO₂", className="fw-bold"),
                                                dcc.RadioItems(
                                                    id="metric-radio",
                                                    options=[
                                                        {"label": " CO₂ total por viaje", "value": "co2_kg_trip"},
                                                        {"label": " CO₂ por pasajero (kg/pax)", "value": "co2_kg_per_passenger"},
                                                    ],
                                                    value="co2_kg_trip",
                                                    labelStyle={"display": "block", "marginBottom": "5px"},
                                                ),
                                                html.Hr(),
                                            ],
                                        )
                                    ],
                                    className="p-3"
                                ),
                            ],
                            color="dark",
                            className="shadow-sm border-light",
                            style={"minHeight": "400px"} # Robustez: los filtros siempre legibles
                        ),
                    ],
                    xs=12, lg=4,
                    className="mb-4 mb-lg-0"
                ),
                
                # COLUMNA DE GRÁFICOS (width=8 en LG, 12 en XS)
                dbc.Col(
                    [
                        # PRIMER GRÁFICO: Emisiones Horarias
                        dbc.Card(
                            [
                                dbc.CardHeader("Emisiones horarias", className="fw-bold bg-dark text-light"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-hourly-graph",
                                        responsive=True,
                                        style={"height": "400px"} # Altura fija mínima de seguridad
                                    ),
                                    className="p-2", 
                                ),
                            ],
                            color="dark",
                            className="shadow-lg border-light mb-4", 
                        ),
                        
                        # SEGUNDO GRÁFICO: Treemap
                        dbc.Card(
                            [
                                dbc.CardHeader("Contribución de CO₂ (Treemap)", className="fw-bold bg-dark text-light"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-treemap-graph",
                                        responsive=True,
                                        style={"height": "500px"} # El Treemap necesita más espacio vertical
                                    ),
                                    className="p-2",
                                ),
                            ],
                            color="dark",
                            className="shadow-lg border-light", 
                        ),
                    ],
                    xs=12, lg=8,
                ),
            ],
            className="g-4", 
        )
    ],
    className="p-4",
    style={
        "minHeight": "100vh", 
        "overflowY": "auto", 
        "overflowX": "hidden"
    }
)
# ----------------------------------------------------------------------
# --- LAYOUT PRINCIPAL ---
# ----------------------------------------------------------------------

app_layout = dbc.Container(
    [
        # Stores (Globales)
        dcc.Store(id="map-memory", data="global_view"),
        dcc.Store(id="filtered-data-store", data=[]),
        
        # Fila 1: Título y Pestañas
        dbc.Row(
            [
                # Título: En móvil ocupa todo (12), en escritorio la mitad (6)
                dbc.Col(
                    html.Div(
                        "Uber NYC Business Insights", # Título algo más corto para robustez
                        className="h3 fw-bold text-light mb-0", # h3 es más estable que display-6
                    ),
                    xs=12, lg=6,
                    className="d-flex align-items-center justify-content-center justify-content-lg-start mb-3 mb-lg-0"
                ),
                # Pestañas: Se alinean al final en escritorio, al centro en móvil
                dbc.Col(
                    dbc.Tabs(
                        [
                            dbc.Tab(label="Viajes", tab_id="tab-viajes"),
                            dbc.Tab(label="Distritos", tab_id="tab-distritos"),
                            dbc.Tab(label="Pagos", tab_id="tab-pagos"),
                            dbc.Tab(label="Evolución", tab_id="tab-evolucion"),
                            dbc.Tab(label="CO₂", tab_id="tab-emisiones-co2"),
                        ],
                        id="tabs",
                        active_tab="tab-viajes",
                        # 'nav-pills' es excelente para robustez táctil
                        className="nav-pills justify-content-center justify-content-lg-end",
                    ),
                    xs=12, lg=6,
                ),
            ],
            # Eliminamos el height fijo de 5vh para evitar cortes de texto
            className="py-3 border-bottom border-secondary align-items-center", 
        ),

        # Fila 2: Contenido de la pestaña activa
        dbc.Row(
            dbc.Col(
                html.Div(id="content-div", className="p-0"), 
                width=12
            ),
            className="flex-grow-1"
        )
    ],
    fluid=True,
    className="bg-dark text-light min-vh-100 d-flex flex-column",
    style={
        "overflowX": "hidden", # Evita desplazamiento horizontal accidental
        "paddingLeft": "2rem",
        "paddingRight": "2rem"
    }
)
