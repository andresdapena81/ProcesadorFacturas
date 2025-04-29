import pyodbc

def obtener_conexion():
    conexion = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"  # o puedes poner "." o "localhost\\SQLEXPRESS" si es Express
        "DATABASE=AUTOMATIZACION;"
        "Trusted_Connection=yes;"
    )
    return conexion