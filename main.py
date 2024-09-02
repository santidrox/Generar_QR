from flask import Flask, render_template, request, jsonify
import csv
import re

app = Flask(__name__)

# Cargar los datos del CSV en un diccionario
def cargar_estudiantes():
    estudiantes = {}
    with open('Listado Cuarto Bachillerato.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            carnet = str(int(float(row['carnet']))).strip()
            estudiantes[carnet] = {
                'nombre': row['nombre'].strip(),
                'apellido': row['apellido'].strip(),
                'carrera': row['carrera'].strip()
            }
    return estudiantes

estudiantes = cargar_estudiantes()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    codigo_qr = request.json['codigo_qr'].strip()  # Eliminar espacios en blanco
    
    # Buscar el carnet en el texto escaneado usando una expresión regular
    carnet_match = re.search(r'Carnet:\s*(\d+)', codigo_qr)
    if carnet_match:
        codigo_qr = carnet_match.group(1)  # Extraer el número de carnet

    # Buscar en el diccionario de estudiantes
    estudiante = estudiantes.get(codigo_qr, None)
    
    if estudiante:
        return jsonify({
            'nombre': estudiante['nombre'],
            'apellido': estudiante['apellido'],
            'carrera': estudiante['carrera'],
            'carnet': codigo_qr
        })
    else:
        return jsonify({'error': 'Estudiante no encontrado'})

if __name__ == '__main__':
    app.run(debug=True)
