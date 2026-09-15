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
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from calculos import calcular
from datos import (CARPETA_BORRADORES, CARPETA_DOCS, RAIZ, TOTAL_MAXIMO, DatosInvalidos,
                   cargar_json_validado, cargar_negocio, carpeta_documento, codigo_de_carpeta,
                   completar_documento, escribir_json, leer_json, proximo_folio, ruta_logo,
                   siguiente_folio, validar_documento)

CARPETA_PAISES = Path(__file__).resolve().parent / "paises.json"
FORMATOS = ("xlsx", "docx", "pdf")


class ArchivoAbierto(Exception):
    pass


def documento_existente(ruta):
    """Si la ruta es el documento.json de uno ya creado, devuelve (tipo, folio) de su carpeta."""
    if ruta.name != "documento.json" or ruta.parent.parent != CARPETA_DOCS:
        return None
    return codigo_de_carpeta(ruta.parent.name)


def cargar_documento(ruta_texto, negocio):
    ruta = Path(ruta_texto)
    if not ruta.is_absolute() and not ruta.exists():
        ruta = RAIZ / ruta
    ruta = ruta.resolve()
    if RAIZ not in ruta.parents:
        raise DatosInvalidos(["archivo: debe estar dentro de la carpeta del proyecto"])
    if not ruta.is_file():
        raise DatosInvalidos([f"archivo: no existe {ruta_texto}"])
    doc = cargar_json_validado(ruta, "archivo")
    errores = validar_documento(doc)
    if errores:
        raise DatosInvalidos(errores)
    doc = completar_documento(doc, negocio)

    existente = documento_existente(ruta)
    if existente:
        # El número y el tipo los manda la carpeta: así no se pisa otro documento.
        tipo, folio = existente
        if doc["tipo"] != tipo or doc.get("folio", folio) != folio:
            raise DatosInvalidos(["documento: a uno ya creado no se le cambia el tipo ni el número. "
                                  "Para eso se crea uno nuevo a partir de este"])
        doc["folio"] = folio
    else:
        doc.pop("folio", None)   # un borrador nunca elige su número

    if calcular(doc, negocio)["total"] >= TOTAL_MAXIMO:
        raise DatosInvalidos(["documento: el total es demasiado grande"])
    return ruta, doc, existente is not None


def imprimir_resumen(vista):
    print(f"{vista['nombre_documento']} {vista['codigo']} · {vista['cliente']['nombre']}")
    print(f"Emisión: {vista['emision']} · Válida hasta: {vista['vence']}")
    print()
    for it in vista["lineas"]:
        desc = f" (desc. {it['descuento_txt']})" if it["descuento_txt"] else ""
        print(f"  {it['n']}. {' '.join(it['descripcion'].split())} — "
              f"{it['cantidad_txt']} × {it['precio_txt']}{desc} = {it['total_txt']}")
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
    if CARPETA_BORRADORES.exists():
        for borrador in sorted(CARPETA_BORRADORES.glob("*.json")):
            print(f"A MEDIAS {borrador.name}")
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
    print("Logo: " + (ruta_logo(n).name if n.get("logo") else "sin logo"))
    return 0


def previa(ruta_texto):
    from contenido import armar
    n = cargar_negocio()
    _, doc, _ = cargar_documento(ruta_texto, n)
    doc.setdefault("folio", proximo_folio(doc["tipo"]))
    imprimir_resumen(armar(doc, n))
    return 0


def crear(ruta_texto):
    from contenido import armar
    import excel
    import pdf
    import word
    modulos = {"xlsx": excel, "docx": word, "pdf": pdf}

    n = cargar_negocio()
    entrada, doc, existente = cargar_documento(ruta_texto, n)
    logo = ruta_logo(n)
    if not existente:
        doc["folio"] = siguiente_folio(doc["tipo"])

    carpeta = carpeta_documento(doc)
    base = carpeta.name
    nombre_anterior = entrada.parent.name if existente else None
    if existente and entrada.parent != carpeta:
        # El cliente cambió de nombre: la carpeta se renombra con él.
        if carpeta.exists():
            raise DatosInvalidos([f"ya existe otra carpeta llamada {base}"])
        try:
            entrada.parent.rename(carpeta)
        except PermissionError:
            raise ArchivoAbierto()
    carpeta.mkdir(parents=True, exist_ok=True)

    vista = armar(doc, n)
    creados, problemas = [], []
    for extension in FORMATOS:
        final = carpeta / f"{base}.{extension}"
        # Primero a un archivo nuevo y recién ahí se reemplaza: si algo falla, la
        # versión anterior sigue intacta. Solo se toca el archivo con este nombre;
        # cualquier otro archivo de la carpeta (una versión firmada, una copia
        # editada) no se toca nunca.
        temporal = carpeta / f"{base}.nuevo.{extension}"
        try:
            modulos[extension].generar(vista, logo, temporal)
            os.replace(temporal, final)
            creados.append(final)
        except PermissionError:
            problemas.append(f"{extension.upper()}: el archivo anterior está abierto en otro programa. "
                             "Hay que cerrarlo y volver a crear")
        except Exception as e:  # un formato que falla no bloquea a los otros
            problemas.append(f"{extension.upper()}: {e}")
        finally:
            temporal.unlink(missing_ok=True)
    escribir_json(carpeta / "documento.json", doc)

    if nombre_anterior and nombre_anterior != base:
        for extension in FORMATOS:
            if (carpeta / f"{base}.{extension}").exists():
                try:
                    (carpeta / f"{nombre_anterior}.{extension}").unlink(missing_ok=True)
                except PermissionError:
                    pass
    if entrada.parent == CARPETA_BORRADORES:
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
    except ArchivoAbierto:
        print("NO SE PUDO: uno de los archivos de este documento está abierto en otro programa "
              "(Word, Excel o un lector de PDF). Hay que cerrarlo y volver a crear.")
        return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv))
