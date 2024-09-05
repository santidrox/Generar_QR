from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import re

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

estudiantes = cargar_estudiantes()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    codigo_qr = request.json['codigo_qr'].strip()
    
   
    carnet_match = re.search(r'Carnet:\s*(\d+)', codigo_qr)
    if carnet_match:
        codigo_qr = carnet_match.group(1)

    estudiante = estudiantes.get(codigo_qr, None)
    
    if estudiante:
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

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
