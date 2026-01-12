# 🐳 Ejecutar la aplicación
```bash
# Construir la imagen
docker build -t dash-app .

# Ejecutar el contenedor
docker run -p 8050:8050 dash-app
```
**Una vez hecho esto, entrar en *localhost:8050*** (Independientemente del texto mostrado en el terminal)

# 🖥️ Análisis del Dashboard
La siguiente sección ofrece información acerca de cómo interactuar con el dashboard. 

El dashboard está dividido en varias secciones, cada una de las cuales pretende ofrecer información sobre una dimensión del negocio de Uber.

## 🚗 Viajes
Debido a la complejidad de esta vista, hay un botón de información (ℹ️) que indica brevemente cómo interactuar con los gráficos y el mapa.  
A continuación se ofrecen indicaciones más detalladas con el objetivo de aprovechar completamente las funcionalidades de la interfaz.

### 🗺️ Mapa de trayectorias
Interactúa con:

* **Botón “Ver salidas/llegadas”**  
    - Permite mostrar en el mapa las **salidas** (lugares donde el conductor ha recogido al pasajero) o **llegadas** (lugares donde el pasajero ha abandonado el vehículo).

* **Selector de hora de inicio y hora fin**  
    - Tanto los gráficos laterales como el mapa se actualizarán con los viajes que hayan comenzado entre las horas elegidas.

* **Click en un icono de coche**  
    - Filtra el mapa para mostrar solo el viaje asociado a ese icono (salida y llegada).  
    - El mapa ajustará el zoom automáticamente para mostrar ambos puntos.  
    - Si se vuelve a hacer click sobre cualquiera de los coches, se mostrará información detallada del viaje: número de pasajeros, dinero total ganado, duración y distancia.  
    - Para volver a ver todos los iconos, pulsa nuevamente el botón *Mostrar salidas/llegadas*.

### 🧳 Plots sobre los viajes
Los plots del tercio derecho **reaccionan dinámicamente** a los viajes mostrados.  
Cualquier interacción en el mapa (zoom, desplazamiento, cambio de hora, etc.) actualiza estos gráficos.

Se muestran tres gráficos principales:
* **Treemap** → Cantidad de viajes realizados según el número de pasajeros.  
* **Violin plots** → Distribución del tiempo y la distancia de los viajes.

Estos gráficos permiten analizar la **frecuencia y dispersión** de los viajes visibles en ese momento en pantalla.



## 🏢 Distritos
Esta pestaña muestra información sobre la **distancia y el tiempo de los viajes** realizados **entre distritos** y **dentro del mismo distrito**.  
Los datos se presentan mediante los siguientes gráficos:

* **Heatmaps de tiempo y distancia**  
    - Muestran la media de tiempo y distancia de los viajes entre cada par de distritos.  
    - Los valores más altos se representan con colores más intensos, facilitando la identificación de trayectos más largos o lentos.

* **Doble Radial Map (tiempo y distancia)**  
    - Permite comparar visualmente las conexiones de cada distrito con el resto.  
    - Un mapa radial muestra la distancia media, y el otro el tiempo medio de viaje.  
    - Al pasar el cursor, se resalta el valor específico del trayecto.

## 💳 Ventana de Pagos
Esta sección permite explorar la información relacionada con los **métodos de pago** y el **flujo económico**.

* **Waffle plot de tipos de pago**  
    - Muestra los tipos de pago utilizados, divididos en 4 rangos de precio.  
    - Al hacer *hover*, se muestra el **porcentaje** que representa ese tipo de pago dentro del rango.

* **Sankey plot del flujo de dinero**  
    - Representa el flujo desde las fuentes de ingreso (**ganancia base, propina y extras**) hasta las categorías finales (**total, recargo y peajes**).  
    - Al pasar el cursor sobre un enlace o nodo, se muestra el **monto exacto** correspondiente.

---

## 📈 Evolución del negocio
La tabla **Evolución** muestra cómo cambian a lo largo de las horas las distintas características clave del negocio:

* Número de pasajeros.
* Ingresos totales.
* Minutos totales de viaje.
* Distancia total recorrida.

Estos datos permiten identificar los **picos de demanda** y los periodos de **mayor actividad**.

---

## 🌿 Emisiones de CO₂
La pestaña de emisiones permite visualizar el impacto ambiental de los viajes de Uber en la ciudad.

* **Tabla de emisiones totales por hora**  
    - Muestra los kilogramos totales de CO₂ emitidos en cada franja horaria.  
    - Al hacer *hover*, se muestra el valor exacto en kg para esa hora.

* **Gráfico de emisiones de CO₂ por distrito**  
    - Permite analizar el CO₂ emitido por viajes que comienzan en un distrito concreto.  
    - Se puede filtrar por **rango de hora** y **distrito de salida**.  
    - Además, se puede alternar entre visualizar las **emisiones totales por viaje** o las **emisiones por pasajero**.

---

# 🧩 Recolección y Procesamiento de Datos
El procesamiento de los datos se realizó en el notebook **`data_preprocessing.ipynb`**, a partir del dataset público de **[praveenluppunda/uber-dataset](https://github.com/praveenluppunda/uber-dataset)**.

### 📦 Limpieza y filtrado de datos
1. **Eliminación de coordenadas inválidas:**  
   Se eliminaron todas las filas con coordenadas (0,0) por no corresponder a ubicaciones reales.

2. **Asignación geoespacial de distritos:**  
   Se implementó un proceso de unión espacial (*spatial join*) entre las coordenadas de inicio y fin del viaje y los límites geográficos de los distritos de Nueva York.  
   Este procedimiento permite identificar a qué **distrito** pertenece cada punto.  
   *(Ver código en la sección de procesamiento geoespacial).*

3. **Transformación de variables categóricas:**  
   - `RatecodeID` y `payment_type` se transformaron de valores numéricos a categorías descriptivas (p. ej. *Standard rate*, *Credit card*, *Cash*, etc.).  
   - Se eliminó la columna `store_and_fwd_flag` por no aportar información relevante.

4. **Eliminación de outliers extremos:**  
   Se eliminaron únicamente los viajes con valores de **distancia o duración excesivos**, considerados fuera del alcance del análisis (basado en el rango intercuartílico, con un umbral de 3×IQR).

---

## 🌍 Procesamiento Geoespacial
El siguiente fragmento muestra cómo se asignan los distritos a las coordenadas de inicio y fin de cada viaje mediante un proceso de unión espacial sobre los límites oficiales de los *distritos* de Nueva York:

```python
# --- PROCESAMIENTO GEOESPACIAL ---
def assign_borough_from_geometry(df: pd.DataFrame, lat_col: str, lon_col: str, output_col: str) -> pd.DataFrame:
    """
    Asigna el distrito (borough) a las coordenadas usando una unión espacial.
    """
    print(f"\n--- Iniciando asignación de distrito para {output_col} ---")
    nyc_boundaries_url = "https://data.cityofnewyork.us/resource/gthc-hcne.geojson"
    try:
        boroughs_gdf = gpd.read_file(nyc_boundaries_url)
        boroughs_gdf.rename(columns={'boroname': 'borough_name_geo'}, inplace=True)
        boroughs_gdf = boroughs_gdf.to_crs(epsg=4326)
    except Exception as e:
        print(f"Error al cargar límites de distritos: {e}")
        return df
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    points_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    join_result = gpd.sjoin(points_gdf, boroughs_gdf[['borough_name_geo', 'geometry']], how="left", predicate="within")
    df[output_col] = join_result['borough_name_geo'].reindex(df.index).fillna('Out of NYC/Unknown')
    return df

```

---

## 💨 Cálculo de Emisiones de CO₂
Las emisiones se estimaron con base en metodologías **EMEP/COPERT** y factores de conversión **DEFRA (UK)**.

**Resumen del cálculo:**

1. **Consumo de combustible dependiente de la velocidad:**
   $$
   \text{consumo\_combustible\_g\_por\_km} = 81.1 - 1.014 \cdot V + 0.0068 \cdot V^2
   $$
   donde \(V\) es la velocidad media del viaje (km/h).

2. **Conversión de consumo a litros por kilómetro:**
   $$
   \text{litros\_por\_km} = \frac{\text{consumo\_g\_por\_km} / 1000}{\rho_{\text{gasolina}}}
   $$
   con \(\rho_{\text{gasolina}} \approx 0.74\, \text{kg/L}\).

3. **Conversión a emisiones de CO₂:**
   $$
   \text{kgCO2\_por\_km} = \text{litros\_por\_km} \times 2.0844
   $$

4. **Emisiones totales y por pasajero:**
   $$
   \text{emisiones\_viaje} = \text{kgCO2\_por\_km} \times \text{distancia\_km}
   $$
   $$
   \text{emisiones\_por\_pasajero} = \frac{\text{emisiones\_viaje}}{\max(1, \text{nº\_pasajeros})}
   $$

```python
# --- ESTIMACIÓN DE CO2 ---
FUEL_DENSITY_KG_PER_L = 0.74
CO2_PER_LITRE_KG = 2.0844

def fuel_g_per_km_emep_petrol(V_kmh: float) -> float:
    if np.isnan(V_kmh) or V_kmh <= 0:
        return np.nan
    V = float(np.clip(V_kmh, 10.0, 130.0))
    return 81.1 - 1.014 * V + 0.0068 * V**2

def co2_per_km_from_speed(V_kmh: float) -> float:
    fuel_g_km = fuel_g_per_km_emep_petrol(V_kmh)
    if np.isnan(fuel_g_km):
        return np.nan
    fuel_kg_km = fuel_g_km / 1000.0
    fuel_l_km = fuel_kg_km / FUEL_DENSITY_KG_PER_L
    return fuel_l_km * CO2_PER_LITRE_KG

def estimate_co2_dataframe(df: pd.DataFrame,
                           distance_col='trip_distance_km',
                           minutes_col='trip_minutes',
                           passengers_col='passenger_count'):
    df = df.copy()
    df['avg_speed_kmh'] = df[distance_col] / (df[minutes_col] / 60.0)
    df['co2_kg_per_km'] = df['avg_speed_kmh'].apply(co2_per_km_from_speed)
    df['co2_kg_trip'] = df['co2_kg_per_km'] * df[distance_col]
    df['passenger_count_safe'] = df[passengers_col].replace({0:1}).fillna(1)
    df['co2_kg_per_passenger'] = df['co2_kg_trip'] / df['passenger_count_safe']
    return df

```


## ⚒️ Transformaciones finales
Antes de la carga de datos al dashboard, se aplicaron las siguientes transformaciones adicionales:
- Conversión de categorías (`RatecodeID`, `payment_type`).
- Eliminación de columnas no necesarias.
- Filtrado de outliers extremos.
- Cálculo final de columnas derivadas:
  - `avg_speed_kmh`
  - `co2_kg_trip`
  - `co2_kg_per_passenger`

```python
# --- TRANSFORMACIONES FINALES ---
ratecode_map = {
    1: "Standard rate",
    2: "JFK",
    3: "Newark",
    4: "Nassau or Westchester",
    5: "Negotiated fare",
    6: "Group ride",
    99: "Null/unknown"
}
if 'RatecodeID' in df.columns:
    df['RatecodeID'] = df['RatecodeID'].map(ratecode_map)

payment_type_map = {
    0: "Flex Fare trip",
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip"
}
if 'payment_type' in df.columns:
    df['payment_type'] = df['payment_type'].map(payment_type_map)

if 'store_and_fwd_flag' in df.columns:
    df = df.drop(columns=['store_and_fwd_flag'])

# Filtrado de outliers extremos
nrows = df.shape[0]
for col in ['trip_distance_km', 'trip_minutes']:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
print(f"{nrows - df.shape[0]} filas eliminadas")

```



## 🧾 Resumen
El pipeline completo permite obtener un dataset **limpio, enriquecido y ambientalmente contextualizado**, que sustenta el dashboard interactivo de Uber.  
El resultado final combina datos operativos, económicos y ecológicos para ofrecer una visión integral del negocio.



## 📚 Referencias
- Agencia Europea del Medio Ambiente (EMEP/COPERT)  
- DEFRA (UK Department for Environment, Food and Rural Affairs)  
- Dataset base: [praveenluppunda/uber-dataset](https://github.com/praveenluppunda/uber-dataset)  
- Datos geográficos: [NYC Open Data – Borough Boundaries](https://data.cityofnewyork.us/resource/gthc-hcne.geojson)


