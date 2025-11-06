# layout.py
# Define el layout completo de la aplicación y el contenido de las pestañas.

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd

# Importar variables pre-calculadas del módulo de datos
from data import data, pickup_markers, center_lat, center_lon

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
                                        # Columna para el Botón (Aproximadamente 4 unidades de ancho)
                                        dbc.Col(
                                            dbc.Button(
                                                "Mostrando salidas",
                                                id="toggle-view-btn",
                                                color="light",
                                                className="w-100",  # w-100 para ocupar todo el ancho de la columna
                                            ),
                                            # Ajustamos la altura del botón para que esté centrado verticalmente
                                            # y definimos el ancho de la columna (e.g., 4 de 12)
                                            width=4,
                                            className="d-flex align-items-center mb-3",
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
                                            width=8,
                                        ),
                                    ],
                                    className="g-2",  # g-0 elimina el espaciado horizontal (gutter) entre columnas
                                ),
                            ]
                        ),
                        # Bloque del Mapa
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Mapa Interactivo de Viajes",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dl.Map(
                                        id="map",
                                        center=[center_lat, center_lon],
                                        zoom=13,
                                        style={"width": "100%", "height": "600px"},
                                        children=[dl.TileLayer()],
                                    )
                                ),
                            ],
                            className="shadow-lg border-light",
                        ),
                    ],
                    width=8,
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
                                            style={"height": "490px"},
                                        ),
                                    ],
                                    className="p-3",
                                ),
                            ],
                            className="shadow-lg border-light",
                        )
                    ],
                    width=4,
                ),
            ],
            className="mt-4",
        ),
    ],
    className="p-4",
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
                                            style={"height": "650px"},
                                        )
                                    ]
                                ),
                            ],
                            className="shadow-lg border-light",
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
                                    "Control de Métrica",
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
                                        ),
                                    ]
                                ),
                            ],
                            className="shadow-lg border-light",
                        )
                    ],
                    width=3,
                ),
            ],
            className="mt-4",
        )
    ],
    className="p-4",
)

# ----------------------------------------------------------------------
# --- CONTENIDO DE LA PESTAÑA PAGOS ---
# ----------------------------------------------------------------------

pagos_content = html.Div(
    [
        dbc.Row(
            [
                # --- Columna Izquierda: Waffle Plot (2/3) --- (AHORA AQUI)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Distribución de Tipos de Pago por Costo (Waffle)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    # Este Div será llenado por el callback con el Waffle Plot generado en HTML
                                    html.Div(
                                        id="waffle-plot-container",
                                        style={"height": "650px", "overflowY": "auto"},
                                    ),
                                    className="p-3",
                                ),
                            ],
                            className="shadow-lg border-light",
                        )
                    ],
                    width=8,
                ),  # Ocupa 2/3 del ancho (8 unidades)
                # --- Columna Derecha: Gráfico Sankey (1/3) --- (AHORA AQUI)
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
                                        id="sankey-graph", style={"height": "650px"}
                                    ),
                                    className="p-0",
                                ),
                            ],
                            className="shadow-lg border-light",
                        )
                    ],
                    width=4,
                ),  # Ocupa 1/3 del ancho (4 unidades)
            ],
            className="mt-4",
        )
    ],
    className="p-4",
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
                                        value='passenger_count', # Valor por defecto
                                        inline=True, # Muestra las opciones en horizontal
                                        className="mb-4",
                                    ),
                                    # El gráfico se renderizará aquí
                                    dcc.Graph(
                                        id="lollipop-chart", 
                                        style={"height": "600px"}
                                    ),
                                ]
                            ),
                        ],
                        className="shadow-lg border-light",
                    ),
                    width=12, # Ocupa todo el ancho
                )
            ],
            className="mt-4",
        )
    ],
    className="p-4",
)
# ----------------------------------------------------------------------
# --- LAYOUT EMISIONES CARBONO ---
# ----------------------------------------------------------------------
emisiones_de_carbono_content = html.Div(
    [
        dbc.Row(
            [
                # CONTROLES (columna derecha más pequeña)
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
                                                html.Label("Borough (Pickup)"),
                                                dcc.Dropdown(
                                                    id="borough-dropdown",
                                                    options=[
                                                        {
                                                            "label": "Todos",
                                                            "value": "ALL",
                                                        }
                                                    ],
                                                    value=["ALL"],
                                                    multi=True,
                                                    placeholder="Selecciona borough(s)...",
                                                ),
                                                html.Br(),
                                                html.Label("Rango de horas (pickup)"),
                                                dcc.RangeSlider(
                                                    id="hour-range-slider",
                                                    min=0,
                                                    max=23,
                                                    step=1,
                                                    value=[0, 23],
                                                    marks={
                                                        i: str(i)
                                                        for i in range(0, 24, 3)
                                                    },
                                                    tooltip={
                                                        "placement": "bottom",
                                                        "always_visible": False,
                                                    },
                                                ),
                                                html.Br(),
                                                html.Label("Métrica de CO₂"),
                                                dcc.RadioItems(
                                                    id="metric-radio",
                                                    options=[
                                                        {
                                                            "label": "CO₂ total por viaje",
                                                            "value": "co2_kg_trip",
                                                        },
                                                        {
                                                            "label": "CO₂ por km (kg/km)",
                                                            "value": "co2_kg_per_km",
                                                        },
                                                        {
                                                            "label": "CO₂ por pasajero (kg/pax)",
                                                            "value": "co2_kg_per_passenger",
                                                        },
                                                    ],
                                                    value="co2_kg_trip",
                                                    inline=False,
                                                ),
                                                html.Hr(),
                                            ]
                                        )
                                    ],
                                    className="p-2",
                                ),
                            ],
                            className="shadow-sm border-light",
                        ),
                    ],
                    width=4,
                ),
                # GRÁFICOS (columna izquierda mayor)
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Emisiones horarias (Total / km / pax)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-hourly-graph", style={"height": "320px"}
                                    ),
                                    className="p-2",
                                ),
                            ],
                            className="shadow-lg border-light mb-3",
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Contribución de CO₂ (Treemap)",
                                    className="fw-bold bg-dark text-light",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="co2-treemap-graph",
                                        style={"height": "500px"},
                                    ),
                                    className="p-2",
                                ),
                            ],
                            className="shadow-lg border-light mb-3",
                        ),
                        # dbc.Card(
                        #     [
                        #         dbc.CardHeader(
                        #             "Mapa de pickups (CO₂ por viaje)",
                        #             className="fw-bold bg-dark text-light",
                        #         ),
                        #         dbc.CardBody(
                        #             dcc.Graph(
                        #                 id="co2-map-graph", style={"height": "520px"}
                        #             ),
                        #             className="p-2",
                        #         ),
                        #     ],
                        #     className="shadow-lg border-light mb-3",
                        # ),
                    ],
                    width=8,
                ),
            ],
            className="mt-4",
        )
    ],
    className="p-4",
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
            className="mb-2 mt-2 align-items-end",
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
