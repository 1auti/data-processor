# 🐍 Fintech Data Processor - Microservicio de Carga Batch

## 🎯 Objetivo
Este microservicio tiene la función de simular la carga de archivos batch (CSV) que contienen transacciones pendientes (depósitos). Su propósito es demostrar la comunicación entre servicios heterogéneos (Python y Java) dentro de un entorno Docker Compose.

## ⚙️ Características Clave
- **Librerías:** `pandas` (lectura de datos), `requests` (cliente HTTP).
- **Proceso:** Lee `lote_depositos.csv` y envía cada fila como una solicitud `POST` a la API Java.
- **Sincronización:** Utiliza la red interna de Docker (`http://app:8080`) y está configurado en el `docker-compose.yml` para esperar la condición `service_healthy` de la API Java.

## 🚀 Uso (Ejecución Atómica)
Este script se ejecuta automáticamente en el arranque completo del sistema.

```bash
# Ejecutar desde la raíz del proyecto principal (fintech-core)
docker compose up --build