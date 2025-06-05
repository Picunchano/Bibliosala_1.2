# analysis.py
import collections
from datetime import datetime, time

# Importar funciones de data_manager (ajustar la ruta si es necesario)
try:
    from .data_manager import cargar_reservas, inicializar_datos_ejemplo
except ImportError:
    from data_manager import cargar_reservas, inicializar_datos_ejemplo

def _filtrar_reservas_por_fecha(reservas: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    """
    Filtra una lista de reservas por año, mes y/o día específico basado en 'FechaSolicitud'.
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
            match = True
            if anio is not None and fecha_obj.year != anio:
                match = False
            if mes is not None and fecha_obj.month != mes:
                match = False
            if dia is not None and fecha_obj.day != dia:
                match = False
            
            if match:
                reservas_filtradas.append(reserva)
        except ValueError:
            print(f"Advertencia: Formato de fecha inválido '{fecha_solicitud_str}' en reserva, se omitirá.")
            continue
    return reservas_filtradas

def alumno_mas_solicitudes(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    """
    Calcula todos los alumnos (NombreAlumno) y sus cantidades de solicitudes de reserva,
    ordenados de más a menos solicitudes.
    Devuelve una lista de tuplas [(nombre_alumno, cantidad_solicitudes), ...].
    """
    if not reservas_originales:
        return []
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return []

    contador_alumnos = collections.Counter()
    for reserva in reservas_a_procesar:
        nombre_alumno = reserva.get('NombreAlumno')
        if nombre_alumno:
            contador_alumnos[nombre_alumno] += 1
    
    return contador_alumnos.most_common() # Devuelve todos, ordenados

def sala_mas_ocupada(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    """
    Calcula todas las salas (IDSala) y la cantidad de veces que fueron reservadas,
    ordenadas de más a menos ocupaciones.
    Devuelve una lista de tuplas [(id_sala, cantidad_ocupaciones), ...].
    """
    if not reservas_originales:
        return []
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return []
    contador_salas = collections.Counter(r.get('IDSala') for r in reservas_a_procesar if r.get('IDSala'))
    return contador_salas.most_common() # Devuelve todas, ordenadas

def conteo_reservas_filtradas(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> int:
    """
    Calcula el número total de solicitudes de salas (reservas) según el filtro de fecha.
    Esta función reemplaza la funcionalidad anterior de 'total_salas_solicitadas' que
    solo devolvía un conteo.
    """
    if not reservas_originales:
        return 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    return len(reservas_a_procesar)


def horarios_mas_activos(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    """
    Calcula la actividad para cada hora del día (cantidad de reservas activas).
    Devuelve una lista de tuplas [(hora_str, actividad), ...],
    ordenada por actividad (descendente) y luego por hora (ascendente).
    Ej: [("10:00-11:00", 5), ("11:00-12:00", 5), ("09:00-10:00", 3), ...]
    """
    if not reservas_originales:
        return []
        
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return []

    actividad_por_hora = [0] * 24 # De 00:00 a 23:00

    for reserva in reservas_a_procesar:
        try:
            hora_inicio_str, hora_fin_str = reserva.get('HoraInicio'), reserva.get('HoraFin')
            if not hora_inicio_str or not hora_fin_str: continue

            h_inicio = int(hora_inicio_str.split(':')[0])
            m_inicio = int(hora_inicio_str.split(':')[1]) # No usado en esta lógica simplificada pero parseado
            h_fin = int(hora_fin_str.split(':')[0])
            m_fin = int(hora_fin_str.split(':')[1])

            current_h = h_inicio
            while current_h <= h_fin:
                if current_h > 23: break # Evitar índice fuera de rango
                if current_h == h_fin and m_fin == 0: # Si termina en HH:00 exacto, no cuenta para la hora HH
                    break 
                
                # Si la reserva es 10:00-11:00, cuenta para la hora 10.
                # Si la reserva es 10:30-11:30, cuenta para la hora 10 y la hora 11.
                actividad_por_hora[current_h] += 1
                
                if current_h == h_fin: # Ya procesamos la hora de fin (si m_fin > 0)
                    break
                current_h +=1
        except (ValueError, IndexError) as e:
            print(f"Error parseando HoraInicio/HoraFin para reserva: {reserva}, error: {e}")
            continue
    
    resultado_horarios = []
    for hora, actividad_count in enumerate(actividad_por_hora):
        if actividad_count > 0: # Solo mostrar horas con alguna actividad
            hora_siguiente = (hora + 1) % 24
            # Formato HH:00 - HH+1:00 (ej. 10:00-11:00)
            hora_str = f"{hora:02d}:00 - {hora_siguiente:02d}:00"
            if hora == 23 : # Caso especial para la última hora del día
                hora_str = f"23:00 - 00:00"

            resultado_horarios.append((hora_str, actividad_count, hora)) # Añadir hora original para ordenar

    # Ordenar por actividad (desc) y luego por la hora de inicio (asc)
    resultado_horarios.sort(key=lambda x: (-x[1], x[2]))
    
    # Devolver solo el string de hora y la actividad para la UI
    return [(h_str, act) for h_str, act, _ in resultado_horarios]


# --- Bloque de prueba ---
if __name__ == "__main__":
    print("Ejecutando pruebas para analysis.py...")
    inicializar_datos_ejemplo() # Asegurar que existan datos de ejemplo
    lista_reservas_prueba = cargar_reservas()

    print(f"\n--- Todos los Alumnos Activos (Año: 2025) ---")
    todos_alumnos_2025 = alumno_mas_solicitudes(lista_reservas_prueba, anio=2025)
    if todos_alumnos_2025:
        for i, (nombre, cantidad) in enumerate(todos_alumnos_2025):
            print(f"{i+1}. Alumno: {nombre}, Solicitudes: {cantidad}")
    else:
        print("No hay datos de alumnos para 2025.")

    print(f"\n--- Todas las Salas Ocupadas (Todos los datos) ---")
    todas_salas = sala_mas_ocupada(lista_reservas_prueba)
    if todas_salas:
        for i, (sala, cantidad) in enumerate(todas_salas):
            print(f"{i+1}. Sala: {sala}, Ocupaciones: {cantidad}")
    else:
        print("No hay datos de salas.")
    
    print(f"\n--- Conteo Total de Reservas Filtradas (Año: 2025) ---")
    conteo_2025 = conteo_reservas_filtradas(lista_reservas_prueba, anio=2025)
    print(f"Total de reservas en 2025: {conteo_2025}")

    print(f"\n--- Horarios de Actividad (Fecha: 23/05/2025 de ejemplos) ---")
    # Usar una fecha donde los datos de ejemplo tengan actividad
    actividad_horaria = horarios_mas_activos(lista_reservas_prueba, anio=2025, mes=5, dia=22) # Los ejemplos están en 22/05/2025
    if actividad_horaria:
        for hora_rango, actividad_count in actividad_horaria:
            print(f"Horario: {hora_rango}, Actividad: {actividad_count} reservas")
    else:
        print("No se encontró actividad o datos para el criterio.")