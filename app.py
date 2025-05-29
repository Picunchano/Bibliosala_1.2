import datetime # Asegúrate que datetime está importado
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from data_manager import (
    guardar_reserva,
    cargar_reservas,
    eliminar_reservas_por_timestamps,
    inicializar_datos_ejemplo
)
import analysis

SALAS_DISPONIBLES = ["Sala A01", "Sala A02", "Sala A03", "Sala A04", "Sala A05", "Sala A06", "Sala A07", "Sala A08", "Sala A09", "Sala A10", "Sala A11", "Sala A12", "Sala A13", "Sala A14"]

class App:
    def __init__(self, root_window):
        inicializar_datos_ejemplo()
        self.root = root_window
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

        # Botón modificado para "Reservas Activas"
        btn_activas_reservas = ttk.Button(main_frame, text="Reservas Activas", command=self.abrir_ventana_reservas_activas)
        btn_activas_reservas.pack(pady=8, fill=tk.X)

        btn_analizar_datos = ttk.Button(main_frame, text="Analizar Datos", command=self.abrir_ventana_analisis)
        btn_analizar_datos.pack(pady=8, fill=tk.X)

        self.ventana_ver_reservas_actual = None
        self.ventana_reserva = None
        self.ventana_analisis_actual = None

    # --- Métodos de Análisis (sin cambios) ---
    def abrir_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.lift()
            return

        self.ventana_analisis_actual = tk.Toplevel(self.root)
        self.ventana_analisis_actual.title("Análisis de Datos de Reservas")
        self.ventana_analisis_actual.geometry("650x550")
        self.ventana_analisis_actual.resizable(True, True)
        self.ventana_analisis_actual.grab_set()
        self.ventana_analisis_actual.transient(self.root)
        self.ventana_analisis_actual.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_analisis)

        main_analysis_frame = ttk.Frame(self.ventana_analisis_actual, padding="15")
        main_analysis_frame.pack(expand=True, fill=tk.BOTH)

        input_frame = ttk.Frame(main_analysis_frame)
        input_frame.pack(pady=10, fill=tk.X)
        ttk.Label(input_frame, text="Filtrar por Fecha (DD/MM/AAAA):").pack(side=tk.LEFT, padx=(0,10))
        current_date = datetime.datetime.now()
        ttk.Label(input_frame, text="Año:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_anio_analisis = ttk.Entry(input_frame, width=6)
        self.entry_anio_analisis.insert(0, str(current_date.year))
        self.entry_anio_analisis.pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(input_frame, text="Mes:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_mes_analisis = ttk.Entry(input_frame, width=4)
        self.entry_mes_analisis.insert(0, str(current_date.month))
        self.entry_mes_analisis.pack(side=tk.LEFT, padx=(0,5))
        ttk.Label(input_frame, text="Día:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_dia_analisis = ttk.Entry(input_frame, width=4)
        self.entry_dia_analisis.insert(0, str(current_date.day))
        self.entry_dia_analisis.pack(side=tk.LEFT, padx=(0,5))
        btn_limpiar_fecha = ttk.Button(input_frame, text="Limpiar Fecha", command=self._limpiar_filtros_fecha_analisis)
        btn_limpiar_fecha.pack(side=tk.LEFT, padx=5)

        buttons_outer_frame = ttk.Frame(main_analysis_frame)
        buttons_outer_frame.pack(pady=5, fill=tk.X)
        buttons_frame_line1 = ttk.Frame(buttons_outer_frame)
        buttons_frame_line1.pack(fill=tk.X)
        btn_analizar_alumno = ttk.Button(buttons_frame_line1, text="Top 10 Alumnos Activos", command=self.realizar_analisis_alumno)
        btn_analizar_alumno.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        btn_analizar_sala = ttk.Button(buttons_frame_line1, text="Sala Más Ocupada", command=self.realizar_analisis_sala)
        btn_analizar_sala.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        buttons_frame_line2 = ttk.Frame(buttons_outer_frame)
        buttons_frame_line2.pack(fill=tk.X, pady=(5,0))
        btn_total_salas = ttk.Button(buttons_frame_line2, text="Cantidad Salas Pedidas", command=self.realizar_analisis_total_salas)
        btn_total_salas.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        btn_horarios_activos = ttk.Button(buttons_frame_line2, text="Horarios Más Activos", command=self.realizar_analisis_horarios)
        btn_horarios_activos.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        results_frame = ttk.LabelFrame(main_analysis_frame, text="Resultados del Análisis", padding="10")
        results_frame.pack(pady=10, expand=True, fill=tk.BOTH)
        ttk.Label(results_frame, text="Top Alumnos Activos:").pack(anchor="w", pady=(5,0))
        self.text_resultado_alumnos = scrolledtext.ScrolledText(results_frame, height=7, width=70, wrap=tk.WORD, state=tk.DISABLED)
        self.text_resultado_alumnos.pack(anchor="w", pady=3, expand=True, fill=tk.X)
        self._actualizar_texto_widget(self.text_resultado_alumnos, "Pendiente...")
        self.label_resultado_sala = ttk.Label(results_frame, text="Sala más ocupada: Pendiente...", wraplength=600)
        self.label_resultado_sala.pack(anchor="w", pady=3)
        self.label_resultado_total_salas = ttk.Label(results_frame, text="Cantidad de salas pedidas: Pendiente...", wraplength=600)
        self.label_resultado_total_salas.pack(anchor="w", pady=3)
        self.label_resultado_horarios = ttk.Label(results_frame, text="Horarios más activos: Pendiente...", wraplength=600)
        self.label_resultado_horarios.pack(anchor="w", pady=3)
        btn_cerrar_analisis = ttk.Button(main_analysis_frame, text="Cerrar Análisis", command=self._cerrar_ventana_analisis)
        btn_cerrar_analisis.pack(pady=15)

    def _actualizar_texto_widget(self, text_widget, content):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete('1.0', tk.END)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def _limpiar_filtros_fecha_analisis(self):
        if hasattr(self, 'entry_dia_analisis'): self.entry_dia_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_mes_analisis'): self.entry_mes_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_anio_analisis'): self.entry_anio_analisis.delete(0, tk.END)
        if hasattr(self, 'text_resultado_alumnos'):
            self._actualizar_texto_widget(self.text_resultado_alumnos, "Top Alumnos Activos: Pendiente...")
        if hasattr(self, 'label_resultado_sala'):
            self.label_resultado_sala.config(text="Sala más ocupada: Pendiente...")
        if hasattr(self, 'label_resultado_total_salas'):
            self.label_resultado_total_salas.config(text="Cantidad de salas pedidas: Pendiente...")
        if hasattr(self, 'label_resultado_horarios'):
            self.label_resultado_horarios.config(text="Horarios más activos: Pendiente...")

    def _cerrar_ventana_analisis(self):
        if self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists():
            self.ventana_analisis_actual.grab_release()
            self.ventana_analisis_actual.destroy()
            self.ventana_analisis_actual = None

    def _obtener_fecha_analisis(self):
        dia_str = self.entry_dia_analisis.get()
        mes_str = self.entry_mes_analisis.get()
        anio_str = self.entry_anio_analisis.get()
        dia_int, mes_int, anio_int = None, None, None
        error_msg = None
        if anio_str:
            try:
                val = int(anio_str)
                if 1900 <= val <= 3000: anio_int = val
                else: error_msg = "Año fuera de rango (1900-3000)."
            except ValueError: error_msg = "Año debe ser un número."
        if mes_str and not error_msg:
            try:
                val = int(mes_str)
                if 1 <= val <= 12: mes_int = val
                else: error_msg = "Mes inválido (1-12)."
            except ValueError: error_msg = "Mes debe ser un número."
        if dia_str and not error_msg:
            try:
                val = int(dia_str)
                if 1 <= val <= 31: dia_int = val
                else: error_msg = "Día inválido (1-31)."
            except ValueError: error_msg = "Día debe ser un número."
        if not error_msg:
            if dia_int is not None and (mes_int is None or anio_int is None):
                error_msg = "Para filtrar por día, también se requieren Mes y Año."
            elif mes_int is not None and anio_int is None:
                error_msg = "Para filtrar por mes, también se requiere Año."
        if error_msg:
            messagebox.showerror("Error en Fecha", error_msg, parent=self.ventana_analisis_actual)
            return None, None, None, "Error en fecha"
        display_str = "Todos los datos"
        if anio_int is not None:
            if mes_int is not None:
                if dia_int is not None: display_str = f"Fecha: {dia_int:02d}/{mes_int:02d}/{anio_int}"
                else: display_str = f"Mes: {mes_int:02d}/{anio_int}"
            else:
                if dia_int is not None:
                    display_str = f"Año: {anio_int} (Día ignorado sin Mes)"
                    dia_int = None
                else: display_str = f"Año: {anio_int}"
        elif mes_int is not None or dia_int is not None:
             display_str = "Filtro de fecha incompleto (Se requiere al menos el Año)"
        return dia_int, mes_int, anio_int, display_str

    def realizar_analisis_alumno(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()): return
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        titulo_resultado = f"Top Alumnos Activos ({display_str}):\n"
        if display_str == "Error en fecha":
             self._actualizar_texto_widget(self.text_resultado_alumnos, f"{titulo_resultado}Error en la validación de la fecha.")
             return
        todas_las_reservas = cargar_reservas()
        if not todas_las_reservas:
            self._actualizar_texto_widget(self.text_resultado_alumnos, f"{titulo_resultado}No hay reservas registradas.")
            return
        top_alumnos = analysis.alumno_mas_solicitudes(todas_las_reservas, anio=anio, mes=mes, dia=dia, top_n=10)
        if top_alumnos:
            resultado_formateado = titulo_resultado
            for i, (nombre, cantidad) in enumerate(top_alumnos):
                resultado_formateado += f"{i+1}. {nombre} - {cantidad} reserva(s)\n"
        else:
            resultado_formateado = f"{titulo_resultado}No se encontraron datos de alumnos para este criterio."
        self._actualizar_texto_widget(self.text_resultado_alumnos, resultado_formateado.strip())

    def realizar_analisis_sala(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()): return
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        if display_str == "Error en fecha":
            self.label_resultado_sala.config(text=f"Sala más ocupada: {display_str}")
            return
        reservas = cargar_reservas()
        if not reservas:
            self.label_resultado_sala.config(text=f"Sala más ocupada ({display_str}): No hay reservas.")
            return
        sala, cant = analysis.sala_mas_ocupada(reservas, anio, mes, dia)
        if sala: texto = f"Sala más ocupada ({display_str}): {sala} con {cant} reserva(s)."
        else: texto = f"Sala más ocupada ({display_str}): Sin datos para este criterio."
        self.label_resultado_sala.config(text=texto)

    def realizar_analisis_total_salas(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()): return
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        if display_str == "Error en fecha":
            self.label_resultado_total_salas.config(text=f"Cantidad de salas pedidas: {display_str}")
            return
        reservas = cargar_reservas()
        total = analysis.total_salas_solicitadas(reservas, anio, mes, dia)
        texto = f"Cantidad de salas pedidas ({display_str}): {total}."
        self.label_resultado_total_salas.config(text=texto)

    def realizar_analisis_horarios(self):
        if not (self.ventana_analisis_actual and self.ventana_analisis_actual.winfo_exists()): return
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        if display_str == "Error en fecha":
            self.label_resultado_horarios.config(text=f"Horarios más activos: {display_str}")
            return
        reservas = cargar_reservas()
        if not reservas:
            self.label_resultado_horarios.config(text=f"Horarios más activos ({display_str}): No hay reservas.")
            return
        h_inicio, h_fin, actividad = analysis.horarios_mas_activos(reservas, anio, mes, dia)
        if h_inicio is not None and actividad > 0:
            texto = f"Horarios más activos ({display_str}): Desde las {h_inicio:02d}:00 hasta las {h_fin + 1:02d}:00 ({h_fin:02d}:xx inclusive), con {actividad} reservas activas."
        else:
            texto = f"Horarios más activos ({display_str}): Sin actividad o datos suficientes para este criterio."
        self.label_resultado_horarios.config(text=texto)

    # --- Métodos de Reserva (sin cambios en nueva reserva) ---
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
        nombres_campos = {'RUTAlumno': 'RUT Alumno', 'NombreAlumno': 'Nombre y Apellido Alumno','IDSala': 'Sala a Reservar', 'FechaSolicitud': 'Fecha Reserva','HoraInicio': 'Hora Inicio', 'HoraFin': 'Hora Fin'}
        for key, widget_or_var in self.entries.items():
            valor = widget_or_var.get() if isinstance(widget_or_var, tk.StringVar) else widget_or_var.get()
            if not valor: campos_faltantes.append(nombres_campos.get(key, key))
            datos_reserva[key] = valor
        if campos_faltantes:
            messagebox.showwarning("Campos Incompletos", f"Por favor, complete los siguientes campos: {', '.join(campos_faltantes)}",parent=self.ventana_reserva)
            return
        if guardar_reserva(datos_reserva): # Aquí se podría añadir la validación de disponibilidad
            messagebox.showinfo("Reserva Exitosa", "La reserva ha sido guardada correctamente.", parent=self.ventana_reserva)
            for key, widget_or_var in self.entries.items():
                if isinstance(widget_or_var, tk.StringVar):
                    if SALAS_DISPONIBLES: widget_or_var.set(SALAS_DISPONIBLES[0])
                else: widget_or_var.delete(0, tk.END)
        else: messagebox.showerror("Error al Guardar", "No se pudo guardar la reserva. Revise la consola para más detalles.", parent=self.ventana_reserva)

    def set_fecha_hora_actual(self):
        ahora = datetime.datetime.now()
        fecha_actual = ahora.strftime("%d/%m/%Y")
        hora_inicio_actual = ahora.strftime("%H:%M")
        # Por defecto, la reserva actual durará 1 hora.
        hora_fin_calculada = (ahora + datetime.timedelta(hours=1)).strftime("%H:%M")
        self.entries['FechaSolicitud'].delete(0, tk.END); self.entries['FechaSolicitud'].insert(0, fecha_actual)
        self.entries['HoraInicio'].delete(0, tk.END); self.entries['HoraInicio'].insert(0, hora_inicio_actual)
        self.entries['HoraFin'].delete(0, tk.END); self.entries['HoraFin'].insert(0, hora_fin_calculada)

    # --- Métodos para Ver/Gestionar Reservas (MODIFICADOS) ---
    def _abrir_ventana_base_ver_reservas(self, titulo_ventana: str, filtrar_activas: bool): # Parámetro renombrado conceptualmente
        """
        Método base para abrir la ventana de visualización de reservas.
        Reutiliza la ventana si ya existe.
        'filtrar_activas' es True para la vista de "Reservas Activas".
        """
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
            self.ventana_ver_reservas_actual.title(titulo_ventana)
            self.ventana_ver_reservas_actual.lift()
        else:
            self.ventana_ver_reservas_actual = tk.Toplevel(self.root)
            self.ventana_ver_reservas_actual.title(titulo_ventana)
            self.ventana_ver_reservas_actual.geometry("800x400")
            self.ventana_ver_reservas_actual.grab_set()
            self.ventana_ver_reservas_actual.transient(self.root)
            self.ventana_ver_reservas_actual.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_ver_reservas)

            tree_frame = ttk.Frame(self.ventana_ver_reservas_actual, padding="10")
            tree_frame.pack(expand=True, fill=tk.BOTH)

            column_ids = ("rut_alumno", "nombre_alumno", "sala", "fecha", "hora_inicio", "hora_fin")
            column_headings = ("RUT Alumno", "Nombre Alumno", "Sala", "Fecha", "Hora Inicio", "Hora Fin")
            self.tree_reservas = ttk.Treeview(tree_frame, columns=column_ids, show='headings', selectmode='extended')

            for i, col_id in enumerate(column_ids):
                self.tree_reservas.heading(col_id, text=column_headings[i])
                width = 150 if col_id == "nombre_alumno" else 120
                anchor = tk.W if col_id == "nombre_alumno" else tk.CENTER
                self.tree_reservas.column(col_id, width=width, anchor=anchor, minwidth=60)

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
            self.tree_reservas.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree_reservas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            buttons_frame = ttk.Frame(self.ventana_ver_reservas_actual, padding="10")
            buttons_frame.pack(fill=tk.X)

            btn_actualizar = ttk.Button(buttons_frame, text="Actualizar Lista",
                                        command=lambda fa=filtrar_activas: self.poblar_treeview_reservas(filtrar_activas=fa))
            btn_actualizar.pack(side=tk.LEFT, padx=5)

            btn_eliminar_seleccion = ttk.Button(buttons_frame, text="Eliminar Seleccionadas", command=self.eliminar_reservas_seleccionadas_action)
            btn_eliminar_seleccion.pack(side=tk.LEFT, padx=5)
            btn_cerrar = ttk.Button(buttons_frame, text="Cerrar", command=self._cerrar_ventana_ver_reservas)
            btn_cerrar.pack(side=tk.RIGHT, padx=5)

        self.poblar_treeview_reservas(filtrar_activas=filtrar_activas)

    def abrir_ventana_historial_reservas(self):
        self._abrir_ventana_base_ver_reservas("Historial de Reservas", filtrar_activas=False)

    def abrir_ventana_reservas_activas(self): # Método renombrado para claridad
        """Abre la ventana para ver solo las reservas ACTIVAS."""
        self._abrir_ventana_base_ver_reservas("Reservas Activas", filtrar_activas=True)

    def _cerrar_ventana_ver_reservas(self):
        if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
            self.ventana_ver_reservas_actual.grab_release()
            self.ventana_ver_reservas_actual.destroy()
            self.ventana_ver_reservas_actual = None
            self.tree_reservas = None

    def poblar_treeview_reservas(self, filtrar_activas: bool = False): # Parámetro renombrado conceptualmente
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas or not self.tree_reservas.winfo_exists():
            return

        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)

        reservas_data = cargar_reservas()
        reservas_a_mostrar = []
        ahora = datetime.datetime.now() # Obtener la hora actual una vez

        if filtrar_activas:
            for reserva in reservas_data:
                fecha_reserva_str = reserva.get('FechaSolicitud')
                hora_inicio_str = reserva.get('HoraInicio')
                hora_fin_str = reserva.get('HoraFin')

                if not fecha_reserva_str or not hora_inicio_str or not hora_fin_str:
                    # print(f"Advertencia: Datos incompletos de fecha/hora en reserva {reserva.get('TimestampReserva')}, se omitirá.")
                    continue # Omitir si falta algún dato esencial

                try:
                    fecha_obj = datetime.datetime.strptime(fecha_reserva_str, "%d/%m/%Y").date()
                    
                    hora_inicio_obj = datetime.datetime.strptime(hora_inicio_str, "%H:%M").time()
                    reserva_dt_inicio = datetime.datetime.combine(fecha_obj, hora_inicio_obj)
                    
                    hora_fin_obj = datetime.datetime.strptime(hora_fin_str, "%H:%M").time()
                    reserva_dt_fin = datetime.datetime.combine(fecha_obj, hora_fin_obj)

                    # Lógica para reserva activa: inicio <= ahora < fin
                    if reserva_dt_inicio <= ahora < reserva_dt_fin:
                        reservas_a_mostrar.append(reserva)
                except ValueError:
                    # print(f"Advertencia: Formato de fecha/hora inválido en reserva {reserva.get('TimestampReserva')}, se omitirá del filtro de activas.")
                    continue
            
            if not reservas_a_mostrar and self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
                 messagebox.showinfo("Información",
                                    "No hay reservas activas en este momento.",
                                    parent=self.ventana_ver_reservas_actual)
                 return
        else: # Mostrar todas (Historial)
            reservas_a_mostrar = list(reservas_data)

        def sort_key_fecha_solicitud(reserva):
            fecha_str = reserva.get('FechaSolicitud')
            hora_str = reserva.get('HoraInicio', '00:00')
            try:
                return datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                try:
                    return datetime.datetime.strptime(fecha_str, "%d/%m/%Y")
                except (ValueError, TypeError):
                    return datetime.datetime.max

        if reservas_a_mostrar:
            # Para activas, ordenar por hora de inicio (las más antiguas activas primero)
            # Para historial, el orden actual (más antiguas primero) también está bien.
            reservas_a_mostrar.sort(key=sort_key_fecha_solicitud, reverse=False)


        if not reservas_a_mostrar and not filtrar_activas:
            if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
                 messagebox.showinfo("Información",
                                    "No hay reservas registradas en el historial.",
                                    parent=self.ventana_ver_reservas_actual)
        else:
            for reserva in reservas_a_mostrar:
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
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas or not self.tree_reservas.winfo_exists(): return
        selected_iids = self.tree_reservas.selection()
        if not selected_iids:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una o más reservas para eliminar.", parent=self.ventana_ver_reservas_actual)
            return

        confirmacion = messagebox.askyesno("Confirmar Eliminación",f"¿Está seguro de que desea eliminar {len(selected_iids)} reserva(s) seleccionada(s)?\nEsta acción no se puede deshacer.",parent=self.ventana_ver_reservas_actual)
        if confirmacion:
            if eliminar_reservas_por_timestamps(list(selected_iids)):
                messagebox.showinfo("Eliminación Exitosa", "Las reservas seleccionadas han sido eliminadas.", parent=self.ventana_ver_reservas_actual)
            else: messagebox.showerror("Error de Eliminación", "Ocurrió un error al intentar eliminar las reservas. Revise la consola.", parent=self.ventana_ver_reservas_actual)

            tipo_vista_filtrada_activas = False
            if self.ventana_ver_reservas_actual and "Activas" in self.ventana_ver_reservas_actual.title():
                tipo_vista_filtrada_activas = True
            self.poblar_treeview_reservas(filtrar_activas=tipo_vista_filtrada_activas)
        
# En app.py, dentro de la clase App

    def poblar_treeview_reservas(self, filtrar_activas: bool = False):
        if not hasattr(self, 'tree_reservas') or not self.tree_reservas or not self.tree_reservas.winfo_exists():
            return

        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)

        reservas_data = cargar_reservas()
        reservas_a_mostrar = []
        ahora = datetime.datetime.now() # Obtener la hora actual una vez

        if filtrar_activas:
            for reserva in reservas_data:
                fecha_reserva_str = reserva.get('FechaSolicitud')
                hora_inicio_str = reserva.get('HoraInicio')
                hora_fin_str = reserva.get('HoraFin')

                if not fecha_reserva_str or not hora_inicio_str or not hora_fin_str:
                    continue

                try:
                    fecha_obj = datetime.datetime.strptime(fecha_reserva_str, "%d/%m/%Y").date()
                    hora_inicio_obj = datetime.datetime.strptime(hora_inicio_str, "%H:%M").time()
                    reserva_dt_inicio = datetime.datetime.combine(fecha_obj, hora_inicio_obj)
                    hora_fin_obj = datetime.datetime.strptime(hora_fin_str, "%H:%M").time()
                    reserva_dt_fin = datetime.datetime.combine(fecha_obj, hora_fin_obj)

                    if reserva_dt_inicio <= ahora < reserva_dt_fin:
                        reservas_a_mostrar.append(reserva)
                except ValueError:
                    continue
            
            if not reservas_a_mostrar and self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
                 messagebox.showinfo("Información",
                                    "No hay reservas activas en este momento.",
                                    parent=self.ventana_ver_reservas_actual)
                 # No retornamos aquí para que la campana suene igualmente, indicando que la actualización se completó.
        else: # Mostrar todas (Historial)
            reservas_a_mostrar = list(reservas_data)

        def sort_key_fecha_solicitud(reserva):
            fecha_str = reserva.get('FechaSolicitud')
            hora_str = reserva.get('HoraInicio', '00:00')
            try:
                return datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                try:
                    return datetime.datetime.strptime(fecha_str, "%d/%m/%Y")
                except (ValueError, TypeError):
                    return datetime.datetime.max

        if reservas_a_mostrar:
            reservas_a_mostrar.sort(key=sort_key_fecha_solicitud, reverse=False)

        # Poblar el treeview
        if reservas_a_mostrar:
            for reserva in reservas_a_mostrar:
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
        elif not filtrar_activas: # Es historial y está vacío después de todo
            if self.ventana_ver_reservas_actual and self.ventana_ver_reservas_actual.winfo_exists():
                 messagebox.showinfo("Información",
                                    "No hay reservas registradas en el historial.",
                                    parent=self.ventana_ver_reservas_actual)
        
        
        # Al final de la función, después de que todas las operaciones de actualización
        # (limpiar, cargar, filtrar, poblar Treeview, o mostrar messageboxes de info)
        # se hayan completado. Esto indica que la acción de "actualizar" del usuario ha terminado.
        if hasattr(self, 'root') and self.root.winfo_exists() and \
           hasattr(self, 'ventana_ver_reservas_actual') and \
           self.ventana_ver_reservas_actual and \
           self.ventana_ver_reservas_actual.winfo_exists():
            # Solo sonar si la ventana donde se actualiza la lista está activa y la raíz existe.
            self.root.bell()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()