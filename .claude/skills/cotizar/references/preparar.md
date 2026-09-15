# Preparar el equipo — primera vez

Todo esto lo haces tú. El usuario solo aprueba los permisos que le pida Claude.

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

Díselo sin tecnicismos:

> *"Para crear los documentos necesito instalar un programa que se llama Python. Es gratis y
> seguro. ¿Lo instalo?"*

Con su permiso:

- **Windows:** `winget install -e --id Python.Python.3.12`. Si `winget` no existe, guíalo a
  https://www.python.org/downloads/ : botón amarillo de descarga, y al instalar **marcar la
  casilla "Add python.exe to PATH"**. Después hay que cerrar y volver a abrir Claude para que lo
  reconozca.
- **Mac:** si tiene Homebrew, `brew install python`. Si no, guíalo a
  https://www.python.org/downloads/ y que abra el instalador descargado.
- **Linux:** `sudo apt install python3 python3-venv` (o el equivalente de su distribución).

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

El PDF se crea con **Google Chrome** o **Microsoft Edge**, el que tenga. Windows trae Edge, así
que casi siempre funciona.

Si `revisar` dice que falta:

> *"Para el PDF necesito Google Chrome. El Word y el Excel te los puedo hacer igual desde ya.
> ¿Quieres instalar Chrome? Es desde google.com/chrome."*

No bloquees el trabajo por esto: sigue con Word y Excel.
