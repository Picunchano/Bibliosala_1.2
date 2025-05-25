# analysis.py
import collections
from datetime import datetime, time
try:
    from .data_manager import cargar_reservas, inicializar_datos_ejemplo
except ImportError:
    from data_manager import cargar_reservas, inicializar_datos_ejemplo

def _filtrar_reservas_por_fecha(reservas: list, anio: int = None, mes: int = None, dia: int = None) -> list:
    # ... (esta función permanece igual que en la respuesta anterior)
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

def alumno_mas_solicitudes(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None, top_n: int = 10):
    """
    Calcula los 'top_n' alumnos (NombreAlumno) con más solicitudes de reserva.

    Args:
        reservas_originales (list): Lista de todas las reservas (diccionarios).
        anio (int, optional): Año para filtrar las reservas.
        mes (int, optional): Mes para filtrar las reservas.
        dia (int, optional): Día para filtrar las reservas.
        top_n (int, optional): Número de alumnos top a devolver. Defaults to 10.

    Returns:
        list: Lista de tuplas [(nombre_alumno, cantidad_solicitudes), ...],
              o una lista vacía si no hay datos.
    """
    if not reservas_originales:
        return []

    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)

    if not reservas_a_procesar:
        return []

    contador_alumnos = collections.Counter()
    for reserva in reservas_a_procesar:
        nombre_alumno = reserva.get('NombreAlumno')
        if nombre_alumno: # Asegurarse de que el nombre del alumno no sea None o vacío
            contador_alumnos[nombre_alumno] += 1
    
    if not contador_alumnos:
        return []
        
    # Devuelve los top_n alumnos más comunes
    return contador_alumnos.most_common(top_n)

# ... (sala_mas_ocupada, total_salas_solicitadas, horarios_mas_activos permanecen iguales)
def sala_mas_ocupada(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    if not reservas_originales:
        return None, 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return None, 0
    contador_salas = collections.Counter(r.get('IDSala') for r in reservas_a_procesar if r.get('IDSala'))
    if not contador_salas:
        return None, 0
    return contador_salas.most_common(1)[0]

def total_salas_solicitadas(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> int:
    if not reservas_originales:
        return 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    return len(reservas_a_procesar)

def horarios_mas_activos(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    if not reservas_originales:
        return None, None, 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return None, None, 0
    actividad_por_hora = [0] * 24
    for reserva in reservas_a_procesar:
        try:
            hora_inicio_str, hora_fin_str = reserva.get('HoraInicio'), reserva.get('HoraFin')
            if not hora_inicio_str or not hora_fin_str: continue
            h_inicio, m_inicio = map(int, hora_inicio_str.split(':'))
            h_fin, m_fin = map(int, hora_fin_str.split(':'))
            current_h = h_inicio
            while current_h <= h_fin:
                if current_h == h_fin and m_fin == 0: break 
                if current_h == h_inicio and current_h == h_fin:
                    if m_fin > m_inicio: actividad_por_hora[current_h] += 1
                elif current_h == h_inicio: actividad_por_hora[current_h] += 1
                elif current_h == h_fin: actividad_por_hora[current_h] += 1
                elif h_inicio < current_h < h_fin: actividad_por_hora[current_h] += 1
                if current_h == h_fin : break
                current_h +=1
                if current_h > 23: break
        except (ValueError, IndexError) as e:
            print(f"Error parseando HoraInicio/HoraFin para reserva: {reserva}, error: {e}")
            continue
    if not any(actividad_por_hora): return None, None, 0
    max_actividad = max(actividad_por_hora)
    if max_actividad == 0: return None, None, 0
    horas_pico = [i for i, count in enumerate(actividad_por_hora) if count == max_actividad]
    if not horas_pico: return None, None, 0
    h_start_range, h_end_range = horas_pico[0], horas_pico[0]
    for i in range(1, len(horas_pico)):
        if horas_pico[i] == h_end_range + 1: h_end_range = horas_pico[i]
        else: break 
    return h_start_range, h_end_range, max_actividad

# --- Bloque de prueba ---
if __name__ == "__main__":
    print("Ejecutando pruebas para analysis.py...")
    inicializar_datos_ejemplo()
    lista_reservas_prueba = cargar_reservas()

    if not lista_reservas_prueba:
        print("Usando datos de prueba en memoria (CSV vacío o no encontrado).")

    print(f"\n--- Top {10} Alumnos más activos (Año: 2025) ---")
    top_alumnos_2025 = alumno_mas_solicitudes(lista_reservas_prueba, anio=2025, top_n=10)
    if top_alumnos_2025:
        for i, (nombre, cantidad) in enumerate(top_alumnos_2025):
            print(f"{i+1}. Alumno: {nombre}, Solicitudes: {cantidad}")
    else:
        print("No hay datos de alumnos para 2025.")

def sala_mas_ocupada(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    if not reservas_originales:
        return None, 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return None, 0
    contador_salas = collections.Counter(r.get('IDSala') for r in reservas_a_procesar if r.get('IDSala'))
    if not contador_salas:
        return None, 0
    return contador_salas.most_common(1)[0]

def total_salas_solicitadas(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None) -> int:
    """
    Calcula el número total de solicitudes de salas (reservas) según el filtro de fecha.
    """
    if not reservas_originales:
        return 0
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    return len(reservas_a_procesar)

def horarios_mas_activos(reservas_originales: list, anio: int = None, mes: int = None, dia: int = None):
    """
    Calcula el rango de horas con la mayor cantidad de reservas activas simultáneamente.
    Devuelve una tupla (hora_inicio_rango, hora_fin_rango, cantidad_max_actividad)
    o (None, None, 0) si no hay datos o actividad.
    La hora_fin_rango es la última hora del rango (ej. si el rango es 9-10, h_fin es 10).
    """
    if not reservas_originales:
        return None, None, 0
        
    reservas_a_procesar = _filtrar_reservas_por_fecha(reservas_originales, anio, mes, dia)
    if not reservas_a_procesar:
        return None, None, 0

    actividad_por_hora = [0] * 24 # De 00:00 a 23:00

    for reserva in reservas_a_procesar:
        try:
            hora_inicio_str = reserva.get('HoraInicio')
            hora_fin_str = reserva.get('HoraFin')

            if not hora_inicio_str or not hora_fin_str:
                continue

            h_inicio = int(hora_inicio_str.split(':')[0])
            m_inicio = int(hora_inicio_str.split(':')[1])
            h_fin = int(hora_fin_str.split(':')[0])
            m_fin = int(hora_fin_str.split(':')[1])

            # Normalizar a objetos time para comparación y manejo de rangos horarios
            # Iterar por las horas que la reserva cubre
            # Una reserva de 10:00 a 11:00 ocupa la hora 10.
            # Una reserva de 10:30 a 11:30 ocupa la hora 10 y la hora 11.
            
            current_h = h_inicio
            while current_h <= h_fin:
                if current_h == h_fin and m_fin == 0: # Si termina en HH:00, no cuenta para la hora HH
                    break 
                if current_h == h_inicio and current_h == h_fin: # Reserva dentro de la misma hora
                    if m_fin > m_inicio:
                         actividad_por_hora[current_h] += 1
                elif current_h == h_inicio: # Primera hora
                    actividad_por_hora[current_h] += 1
                elif current_h == h_fin: # Última hora (y m_fin > 0 ya chequeado arriba)
                    actividad_por_hora[current_h] += 1
                elif h_inicio < current_h < h_fin: # Horas intermedias
                    actividad_por_hora[current_h] += 1
                
                if current_h == h_fin : # Ya procesamos la hora de fin (si m_fin > 0)
                    break
                current_h +=1
                if current_h > 23: # Control por si acaso, aunque no debería pasar con datos válidos
                    break


        except (ValueError, IndexError) as e:
            print(f"Error parseando HoraInicio/HoraFin para reserva: {reserva}, error: {e}")
            continue
    
    if not any(actividad_por_hora): # Si todas las horas tienen 0 actividad
        return None, None, 0

    max_actividad = max(actividad_por_hora)
    if max_actividad == 0:
        return None, None, 0

    horas_pico = [i for i, count in enumerate(actividad_por_hora) if count == max_actividad]

    if not horas_pico:
        return None, None, 0

    # Encontrar el primer rango contiguo de horas pico
    h_start_range = horas_pico[0]
    h_end_range = h_start_range
    for i in range(1, len(horas_pico)):
        if horas_pico[i] == h_end_range + 1:
            h_end_range = horas_pico[i]
        else:
            # Consideramos solo el primer rango contiguo para simplificar el mensaje "desde X a Y"
            break 
            
    return h_start_range, h_end_range, max_actividad


# --- Bloque de prueba ---
if __name__ == "__main__":
    print("Ejecutando pruebas para analysis.py...")
    inicializar_datos_ejemplo()
    lista_reservas_prueba = cargar_reservas()

    if not lista_reservas_prueba:
         # Fallback data si CSV loading fails or is empty after init
        lista_reservas_prueba = [
            {'TimestampReserva': '2024-01-15 10:00:00.000000', 'RUTAlumno': 'RUT001', 'NombreAlumno': 'Ana López', 'IDSala': 'Sala A01', 'FechaSolicitud': '15/01/2024', 'HoraInicio': '10:00', 'HoraFin': '11:00'},
            {'TimestampReserva': '2025-05-23 11:00:00.000000', 'RUTAlumno': 'RUT002', 'NombreAlumno': 'Luis Paz', 'IDSala': 'Sala A02', 'FechaSolicitud': '23/05/2025', 'HoraInicio': '10:30', 'HoraFin': '11:30'}, # Activa en 10 y 11
            {'TimestampReserva': '2025-05-23 10:30:00.000000', 'RUTAlumno': 'RUT001', 'NombreAlumno': 'Ana López', 'IDSala': 'Sala A01', 'FechaSolicitud': '23/05/2025', 'HoraInicio': '10:00', 'HoraFin': '12:00'}, # Activa en 10 y 11
            {'TimestampReserva': '2025-05-23 12:00:00.000000', 'RUTAlumno': 'RUT003', 'NombreAlumno': 'Pedro Mas', 'IDSala': 'Sala A03', 'FechaSolicitud': '23/05/2025', 'HoraInicio': '11:00', 'HoraFin': '11:50'}, # Activa en 11
        ]
        print("Usando datos de prueba en memoria.")
    else:
        print(f"Pruebas realizadas con {len(lista_reservas_prueba)} reservas cargadas de reservas.csv.")

    print(f"\n--- Total de Salas Solicitadas (Todos los datos) ---")
    total = total_salas_solicitadas(lista_reservas_prueba)
    print(f"Total: {total}")

    print(f"\n--- Total de Salas Solicitadas (Año: 2025) ---")
    total_2025 = total_salas_solicitadas(lista_reservas_prueba, anio=2025)
    print(f"Total (2025): {total_2025}")
    
    print(f"\n--- Horarios más activos (Fecha: 23/05/2025) ---")
    h_inicio, h_fin, actividad = horarios_mas_activos(lista_reservas_prueba, anio=2025, mes=5, dia=23)
    if h_inicio is not None:
        # La hora fin del rango devuelta es inclusiva. Para el mensaje "hasta las Y", Y es h_fin + 1
        print(f"Rango más activo: Desde las {h_inicio:02d}:00 hasta las {h_fin + 1:02d}:00 (hora {h_fin} inclusive), con {actividad} reservas activas.")
    else:
        print("No se encontró actividad o datos para el criterio.")

    print(f"\n--- Horarios más activos (Todos los datos) ---")
    h_inicio_todos, h_fin_todos, actividad_todos = horarios_mas_activos(lista_reservas_prueba)
    if h_inicio_todos is not None:
        print(f"Rango más activo: Desde las {h_inicio_todos:02d}:00 hasta las {h_fin_todos + 1:02d}:00 (hora {h_fin_todos} inclusive), con {actividad_todos} reservas activas.")
    else:
        print("No se encontró actividad o datos para el criterio.")