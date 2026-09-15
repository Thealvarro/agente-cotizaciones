import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "tests" / "_salida"
sys.path.insert(0, str(RAIZ / "generador"))


def carpeta_limpia(nombre):
    """Carpeta de datos aislada para una prueba: nunca toca mi-negocio real."""
    ruta = SALIDA / nombre
    shutil.rmtree(ruta, ignore_errors=True)
    (ruta / "mi-negocio").mkdir(parents=True)
    return ruta


def guardar(ruta, datos):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def generar(carpeta, *argumentos):
    """Corre generar.py como lo corre el agente, apuntando a la carpeta aislada."""
    entorno = {**os.environ, "COTIZAR_DATOS": str(carpeta), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(RAIZ / "generador" / "generar.py"), *argumentos],
                          capture_output=True, text=True, encoding="utf-8", env=entorno, cwd=RAIZ)
