# app_main.py
import tkinter as tk
from tkinter import ttk, messagebox # Asegúrate de importar messagebox
import datetime # Necesario para la nueva funcionalidad

# Importar las clases de las ventanas y funciones de data_manager
from ui_nueva_reserva import NuevaReservaWindow
from ui_ver_reservas import VerReservasWindow
from ui_analisis_datos import AnalisisWindow
from data_manager import inicializar_datos_ejemplo, cargar_reservas # Importar cargar_reservas

class App:
    def __init__(self, root_window):
        self.root = root_window
        inicializar_datos_ejemplo() # Inicializar datos al arrancar

        self.root.title("Sistema de Reserva de Salas")
        self.root.geometry("400x300")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(main_frame, text="Gestión de Salas de Estudio", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        btn_nueva_reserva = ttk.Button(main_frame, text="Realizar Nueva Reserva", command=self.abrir_ventana_nueva_reserva)
        btn_nueva_reserva.pack(pady=8, fill=tk.X)

        btn_historial_reservas = ttk.Button(main_frame, text="Historial de Reservas", command=self.abrir_ventana_historial_reservas)
        btn_historial_reservas.pack(pady=8, fill=tk.X)

        btn_activas_reservas = ttk.Button(main_frame, text="Reservas Activas", command=self.abrir_ventana_reservas_activas)
        btn_activas_reservas.pack(pady=8, fill=tk.X)

        btn_analizar_datos = ttk.Button(main_frame, text="Analizar Datos", command=self.abrir_ventana_analisis)
        btn_analizar_datos.pack(pady=8, fill=tk.X)

        # Control para ventanas Toplevel
        self.ventana_reserva_actual = None
        self.ventana_ver_reservas_actual = None
        self.ventana_analisis_actual = None

        # --- INICIO: Funcionalidad de notificación de reservas finalizadas ---
        self.reservas_finalizadas_notificadas_sesion = set()
        self.ultima_verificacion_notificaciones = datetime.datetime.now()
        self.intervalo_verificacion_ms = 60000  # 60000 ms = 1 minuto
        self.root.after(self.intervalo_verificacion_ms, self._verificar_reservas_finalizadas_periodicamente)
        # --- FIN: Funcionalidad de notificación ---


    def _verificar_reservas_finalizadas_periodicamente(self):
        """
        Verifica periódicamente si alguna reserva activa ha finalizado y notifica al usuario.
        """
        # print(f"Verificando finalización de reservas a las {datetime.datetime.now()}") # Para depuración
        
        ahora = datetime.datetime.now()
        # El intervalo de chequeo es desde la última vez que verificamos hasta ahora.
        tiempo_inicio_intervalo = self.ultima_verificacion_notificaciones
        
        try:
            todas_las_reservas = cargar_reservas()
        except Exception as e:
            print(f"Error al cargar reservas para verificación periódica: {e}")
            # Reintentar después
            self.root.after(self.intervalo_verificacion_ms, self._verificar_reservas_finalizadas_periodicamente)
            return

        notificaciones_pendientes_msg = []

        for reserva in todas_las_reservas:
            timestamp = reserva.get('TimestampReserva')
            if not timestamp or timestamp in self.reservas_finalizadas_notificadas_sesion:
                continue

            fecha_str = reserva.get('FechaSolicitud')
            hora_inicio_str = reserva.get('HoraInicio')
            hora_fin_str = reserva.get('HoraFin')

            if not (fecha_str and hora_inicio_str and hora_fin_str):
                continue

            try:
                fecha_obj = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                dt_inicio = datetime.datetime.combine(fecha_obj, datetime.datetime.strptime(hora_inicio_str, "%H:%M").time())
                dt_fin = datetime.datetime.combine(fecha_obj, datetime.datetime.strptime(hora_fin_str, "%H:%M").time())

                # Condición: La reserva finalizó DESPUÉS de la última verificación Y ANTES O IGUAL que ahora.
                # Y la reserva ya había comenzado o estaba por comenzar antes de su finalización.
                if dt_fin > tiempo_inicio_intervalo and dt_fin <= ahora:
                    if dt_inicio <= dt_fin: # Asegurar que la reserva era válida (inicio antes o igual a fin)
                        msg = (f"- La reserva para '{reserva.get('NombreAlumno', 'N/A')}' "
                               f"en '{reserva.get('IDSala', 'N/A')}' "
                               f"({hora_inicio_str} - {hora_fin_str}) ha finalizado.")
                        notificaciones_pendientes_msg.append(msg)
                        self.reservas_finalizadas_notificadas_sesion.add(timestamp)
            
            except ValueError as ve:
                # print(f"Error de formato de fecha/hora al verificar reserva {timestamp}: {ve}")
                continue # Saltar esta reserva si hay error de parseo
            except Exception as ex:
                # print(f"Error inesperado al procesar reserva {timestamp} para notificación: {ex}")
                continue


        if notificaciones_pendientes_msg:
            mensaje_completo = "Las siguientes reservas han finalizado:\n\n" + "\n".join(notificaciones_pendientes_msg)
            if self.root.winfo_exists(): # Solo mostrar si la ventana principal existe
                messagebox.showinfo("Reservas Completadas", mensaje_completo, parent=self.root)

            # Si la ventana de "Reservas Activas" está abierta, actualizarla
            if self.ventana_ver_reservas_actual and \
               self.ventana_ver_reservas_actual.winfo_exists() and \
               hasattr(self.ventana_ver_reservas_actual, 'filtrar_activas_flag') and \
               self.ventana_ver_reservas_actual.filtrar_activas_flag:
                try:
                    self.ventana_ver_reservas_actual.poblar_treeview_reservas()
                except Exception as e_poblar:
                    print(f"Error al intentar actualizar la vista de reservas activas: {e_poblar}")


        self.ultima_verificacion_notificaciones = ahora
        # Volver a programar la verificación
        if self.root.winfo_exists(): # Solo reprogramar si la app sigue corriendo
            self.root.after(self.intervalo_verificacion_ms, self._verificar_reservas_finalizadas_periodicamente)


    def abrir_ventana_nueva_reserva(self):
        if self.ventana_reserva_actual and self.ventana_reserva_actual.winfo_exists():
            self.ventana_reserva_actual.lift()
        else:
            self.ventana_reserva_actual = NuevaReservaWindow(self.root)

    def abrir_ventana_historial_reservas(self):
        # Si ya existe una ventana de "Ver Reservas", la cerramos para evitar conflictos
        # o comportamientos inesperados al cambiar entre "Historial" y "Activas".
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
             self.ventana_ver_reservas_actual.destroy()
        
        self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Historial de Reservas", filtrar_activas=False)


    def abrir_ventana_reservas_activas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
             self.ventana_ver_reservas_actual.destroy()
        
        # El título podría ser solo "Reservas Activas"
        self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Reservas Activas", filtrar_activas=True)


    def abrir_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.lift()
        else:
            self.ventana_analisis_actual = AnalisisWindow(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()