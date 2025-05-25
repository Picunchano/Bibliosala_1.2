# analysis.py
import collections
from datetime import datetime
try:
    from .data_manager import cargar_reservas, inicializar_datos_ejemplo
except ImportError:
    from data_manager import cargar_reservas, inicializar_datos_ejemplo

def _filtrar_reservas_por_fecha(reservas: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    """
    Filtra una lista de reservas por año, mes y/o día específico basado en 'FechaSolicitud'.
    Formato esperado de FechaSolicitud: 'DD/MM/AAAA'.
    Si un componente de fecha (año, mes, día) es None, no se filtra por ese componente.
    """
    if anio is None and mes is None and dia is None:
        return list(reservas)

    reservas_filtradas = []
    for reserva in reservas:
        fecha_solicitud_str = reserva.get('FechaSolicitud')
        if not fecha_solicitud_str:
            continue
        
        try:
            fecha_obj = datetime.strptime(fecha_solicitud_str, "%d/%m/%Y")
            
            if anio is not None and fecha_obj.year != anio:
                continue
            
            if mes is not None and fecha_obj.month != mes:
                continue
                
            if dia is not None and fecha_obj.day != dia:
                continue
                
            reservas_filtradas.append(reserva)
            
        except ValueError:
            print(f"Advertencia: Formato de fecha inválido '{fecha_solicitud_str}' en reserva {reserva.get('TimestampReserva', '')}, se omitirá del filtro.")
            continue
    return reservas_filtradas

def alumno_mas_solicitudes(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    """
    Calcula el alumno (NombreAlumno) con más solicitudes de reserva.
    Filtra por año, mes y/o día si se proporcionan.
    """
    if not reservas_originales:
        return None, 0

    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)

    if not reservas_a_procesar:
        return None, 0

    contador_alumnos = collections.Counter()
    for reserva in reservas_a_procesar:
        nombre_alumno = reserva.get('NombreAlumno')
        if nombre_alumno:
            contador_alumnos[nombre_alumno] += 1
    
    if not contador_alumnos:
        return None, 0
        
    alumno_top = contador_alumnos.most_common(1)
    return alumno_top[0]

def sala_mas_ocupada(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    """
    Calcula la sala (IDSala) más ocupada (reservada más veces).
    Filtra por año, mes y/o día si se proporcionan.
    """
    if not reservas_originales:
        return None, 0
        
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)

    if not reservas_a_procesar:
        return None, 0

    contador_salas = collections.Counter()
    for reserva in reservas_a_procesar:
        id_sala = reserva.get('IDSala')
        if id_sala:
            contador_salas[id_sala] += 1
            
    if not contador_salas:
        return None, 0

    sala_top = contador_salas.most_common(1)
    return sala_top[0]

def total_salas_solicitadas(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> int:
    """
    Calcula el número total de solicitudes de salas para un período específico.
    Filtra por año, mes y/o día si se proporcionan.
    """
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    return len(reservas_a_procesar)


# --- Bloque de prueba ---
if __name__ == "__main__":
    print("Ejecutando pruebas para analysis.py...")
    
    inicializar_datos_ejemplo()
    lista_reservas_prueba = cargar_reservas()

    if not lista_reservas_prueba:
        print("No hay reservas para probar. Creando datos de prueba en memoria (esto no debería pasar si inicializar_datos_ejemplo funciona)...")
        lista_reservas_prueba = [
            {'TimestampReserva': '2024-01-15 10:00:00.000000', 'RUTAlumno': 'RUT001', 'NombreAlumno': 'Ana López', 'IDSala': 'Sala A01', 'FechaSolicitud': '15/01/2024', 'HoraInicio': '10:00', 'HoraFin': '11:00'},
            {'TimestampReserva': '2025-05-23 11:00:00.000000', 'RUTAlumno': 'RUT002', 'NombreAlumno': 'Luis Paz', 'IDSala': 'Sala A02', 'FechaSolicitud': '23/05/2025', 'HoraInicio': '11:00', 'HoraFin': '12:00'},
            {'TimestampReserva': '2025-05-23 10:30:00.000000', 'RUTAlumno': 'RUT001', 'NombreAlumno': 'Ana López', 'IDSala': 'Sala A01', 'FechaSolicitud': '23/05/2025', 'HoraInicio': '10:30', 'HoraFin': '11:30'},
            {'TimestampReserva': '2025-05-24 09:00:00.000000', 'RUTAlumno': 'RUT003', 'NombreAlumno': 'Pedro Giménez', 'IDSala': 'Sala B03', 'FechaSolicitud': '24/05/2025', 'HoraInicio': '09:00', 'HoraFin': '10:00'},
            {'TimestampReserva': '2025-05-24 14:00:00.000000', 'RUTAlumno': 'RUT004', 'NombreAlumno': 'María Sol', 'IDSala': 'Sala A02', 'FechaSolicitud': '24/05/2025', 'HoraInicio': '14:00', 'HoraFin': '15:00'},
        ]
    else:
        print(f"Pruebas realizadas con {len(lista_reservas_prueba)} reservas cargadas de reservas.csv.")

    print("\n--- Alumno más solicitudes (todos los datos) ---")
    nombre_alumno, cantidad = alumno_mas_solicitudes(lista_reservas_prueba)
    print(f"Resultado: {nombre_alumno}, Solicitudes: {cantidad}")

    print("\n--- Alumno más solicitudes (Año: 2025) ---")
    nombre_alumno_2025, cantidad_2025 = alumno_mas_solicitudes(lista_reservas_prueba, anio=2025)
    print(f"Resultado (2025): {nombre_alumno_2025}, Solicitudes: {cantidad_2025}")

    print("\n--- Alumno más solicitudes (Fecha: 23/05/2025) ---")
    nombre_alumno_fecha, cantidad_fecha = alumno_mas_solicitudes(lista_reservas_prueba, anio=2025, mes=5, dia=23)
    print(f"Resultado (23/05/2025): {nombre_alumno_fecha}, Solicitudes: {cantidad_fecha}")
    
    print("\n--- Sala más ocupada (Mes: 05, Año: 2025) ---")
    id_sala_mes_anio, cantidad_sala_mes_anio = sala_mas_ocupada(lista_reservas_prueba, anio=2025, mes=5)
    print(f"Resultado (05/2025): {id_sala_mes_anio}, Ocupaciones: {cantidad_sala_mes_anio}")

    # --- Nuevo análisis: Total de salas solicitadas ---
    print("\n--- Total de salas solicitadas (todos los datos) ---")
    total_general = total_salas_solicitadas(lista_reservas_prueba)
    print(f"Total de salas solicitadas (todas las fechas): {total_general}")

    print("\n--- Total de salas solicitadas (Año: 2025) ---")
    total_2025 = total_salas_solicitadas(lista_reservas_prueba, anio=2025)
    print(f"Total de salas solicitadas (año 2025): {total_2025}")

    print("\n--- Total de salas solicitadas (Fecha: 23/05/2025) ---")
    total_23_05_2025 = total_salas_solicitadas(lista_reservas_prueba, anio=2025, mes=5, dia=23)
    print(f"Total de salas solicitadas (23/05/2025): {total_23_05_2025}")

    print("\n--- Total de salas solicitadas (Fecha: 24/05/2025) ---")
    total_24_05_2025 = total_salas_solicitadas(lista_reservas_prueba, anio=2025, mes=5, dia=24)
    print(f"Total de salas solicitadas (24/05/2025): {total_24_05_2025}")