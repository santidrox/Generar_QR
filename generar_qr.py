import qrcode
import pandas as pd
import os


csv_file = 'BASE.csv'
if not os.path.exists(csv_file):
    print(f"El archivo {csv_file} no se encontró. Asegúrate de que esté en el mismo directorio que este script.")
    exit()


try:
    data = pd.read_csv(csv_file)
except Exception as e:
    print(f"Hubo un problema al leer el archivo {csv_file}: {e}")
    exit()


output_dir = 'img'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


for i in range(len(data)):
    try:
        cod_proveedor = str(data.iloc[i, 0])
        nombre_proveedor = str(data.iloc[i, 1])

      
        img = qrcode.make(cod_proveedor)
        
        
        img.save(os.path.join(output_dir, f"{nombre_proveedor}.png"))
        print(f"Código QR generado para {nombre_proveedor} con código {cod_proveedor}")
    except Exception as e:
        print(f"Hubo un problema al generar el código QR para la fila {i}: {e}")
