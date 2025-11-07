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
                # Columna Izquierda (Mapa - 2/3)
                dbc.Col(
                    [
                        # 1. Controles: Usamos un dbc.Row para alinear horizontalmente el botón y el DatePicker
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        # icono de info
                                        dbc.Col(
                                            InfoIcon(
                                                id_prefix="tab1-info",
                                                content_dict={
                                                    "b": "🗺️ Información geográfica de los viajes",
                                                    "ul": [
                                                        "Usa el botón para ver las salidas o llegadas de los viajes.",
                                                        "Haz clic sobre un coche para ver un viaje individual.",
                                                        "Una vez has aislado un viaje, vuelve a hacer click en cualquier coche para ver información detallada del viaje",
                                                        "Elige una hora de inicio y final para ver todos los viajes hechos en esa hora y hacer que los gráficos reaccionen",
                                                        "Muévete por el mapa para que los gráficos de la derecha reaccionen a lo que se ve en el mapa."
                                                    ]
                                                }
                                            ),
                                            width=1,
                                            className="d-flex align-items-center"
                                        ),

                                        # Columna para el Botón (Aproximadamente 4 unidades de ancho)
                                        dbc.Col(
                                            dbc.Button(
                                                "Mostrando salidas",
                                                id="toggle-view-btn",
                                                color="light",
                                                className="w-100",
                                            ),
                                            width=4,
                                            className="d-flex flex-column justify-content-end", 
                                        ),
                                        
                                        # Columna para el Filtro de Fecha (Aproximadamente 8 unidades de ancho)
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.H6(
                                                        "Filtro por Hora de Recogida",
                                                        className="text-secondary mb-0",
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                html.Div(
                                                                    [
                                                                        html.Label(
                                                                            "Hora inicio",
                                                                            className="small",
                                                                        ),
                                                                        dbc.Input(
                                                                            id="start-time-input",
                                                                            type="time",
                                                                            value=default_start_time,
                                                                            className="form-control",
                                                                        ),
                                                                    ]
                                                                ),
                                                                width=6,
                                                            ),
                                                            dbc.Col(
                                                                html.Div(
                                                                    [
                                                                        html.Label(
                                                                            "Hora fin",
                                                                            className="small",
                                                                        ),
                                                                        dbc.Input(
                                                                            id="end-time-input",
                                                                            type="time",
                                                                            value=default_end_time,
                                                                            className="form-control",
                                                                        ),
                                                                    ]
                                                                ),
                                                                width=6,
                                                            ),
                                                            # Store con la fecha fija (minima)
                                                            dcc.Store(
                                                                id="fixed-date-store",
                                                                data=min_date_str,
                                                            ),
                                                        ],
                                                        className="mt-2",
                                                    ),
                                                    # html.Div(html.Small(f"Fecha fija: {min_date_str}", className="text-muted"), className="mt-1")
                                                ]
                                            ),
                                            width=7,
                                        ),
                                    ],
                                    className="g-3 align-items-end", 
                                )
                            ],
                            className="g-3"
                        ),
                        # Bloque del Mapa
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Mapa Interactivo de Viajes",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    html.Div(
                                        dl.Map(
                                            id="map",
                                            center=[center_lat, center_lon],
                                            zoom=13,
                                            children=[html.Div(id="map-tiles"),],
                                            style={"width": "100%", "flex": "1", "max-height":"550px"}, 

                                        ),
                                        # Convertimos este Div en un contenedor flex para que el mapa crezca
                                        className="d-flex flex-column h-100", 
                                    ),
                                # CardBody debe ser un contenedor flex vertical para que su hijo crezca
                                className="d-flex flex-column p-0", 
                                )
                                
                            ],
                            # flex-grow-1, h-100, d-flex flex-column. Crece para llenar el espacio disponible
                            className="shadow-lg border-light flex-grow-1 d-flex flex-column h-100",
                        ), 
                    ],
                    width=8,
                    # La columna entera debe ser un contenedor flex vertical
                    className="h-100 d-flex flex-column",
                ),
                # Columna Derecha (Gráficos - 1/3)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Análisis de Viajes Seleccionados",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(
                                            id="analysis-dropdown",
                                            options=[
                                                {"label": "Número de pasajeros", "value": "passengers"},
                                                {"label": "Distribución del tiempo de viaje", "value": "trip_time"},
                                                {"label": "Distribución de la distancia de viaje", "value": "trip_distance"},
                                            ],
                                            value="passengers",
                                            clearable=False,
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            id="map-info",
                                            className="mb-3 p-2 border rounded border-light bg-secondary",
                                        ),
                                        dcc.Graph(
                                            id="analysis-graph",
                                            style={"width": "100%", "flex": "1", "max-height":"550px"}, 
                                        ),
                                    ],
                                    className="p-3 d-flex flex-column",
                                ),
                            ],
                            # h-100, d-flex flex-column. Ocupa 100% de la columna y es contenedor flex
                            className="shadow-lg border-light h-100 d-flex flex-column",
                        )
                    ],
                    width=4,
                    # La columna entera debe ser un contenedor flex vertical
                    className="h-100 d-flex flex-column",
                ),
            ],
            # La Row principal crece para ocupar el 100% del contenedor viajes_content
            className="mt-4 flex-grow-1",
        ),
    ],
    # Contenedor principal. Fija la altura y se convierte en contenedor flex vertical.
    style={"height": "80vh", "max-height":"85vh"},
    className="p-4 d-flex flex-column",
)


# Contenido para la pestaña Distritos
distritos_content = html.Div(
    [
        dbc.Row(
            [
                # Columna Izquierda (Gráfico)
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
                                            style={"flex": "1"},
                                            responsive=True
                                        )
                                    ]
                                ),
                            ],
                            className="shadow-lg border-light h-100 d-flex flex-column",
                        )
                    ],
                    width=9,
                ),
                # Columna Derecha (Controles)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    dbc.Row(
                                        [
                                            # dbc.Col(
                                            #     InfoIcon(
                                            #         id_prefix="tab1-info",
                                            #         content_dict={
                                            #             "b": "🏢 Información agrupada por distritos",
                                            #             "p": "Observa el tiempo y distancia requeridos para ir de un distrito a otro"
                                            #         }
                                            #     ),
                                            #     width="auto",
                                            #     className="d-flex align-items-center"
                                            # ),
                                            dbc.Col(
                                                "Control de Métrica",
                                                className="d-flex align-items-center"
                                            ),
                                        ],
                                        className="g-2"
                                    ),
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Seleccione la visualización:",
                                            className="text-light",
                                        ),
                                        dcc.Dropdown(
                                            id="distritos-dropdown",
                                            options=[
                                                {
                                                    "label": "Mostrar Distancia Promedio (Heatmap)",
                                                    "value": "distance",
                                                },
                                                {
                                                    "label": "Mostrar Tiempo Promedio (Heatmap)",
                                                    "value": "time",
                                                },
                                                {
                                                    "label": "Comparar Tiempo vs Distancia (Pirámide)",
                                                    "value": "pyramid",
                                                },
                                            ],
                                            value="distance",
                                            clearable=False,
                                            className="mb-3",
                                            style={"flex": "1"}
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-lg border-light d-flex flex-column flex-grow-1",
                        )
                    ],
                    width=3,
                    className="shadow-lg border-light h-100 d-flex flex-column",
                ),
            ],
            className="mt-4 h-100",
        )
    ],
    className="p-4 d-flex flex-column",
    style={"height": "85vh"} 
)

# ----------------------------------------------------------------------
# --- CONTENIDO DE LA PESTAÑA PAGOS ---
# ----------------------------------------------------------------------

pagos_content = html.Div(
    [
        dbc.Row(
            [
                # --- Columna Izquierda: Waffle Plot (2/3) 
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Distribución de Tipos de Pago por Costo (Waffle)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    # El CardBody necesita ser un contenedor flex para que su contenido (el Div) crezca
                                    html.Div(
                                        id="waffle-plot-container",
                                        # 'flex: 1' para que el Div ocupe todo el espacio restante dentro del CardBody
                                        style={"flex": "1"}, 
                                    ),
                                    # 'd-flex flex-column' permite que el div interno crezca
                                    className="p-3 d-flex flex-column",
                                ),
                            ],
                            # h-100 para que la Card ocupe el 100% de la altura de la Columna
                            className="shadow-lg border-light h-100 d-flex flex-column",
                            #style={"height": "80vh"} 
                        )
                    ],
                    width=8,  # Ocupa 2/3 del ancho
                    # La columna debe tomar 100% de la altura de la Row
                    className="h-100", 
                ),
                # --- Columna Derecha: Gráfico Sankey (1/3) 
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
                                        # 'flex: 1' para que el dcc.Graph ocupe todo el CardBody
                                        style={"flex": "1"},
                                        responsive=True # Ayuda a que Plotly.js se ajuste al nuevo tamaño
                                    ),
                                    # CardBody sin padding (p-0) debe ser un contenedor flex
                                    className="p-3 d-flex flex-column",
                                ),
                            ],
                            # La Card debe ser y 'd-flex flex-column' para que CardBody pueda crecer
                            className="shadow-lg border-light h-100 d-flex flex-column",
                        )
                    ],
                    width=4,  # Ocupa 1/3 del ancho
                    # La columna también debe tomar 100% de la altura de la Row
                    className="h-100", 
                ),
            ],
            # La Row necesita crecer para ocupar todo el espacio del Div padre
            className="mt-4 flex-grow-1",
        )
    ],
    # El Div principal establece la altura total (75vh) y es el contenedor Flexbox raíz
    className="p-4 d-flex flex-column",
    style={"height": "80vh"} 
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
                                        # ELIMINADO: style={"height": "600px"}
                                        style={"flex": "1"}, # El gráfico "crece" para llenar el espacio restante
                                        responsive=True # Asegura que Plotly se redibuje al cambiar el tamaño
                                    ),
                                ],
                                className="d-flex flex-column flex-grow-1" # El CardBody crece y apila a sus hijos
                            ),
                        ],
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
                # COLUMNA DE CONTROLES (width=4)
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
                                        # Todo el contenido de filtros tiene altura NATURAL (no crece)
                                        html.Div(
                                            [
                                                html.Label("Borough (Pickup)"),
                                                dcc.Dropdown(
                                                    id="borough-dropdown",
                                                    options=[{"label": "Todos", "value": "ALL"}],
                                                    value=["ALL"],
                                                    multi=True,
                                                    placeholder="Selecciona borough(s)...",
                                                ),
                                                html.Br(),
                                                html.Label("Rango de horas (pickup)"),
                                                dcc.RangeSlider(
                                                    id="hour-range-slider",
                                                    min=0, max=23, step=1, value=[0, 23],
                                                    marks={i: str(i) for i in range(0, 24, 3)},
                                                    tooltip={"placement": "bottom", "always_visible": False},
                                                ),
                                                html.Br(),
                                                html.Label("Métrica de CO₂"),
                                                dcc.RadioItems(
                                                    id="metric-radio",
                                                    options=[
                                                        {"label": "CO₂ total por viaje", "value": "co2_kg_trip"},
                                                        {"label": "CO₂ por km (kg/km)", "value": "co2_kg_per_km"},
                                                        {"label": "CO₂ por pasajero (kg/pax)", "value": "co2_kg_per_passenger"},
                                                    ],
                                                    value="co2_kg_trip",
                                                    inline=False,
                                                ),
                                                html.Hr(),
                                            ],
                                        )
                                    ],
                                    className="p-2 flex-grow-1" # Permitimos que CardBody crezca si la Card lo necesita
                                ),
                            ],
                            className="shadow-sm border-light h-100", # Ocupa el 100% de la Columna
                        ),
                    ],
                    width=4,
                    className="h-100 d-flex flex-column", # Columna toma 100% de altura y es un contenedor flex
                ),
                # COLUMNA DE GRÁFICOS (width=8)
                dbc.Col(
                    [
                        # PRIMER GRÁFICO (Se le permite crecer, pero tiene un mínimo)
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Emisiones horarias (Total / km / pax)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-hourly-graph",
                                        # Eliminamos la altura fija. Usamos flex: 1 para que tome la mitad del espacio restante
                                        style={"flex": "1"}, 
                                        responsive=True 
                                    ),
                                    # CardBody es flex-column para que el dcc.Graph pueda crecer
                                    className="p-2 d-flex flex-column", 
                                ),
                            ],
                            # flex-grow-1, shadow-lg, border-light, mb-3
                            # El mb-3 es un margen que no queremos que flex-grow absorba
                            className="shadow-lg border-light mb-3 flex-grow-1 d-flex flex-column", 
                        ),
                        # SEGUNDO GRÁFICO (Se le permite crecer y tiene una preferencia de espacio)
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Contribución de CO₂ (Treemap)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-treemap-graph",
                                        # ELIMINADO: style={"height": "500px"}
                                        # Usamos flex: 1 para que tome la mitad del espacio restante
                                        style={"flex": "1"}, 
                                        responsive=True
                                    ),
                                    # CardBody es flex-column para que el dcc.Graph pueda crecer
                                    className="p-2 d-flex flex-column",
                                ),
                            ],
                            # flex-grow-1, shadow-lg, border-light, mb-3
                            className="shadow-lg border-light mb-3 flex-grow-1 d-flex flex-column", 
                        ),
                        # Si quieres añadir el tercer gráfico (Mapa), hazlo de la misma forma:
                        # dbc.Card(..., className="... flex-grow-1 d-flex flex-column")
                    ],
                    width=8,
                    # Columna toma 100% de altura y es un contenedor flex vertical para los dos Cards
                    className="h-100 d-flex flex-column", 
                ),
            ],
            # La Row crece para llenar el Div principal
            className="mt-4 flex-grow-1", 
        )
    ],
    # Altura total limitada a 75vh y convertido en contenedor flex vertical
    style={"height": "85vh"},
    className="p-4 d-flex flex-column",
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
            className="mb-2 mt-2 align-items-center",
            style={"height": "5vh", "maxHeight": "10vh"},
            children=[
                # Título a la izquierda
                dbc.Col(
                    html.Div(
                        "Comprendiendo el negocio de Uber en Nueva York",
                        className="display-6 fw-bold text-light",
                    ),
                    width={"size": 6},
                ),
                # Pestañas a la derecha
                dbc.Col(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                label="Viajes",
                                tab_id="tab-viajes",
                                tab_class_name="bg-dark text-secondary",
                                active_tab_class_name="fw-bold text-light bg-primary",
                            ),
                            dbc.Tab(
                                label="Distritos",
                                tab_id="tab-distritos",
                                tab_class_name="bg-dark text-secondary",
                            ),
                            dbc.Tab(
                                label="Pagos",
                                tab_id="tab-pagos",
                                tab_class_name="bg-dark text-secondary",
                            ),
                            dbc.Tab(
                                label="Evolucion",
                                tab_id="tab-evolucion",
                                tab_class_name="bg-dark text-secondary",
                            ),
                            dbc.Tab(
                                label="Emisiones de CO2",
                                tab_id="tab-emisiones-co2",
                                tab_class_name="bg-dark text-secondary",
                            ),
                        ],
                        id="tabs",
                        active_tab="tab-viajes",
                        className="nav-pills",
                    ),
                    width={"size": 6, "offset": 0},
                    className="d-flex justify-content-end",
                ),
            ],
        ),
        # Fila 2: Contenido de la pestaña activa (cargado por callback)
        dbc.Row(dbc.Col(html.Div(id="content-div", className="p-0"), width=12)),
    ],
    fluid=True,
    className="bg-dark text-light p-4",
)
