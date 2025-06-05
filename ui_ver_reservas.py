# ui_ver_reservas.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from data_manager import cargar_reservas, eliminar_reservas_por_timestamps

class VerReservasWindow(tk.Toplevel):
    def __init__(self, parent, titulo_ventana: str, filtrar_activas: bool):
        super().__init__(parent)
        self.parent = parent
        self.filtrar_activas_flag = filtrar_activas # Guardar el estado de filtrado

        self.title(titulo_ventana)
        self.geometry("800x400")
        self.grab_set()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.tree_reservas = None # Inicializar
        self._crear_widgets()
        self.poblar_treeview_reservas()


    def _crear_widgets(self):
        tree_frame = ttk.Frame(self, padding="10")
        tree_frame.pack(expand=True, fill=tk.BOTH)

        column_ids = ("rut_alumno", "nombre_alumno", "sala", "fecha", "hora_inicio", "hora_fin")
        column_headings = ("RUT Alumno", "Nombre Alumno", "Sala", "Fecha Solicitud", "Hora Inicio", "Hora Fin")
        self.tree_reservas = ttk.Treeview(tree_frame, columns=column_ids, show='headings', selectmode='extended')

        for i, col_id in enumerate(column_ids):
            self.tree_reservas.heading(col_id, text=column_headings[i])
            width = 150 if col_id == "nombre_alumno" else 110
            if col_id == "fecha": width = 100
            if col_id == "hora_inicio" or col_id == "hora_fin": width = 80
            anchor = tk.W if col_id == "nombre_alumno" else tk.CENTER
            self.tree_reservas.column(col_id, width=width, anchor=anchor, minwidth=60)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_reservas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        buttons_frame = ttk.Frame(self, padding="10")
        buttons_frame.pack(fill=tk.X)

        btn_actualizar = ttk.Button(buttons_frame, text="Actualizar Lista",
                                    command=self.poblar_treeview_reservas) # Llama sin argumentos
        btn_actualizar.pack(side=tk.LEFT, padx=5)

        if not self.filtrar_activas_flag: # Botón de eliminar solo para historial completo
            btn_eliminar_seleccion = ttk.Button(buttons_frame, text="Eliminar Seleccionadas", command=self._eliminar_reservas_seleccionadas_action)
            btn_eliminar_seleccion.pack(side=tk.LEFT, padx=5)
        
        btn_cerrar = ttk.Button(buttons_frame, text="Cerrar", command=self._on_close)
        btn_cerrar.pack(side=tk.RIGHT, padx=5)

    def poblar_treeview_reservas(self): # El flag de filtrar se usa desde self.filtrar_activas_flag
        if not self.tree_reservas or not self.tree_reservas.winfo_exists():
            return

        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)

        reservas_data = cargar_reservas()
        reservas_a_mostrar = []
        ahora = datetime.datetime.now()

        if self.filtrar_activas_flag:
            for reserva in reservas_data:
                fecha_reserva_str, hora_inicio_str, hora_fin_str = reserva.get('FechaSolicitud'), reserva.get('HoraInicio'), reserva.get('HoraFin')
                if not (fecha_reserva_str and hora_inicio_str and hora_fin_str): continue
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_reserva_str, "%d/%m/%Y").date()
                    reserva_dt_inicio = datetime.datetime.combine(fecha_obj, datetime.datetime.strptime(hora_inicio_str, "%H:%M").time())
                    reserva_dt_fin = datetime.datetime.combine(fecha_obj, datetime.datetime.strptime(hora_fin_str, "%H:%M").time())
                    if reserva_dt_inicio <= ahora < reserva_dt_fin:
                        reservas_a_mostrar.append(reserva)
                except ValueError: continue
            
            if not reservas_a_mostrar:
                 messagebox.showinfo("Información","No hay reservas activas en este momento.", parent=self)
        else:
            reservas_a_mostrar = list(reservas_data)

        def sort_key_fecha_solicitud(reserva):
            fecha_str, hora_str = reserva.get('FechaSolicitud'), reserva.get('HoraInicio', '00:00')
            try: return datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                try: return datetime.datetime.strptime(fecha_str, "%d/%m/%Y")
                except (ValueError, TypeError): return datetime.datetime.max
        
        if reservas_a_mostrar:
            reservas_a_mostrar.sort(key=sort_key_fecha_solicitud, reverse=self.filtrar_activas_flag) 

        if reservas_a_mostrar:
            for reserva in reservas_a_mostrar:
                valores = (reserva.get(k, '') for k in ['RUTAlumno', 'NombreAlumno', 'IDSala', 'FechaSolicitud', 'HoraInicio', 'HoraFin'])
                self.tree_reservas.insert('', tk.END, iid=reserva.get('TimestampReserva'), values=tuple(valores))
        elif not self.filtrar_activas_flag:
             messagebox.showinfo("Información","No hay reservas registradas en el historial.", parent=self)
        
        if self.winfo_exists(): # Solo sonar si la ventana actual existe
            self.bell()


    def _eliminar_reservas_seleccionadas_action(self):
        if not self.tree_reservas or not self.tree_reservas.winfo_exists(): return
        selected_iids = self.tree_reservas.selection()
        if not selected_iids:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una o más reservas para eliminar.", parent=self)
            return
        confirmacion = messagebox.askyesno("Confirmar Eliminación",f"¿Está seguro de que desea eliminar {len(selected_iids)} reserva(s) seleccionada(s)?\nEsta acción no se puede deshacer.",parent=self)
        if confirmacion:
            if eliminar_reservas_por_timestamps(list(selected_iids)):
                messagebox.showinfo("Eliminación Exitosa", "Las reservas seleccionadas han sido eliminadas.", parent=self)
            else: messagebox.showerror("Error de Eliminación", "Ocurrió un error al intentar eliminar las reservas.", parent=self)
            self.poblar_treeview_reservas() # Actualizar la vista

    def _on_close(self):
        self.grab_release()
        self.destroy()
        if hasattr(self.parent, 'ventana_ver_reservas_actual') and self.parent.ventana_ver_reservas_actual == self:
             self.parent.ventana_ver_reservas_actual = None