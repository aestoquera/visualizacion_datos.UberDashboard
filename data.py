# data.py
# Responsable de la carga, pre-procesamiento de datos y definiciones de activos.

import pandas as pd
import dash_leaflet as dl
from dash import html

# --- Cargar datos ---
try:
    print("Leyendo datos...")
    data = pd.read_csv("uber_dataset_con_distritos.csv")
    print("Datos leidos!")
    data["tpep_pickup_datetime"] = pd.to_datetime(data["tpep_pickup_datetime"])
    data["tpep_dropoff_datetime"] = pd.to_datetime(data["tpep_dropoff_datetime"])
    #data = data.sample(1_000)
    print("Datos listos!")
except FileNotFoundError:
    print("Error: El archivo 'uber_dataset_procesado.csv' no se encontró.")
    # Crear un DataFrame vacío para evitar que la app falle al importar
    data = pd.DataFrame(
        columns=[
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "passenger_count",
            "total_amount",
            "trip_minutes",
            "trip_distance_km",
        ]
    )

# --- Íconos ---
green_icon = {"iconUrl": "/assets/green_car.png", "iconSize": [25, 25]}
red_icon = {"iconUrl": "/assets/red_car.png", "iconSize": [25, 25]}
ICON_MAP = {
    "Credit card": "/assets/credit_card.png",
    "Cash": "/assets/cash.png",
    "No charge": "/assets/no_charge.png",
    "Dispute": "/assets/dispute.png",
    "Otros": "/assets/unknown.png", 
}

# --- Marcadores ---
pickup_markers = []
dropoff_markers = []

if not data.empty:
    for i, row in data.iterrows():
        popup_content = html.Div(
            [
                html.H5("🚖 Información del viaje", className="text-dark"),
                html.P(f"👤 Pasajeros: {row['passenger_count']}"),
                html.P(f"💰 Total: ${row['total_amount']:.2f}"),
                html.P(f"⏱️ Duración: {row['trip_minutes']:.1f} min"),
                html.P(f"🛣️ Distancia: {row['trip_distance_km']:.2f} km"),
            ],
            className="text-secondary",
        )

# --- Centro del mapa ---
if not data.empty:
    center_lat = data["pickup_latitude"].median()
    center_lon = data["pickup_longitude"].median()
else:
    center_lat = 40.7128  # Coordenadas de NYC como fallback
    center_lon = -74.0060
