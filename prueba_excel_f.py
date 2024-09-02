#El siguiente archivo es una prueba fallida por el momento, de escanear el qr y registrarlo en Excel
import cv2
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import messagebox

# Función para mostrar el mensaje emergente
def show_message(name):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    messagebox.showinfo("Asistencia Registrada", f"Su asistencia ha sido registrada para: {name}")
    root.destroy()

# Inicializar la videocaptura
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

# Variable para controlar la asistencia ya registrada
assistance_registered = False

while True:
    # Leemos los frames
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar el frame.")
        break

    # Leemos los códigos QR
    decoded_objects = decode(frame)
    
    # Verificamos si se ha detectado algún QR
    if decoded_objects:
        for codes in decoded_objects:
            # Extraemos y decodificamos la información
            info = codes.data.decode('utf-8')
            print("Código QR detectado:", info)

            # Suponiendo que la información está separada por comas: "Nombre,Carrera,Código"
            datos = info.split(',')
            if len(datos) == 3:
                nombre = datos[0]
                carrera = datos[1]
                codigo_personal = datos[2]

                # Mostrar mensaje de confirmación en ventana emergente
                if not assistance_registered:
                    show_message(nombre)
                    assistance_registered = True  # Evita mostrar el mensaje más de una vez

                # Dibujar un rectángulo alrededor del QR
                pts = codes.polygon
                if len(pts) > 4:
                    hull = cv2.convexHull(np.array([pt for pt in pts], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else:
                    hull = pts
                n = len(hull)
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 255, 0), 3)

    # Mostramos el frame con las anotaciones
    cv2.imshow("LECTOR DE QR", frame)

    # Leemos el teclado y cerramos si se presiona 'ESC'
    if cv2.waitKey(5) == 27:
        break

# Liberamos la cámara y cerramos las ventanas
cap.release()
cv2.destroyAllWindows()
