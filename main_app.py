# main_app.py
import sys
import login

def main():
    login.Iniciar()  #Inicia Login

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupción por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
