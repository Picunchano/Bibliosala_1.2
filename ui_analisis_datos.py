# ui_analisis_datos.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import analysis # El módulo de análisis con las funciones lógicas
from data_manager import cargar_reservas

class AnalisisWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Análisis de Datos de Reservas")
        self.geometry("700x650")
        self.resizable(True, True)
        self.grab_set()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._crear_widgets()

    def _crear_widgets(self):
        main_analysis_frame = ttk.Frame(self, padding="15")
        main_analysis_frame.pack(expand=True, fill=tk.BOTH)

        # --- Sección para ingresar fecha ---
        input_frame = ttk.Frame(main_analysis_frame)
        input_frame.pack(pady=10, fill=tk.X, anchor="n")
        ttk.Label(input_frame, text="Filtrar por Fecha (DD/MM/AAAA):").pack(side=tk.LEFT, padx=(0,5))
        current_date = datetime.datetime.now()
        # Año
        ttk.Label(input_frame, text="Año:").pack(side=tk.LEFT, padx=(5,0))
        self.entry_anio_analisis = ttk.Entry(input_frame, width=6)
        self.entry_anio_analisis.insert(0, str(current_date.year))
        self.entry_anio_analisis.pack(side=tk.LEFT, padx=(0,5))
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
        btn_limpiar_fecha = ttk.Button(input_frame, text="Limpiar Filtros", command=self._limpiar_filtros_fecha_analisis)
        btn_limpiar_fecha.pack(side=tk.LEFT, padx=5)

        # Botones de análisis
        buttons_outer_frame = ttk.Frame(main_analysis_frame)
        buttons_outer_frame.pack(pady=5, fill=tk.X, anchor="n")
        buttons_frame_line1 = ttk.Frame(buttons_outer_frame)
        buttons_frame_line1.pack(fill=tk.X)
        btn_analizar_alumno = ttk.Button(buttons_frame_line1, text="Alumnos Activos (Todos)", command=self._realizar_analisis_alumno)
        btn_analizar_alumno.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        btn_analizar_sala = ttk.Button(buttons_frame_line1, text="Salas Ocupadas (Todas)", command=self._realizar_analisis_sala)
        btn_analizar_sala.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        
        buttons_frame_line2 = ttk.Frame(buttons_outer_frame)
        buttons_frame_line2.pack(fill=tk.X, pady=(5,0))
        btn_total_reservas = ttk.Button(buttons_frame_line2, text="Total Reservas Filtradas", command=self._realizar_analisis_conteo_total)
        btn_total_reservas.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        btn_horarios_activos = ttk.Button(buttons_frame_line2, text="Horarios de Actividad", command=self._realizar_analisis_horarios)
        btn_horarios_activos.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        # Sección para mostrar resultados
        results_frame = ttk.LabelFrame(main_analysis_frame, text="Resultados del Análisis", padding="10")
        results_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        top_results_display_frame = ttk.Frame(results_frame)
        top_results_display_frame.pack(fill=tk.X, expand=False)
        alumnos_frame = ttk.Frame(top_results_display_frame)
        alumnos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(alumnos_frame, text="Alumnos por N° de Solicitudes:").pack(anchor="w")
        self.text_resultado_alumnos = scrolledtext.ScrolledText(alumnos_frame, height=10, width=35, wrap=tk.WORD, state=tk.DISABLED)
        self.text_resultado_alumnos.pack(anchor="w", pady=3, expand=True, fill=tk.BOTH)
        
        salas_frame = ttk.Frame(top_results_display_frame)
        salas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(salas_frame, text="Salas por N° de Solicitudes:").pack(anchor="w")
        self.text_resultado_salas = scrolledtext.ScrolledText(salas_frame, height=10, width=35, wrap=tk.WORD, state=tk.DISABLED)
        self.text_resultado_salas.pack(anchor="w", pady=3, expand=True, fill=tk.BOTH)
        
        bottom_results_display_frame = ttk.Frame(results_frame)
        bottom_results_display_frame.pack(fill=tk.X, expand=False, pady=(10,0))
        horarios_frame = ttk.Frame(bottom_results_display_frame)
        horarios_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(horarios_frame, text="Actividad por Hora:").pack(anchor="w")
        self.text_resultado_horarios = scrolledtext.ScrolledText(horarios_frame, height=10, width=35, wrap=tk.WORD, state=tk.DISABLED)
        self.text_resultado_horarios.pack(anchor="w", pady=3, expand=True, fill=tk.BOTH)

        total_frame = ttk.Frame(bottom_results_display_frame)
        total_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=5, anchor='n')
        self.label_resultado_conteo_total = ttk.Label(total_frame, text="Total Reservas Filtradas: Pendiente...", wraplength=280)
        self.label_resultado_conteo_total.pack(anchor="nw", pady=3)

        self._limpiar_filtros_fecha_analisis() # Poner texto pendiente inicial

        btn_cerrar_analisis = ttk.Button(main_analysis_frame, text="Cerrar Análisis", command=self._on_close)
        btn_cerrar_analisis.pack(pady=15, anchor="s")

    def _actualizar_texto_widget(self, text_widget, content):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete('1.0', tk.END)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def _limpiar_filtros_fecha_analisis(self):
        if hasattr(self, 'entry_dia_analisis'): self.entry_dia_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_mes_analisis'): self.entry_mes_analisis.delete(0, tk.END)
        if hasattr(self, 'entry_anio_analisis'): self.entry_anio_analisis.delete(0, tk.END)
        
        self._actualizar_texto_widget(self.text_resultado_alumnos, "Pendiente...")
        self._actualizar_texto_widget(self.text_resultado_salas, "Pendiente...")
        self.label_resultado_conteo_total.config(text="Total Reservas Filtradas: Pendiente...")
        self._actualizar_texto_widget(self.text_resultado_horarios, "Pendiente...")

    def _obtener_fecha_analisis(self):
        # (Este método es idéntico al que tenías en App, solo cambia el parent de messagebox)
        dia_str = self.entry_dia_analisis.get()
        mes_str = self.entry_mes_analisis.get()
        anio_str = self.entry_anio_analisis.get()
        dia_int, mes_int, anio_int = None, None, None
        error_msg = None
        if anio_str:
            try: val = int(anio_str); anio_int = val if 1900 <= val <= 3000 else error_msg == "Año fuera de rango (1900-3000)."
            except ValueError: error_msg = "Año debe ser un número."
        if mes_str and not error_msg:
            try: val = int(mes_str); mes_int = val if 1 <= val <= 12 else error_msg == "Mes inválido (1-12)."
            except ValueError: error_msg = "Mes debe ser un número."
        if dia_str and not error_msg:
            try: val = int(dia_str); dia_int = val if 1 <= val <= 31 else error_msg == "Día inválido (1-31)."
            except ValueError: error_msg = "Día debe ser un número."
        if not error_msg:
            if dia_int is not None and (mes_int is None or anio_int is None): error_msg = "Para filtrar por día, también se requieren Mes y Año."
            elif mes_int is not None and anio_int is None: error_msg = "Para filtrar por mes, también se requiere Año."
        if error_msg:
            messagebox.showerror("Error en Fecha", error_msg, parent=self) # parent es self (Toplevel)
            return None, None, None, "Error en fecha"
        display_str = "Todos los datos"
        if anio_int is not None:
            if mes_int is not None:
                if dia_int is not None: display_str = f"Fecha: {dia_int:02d}/{mes_int:02d}/{anio_int}"
                else: display_str = f"Mes: {mes_int:02d}/{anio_int}"
            else: 
                if dia_int is not None: display_str = f"Año: {anio_int} (Día ignorado sin Mes)"; dia_int = None 
                else: display_str = f"Año: {anio_int}"
        elif mes_int is not None or dia_int is not None: display_str = "Filtro incompleto (Se requiere Año)"
        return dia_int, mes_int, anio_int, display_str

    def _realizar_analisis_alumno(self):
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        titulo_base = "Alumnos por N° de Solicitudes"
        if display_str == "Error en fecha":
             self._actualizar_texto_widget(self.text_resultado_alumnos, f"{titulo_base} ({display_str}):\nError en fecha.")
             return
        reservas = cargar_reservas()
        if not reservas:
            self._actualizar_texto_widget(self.text_resultado_alumnos, f"{titulo_base} ({display_str}):\nNo hay reservas.")
            return
        lista_alumnos = analysis.alumno_mas_solicitudes(reservas, anio, mes, dia)
        texto = f"{titulo_base} ({display_str}):\n"
        if lista_alumnos: texto += "".join(f"{i+1}. {n} - {c} sol.\n" for i, (n, c) in enumerate(lista_alumnos))
        else: texto += "Sin datos para este criterio."
        self._actualizar_texto_widget(self.text_resultado_alumnos, texto.strip())

    def _realizar_analisis_sala(self):
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        titulo_base = "Salas por N° de Solicitudes"
        if display_str == "Error en fecha":
            self._actualizar_texto_widget(self.text_resultado_salas, f"{titulo_base} ({display_str}):\nError en fecha.")
            return
        reservas = cargar_reservas()
        if not reservas:
            self._actualizar_texto_widget(self.text_resultado_salas, f"{titulo_base} ({display_str}):\nNo hay reservas.")
            return
        lista_salas = analysis.sala_mas_ocupada(reservas, anio, mes, dia)
        texto = f"{titulo_base} ({display_str}):\n"
        if lista_salas: texto += "".join(f"{i+1}. {s} - {c} sol.\n" for i, (s, c) in enumerate(lista_salas))
        else: texto += "Sin datos para este criterio."
        self._actualizar_texto_widget(self.text_resultado_salas, texto.strip())

    def _realizar_analisis_conteo_total(self):
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        if display_str == "Error en fecha":
            self.label_resultado_conteo_total.config(text=f"Total Reservas: Error en fecha")
            return
        reservas = cargar_reservas()
        total = analysis.conteo_reservas_filtradas(reservas, anio, mes, dia)
        self.label_resultado_conteo_total.config(text=f"Total Reservas ({display_str}): {total}.")

    def _realizar_analisis_horarios(self):
        dia, mes, anio, display_str = self._obtener_fecha_analisis()
        titulo_base = "Actividad por Hora"
        if display_str == "Error en fecha":
            self._actualizar_texto_widget(self.text_resultado_horarios, f"{titulo_base} ({display_str}):\nError en fecha.")
            return
        reservas = cargar_reservas()
        if not reservas:
            self._actualizar_texto_widget(self.text_resultado_horarios, f"{titulo_base} ({display_str}):\nNo hay reservas.")
            return
        lista_horarios = analysis.horarios_mas_activos(reservas, anio, mes, dia)
        texto = f"{titulo_base} ({display_str}):\n"
        if lista_horarios: texto += "".join(f"{r_h} - {act} res. activa(s)\n" for r_h, act in lista_horarios)
        else: texto += "Sin actividad para este criterio."
        self._actualizar_texto_widget(self.text_resultado_horarios, texto.strip())

    def _on_close(self):
        self.grab_release()
        self.destroy()
        if hasattr(self.parent, 'ventana_analisis_actual') and self.parent.ventana_analisis_actual == self:
             self.parent.ventana_analisis_actual = None