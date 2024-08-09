import threading 
import time
import random
import requests

# Configuración de los servicios
servicios = [
    {"nombre": "Service 1", "token": "token1", "port": 5001},
    {"nombre": "Service 2", "token": "token2", "port": 5002},
    {"nombre": "Service 3", "token": "token3", "port": 5003},
]

# Función para generar logs
def generar_log(servicio):
    log = {
        "marca_tiempo": int(time.time()),
        "nombre_servicio": servicio["nombre"],
        "gravedad": random.choice(["INFO", "ERROR", "DEBUG"]),
        "mensaje": f"Registro desde {servicio['nombre']}",
    }
    return log

# Función para enviar logs al servidor central
def enviar_log(log, servicio):
    headers = {"Authorization": f"Bearer {servicio['token']}"}
    respuesta = requests.post(f"http://localhost:5000/logs", json=log, headers=headers)
    if respuesta.status_code == 200:
        print(f"Registro enviado al servidor: {log}")
    else:
        print(f"Error al enviar registro: {respuesta.text}")

# Función para ejecutar un servicio
def ejecutar_servicio(servicio):
    while True:
        log = generar_log(servicio)
        enviar_log(log, servicio)
        time.sleep(random.randint(1, 5))  # Esperar un tiempo aleatorio antes de generar el próximo log

# Crear hilos para cada servicio
hilos = []
for servicio in servicios:
    t = threading.Thread(target=ejecutar_servicio, args=(servicio,))
    hilos.append(t)
    t.start()

# Esperar a que los hilos terminen
for t in hilos:
    t.join()
