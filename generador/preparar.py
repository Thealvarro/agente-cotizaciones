"""
Prepara todo lo necesario la primera vez: un entorno de Python aislado dentro
de la carpeta y las tres librerías que usa el generador.

Se aísla en .venv para no tocar el Python del sistema: en Mac y en varios
Linux instalar librerías globales está bloqueado, y así además no hay choques
con otros programas.

    python generador/preparar.py

Al final imprime una línea PYTHON=... con el intérprete que hay que usar.
"""
import subprocess
import sys
import venv
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
VENV = RAIZ / ".venv"
REQUISITOS = RAIZ / "generador" / "requirements.txt"


def python_del_venv():
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def main():
    if sys.version_info < (3, 10):
        print(f"FALTA: se necesita Python 3.10 o superior (este es {sys.version.split()[0]}).")
        return 1

    py = python_del_venv()
    if not py.exists():
        print("Creando el entorno aislado...")
        venv.create(VENV, with_pip=True)

    print("Instalando librerías...")
    r = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
                        "-r", str(REQUISITOS)], capture_output=True, text=True)
    if r.returncode != 0:
        print("FALTA: no se pudieron instalar las librerías.")
        print(r.stderr[-1500:])
        return 1

    print("Revisando...")
    r = subprocess.run([str(py), str(RAIZ / "generador" / "generar.py"), "revisar"])
    print(f"PYTHON={py}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
