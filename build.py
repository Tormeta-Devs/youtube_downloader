import subprocess

def build_executable():
    try:
        # Ejecutar el comando de PyInstaller
        subprocess.run(['pyinstaller', '--onefile', '--windowed', '--add-data', 'FFmpeg;FFmpeg', 'code.py'], check=True)
        print("Empaquetado exitoso.")
    except subprocess.CalledProcessError as e:
        print(f"Error al empaquetar la aplicación: {e}")

if __name__ == '__main__':
    build_executable()
