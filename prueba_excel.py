from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import re
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

app = Flask(__name__)

IMAGE_FOLDER = 'img'
AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

def cargar_estudiantes():
    estudiantes = {}
    with open('Listado Cuarto Bachillerato.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            carnet = str(int(float(row['carnet']))).strip()
            estudiantes[carnet] = {
                'nombre': row['nombre'].strip(),
                'apellido': row['apellido'].strip(),
                'carrera': row['carrera'].strip(),
                'imagen': f"{carnet}.jpg",
                'audio': f"{carnet}.mp3"
            }
    return estudiantes

# Cargar estudiantes en memoria
estudiantes = cargar_estudiantes()

# Variables para Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
KEY = 'key.json'  # Ruta a tu archivo de credenciales JSON
SPREADSHEET_ID = '115618885441416093269'  # ID de tu Google Spreadsheet

# Conectar a la API de Google Sheets usando el archivo de credenciales
def conectar_google_sheets_api():
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

# Registrar asistencia en Google Sheets mediante la API
def registrar_asistencia_google_sheets(carnet, nombre, apellido, carrera):
    sheet = conectar_google_sheets_api()

    # Obtener la hora actual
    hora_entrada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Datos a insertar en la hoja de cálculo
    values = [[carnet, nombre, apellido, carrera, hora_entrada]]

    # Escribir los datos en la hoja, en la celda adecuada (ejemplo en la primera hoja, comenzando en A1)
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='A1',
        valueInputOption='USER_ENTERED',
        body={'values': values}
    ).execute()

    print(f"Datos insertados correctamente. {result.get('updates').get('updatedCells')} celdas actualizadas.")

# Ruta principal para mostrar el HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar el escaneo del código QR
@app.route('/scan', methods=['POST'])
def scan():
    codigo_qr = request.json['codigo_qr'].strip()

    # Buscar el carnet en el código QR usando expresión regular
    carnet_match = re.search(r'Carnet:\s*(\d+)', codigo_qr)
    if carnet_match:
        codigo_qr = carnet_match.group(1)

    # Buscar el estudiante en la base de datos
    estudiante = estudiantes.get(codigo_qr, None)

    if estudiante:
        # Registrar asistencia en Google Sheets
        registrar_asistencia_google_sheets(
            carnet=codigo_qr,
            nombre=estudiante['nombre'],
            apellido=estudiante['apellido'],
            carrera=estudiante['carrera']
        )

        audio_url = f"/audio/{estudiante['audio']}"
        return jsonify({
            'nombre': estudiante['nombre'],
            'apellido': estudiante['apellido'],
            'carrera': estudiante['carrera'],
            'carnet': codigo_qr,
            'imagen': f"/images/{estudiante['imagen']}",
            'audio': audio_url
        })
    else:
        return jsonify({'error': 'Estudiante no encontrado'})

# Rutas para servir imágenes y audios
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
