# Preparar el equipo — primera vez

Todo esto lo haces tú. La persona solo aprueba los permisos que le pida Claude.

---

## 1. Python

Corre `generador/preparar.py` con el Python del sistema:

| Sistema | Prueba en este orden |
|---|---|
| Windows | `py -3`, después `python` |
| Mac | `python3` |
| Linux | `python3` |

Necesita **Python 3.10 o superior**. El script lo revisa.

### Si no hay Python

Díselo sin nombrarlo:

> *"Para crear los documentos necesito instalar un programa gratuito. Te va a pedir permiso:
> dile que sí."*

- **Windows:**

  ```
  winget install -e --id Python.Python.3.12 --source winget --accept-source-agreements --accept-package-agreements
  ```

  Las dos últimas opciones son necesarias: sin ellas, la primera vez que se usa `winget` se queda
  esperando una confirmación que nadie ve.

  ⚠️ **No le pidas cerrar y volver a abrir Claude.** El sistema no reconoce el programa recién
  instalado hasta reiniciar, pero no hace falta: úsalo por su ruta completa. Prueba en orden
  `py -3` y estas dos:

  ```
  %LOCALAPPDATA%\Programs\Python\Python312\python.exe
  %ProgramFiles%\Python312\python.exe
  ```

  Si `winget` no existe (Windows muy antiguo), guíalo a https://www.python.org/downloads/ : botón
  amarillo, y al instalar **marcar la primera casilla de abajo** antes de apretar instalar.

- **Mac:** si tiene Homebrew, `brew install python`. Si no, guíalo a
  https://www.python.org/downloads/ y que abra el instalador descargado.

- **Linux:** `sudo apt install python3 python3-venv` o el equivalente de su distribución.

Después vuelve a correr `preparar.py`.

---

## 2. Qué hace preparar.py

1. Crea un entorno aislado en `.venv` dentro de la carpeta. No toca nada del resto del equipo.
2. Instala las tres librerías de `generador/requirements.txt`.
3. Corre `generar.py revisar` y al final imprime `PYTHON=...` con el Python que usarás de ahí en
   adelante.

Si falla la instalación, lee el mensaje. Lo más común es no tener internet o un antivirus
bloqueando. Díselo en una frase y reintenta cuando lo resuelva.

---

## 3. El navegador para el PDF

El PDF se crea con **Google Chrome** o **Microsoft Edge**. Windows trae Edge, así que casi
siempre funciona.

Si `revisar` dice que falta:

> *"Para el PDF necesito Google Chrome. La cotización en Word y en Excel te la hago igual desde
> ya. ¿Quieres instalar Chrome? Es desde google.com/chrome."*

No bloquees el trabajo por esto.
