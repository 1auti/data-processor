# -------------------------------------------------------------------
# ETAPA 1: IMAGEN BASE
# Usamos la imagen oficial de Python
# -------------------------------------------------------------------
FROM python:3.11-slim

# Creamos la carpeta de trabajo
WORKDIR /app

# -------------------------------------------------------------------
# ETAPA 2: INSTALACIÓN DE DEPENDENCIAS
# -------------------------------------------------------------------
# Copiamos el archivo de dependencias (necesitas crearlo, ver Paso 2)
COPY requirements.txt .

# Instalamos las librerías necesarias (requests y pandas)
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------------
# ETAPA 3: COPIAR CÓDIGO Y DATOS
# -------------------------------------------------------------------
# Copiamos el script Python y el archivo CSV de entrada
COPY procesador.py .
COPY lote_depositos.csv .

# -------------------------------------------------------------------
# ETAPA 4: COMANDO DE EJECUCIÓN
# -------------------------------------------------------------------
# Definimos el comando que se ejecutará al iniciar el contenedor
CMD ["python", "procesador.py"]