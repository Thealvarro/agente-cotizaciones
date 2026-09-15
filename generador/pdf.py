"""
PDF: plantilla HTML con escape automático + Chrome o Edge en modo headless.

Se usa el navegador que el usuario ya tiene instalado, así no hay que instalar
motores de PDF que en Windows suelen dar problemas.
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PLANTILLAS = Path(__file__).resolve().parent / "plantillas"

NAVEGADORES = {
    "win32": [
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
        r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
        r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    ],
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ],
    "linux": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"],
}


def buscar_navegador():
    plataforma = "linux" if sys.platform.startswith("linux") else sys.platform
    for candidato in NAVEGADORES.get(plataforma, []):
        ruta = os.path.expanduser(os.path.expandvars(candidato))
        if os.path.isfile(ruta):
            return ruta
        encontrado = shutil.which(candidato)
        if encontrado:
            return encontrado
    return None


def html(vista, ruta_logo):
    # autoescape=True siempre: todo texto del usuario sale escapado.
    entorno = Environment(loader=FileSystemLoader(PLANTILLAS), autoescape=True)
    plantilla = "propuesta.html" if vista["tipo"] == "propuesta" else "cotizacion.html"
    logo_src = ""
    if ruta_logo:
        tipo = "png" if ruta_logo.suffix.lower() == ".png" else "jpeg"
        logo_src = f"data:image/{tipo};base64," + base64.b64encode(ruta_logo.read_bytes()).decode()
    return entorno.get_template(plantilla).render(v=vista, logo_src=logo_src)


def generar(vista, ruta_logo, destino):
    navegador = buscar_navegador()
    if not navegador:
        raise RuntimeError("No encontré Google Chrome ni Microsoft Edge. Hace falta uno de los dos para crear el PDF.")
    destino = Path(destino)
    destino.unlink(missing_ok=True)
    # En Linux, Chromium instalado como snap no puede leer /tmp: se usa la carpeta
    # de destino, que está dentro de la carpeta personal.
    carpeta_tmp = str(destino.parent) if sys.platform.startswith("linux") else None
    with tempfile.TemporaryDirectory(dir=carpeta_tmp, ignore_cleanup_errors=True) as tmp:
        entrada = Path(tmp) / "documento.html"
        entrada.write_text(html(vista, ruta_logo), encoding="utf-8")
        subprocess.run([
            navegador,
            "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--user-data-dir={Path(tmp) / 'perfil'}",   # no choca con el navegador abierto
            "--virtual-time-budget=5000",
            f"--print-to-pdf={destino}",
            entrada.as_uri(),
        ], capture_output=True, timeout=120)
    if not destino.exists() or destino.stat().st_size < 1000:
        raise RuntimeError("El navegador no pudo crear el PDF.")
    return destino
