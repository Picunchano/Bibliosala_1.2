import datetime
import tkinter as tk
from tkinter import ttk, messagebox
# Asegúrate que la importación de data_manager sea correcta
from data_manager import guardar_reserva, cargar_reservas, eliminar_reservas_por_timestamps 

# Lista predefinida de salas
SALAS_DISPONIBLES = ["Sala A01", "Sala A02", "Sala A03", "Sala A04", "Sala A05", "Sala A06", "Sala A07", "Sala A08", "Sala A09", "Sala A10", "Sala A11", "Sala A12", "Sala A13", "Sala A14"]

class App:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Sistema de Reserva de Salas")
        self.root.geometry("400x250") 

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(main_frame, text="Gestión de Salas de Estudio", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        btn_nueva_reserva = ttk.Button(main_frame, text="Realizar Nueva Reserva", command=self.abrir_ventana_nueva_reserva)
        btn_nueva_reserva.pack(pady=10, fill=tk.X)

        btn_ver_reservas = ttk.Button(main_frame, text="Ver Reservas Existentes", command=self.abrir_ventana_ver_reservas)
        btn_ver_reservas.pack(pady=10, fill=tk.X)

        btn_analizar_datos = ttk.Button(main_frame, text="Analizar Datos", command=self.accion_placeholder)
        btn_analizar_datos.pack(pady=10, fill=tk.X)

        self.ventana_ver_reservas_actual = None 
        self.ventana_reserva = None # Para la ventana de nueva reserva

    def accion_placeholder(self):
        messagebox.showinfo("En Desarrollo", "Esta funcionalidad aún no ha sido implementada.")

    def abrir_ventana_nueva_reserva(self):
        if self.ventana_reserva and self.ventana_reserva.winfo_exists():
            self.ventana_reserva.lift()
            return

        self.ventana_reserva = tk.Toplevel(self.root)
        self.ventana_reserva.title("Nueva Reserva")
        self.ventana_reserva.geometry("400x380")
        self.ventana_reserva.resizable(False, False)
        self.ventana_reserva.grab_set() 
        self.ventana_reserva.transient(self.root)
        self.ventana_reserva.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_nueva_reserva)


        form_frame = ttk.Frame(self.ventana_reserva, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)

        self.entries = {}

        ttk.Label(form_frame, text="RUT Alumno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entries['RUTAlumno'] = ttk.Entry(form_frame, width=30)
        self.entries['RUTAlumno'].grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Nombre y Apellido Alumno:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entries['NombreAlumno'] = ttk.Entry(form_frame, width=30)
        self.entries['NombreAlumno'].grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Sala a Reservar:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entries['IDSala'] = tk.StringVar(form_frame)
        if SALAS_DISPONIBLES:
            self.entries['IDSala'].set(SALAS_DISPONIBLES[0]) 
            sala_option_menu = ttk.OptionMenu(form_frame, self.entries['IDSala'], SALAS_DISPONIBLES[0], *SALAS_DISPONIBLES)
            sala_option_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        else:
            ttk.Label(form_frame, text="No hay salas disponibles.").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Fecha Reserva (DD/MM/AAAA):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entries['FechaSolicitud'] = ttk.Entry(form_frame, width=30)
        self.entries['FechaSolicitud'].grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Hora Inicio (HH:MM):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entries['HoraInicio'] = ttk.Entry(form_frame, width=30)
        self.entries['HoraInicio'].grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Hora Fin (HH:MM):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entries['HoraFin'] = ttk.Entry(form_frame, width=30)
        self.entries['HoraFin'].grid(row=5, column=1, padx=5, pady=5)

        btn_TimeNow = ttk.Button(form_frame, text="Usar fecha y hora actual", command=self.set_fecha_hora_actual)
        btn_TimeNow.grid(row=6, column=0, columnspan=2, pady=10)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)

        confirmar_btn = ttk.Button(btn_frame, text="Confirmar Reserva", command=self.confirmar_reserva_action)
        confirmar_btn.pack(side=tk.LEFT, padx=10)

        cancelar_btn = ttk.Button(btn_frame, text="Cancelar", command=self._cerrar_ventana_nueva_reserva)
        cancelar_btn.pack(side=tk.LEFT, padx=10)

    def _cerrar_ventana_nueva_reserva(self):
        if self.ventana_reserva and self.ventana_reserva.winfo_exists():
            self.ventana_reserva.grab_release()
            self.ventana_reserva.destroy()
            self.ventana_reserva = None

    def confirmar_reserva_action(self):
        datos_reserva = {}
        campos_faltantes = []
        nombres_campos = {
            'RUTAlumno': 'RUT Alumno', 'NombreAlumno': 'Nombre y Apellido Alumno',
            'IDSala': 'Sala a Reservar', 'FechaSolicitud': 'Fecha Reserva',
            'HoraInicio': 'Hora Inicio', 'HoraFin': 'Hora Fin'
        }

        for key, widget_or_var in self.entries.items():
            valor = widget_or_var.get() if isinstance(widget_or_var, tk.StringVar) else widget_or_var.get()
            if not valor: campos_faltantes.append(nombres_campos.get(key, key))
            datos_reserva[key] = valor
        
        if campos_faltantes:
            messagebox.showwarning("Campos Incompletos", 
                                   f"Por favor, complete los siguientes campos: {', '.join(campos_faltantes)}",
                                   parent=self.ventana_reserva)
            return

        if guardar_reserva(datos_reserva):
            messagebox.showinfo("Reserva Exitosa", "La reserva ha sido guardada correctamente.", parent=self.ventana_reserva)
            for key, widget_or_var in self.entries.items():
                if isinstance(widget_or_var, tk.StringVar):
                    if SALAS_DISPONIBLES: widget_or_var.set(SALAS_DISPONIBLES[0])
                else: widget_or_var.delete(0, tk.END)
        else:
            messagebox.showerror("Error al Guardar", "No se pudo guardar la reserva. Revise la consola para más detalles.", parent=self.ventana_reserva)

    def set_fecha_hora_actual(self):
        ahora = datetime.datetime.now()
        fecha_actual = ahora.strftime("%d/%m/%Y")
        hora_inicio_actual = ahora.strftime("%H:%M")
        hora_fin_calculada = (ahora + datetime.timedelta(hours=1)).strftime("%H:%M")

        self.entries['FechaSolicitud'].delete(0, tk.END); self.entries['FechaSolicitud'].insert(0, fecha_actual)
        self.entries['HoraInicio'].delete(0, tk.END); self.entries['HoraInicio'].insert(0, hora_inicio_actual)
        self.entries['HoraFin'].delete(0, tk.END); self.entries['HoraFin'].insert(0, hora_fin_calculada)

    def abrir_ventana_ver_reservas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
            self.ventana_ver_reservas_actual.lift()
            return

        self.ventana_ver_reservas_actual = tk.Toplevel(self.root)
        self.ventana_ver_reservas_actual.title("Reservas Existentes")
        self.ventana_ver_reservas_actual.geometry("800x400") # Un poco más ancho para el nuevo botón
        self.ventana_ver_reservas_actual.grab_set()
        self.ventana_ver_reservas_actual.transient(self.root)
        self.ventana_ver_reservas_actual.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_ver_reservas)

        tree_frame = ttk.Frame(self.ventana_ver_reservas_actual, padding="10")
        tree_frame.pack(expand=True, fill=tk.BOTH)

        column_ids = ("rut_alumno", "nombre_alumno", "sala", "fecha", "hora_inicio", "hora_fin")
        column_headings = ("RUT Alumno", "Nombre Alumno", "Sala", "Fecha", "Hora Inicio", "Hora Fin")
        
        # Configurar Treeview para selección múltiple
        self.tree_reservas = ttk.Treeview(tree_frame, columns=column_ids, show='headings', selectmode='extended')

        for i, col_id in enumerate(column_ids):
            self.tree_reservas.heading(col_id, text=column_headings[i])
            width = 200 if col_id == "nombre_alumno" else 120 # Ancho ajustado
            anchor = tk.W if col_id == "nombre_alumno" else tk.CENTER
            self.tree_reservas.column(col_id, width=width, anchor=anchor, minwidth=60)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_reservas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        buttons_frame = ttk.Frame(self.ventana_ver_reservas_actual, padding="10")
        buttons_frame.pack(fill=tk.X)

        btn_actualizar = ttk.Button(buttons_frame, text="Actualizar Lista", command=self.poblar_treeview_reservas)
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        # Nuevo botón para eliminar reservas seleccionadas
        btn_eliminar_seleccion = ttk.Button(buttons_frame, text="Eliminar Seleccionadas", command=self.eliminar_reservas_seleccionadas_action)
        btn_eliminar_seleccion.pack(side=tk.LEFT, padx=5)

        btn_cerrar = ttk.Button(buttons_frame, text="Cerrar", command=self._cerrar_ventana_ver_reservas)
        btn_cerrar.pack(side=tk.RIGHT, padx=5) # Movido a la derecha
        
        self.poblar_treeview_reservas()

    def _cerrar_ventana_ver_reservas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
            self.ventana_ver_reservas_actual.grab_release()
            self.ventana_ver_reservas_actual.destroy()
            self.ventana_ver_reservas_actual = None

    def poblar_treeview_reservas(self):
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas.winfo_exists():
            return

        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)

        reservas_data = cargar_reservas() # Nombre cambiado para claridad

        if not reservas_data:
            messagebox.showinfo("Información", 
                                "No hay reservas registradas o el archivo 'reservas.csv' está vacío/no se encuentra.",
                                parent=self.ventana_ver_reservas_actual if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists() else self.root)
        else:
            for reserva in reservas_data:
                # Usar TimestampReserva como iid (identificador de ítem)
                # Las claves deben coincidir con las del CSV
                timestamp_id = reserva.get('TimestampReserva') 
                valores_visibles = (
                    reserva.get('RUTAlumno', ''), 
                    reserva.get('NombreAlumno', ''),
                    reserva.get('IDSala', ''),
                    reserva.get('FechaSolicitud', ''),
                    reserva.get('HoraInicio', ''),
                    reserva.get('HoraFin', '')
                )
                if timestamp_id: # Asegurarse de que el timestamp existe para usarlo como iid
                    self.tree_reservas.insert('', tk.END, iid=timestamp_id, values=valores_visibles)
                else:
                    # Fallback si no hay timestamp, aunque no debería pasar con la lógica actual de guardado
                    self.tree_reservas.insert('', tk.END, values=valores_visibles)


    def eliminar_reservas_seleccionadas_action(self):
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas.winfo_exists():
            return

        selected_iids = self.tree_reservas.selection() # Obtiene los iids (timestamps) de los ítems seleccionados

        if not selected_iids:
            messagebox.showwarning("Sin Selección", 
                                   "Por favor, seleccione una o más reservas para eliminar.",
                                   parent=self.ventana_ver_reservas_actual)
            return

        # Confirmación del usuario
        confirmacion = messagebox.askyesno("Confirmar Eliminación",
                                           f"¿Está seguro de que desea eliminar {len(selected_iids)} reserva(s) seleccionada(s)?\nEsta acción no se puede deshacer.",
                                           parent=self.ventana_ver_reservas_actual)
        
        if confirmacion:
            # Llamar a la función del data_manager para eliminar
            if eliminar_reservas_por_timestamps(list(selected_iids)):
                messagebox.showinfo("Eliminación Exitosa", 
                                    "Las reservas seleccionadas han sido eliminadas.",
                                    parent=self.ventana_ver_reservas_actual)
            else:
                messagebox.showerror("Error de Eliminación",
                                     "Ocurrió un error al intentar eliminar las reservas. Revise la consola.",
                                     parent=self.ventana_ver_reservas_actual)
            
            # Actualizar el Treeview para reflejar los cambios
            self.poblar_treeview_reservas()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()