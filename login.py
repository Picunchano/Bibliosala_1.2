# login.py

import tkinter as tk
from tkinter import messagebox
from user import Usuario

class LoginApp:

    # Propiedades Ventana
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        root.geometry("600x400")

        # Frame contiene etiquetas y boton
        frame = tk.Frame(root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Etiqueta usuario
        tk.Label(frame, text="Usuario").grid(row=0, column=0, padx=10, pady=10)
        self.entry_username = tk.Entry(frame)
        self.entry_username.grid(row=0, column=1)
        self.entry_username.bind("<Return>", self.ENTER)


        # Etiqueta contraseña
        tk.Label(frame, text="Contraseña").grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = tk.Entry(frame, show="*")
        self.entry_password.grid(row=1, column=1)
        self.entry_password.bind("<Return>", self.ENTER)

        # Botón login
        tk.Button(frame, text="Iniciar sesión", command=self.login).grid(row=2, columnspan=2, pady=10)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Creamos el usuario
        user = Usuario(username, password)

        # Verifica usuarios y contraseña
        if not username or not password:
             messagebox.showerror("Error", "Usuario o contraseña vacíos.")
        elif username != "admin" or password != "1234":
             messagebox.showerror("Error", "Usuario o contraseña erróneos.")
        else:
             messagebox.showinfo("Login correcto", f"Bienvenido {username}")

    # ENTER en las etiquetas
    def ENTER(self, event):
        self.login()

# Ejecutar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

