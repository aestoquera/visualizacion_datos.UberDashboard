# Usar una imagen base oficial de Python 3.10
FROM python:3.10-slim

# Establecer directorio de trabajo en el contenedor
WORKDIR /app

# Copiar archivos de requerimientos y código al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto por defecto de Dash
EXPOSE 8050

# Comando para ejecutar la app
CMD ["python", "dashboard.py"]
