import os
import re
import pdfplumber
from database.conexion import obtener_conexion
from models.factura_model import Factura

def extraer_datos_factura_pdfplumber(path_pdf):
    texto = ""
    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()

    numero_factura = re.search(r'Factura\s+#?([\w\-]+)', texto)
    fecha = re.search(r'Fecha de emisión:\s*(\d{4}-\d{2}-\d{2})', texto)
    descripcion = re.search(r'Descripción\s+Importe\s+(.*?)\s+Subtotal', texto, re.DOTALL)
    valor = re.search(r'Total\s+([\d.,]+)\$', texto)

    if numero_factura and fecha and descripcion and valor:
        return Factura(
            numero_factura.group(1).strip(),
            fecha.group(1).strip(),
            descripcion.group(1).strip(),
            float(valor.group(1).replace(',', '').strip())
        )
    else:
        return None

def factura_ya_existe(numero_factura):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('SELECT COUNT(*) FROM Facturas WHERE NumeroFactura = ?', (numero_factura,))
    resultado = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return resultado > 0

def insertar_factura(factura):
    if factura_ya_existe(factura.numero_factura):
        print(f"⏭️  Factura {factura.numero_factura} ya existe. Se omite.")
        return

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO Facturas (NumeroFactura, FechaEmision, Descripcion, Valor)
        VALUES (?, ?, ?, ?)
    ''', (factura.numero_factura, factura.fecha_emision, factura.descripcion, factura.valor))
    conexion.commit()
    cursor.close()
    conexion.close()
    print(f"✅ Factura {factura.numero_factura} insertada.")

def procesar_facturas_en_subcarpetas(ruta_principal):
    for root, dirs, files in os.walk(ruta_principal):
        for archivo in files:
            if archivo.lower().endswith('.pdf') and 'factura' in archivo.lower():
                ruta_pdf = os.path.join(root, archivo)
                factura = extraer_datos_factura_pdfplumber(ruta_pdf)
                if factura:
                    insertar_factura(factura)
                else:
                    print(f"⚠️  Datos incompletos en {archivo}, no se insertó.")
