import os
import re
from PyPDF2 import PdfReader
from database.conexion import obtener_conexion
from models.factura_model import Factura

def extraer_datos_factura(path_pdf):
    reader = PdfReader(path_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()

    print(f"Texto extraído de {path_pdf}:\n{texto}\n{'-'*50}")

    numero_factura = re.search(r'Factura\s+#?([\w\-]+)', texto)
    fecha = re.search(r'Fecha de emisión:\s*(\d{4}-\d{2}-\d{2})', texto)
    descripcion = re.search(r'Descripción\s+Importe\s+(.*?)\s+Subtotal', texto, re.DOTALL)
    valor = re.search(r'Total\s+([\d,.]+)\$', texto)

    if numero_factura and fecha and descripcion and valor:
        return Factura(
            numero_factura.group(1).strip(),
            fecha.group(1).strip(),
            descripcion.group(1).strip(),
            float(valor.group(1).replace(',', '').strip())
        )
    else:
        print(f"Datos no encontrados en {path_pdf}")
        return None


def insertar_factura(factura):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO Facturas (NumeroFactura, FechaEmision, Descripcion, Valor)
        VALUES (?, ?, ?, ?)
    ''', (factura.numero_factura, factura.fecha_emision, factura.descripcion, factura.valor))
    conexion.commit()
    cursor.close()
    conexion.close()

def procesar_facturas(ruta_carpeta):
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith('.pdf') and 'factura' in archivo.lower():
            ruta_pdf = os.path.join(ruta_carpeta, archivo)
            factura = extraer_datos_factura(ruta_pdf)
            if factura:
                insertar_factura(factura)
                print(f"Factura {factura.numero_factura} procesada correctamente.")
            else:
                print(f"Datos incompletos en {archivo}, no se insertó.")
