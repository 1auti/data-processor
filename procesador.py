import pandas as pd
import requests
import time
from requests.auth import HTTPBasicAuth

# CONFIGURACIÓN
API_URL = "http://app:8080/api/transacciones/depositar"
# Usamos las credenciales del usuario (Superman o el que creaste)
USUARIO = "superman@dailyplanet.com"
CLAVE = "kryptonita123"

def procesar_lote(archivo_csv):
    print(f"📂 Leyendo archivo: {archivo_csv}...")
    
    try:
        # 1. Leer el CSV con Pandas (La herramienta n.º 1 de datos)
        df = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        print("❌ Error: No se encuentra el archivo CSV.")
        return

    print(f"📊 Se encontraron {len(df)} transacciones para procesar.\n")

    # 2. Iterar por cada fila y enviarla a Java
    exitos = 0
    errores = 0

    for index, fila in df.iterrows():
        cuenta_id = int(fila['cuenta_id'])
        monto = float(fila['monto'])
        
        # Preparamos el JSON para la API de Java
        payload = {
            "cuentaId": cuenta_id,
            "monto": monto
        }

        print(f"🔄 Procesando transacción #{index + 1}: Depósito de ${monto} a Cuenta {cuenta_id}...")

        try:
            # 3. LLAMADA HTTP A JAVA (El puente entre los dos lenguajes)
            respuesta = requests.post(
                API_URL, 
                json=payload, 
                auth=HTTPBasicAuth(USUARIO, CLAVE) # Autenticación Segura
            )

            if respuesta.status_code == 200:
                print(f"   ✅ Éxito! Nuevo saldo: {respuesta.json()['saldo']}")
                exitos += 1
            else:
                print(f"   ❌ Error API ({respuesta.status_code}): {respuesta.text}")
                errores += 1

        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            errores += 1
        
        # Pequeña pausa para simular procesamiento real y no saturar
        time.sleep(0.5)

    print("\n" + "="*40)
    print(f"🏁 PROCESO TERMINADO")
    print(f"✅ Exitosos: {exitos}")
    print(f"❌ Fallidos: {errores}")
    print("="*40)

if __name__ == "__main__":
    procesar_lote("lote_depositos.csv")