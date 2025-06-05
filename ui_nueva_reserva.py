# ui_nueva_reserva.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from data_manager import guardar_reserva # Asumiendo que data_manager.py está en el mismo directorio o PYTHONPATH
from constants import SALAS_DISPONIBLES # Importar desde constants.py

class NuevaReservaWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Nueva Reserva")
        self.geometry("400x380")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._crear_widgets()

    def _crear_widgets(self):
        form_frame = ttk.Frame(self, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)

        self.entries = {} # Para almacenar los widgets de entrada

        # RUT Alumno
        ttk.Label(form_frame, text="RUT Alumno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entries['RUTAlumno'] = ttk.Entry(form_frame, width=30)
        self.entries['RUTAlumno'].grid(row=0, column=1, padx=5, pady=5)

        # Nombre y Apellido Alumno
        ttk.Label(form_frame, text="Nombre y Apellido Alumno:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entries['NombreAlumno'] = ttk.Entry(form_frame, width=30)
        self.entries['NombreAlumno'].grid(row=1, column=1, padx=5, pady=5)

        # Sala a Reservar
        ttk.Label(form_frame, text="Sala a Reservar:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entries['IDSala'] = tk.StringVar(form_frame)
        if SALAS_DISPONIBLES:
            self.entries['IDSala'].set(SALAS_DISPONIBLES[0]) 
            sala_option_menu = ttk.OptionMenu(form_frame, self.entries['IDSala'], SALAS_DISPONIBLES[0], *SALAS_DISPONIBLES)
            sala_option_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        else:
            ttk.Label(form_frame, text="No hay salas disponibles.").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Fecha Reserva
        ttk.Label(form_frame, text="Fecha Reserva (DD/MM/AAAA):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entries['FechaSolicitud'] = ttk.Entry(form_frame, width=30)
        self.entries['FechaSolicitud'].grid(row=3, column=1, padx=5, pady=5)

        # Hora Inicio
        ttk.Label(form_frame, text="Hora Inicio (HH:MM):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entries['HoraInicio'] = ttk.Entry(form_frame, width=30)
        self.entries['HoraInicio'].grid(row=4, column=1, padx=5, pady=5)

        # Hora Fin
        ttk.Label(form_frame, text="Hora Fin (HH:MM):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entries['HoraFin'] = ttk.Entry(form_frame, width=30)
        self.entries['HoraFin'].grid(row=5, column=1, padx=5, pady=5)

        # Botón Fecha y Hora Actual
        btn_TimeNow = ttk.Button(form_frame, text="Usar fecha y hora actual", command=self.set_fecha_hora_actual)
        btn_TimeNow.grid(row=6, column=0, columnspan=2, pady=10)

        # Botones de Acción
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)

        confirmar_btn = ttk.Button(btn_frame, text="Confirmar Reserva", command=self._confirmar_reserva_action)
        confirmar_btn.pack(side=tk.LEFT, padx=10)

        cancelar_btn = ttk.Button(btn_frame, text="Cancelar", command=self._on_close)
        cancelar_btn.pack(side=tk.LEFT, padx=10)

    def set_fecha_hora_actual(self):
        ahora = datetime.datetime.now()
        fecha_actual = ahora.strftime("%d/%m/%Y")
        hora_inicio_actual = ahora.strftime("%H:%M")
        hora_fin_calculada = (ahora + datetime.timedelta(hours=1)).strftime("%H:%M")

        if 'FechaSolicitud' in self.entries: self.entries['FechaSolicitud'].delete(0, tk.END); self.entries['FechaSolicitud'].insert(0, fecha_actual)
        if 'HoraInicio' in self.entries: self.entries['HoraInicio'].delete(0, tk.END); self.entries['HoraInicio'].insert(0, hora_inicio_actual)
        if 'HoraFin' in self.entries: self.entries['HoraFin'].delete(0, tk.END); self.entries['HoraFin'].insert(0, hora_fin_calculada)

    def _confirmar_reserva_action(self):
        datos_reserva = {}
        campos_faltantes = []
        nombres_campos = {
            'RUTAlumno': 'RUT Alumno', 'NombreAlumno': 'Nombre y Apellido Alumno',
            'IDSala': 'Sala a Reservar', 'FechaSolicitud': 'Fecha Reserva',
            'HoraInicio': 'Hora Inicio', 'HoraFin': 'Hora Fin'
        }

        for key, widget_or_var in self.entries.items():
            valor = widget_or_var.get() if isinstance(widget_or_var, tk.StringVar) else widget_or_var.get()
            if not valor: 
                campos_faltantes.append(nombres_campos.get(key, key))
            datos_reserva[key] = valor
        
        if campos_faltantes:
            messagebox.showwarning("Campos Incompletos", 
                                   f"Por favor, complete los siguientes campos: {', '.join(campos_faltantes)}",
                                   parent=self) # parent es la Toplevel window
            return

        if guardar_reserva(datos_reserva):
            messagebox.showinfo("Reserva Exitosa", "La reserva ha sido guardada correctamente.", parent=self)
            for key, widget_or_var in self.entries.items(): # Limpiar campos
                if isinstance(widget_or_var, tk.StringVar):
                    if SALAS_DISPONIBLES: widget_or_var.set(SALAS_DISPONIBLES[0])
                elif isinstance(widget_or_var, ttk.Entry):
                     widget_or_var.delete(0, tk.END)
            # Podrías cerrar la ventana automáticamente o dejarla abierta para más reservas
            # self._on_close() 
        else:
            messagebox.showerror("Error al Guardar", "No se pudo guardar la reserva. Revise la consola para más detalles.", parent=self)

    def _on_close(self):
        self.grab_release()
        self.destroy()
        if hasattr(self.parent, 'ventana_reserva_actual') and self.parent.ventana_reserva_actual == self:
             self.parent.ventana_reserva_actual = None # Informar al padre que se cerró