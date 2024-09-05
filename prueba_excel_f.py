from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import re
import pandas as pd
import datetime

app = Flask(__name__)

IMAGE_FOLDER = 'img'
AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
EXCEL_FILE = 'asistencia.xlsx'  # Archivo Excel para registrar asistencia


# Función para cargar los estudiantes desde un archivo CSV
def cargar_estudiantes():
    estudiantes = {}
    with open('Listado Cuarto Bachillerato.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            carnet = str(int(float(row['carnet']))).strip()  # Ajustar formato del carnet
            estudiantes[carnet] = {
                'nombre': row['nombre'].strip(),
                'apellido': row['apellido'].strip(),
                'carrera': row['carrera'].strip(),
                'imagen': f"{carnet}.jpg",  # Asume que la imagen se nombra según el carnet
                'audio': f"{carnet}.mp3"    # Asume que el audio se nombra según el carnet
            }
    return estudiantes

# Cargar los estudiantes al inicio
estudiantes = cargar_estudiantes()

# Función para registrar la asistencia en el archivo Excel
def registrar_asistencia(carnet, nombre, apellido, carrera):
    # Obtener la hora actual
    hora_entrada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Crear un diccionario con la información a registrar
    registro = {
        'Carnet': carnet,
        'Nombre': nombre,
        'Apellido': apellido,
        'Carrera': carrera,
        'Hora de Entrada': hora_entrada
    }
    
    # Verificar si el archivo Excel ya existe
    if not os.path.exists(EXCEL_FILE):
        # Si no existe, crear un DataFrame nuevo con las columnas correspondientes
        df = pd.DataFrame(columns=['Carnet', 'Nombre', 'Apellido', 'Carrera', 'Hora de Entrada'])
    else:
        # Leer el archivo Excel existente
        df = pd.read_excel(EXCEL_FILE)
    
    # Agregar el nuevo registro al DataFrame
    df = df.append(registro, ignore_index=True)
    
    # Guardar el DataFrame en el archivo Excel
    df.to_excel(EXCEL_FILE, index=False)


# Ruta principal para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar el escaneo del código QR
@app.route('/scan', methods=['POST'])
def scan():
    # Obtener el código QR desde la solicitud
    codigo_qr = request.json['codigo_qr'].strip()
    
    # Extraer el carnet del código QR usando una expresión regular
    carnet_match = re.search(r'Carnet:\s*(\d+)', codigo_qr)
    if carnet_match:
        codigo_qr = carnet_match.group(1)

    # Buscar al estudiante en el diccionario de estudiantes
    estudiante = estudiantes.get(codigo_qr, None)
    
    if estudiante:
        # Registrar la asistencia del estudiante
        registrar_asistencia(
            carnet=codigo_qr,
            nombre=estudiante['nombre'],
            apellido=estudiante['apellido'],
            carrera=estudiante['carrera']
        )

        # Construir la respuesta con la información del estudiante
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
        # Si no se encuentra el estudiante, devolver un error
        return jsonify({'error': 'Estudiante no encontrado'})

# Ruta para servir las imágenes de los estudiantes
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Ruta para servir los audios de los estudiantes
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
