
from services.factura_service import procesar_facturas
from services.factura_service_plumber import procesar_facturas_en_subcarpetas

if __name__ == "__main__":
    ruta = input("Ingrese la ruta de la carpeta de facturas: ").strip()
    #procesar_facturas(ruta)
    procesar_facturas_en_subcarpetas(ruta)
