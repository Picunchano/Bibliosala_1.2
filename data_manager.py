# data_manager.py
import csv
import os
from datetime import datetime

# Nombre del archivo CSV para almacenar las reservas
CSV_FILE = 'reservas.csv'
# Cabeceras para el archivo CSV
FIELDNAMES = ['TimestampReserva', 'RUTAlumno', 'NombreAlumno', 'IDSala', 'FechaSolicitud', 'HoraInicio', 'HoraFin']

def guardar_reserva(datos_reserva: dict):
    """
    Guarda una nueva reserva en el archivo CSV.
    Crea el archivo y escribe las cabeceras si no existe.

    Args:
        datos_reserva (dict): Un diccionario con los datos de la reserva.
                              Debe contener las claves: RUTAlumno, NombreAlumno,
                              IDSala, FechaSolicitud, HoraInicio, HoraFin.
    """
    try:
        # Generar el timestamp actual para la reserva
        timestamp_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        reserva_completa = {
            'TimestampReserva': timestamp_actual,
            'RUTAlumno': datos_reserva.get('RUTAlumno', ''),
            'NombreAlumno': datos_reserva.get('NombreAlumno', ''),
            'IDSala': datos_reserva.get('IDSala', ''),
            'FechaSolicitud': datos_reserva.get('FechaSolicitud', ''),
            'HoraInicio': datos_reserva.get('HoraInicio', ''),
            'HoraFin': datos_reserva.get('HoraFin', '')
        }

        file_exists = os.path.isfile(CSV_FILE)
        
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            if not file_exists or os.path.getsize(CSV_FILE) == 0:
                writer.writeheader()
            writer.writerow(reserva_completa)
        
        print(f"Reserva guardada exitosamente a las {timestamp_actual}")
        return True
    except Exception as e:
        print(f"Error al guardar la reserva: {e}")
        return False

def cargar_reservas() -> list:
    """
    Carga todas las reservas desde el archivo CSV.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa una reserva.
              Retorna una lista vacía si el archivo no existe o está vacío (después de las cabeceras).
    """
    reservas = []
    if not os.path.isfile(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        # No es necesario imprimir aquí si el mensaje se manejará en la UI
        # print(f"El archivo {CSV_FILE} no existe o está vacío.")
        return reservas 

    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames: 
                # print(f"El archivo {CSV_FILE} parece no tener cabeceras válidas.")
                return reservas

            # Opcional: Verificar si todas las FIELDNAMES esperadas están en reader.fieldnames
            # if not all(fieldname in reader.fieldnames for fieldname in FIELDNAMES):
            # print(f"Advertencia: Las cabeceras en {CSV_FILE} no coinciden con las esperadas.")
            
            for row in reader:
                if any(row.values()): 
                    reservas.append(row)
        # print(f"Se cargaron {len(reservas)} reservas.") # Mensaje para depuración
        return reservas
    except FileNotFoundError:
        # print(f"El archivo {CSV_FILE} no fue encontrado.") # Mensaje para depuración
        return []
    except Exception as e:
        print(f"Error al cargar las reservas: {e}") # Mensaje para depuración
        return []

if __name__ == '__main__':
    print(f"Probando el módulo data_manager.py...")
    print(f"Las reservas se guardarán/cargarán desde: {os.path.abspath(CSV_FILE)}")
    
    # # Prueba de guardado (descomentar para crear un archivo de prueba si no existe)
    # reserva_prueba_1 = {
    # 'RUTAlumno': 'ALU001', 'NombreAlumno': 'Juan Perez', 'IDSala': 'Sala A01',
    # 'FechaSolicitud': '22/05/2025', 'HoraInicio': '10:00', 'HoraFin': '11:00'
    # }
    # reserva_prueba_2 = {
    # 'RUTAlumno': 'ALU002', 'NombreAlumno': 'Ana Gomez', 'IDSala': 'Sala B02',
    # 'FechaSolicitud': '23/05/2025', 'HoraInicio': '14:00', 'HoraFin': '15:30'
    # }
    # guardar_reserva(reserva_prueba_1)
    # guardar_reserva(reserva_prueba_2)

    print("\nCargando reservas existentes:")
    lista_reservas = cargar_reservas()
    if lista_reservas:
        for idx, reserva in enumerate(lista_reservas):
            print(f"Reserva {idx + 1}: {reserva}")
    else:
        print("No se encontraron reservas o hubo un error al cargar.")