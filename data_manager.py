# data_manager.py
import csv
import os
from datetime import datetime

# Nombre del archivo CSV para almacenar las reservas
CSV_FILE = 'reservas.csv'
# Cabeceras para el archivo CSV
FIELDNAMES = ['TimestampReserva', 'RUTAlumno', 'NombreAlumno', 'IDSala', 'FechaSolicitud', 'HoraInicio', 'HoraFin']

def inicializar_datos_ejemplo():
    """
    Crea el archivo reservas.csv con datos de ejemplo si no existe.
    """
    if not os.path.exists(CSV_FILE):
        print(f"Archivo {CSV_FILE} no encontrado. Creando con datos de ejemplo...")
        
        # Generar timestamps únicos para los ejemplos, basados en la fecha 2025-05-21
        # para mantener coherencia con la solicitud y asegurar unicidad.
        # Usamos una hora base y aumentamos los segundos/microsegundos.
        base_datetime_obj = datetime(2025, 5, 21, 9, 0, 0) # 21 de Mayo de 2025, 09:00:00

        datos_ejemplo = [
            {
                'TimestampReserva': (base_datetime_obj.replace(second=1, microsecond=100000)).strftime('%Y-%m-%d %H:%M:%S.%f'),
                'RUTAlumno': '20123450-7', 
                'NombreAlumno': 'Jose Miguel', 
                'IDSala': 'Sala A01', 
                'FechaSolicitud': '21/05/2025', 
                'HoraInicio': '11:00', 
                'HoraFin': '12:00'
            },
            {
                'TimestampReserva': (base_datetime_obj.replace(second=2, microsecond=200000)).strftime('%Y-%m-%d %H:%M:%S.%f'),
                'RUTAlumno': '20123450-8', 
                'NombreAlumno': 'Olga Maria', 
                'IDSala': 'Sala A02', 
                'FechaSolicitud': '22/05/2025', 
                'HoraInicio': '13:00', 
                'HoraFin': '14:00'
            },
            {
                'TimestampReserva': (base_datetime_obj.replace(second=3, microsecond=300000)).strftime('%Y-%m-%d %H:%M:%S.%f'),
                'RUTAlumno': '20123450-9', 
                'NombreAlumno': 'Juan Perez', 
                'IDSala': 'Sala A01', 
                'FechaSolicitud': '22/05/2025', 
                'HoraInicio': '10:30', 
                'HoraFin': '11:30'
            }
        ]
        
        try:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(datos_ejemplo)
            print(f"Archivo {CSV_FILE} creado exitosamente con {len(datos_ejemplo)} reservas de ejemplo.")
        except Exception as e:
            print(f"Error al crear el archivo de reservas de ejemplo: {e}")


def guardar_reserva(datos_reserva: dict):
    """
    Guarda una nueva reserva en el archivo CSV.
    Crea el archivo y escribe las cabeceras si no existe.
    """
    try:
        # Timestamp con microsegundos para mayor unicidad
        timestamp_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') 
        
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
            # Si el archivo no existía o está vacío (incluso después de crearlo en modo 'a' si es la primera vez)
            if not file_exists or os.path.getsize(CSV_FILE) == 0:
                writer.writeheader()
            writer.writerow(reserva_completa)
        
        return True
    except Exception as e:
        print(f"Error al guardar la reserva: {e}")
        return False

def cargar_reservas() -> list:
    """
    Carga todas las reservas desde el archivo CSV.
    Retorna una lista vacía si el archivo no existe o está vacío (después de las cabeceras).
    """
    # Asegura que los datos de ejemplo se creen si es necesario ANTES de intentar cargar.
    # Esto es redundante si se llama desde app.py al inicio, pero es una salvaguarda.
    # inicializar_datos_ejemplo() # Comentado si se llama desde app.py

    reservas = []
    if not os.path.isfile(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        # Si el archivo aún no existe o está vacío después de la inicialización (si falló o no se llamó)
        return reservas 

    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames: 
                return reservas # Archivo podría estar corrupto o solo tener una línea vacía
            
            for row in reader:
                # Verificar que la fila no esté completamente vacía y tenga un TimestampReserva
                if any(row.values()) and row.get('TimestampReserva'): 
                    reservas.append(row)
        return reservas
    except FileNotFoundError: # Aunque os.path.isfile debería cubrir esto
        return []
    except Exception as e:
        print(f"Error al cargar las reservas: {e}")
        return []

def eliminar_reservas_por_timestamps(timestamps_a_eliminar: list) -> bool:
    """
    Elimina las reservas del archivo CSV que coincidan con los timestamps proporcionados.
    """
    if not timestamps_a_eliminar:
        return True 

    reservas_actuales = cargar_reservas()
    # Si cargar_reservas devuelve lista vacía porque el archivo no existe o está vacío,
    # no hay nada que hacer aquí, o podría ser un error si se esperaban datos.
    if not reservas_actuales and os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0 :
        # Hubo un problema al cargar datos de un archivo que sí existe y no está vacío
        print("Error: No se pudieron cargar las reservas existentes para la eliminación.")
        return False
    
    reservas_a_mantener = [
        reserva for reserva in reservas_actuales 
        if reserva.get('TimestampReserva') not in timestamps_a_eliminar
    ]

    # Si la cantidad de reservas a mantener es la misma que las actuales,
    # y se intentó eliminar algo, significa que los timestamps no se encontraron.
    if len(reservas_a_mantener) == len(reservas_actuales) and timestamps_a_eliminar:
        print(f"Advertencia: Ninguno de los timestamps proporcionados {timestamps_a_eliminar} fue encontrado en las reservas.")
        # Se podría retornar False o True dependiendo de si se considera error o no.
        # Por ahora, si no se borró nada porque no coincidió, la operación de "reescribir" es exitosa.

    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader() # Siempre escribir cabecera al reescribir
            if reservas_a_mantener: # Solo escribir filas si hay algo que mantener
                writer.writerows(reservas_a_mantener)
        return True
    except Exception as e:
        print(f"Error al reescribir el archivo de reservas: {e}")
        return False

# Llamada para asegurar que los datos de ejemplo se creen al ejecutar el módulo directamente (para pruebas)
if __name__ == '__main__':
    print(f"Probando el módulo data_manager.py...")
    print(f"Las reservas se guardarán/cargarán desde: {os.path.abspath(CSV_FILE)}")
    
    # Si el archivo ya existe y quieres probar la creación de ejemplos, bórralo primero.
    # if os.path.exists(CSV_FILE):
    #     os.remove(CSV_FILE)
    #     print(f"Archivo {CSV_FILE} eliminado para probar la creación de ejemplos.")

    inicializar_datos_ejemplo() # Crear datos de ejemplo si es necesario

    print("\nCargando reservas existentes:")
    lista_reservas = cargar_reservas()
    if lista_reservas:
        for idx, reserva in enumerate(lista_reservas):
            print(f"Reserva {idx + 1}: {reserva.get('TimestampReserva')} - {reserva.get('NombreAlumno')}")
    else:
        print("No se encontraron reservas o hubo un error al cargar.")