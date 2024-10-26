from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuración inicial de la base de datos
def inicializar_db():
    conn = sqlite3.connect('sensores.db')  
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temperaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL NOT NULL,
            humedad REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


inicializar_db()


@app.route('/api/ambiente', methods=['POST'])
def recibir_ambiente():
    data = request.get_json()  
    temperatura = data.get('temperatura')  
    humedad = data.get('humedad')          

    if temperatura is not None and humedad is not None:
        guardar_ambiente(temperatura, humedad)
        print(f"Temperatura recibida y guardada: {temperatura} °C, Humedad: {humedad} %")
        return jsonify({"mensaje": "Datos recibidos correctamente"}), 200
    else:
        return jsonify({"error": "No se recibieron datos completos"}), 400

# Función para guardar los datos en la base de datos
def guardar_ambiente(temperatura, humedad):
    conn = sqlite3.connect('sensores.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
    cursor.execute('''
        INSERT INTO temperaturas (temperatura, humedad, timestamp)
        VALUES (?, ?, ?)
    ''', (temperatura, humedad, timestamp))
    conn.commit()
    conn.close()

# Ruta para mostrar los datos en una página HTML
@app.route('/datos')
def ver_datos():
    conn = sqlite3.connect('sensores.db')
    cursor = conn.cursor()
    cursor.execute("SELECT temperatura, humedad, timestamp FROM temperaturas ORDER BY timestamp DESC")
    datos = cursor.fetchall()  
    conn.close()

    
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Datos del Cultivo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            h1 {
                color: #444;
            }
            table {
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            th, td {
                padding: 12px;
                text-align: center;
            }
            th {
                background-color: #6c757d;
                color: #ffffff;
                font-weight: bold;
                border-bottom: 3px solid #dee2e6;
            }
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            tr:nth-child(odd) {
                background-color: #e9ecef;
            }
            tr:hover {
                background-color: #dfe4ea;
            }
            td {
                border-bottom: 1px solid #dee2e6;
                border-right: 1px solid #dee2e6;
            }
            td:last-child {
                border-right: none;
            }
            th:last-child {
                border-right: none;
            }
            .status-on {
                background-color: rgba(40, 167, 69, 0.3); /* Verde opaco */
                color: #28a745;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            .status-off {
                background-color: rgba(220, 53, 69, 0.3); /* Rojo opaco */
                color: #dc3545;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Temperatura y Humedad Registradas</h1>
        <table border="1">
            <tr>
                <th>Temperatura (°C)</th>
                <th>Humedad (%)</th>
                <th>Fecha y Hora</th>
                <th>Ventilador</th>
                <th>Caloventor</th>
                <th>Humidificador</th>
            </tr>
            {% for temp, hum, timestamp in datos %}
            <tr>
                <td>{{ temp }}</td>
                <td>{{ hum }}</td>
                <td>{{ timestamp }}</td>
                <td class="{{ 'status-on' if temp > 25 else 'status-off' }}">{{ 'Encendido' if temp > 25 else 'Apagado' }}</td>
                <td class="{{ 'status-on' if temp < 18 else 'status-off' }}">{{ 'Encendido' if temp < 18 else 'Apagado' }}</td>
                <td class="{{ 'status-on' if hum < 40 else 'status-off' }}">{{ 'Encendido' if hum < 40 else 'Apagado' }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    return render_template_string(html, datos=datos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
