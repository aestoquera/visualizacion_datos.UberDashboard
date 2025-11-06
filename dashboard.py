# app.py
# Punto de entrada principal de la aplicación Dash.

from dash import Dash
import dash_bootstrap_components as dbc

# Importar el layout y la función de registro de callbacks
from layout import app_layout
from callbacks import register_callbacks

# --- Crear app ---
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
)

# Asignar el layout a la aplicación
app.layout = app_layout

# Registrar todos los callbacks en la aplicación
register_callbacks(app)

# --- Ejecutar ---
if __name__ == "__main__":
    app.run(debug=True)
