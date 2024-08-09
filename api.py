import sqlite3
import threading
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

_hilo_local = threading.local()

def obtener_db():
    if not hasattr(_hilo_local, 'db'):
        _hilo_local.db = sqlite3.connect("logs.db")
        _hilo_local.cursor = _hilo_local.db.cursor()
    return _hilo_local.cursor

def crear_tabla():
    cursor = obtener_db()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            marca_tiempo INTEGER,
            nombre_servicio TEXT,
            gravedad TEXT,
            mensaje TEXT,
            recibido_en INTEGER
        );
    """)
    _hilo_local.db.commit()

crear_tabla()

# API endpoint para recibir logs
@app.route("/logs", methods=["POST"])
def recibir_log():
    log = request.get_json()
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        if token in ["token1", "token2", "token3"]:  # Tokens válidos
            cursor = obtener_db()
            cursor.execute("""
                INSERT INTO logs (marca_tiempo, nombre_servicio, gravedad, mensaje, recibido_en)
                VALUES (?, ?, ?, ?, ?);
            """, (log["marca_tiempo"], log["nombre_servicio"], log["gravedad"], log["mensaje"], int(time.time())))
            _hilo_local.db.commit()
            return jsonify({"mensaje": "Log recibido con exito"}), 200
        else:
            return jsonify({"error": "Token no valido"}), 401
    else:
        return jsonify({"error": "Token ausente"}), 401

# API endpoint para obtener logs
@app.route("/logs", methods=["GET"])
def obtener_logs():
    filtros = []
    valores = []

    if "fecha_inicio" in request.args and "fecha_fin" in request.args:
        filtros.append("marca_tiempo BETWEEN ? AND ?")
        valores.extend([request.args['fecha_inicio'], request.args['fecha_fin']])

    if "nombre_servicio" in request.args:
        filtros.append("nombre_servicio = ?")
        valores.append(request.args['nombre_servicio'])

    query = "SELECT * FROM logs"
    if filtros:
        query += " WHERE " + " AND ".join(filtros)

    cursor = obtener_db()
    cursor.execute(query, valores)
    logs = cursor.fetchall()

    # Convertir los resultados en una lista de diccionarios
    resultado = [dict(zip([desc[0] for desc in cursor.description], row)) for row in logs]

    return jsonify(resultado), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
