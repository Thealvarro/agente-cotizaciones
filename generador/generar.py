"""
Comando principal. Lo usa el agente; el usuario nunca lo escribe.

    python generador/generar.py revisar            ¿está todo instalado?
    python generador/generar.py paises             países con valores sugeridos
    python generador/generar.py pais "Chile"       valores de un país
    python generador/generar.py negocio            valida mi-negocio/negocio.json
    python generador/generar.py previa ARCHIVO     totales calculados, sin crear nada
    python generador/generar.py crear ARCHIVO      crea PDF, Word y Excel
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from datos import (CARPETA_DOCS, RAIZ, DatosInvalidos, carpeta_documento, cargar_negocio,
                   codigo_documento, completar_documento, escribir_json, leer_json,
                   nombre_seguro, proximo_folio, ruta_logo, siguiente_folio, validar_documento)

CARPETA_PAISES = Path(__file__).resolve().parent / "paises.json"


def cargar_documento(ruta_texto, negocio):
    ruta = Path(ruta_texto)
    if not ruta.is_absolute() and not ruta.exists():
        ruta = RAIZ / ruta
    ruta = ruta.resolve()
    if RAIZ not in ruta.parents:
        raise DatosInvalidos(["archivo: debe estar dentro de la carpeta del proyecto"])
    if not ruta.is_file():
        raise DatosInvalidos([f"archivo: no existe {ruta_texto}"])
    try:
        doc = leer_json(ruta)
    except ValueError as e:
        raise DatosInvalidos([f"archivo: no es un JSON válido ({e})"])
    errores = validar_documento(doc)
    if errores:
        raise DatosInvalidos(errores)
    return ruta, completar_documento(doc, negocio)


def imprimir_resumen(vista):
    print(f"{vista['nombre_documento']} {vista['codigo']} · {vista['cliente']['nombre']}")
    print(f"Emisión: {vista['emision']} · Válida hasta: {vista['vence']}")
    print()
    for it in vista["lineas"]:
        desc = f" (desc. {it['descuento_txt']})" if it["descuento_txt"] else ""
        print(f"  {it['n']}. {' '.join(it['descripcion'].split())} — {it['cantidad_txt']} × {it['precio_txt']}{desc} = {it['total_txt']}")
    print()
    for t in vista["totales"]:
        print(f"  {t['etiqueta']}: {t['texto']}")
    if vista["nota_impuesto"]:
        print(f"  ({vista['nota_impuesto']})")


# ------------------------------------------------------------------ comandos

def revisar():
    ok = True
    try:
        import jinja2, docx, xlsxwriter  # noqa: F401
        print("OK librerías instaladas")
    except ImportError as e:
        ok = False
        print(f"FALTA librerías: {e.name}. Correr: python generador/preparar.py")
    from pdf import buscar_navegador
    nav = buscar_navegador()
    if nav:
        print(f"OK navegador para PDF: {nav}")
    else:
        ok = False
        print("FALTA navegador: instalar Google Chrome (https://www.google.com/chrome/)")
    try:
        n = cargar_negocio()
        print(f"OK negocio configurado: {n['nombre']}")
    except DatosInvalidos as e:
        print("PENDIENTE negocio: " + "; ".join(e.errores))
    return 0 if ok else 1


def paises():
    for nombre in leer_json(CARPETA_PAISES):
        if not nombre.startswith("_"):
            print(nombre)
    return 0


def pais(nombre):
    datos = leer_json(CARPETA_PAISES)
    if nombre not in datos or nombre.startswith("_"):
        print(f"Sin valores sugeridos para '{nombre}'. Preguntar moneda, impuesto e identificación al usuario.")
        return 1
    print(json.dumps(datos[nombre], ensure_ascii=False, indent=2))
    return 0


def negocio():
    n = cargar_negocio()
    print(f"OK {n['nombre']} · {n.get('pais', '')}")
    print(f"Moneda {n['moneda']['codigo']} · {n['impuesto']['nombre']} {n['impuesto']['tasa']}%"
          + (" incluido en los precios" if n["impuesto"].get("incluido_en_precios") else ""))
    print("Logo: " + (str(ruta_logo(n).name) if n.get("logo") else "sin logo"))
    return 0


def previa(ruta_texto):
    from contenido import armar
    n = cargar_negocio()
    _, doc = cargar_documento(ruta_texto, n)
    if doc.get("folio") is None:
        doc["folio"] = proximo_folio(doc["tipo"])
    imprimir_resumen(armar(doc, n))
    return 0


def crear(ruta_texto):
    from contenido import armar
    import excel
    import pdf
    import word

    n = cargar_negocio()
    entrada, doc = cargar_documento(ruta_texto, n)
    logo = ruta_logo(n)
    if doc.get("folio") is None:
        doc["folio"] = siguiente_folio(doc["tipo"])

    carpeta = carpeta_documento(doc)
    # Si se regenera un documento cuyo cliente cambió de nombre, se mueve su carpeta.
    if entrada.name == "documento.json" and entrada.parent.parent == CARPETA_DOCS and entrada.parent != carpeta:
        if not carpeta.exists():
            entrada.parent.rename(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    for viejo in [*carpeta.glob("*.pdf"), *carpeta.glob("*.docx"), *carpeta.glob("*.xlsx")]:
        viejo.unlink()
    escribir_json(carpeta / "documento.json", doc)

    vista = armar(doc, n)
    base = f"{codigo_documento(doc)} {nombre_seguro(doc['cliente']['nombre'])}"
    creados, problemas = [], []
    for extension, modulo in (("xlsx", excel), ("docx", word), ("pdf", pdf)):
        destino = carpeta / f"{base}.{extension}"
        try:
            modulo.generar(vista, logo, destino)
            creados.append(destino)
        except Exception as e:  # un formato que falla no bloquea a los otros
            problemas.append(f"{extension.upper()}: {e}")

    borradores = CARPETA_DOCS / "borradores"
    if entrada.parent == borradores:
        entrada.unlink(missing_ok=True)

    imprimir_resumen(vista)
    print()
    print(f"Carpeta: {carpeta}")
    for ruta in creados:
        print(f"  CREADO {ruta.name}")
    for p in problemas:
        print(f"  NO SE PUDO {p}")
    return 0 if not problemas else 3


def main(argv):
    comandos = {"revisar": (revisar, 0), "paises": (paises, 0), "pais": (pais, 1),
                "negocio": (negocio, 0), "previa": (previa, 1), "crear": (crear, 1)}
    if len(argv) < 2 or argv[1] not in comandos:
        print(__doc__)
        return 1
    funcion, argumentos = comandos[argv[1]]
    if len(argv) - 2 != argumentos:
        print(__doc__)
        return 1
    try:
        return funcion(*argv[2:])
    except DatosInvalidos as e:
        print("NO SE PUDO. Datos a corregir:")
        for error in e.errores:
            print(f"  - {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
