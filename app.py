import datetime
import tkinter as tk
from tkinter import ttk, messagebox
# Asegúrate que la importación de data_manager sea correcta
from data_manager import (
    guardar_reserva,
    cargar_reservas,
    eliminar_reservas_por_timestamps,
    inicializar_datos_ejemplo
)
# Importar funciones de analysis.py
import analysis # O from analysis import alumno_mas_solicitudes, sala_mas_ocupada, total_salas_solicitadas

# Lista predefinida de salas
SALAS_DISPONIBLES = ["Sala A01", "Sala A02", "Sala A03", "Sala A04", "Sala A05", "Sala A06", "Sala A07", "Sala A08", "Sala A09", "Sala A10", "Sala A11", "Sala A12", "Sala A13", "Sala A14"]

class App:
    def __init__(self, root_window):
        inicializar_datos_ejemplo()

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

        btn_analizar_datos = ttk.Button(main_frame, text="Analizar Datos", command=self.abrir_ventana_analisis)
        btn_analizar_datos.pack(pady=10, fill=tk.X)

        self.ventana_ver_reservas_actual = None
        self.ventana_reserva = None
        self.ventana_analisis_actual = None

    def abrir_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.lift()
            return

        self.ventana_analisis_actual = tk.Toplevel(self.root)
        self.ventana_analisis_actual.title("Análisis de Datos de Reservas")
        self.ventana_analisis_actual.geometry("550x420") # Ajustado para más espacio
        self.ventana_analisis_actual.resizable(False, False)
        self.ventana_analisis_actual.grab_set()
        self.ventana_analisis_actual.transient(self.root)
        self.ventana_analisis_actual.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_analisis)

        main_analysis_frame = ttk.Frame(self.ventana_analisis_actual, padding="15")
        main_analysis_frame.pack(expand=True, fill=tk.BOTH)

        # --- Sección para ingresar fecha ---
        input_frame = ttk.Frame(main_analysis_frame)
        input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(input_frame, text="Filtrar por Fecha (DD/MM/AAAA):").pack(side=tk.LEFT, padx=(0,10))

        current_date = datetime.datetime.now()

        # Año
        ttk.Label(input_frame, text="Año:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_anio_analisis = ttk.Entry(input_frame, width=6)
        self.entry_anio_analisis.insert(0, str(current_date.year))
        self.entry_anio_analisis.pack(side=tk.LEFT, padx=(0,10))

        # Mes
        ttk.Label(input_frame, text="Mes:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_mes_analisis = ttk.Entry(input_frame, width=4)
        self.entry_mes_analisis.insert(0, str(current_date.month))
        self.entry_mes_analisis.pack(side=tk.LEFT, padx=(0,5))

        # Día
        ttk.Label(input_frame, text="Día:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_dia_analisis = ttk.Entry(input_frame, width=4)
        self.entry_dia_analisis.insert(0, str(current_date.day))
        self.entry_dia_analisis.pack(side=tk.LEFT, padx=(0,5))

        # Botón para Limpiar Filtro de Fecha
        btn_limpiar_fecha = ttk.Button(input_frame, text="Limpiar Fecha", command=self._limpiar_filtros_fecha_analisis)
        btn_limpiar_fecha.pack(side=tk.LEFT, padx=5)


        # Botones de análisis
        buttons_frame = ttk.Frame(main_analysis_frame)
        buttons_frame.pack(pady=10, fill=tk.X)

        btn_analizar_alumno = ttk.Button(buttons_frame, text="Analizar Alumno Más Activo", command=self.realizar_analisis_alumno)
        btn_analizar_alumno.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        btn_analizar_sala = ttk.Button(buttons_frame, text="Analizar Sala Más Ocupada", command=self.realizar_analisis_sala)
        btn_analizar_sala.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # --- Nuevo botón para el total de salas pedidas ---
        btn_total_salas = ttk.Button(buttons_frame, text="Analizar Cantidad de Salas Pedidas", command=self.realizar_analisis_total_salas)
        btn_total_salas.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)


        # Sección para mostrar resultados
        results_frame = ttk.LabelFrame(main_analysis_frame, text="Resultados del Análisis", padding="10")
        results_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.label_resultado_alumno = ttk.Label(results_frame, text="Alumno más activo: Pendiente...", wraplength=500)
        self.label_resultado_alumno.pack(anchor="w", pady=5)

        self.label_resultado_sala = ttk.Label(results_frame, text="Sala más ocupada: Pendiente...", wraplength=500)
        self.label_resultado_sala.pack(anchor="w", pady=5)

        # --- Nuevo Label para el resultado del total de salas pedidas ---
        self.label_resultado_total_salas = ttk.Label(results_frame, text="Cantidad de salas pedidas: Pendiente...", wraplength=500)
        self.label_resultado_total_salas.pack(anchor="w", pady=5)

        # Botón de cerrar ventana de análisis
        btn_cerrar_analisis = ttk.Button(main_analysis_frame, text="Cerrar Análisis", command=self._cerrar_ventana_analisis)
        btn_cerrar_analisis.pack(pady=15)

    def _limpiar_filtros_fecha_analisis(self):
        """Limpia los campos de entrada de fecha y los resultados de análisis."""
        if hasattr(self, 'entry_dia_analisis'): self.entry_dia_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_mes_analisis'): self.entry_mes_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_anio_analisis'): self.entry_anio_analisis.delete(0, tk.END)
        self.label_resultado_alumno.config(text="Alumno más activo: Pendiente...")
        self.label_resultado_sala.config(text="Sala más ocupada: Pendiente...")
        self.label_resultado_total_salas.config(text="Cantidad de salas pedidas: Pendiente...")


    def _cerrar_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.grab_release()
            self.ventana_analisis_actual.destroy()
            self.ventana_analisis_actual = None

    def _obtener_fecha_analisis(self):
        """
        Helper para obtener y validar la fecha (día, mes, año) de los Entries.
        Devuelve (dia_int, mes_int, anio_int, display_str_para_resultados).
        Si los campos están vacíos, los _int correspondientes serán None.
        """
        dia_str = self.entry_dia_analisis.get()
        mes_str = self.entry_mes_analisis.get()
        anio_str = self.entry_anio_analisis.get()

        dia_int, mes_int, anio_int = None, None, None
        error_msg = None

        # Procesar y validar año
        if anio_str:
            try:
                val = int(anio_str)
                if 1900 <= val <= 3000: # Rango razonable
                    anio_int = val
                else:
                    error_msg = "Año fuera de rango (1900-3000)."
            except ValueError:
                error_msg = "Año debe ser un número."

        # Procesar y validar mes (solo si no hay error previo)
        if mes_str and not error_msg:
            try:
                val = int(mes_str)
                if 1 <= val <= 12:
                    mes_int = val
                else:
                    error_msg = "Mes inválido (1-12)."
            except ValueError:
                error_msg = "Mes debe ser un número."

        # Procesar y validar día (solo si no hay error previo)
        if dia_str and not error_msg:
            try:
                val = int(dia_str)
                # Validación básica, podría mejorarse con calendar.monthrange si mes y año son válidos
                if 1 <= val <= 31:
                    dia_int = val
                else:
                    error_msg = "Día inválido (1-31)."
            except ValueError:
                error_msg = "Día debe ser un número."

        # Lógica de dependencia para el filtro (ej. día necesita mes y año)
        if not error_msg:
            if dia_int is not None and (mes_int is None or anio_int is None):
                error_msg = "Para filtrar por día, también se requieren Mes y Año."
            elif mes_int is not None and anio_int is None:
                error_msg = "Para filtrar por mes, también se requiere Año."

        if error_msg:
            messagebox.showerror("Error en Fecha", error_msg, parent=self.ventana_analisis_actual)
            return None, None, None, "Error en fecha" # Indicador de error

        # Construir la cadena para mostrar en los resultados
        display_str = "Todos los datos"
        if anio_int is not None:
            if mes_int is not None:
                if dia_int is not None:
                    display_str = f"Fecha: {dia_int:02d}/{mes_int:02d}/{anio_int}"
                else: # Año y Mes
                    display_str = f"Mes: {mes_int:02d}/{anio_int}"
            else: # Solo Año
                if dia_int is not None:
                    display_str = f"Año: {anio_int} (Día ignorado sin Mes)"
                    dia_int = None # No filtrar por día si no hay mes
                else:
                    display_str = f"Año: {anio_int}"
        elif mes_int is not None or dia_int is not None:
             display_str = "Filtro de fecha incompleto (Se requiere al menos el Año)"

        return dia_int, mes_int, anio_int, display_str


    def realizar_analisis_alumno(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()):
            return

        dia, mes, anio, display_str = self._obtener_fecha_analisis()

        if display_str == "Error en fecha":
             self.label_resultado_alumno.config(text=f"Alumno más activo: {display_str}")
             return

        todas_las_reservas = cargar_reservas()
        if not todas_las_reservas:
            self.label_resultado_alumno.config(text=f"Alumno más activo ({display_str}): No hay reservas registradas.")
            return

        nombre_alumno, cantidad = analysis.alumno_mas_solicitudes(todas_las_reservas, anio=anio, mes=mes, dia=dia)

        if nombre_alumno:
            resultado_texto = f"Alumno más activo ({display_str}): {nombre_alumno} con {cantidad} reserva(s)."
        else:
            resultado_texto = f"Alumno más activo ({display_str}): No se encontraron datos para este criterio."
        self.label_resultado_alumno.config(text=resultado_texto)


    def realizar_analisis_sala(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()):
            return

        dia, mes, anio, display_str = self._obtener_fecha_analisis()

        if display_str == "Error en fecha":
            self.label_resultado_sala.config(text=f"Sala más ocupada: {display_str}")
            return

        todas_las_reservas = cargar_reservas()
        if not todas_las_reservas:
            self.label_resultado_sala.config(text=f"Sala más ocupada ({display_str}): No hay reservas registradas.")
            return

        id_sala, cantidad = analysis.sala_mas_ocupada(todas_las_reservas, anio=anio, mes=mes, dia=dia)

        if id_sala:
            resultado_texto = f"Sala más ocupada ({display_str}): {id_sala} con {cantidad} reserva(s)."
        else:
            resultado_texto = f"Sala más ocupada ({display_str}): No se encontraron datos para este criterio."
        self.label_resultado_sala.config(text=resultado_texto)

    # --- Nuevo método para analizar el total de salas pedidas ---
    def realizar_analisis_total_salas(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()):
            return

        dia, mes, anio, display_str = self._obtener_fecha_analisis()

        if display_str == "Error en fecha":
            self.label_resultado_total_salas.config(text=f"Cantidad de salas pedidas: {display_str}")
            return

        todas_las_reservas = cargar_reservas()
        if not todas_las_reservas:
            self.label_resultado_total_salas.config(text=f"Cantidad de salas pedidas ({display_str}): No hay reservas registradas.")
            return

        # Llama a la nueva función de analysis.py
        total_salas = analysis.total_salas_solicitadas(todas_las_reservas, anio=anio, mes=mes, dia=dia)

        resultado_texto = f"Cantidad de salas pedidas ({display_str}): {total_salas}."
        self.label_resultado_total_salas.config(text=resultado_texto)


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
        self.ventana_ver_reservas_actual.geometry("800x400")
        self.ventana_ver_reservas_actual.grab_set()
        self.ventana_ver_reservas_actual.transient(self.root)
        self.ventana_ver_reservas_actual.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_ver_reservas)

        tree_frame = ttk.Frame(self.ventana_ver_reservas_actual, padding="10")
        tree_frame.pack(expand=True, fill=tk.BOTH)

        column_ids = ("rut_alumno", "nombre_alumno", "sala", "fecha", "hora_inicio", "hora_fin")
        column_headings = ("ID Alumno", "Nombre Alumno", "Sala", "Fecha", "Hora Inicio", "Hora Fin")

        self.tree_reservas = ttk.Treeview(tree_frame, columns=column_ids, show='headings', selectmode='extended')

        for i, col_id in enumerate(column_ids):
            self.tree_reservas.heading(col_id, text=column_headings[i])
            width = 200 if col_id == "nombre_alumno" else 120
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

        btn_eliminar_seleccion = ttk.Button(buttons_frame, text="Eliminar Seleccionadas", command=self.eliminar_reservas_seleccionadas_action)
        btn_eliminar_seleccion.pack(side=tk.LEFT, padx=5)

        btn_cerrar = ttk.Button(buttons_frame, text="Cerrar", command=self._cerrar_ventana_ver_reservas)
        btn_cerrar.pack(side=tk.RIGHT, padx=5)

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

        reservas_data = cargar_reservas()

        if not reservas_data:
            if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
                 messagebox.showinfo("Información",
                                    "No hay reservas registradas.",
                                    parent=self.ventana_ver_reservas_actual)
        else:
            for reserva in reservas_data:
                timestamp_id = reserva.get('TimestampReserva')
                valores_visibles = (
                    reserva.get('RUTAlumno', ''),
                    reserva.get('NombreAlumno', ''),
                    reserva.get('IDSala', ''),
                    reserva.get('FechaSolicitud', ''),
                    reserva.get('HoraInicio', ''),
                    reserva.get('HoraFin', '')
                )
                if timestamp_id:
                    self.tree_reservas.insert('', tk.END, iid=timestamp_id, values=valores_visibles)
                else:
                    self.tree_reservas.insert('', tk.END, values=valores_visibles)


    def eliminar_reservas_seleccionadas_action(self):
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas.winfo_exists():
            return

        selected_iids = self.tree_reservas.selection()

        if not selected_iids:
            messagebox.showwarning("Sin Selección",
                                   "Por favor, seleccione una o más reservas para eliminar.",
                                   parent=self.ventana_ver_reservas_actual)
            return

        confirmacion = messagebox.askyesno("Confirmar Eliminación",
                                           f"¿Está seguro de que desea eliminar {len(selected_iids)} reserva(s) seleccionada(s)?\nEsta acción no se puede deshacer.",
                                           parent=self.ventana_ver_reservas_actual)

        if confirmacion:
            if eliminar_reservas_por_timestamps(list(selected_iids)):
                messagebox.showinfo("Eliminación Exitosa",
                                    "Las reservas seleccionadas han sido eliminadas.",
                                    parent=self.ventana_ver_reservas_actual)
            else:
                messagebox.showerror("Error de Eliminación",
                                     "Ocurrió un error al intentar eliminar las reservas. Revise la consola.",
                                     parent=self.ventana_ver_reservas_actual)

            self.poblar_treeview_reservas()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()