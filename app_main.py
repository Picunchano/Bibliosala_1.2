# app_main.py
import tkinter as tk
from tkinter import ttk
from data_manager import inicializar_datos_ejemplo
# Importar las clases de las ventanas
from ui_nueva_reserva import NuevaReservaWindow
from ui_ver_reservas import VerReservasWindow
from ui_analisis_datos import AnalisisWindow

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

        btn_activas_reservas = ttk.Button(main_frame, text="Reservas Activas Hoy", command=self.abrir_ventana_reservas_activas)
        btn_activas_reservas.pack(pady=8, fill=tk.X)

        btn_analizar_datos = ttk.Button(main_frame, text="Analizar Datos", command=self.abrir_ventana_analisis)
        btn_analizar_datos.pack(pady=8, fill=tk.X)

        # Control para ventanas Toplevel (una instancia a la vez)
        self.ventana_reserva_actual = None
        self.ventana_ver_reservas_actual = None
        self.ventana_analisis_actual = None

    def abrir_ventana_nueva_reserva(self):
        if self.ventana_reserva_actual and self.ventana_reserva_actual.winfo_exists():
            self.ventana_reserva_actual.lift()
        else:
            self.ventana_reserva_actual = NuevaReservaWindow(self.root)

    def abrir_ventana_historial_reservas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
            # Podríamos reconfigurar la ventana existente o cerrarla y abrir una nueva
            # Por simplicidad, cerramos y abrimos para asegurar el estado correcto del filtro.
            # O mejor, la clase VerReservasWindow podría tener un método para reconfigurarse.
            # Por ahora, la instancia de VerReservasWindow maneja su propio título y lógica de filtrado en __init__.
            # Si se hace clic repetidamente, el lift() es suficiente si la ventana es la misma.
            # Si el tipo de vista (activas vs historial) cambia, es mejor una nueva o reconfigurar.
            # La lógica actual en ui_ver_reservas crea una nueva Toplevel cada vez si la anterior se cerró.
             self.ventana_ver_reservas_actual.destroy() # Cerrar la anterior si existe
             self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Historial de Reservas", filtrar_activas=False)
        else:
            self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Historial de Reservas", filtrar_activas=False)


    def abrir_ventana_reservas_activas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
             self.ventana_ver_reservas_actual.destroy() # Cerrar la anterior si existe
             self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Reservas Activas Hoy", filtrar_activas=True)
        else:
            self.ventana_ver_reservas_actual = VerReservasWindow(self.root, "Reservas Activas Hoy", filtrar_activas=True)


    def abrir_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.lift()
        else:
            self.ventana_analisis_actual = AnalisisWindow(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()