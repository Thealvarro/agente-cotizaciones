"""
Carga, validación y todo lo que tiene que ver con seguridad de la entrada.

Los datos llegan de una conversación: pueden traer cualquier cosa. Acá se
revisan antes de que toquen una plantilla, un archivo o una fórmula.
"""
import json
import os
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Las pruebas apuntan esto a una carpeta aparte para no tocar los datos reales.
DATOS = Path(os.environ.get("COTIZAR_DATOS", RAIZ)).resolve()
CARPETA_NEGOCIO = DATOS / "mi-negocio"
CARPETA_DOCS = DATOS / "mis-documentos"
ARCHIVO_NEGOCIO = CARPETA_NEGOCIO / "negocio.json"

PREFIJOS = {"cotizacion": "COT", "propuesta": "PROP"}
LOGO_MAX_BYTES = 5 * 1024 * 1024
FIRMAS_IMAGEN = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpg"}
RESERVADOS_WINDOWS = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                      *(f"LPT{i}" for i in range(1, 10))}


class DatosInvalidos(Exception):
    def __init__(self, errores):
        self.errores = errores
        super().__init__("\n".join(errores))


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------ reglas sueltas

def es_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def color_valido(v):
    # Estricto a propósito: el color se inserta dentro de <style>, donde el
    # escape de HTML no protege. Solo #rrggbb.
    return isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) is not None


def texto(errores, obj, clave, donde, requerido=False, maximo=500):
    v = obj.get(clave)
    if v is None or v == "":
        if requerido:
            errores.append(f"{donde}: falta '{clave}'")
        return
    if not isinstance(v, str):
        errores.append(f"{donde}: '{clave}' debe ser texto")
    elif len(v) > maximo:
        errores.append(f"{donde}: '{clave}' supera {maximo} caracteres")


def numero(errores, obj, clave, donde, minimo, maximo, requerido=True):
    v = obj.get(clave)
    if v is None:
        if requerido:
            errores.append(f"{donde}: falta '{clave}'")
        return
    if not es_numero(v):
        errores.append(f"{donde}: '{clave}' debe ser un número sin separadores de miles (ej: 150000 o 1500.5)")
    elif not (minimo <= v <= maximo):
        errores.append(f"{donde}: '{clave}' debe estar entre {minimo} y {maximo}")


def lista_textos(errores, obj, clave, donde, maximo_items=50):
    v = obj.get(clave, [])
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        errores.append(f"{donde}: '{clave}' debe ser una lista de textos")
    elif len(v) > maximo_items:
        errores.append(f"{donde}: '{clave}' tiene más de {maximo_items} elementos")


# ------------------------------------------------------------------ negocio

def validar_negocio(n):
    e = []
    texto(e, n, "nombre", "negocio", requerido=True, maximo=120)
    texto(e, n, "pais", "negocio", maximo=60)
    for clave in ("direccion", "email", "telefono", "web"):
        texto(e, n, clave, "negocio", maximo=200)
    texto(e, n, "datos_pago", "negocio", maximo=1000)
    texto(e, n, "nombre_documento", "negocio", maximo=30)
    texto(e, n, "logo", "negocio", maximo=100)

    idt = n.get("id_tributario", {})
    if not isinstance(idt, dict):
        e.append("negocio: 'id_tributario' debe tener 'etiqueta' y 'valor'")
    else:
        texto(e, idt, "etiqueta", "negocio.id_tributario", maximo=30)
        texto(e, idt, "valor", "negocio.id_tributario", maximo=40)

    if not color_valido(n.get("color_principal")):
        e.append("negocio: 'color_principal' debe tener el formato #rrggbb")
    if n.get("color_acento") and not color_valido(n["color_acento"]):
        e.append("negocio: 'color_acento' debe tener el formato #rrggbb")

    m = n.get("moneda")
    if not isinstance(m, dict):
        e.append("negocio: falta 'moneda'")
    else:
        texto(e, m, "codigo", "negocio.moneda", requerido=True, maximo=3)
        texto(e, m, "simbolo", "negocio.moneda", requerido=True, maximo=4)
        if m.get("decimales") not in (0, 1, 2, 3):
            e.append("negocio.moneda: 'decimales' debe ser 0, 1, 2 o 3")
        if m.get("miles") not in (".", ",", " ", "'"):
            e.append("negocio.moneda: 'miles' debe ser '.', ',', ' ' o '''")
        if m.get("decimal") not in (".", ","):
            e.append("negocio.moneda: 'decimal' debe ser '.' o ','")
        elif m.get("decimal") == m.get("miles"):
            e.append("negocio.moneda: 'miles' y 'decimal' no pueden ser iguales")

    imp = n.get("impuesto")
    if not isinstance(imp, dict):
        e.append("negocio: falta 'impuesto'")
    else:
        texto(e, imp, "nombre", "negocio.impuesto", requerido=True, maximo=20)
        numero(e, imp, "tasa", "negocio.impuesto", 0, 100)

    cond = n.get("condiciones_por_defecto", {})
    if not isinstance(cond, dict):
        e.append("negocio: 'condiciones_por_defecto' debe ser un objeto")
    else:
        for clave in ("pago", "entrega", "notas"):
            texto(e, cond, clave, "negocio.condiciones_por_defecto", maximo=2000)
    return e


def ruta_logo(negocio):
    """Devuelve la ruta del logo validado, o None si no hay. Lanza si es inseguro."""
    nombre = negocio.get("logo")
    if not nombre:
        return None
    ruta = (CARPETA_NEGOCIO / nombre).resolve()
    if CARPETA_NEGOCIO.resolve() not in ruta.parents:
        raise DatosInvalidos(["logo: debe estar dentro de la carpeta mi-negocio"])
    if ruta.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        raise DatosInvalidos(["logo: solo se aceptan PNG o JPG (los SVG pueden traer código)"])
    if not ruta.is_file():
        raise DatosInvalidos([f"logo: no existe el archivo {nombre} en mi-negocio"])
    if ruta.stat().st_size > LOGO_MAX_BYTES:
        raise DatosInvalidos(["logo: pesa más de 5 MB"])
    cabecera = ruta.read_bytes()[:8]
    if not any(cabecera.startswith(f) for f in FIRMAS_IMAGEN):
        raise DatosInvalidos(["logo: el archivo no es realmente un PNG o JPG"])
    return ruta


def cargar_negocio():
    if not ARCHIVO_NEGOCIO.exists():
        raise DatosInvalidos(["negocio: todavía no está configurado (falta mi-negocio/negocio.json)"])
    n = leer_json(ARCHIVO_NEGOCIO)
    errores = validar_negocio(n)
    if errores:
        raise DatosInvalidos(errores)
    ruta_logo(n)
    return n


# ---------------------------------------------------------------- documento

def validar_documento(d):
    e = []
    if d.get("tipo") not in PREFIJOS:
        e.append("documento: 'tipo' debe ser 'cotizacion' o 'propuesta'")
    try:
        date.fromisoformat(d.get("fecha", ""))
    except (TypeError, ValueError):
        e.append("documento: 'fecha' debe tener el formato AAAA-MM-DD")
    numero(e, d, "validez_dias", "documento", 1, 365, requerido=False)
    folio = d.get("folio")
    if folio is not None and (not isinstance(folio, int) or isinstance(folio, bool) or folio < 1):
        e.append("documento: 'folio' debe ser un entero positivo o no venir")

    c = d.get("cliente")
    if not isinstance(c, dict):
        e.append("documento: falta 'cliente'")
    else:
        texto(e, c, "nombre", "cliente", requerido=True, maximo=120)
        for clave in ("empresa", "id_tributario", "email", "telefono", "direccion", "contacto"):
            texto(e, c, clave, "cliente", maximo=200)

    items = d.get("items")
    if not isinstance(items, list) or not items:
        e.append("documento: debe tener al menos un ítem")
    elif len(items) > 200:
        e.append("documento: máximo 200 ítems")
    else:
        for i, it in enumerate(items, 1):
            donde = f"ítem {i}"
            if not isinstance(it, dict):
                e.append(f"{donde}: formato inválido")
                continue
            texto(e, it, "descripcion", donde, requerido=True, maximo=300)
            texto(e, it, "detalle", donde, maximo=1000)
            texto(e, it, "unidad", donde, maximo=20)
            numero(e, it, "cantidad", donde, 0.0001, 1e9)
            numero(e, it, "precio_unitario", donde, 0, 1e13)
            numero(e, it, "descuento_pct", donde, 0, 100, requerido=False)

    numero(e, d, "descuento_global_pct", "documento", 0, 100, requerido=False)
    for clave in ("exento", "precios_incluyen_impuesto"):
        if clave in d and not isinstance(d[clave], bool):
            e.append(f"documento: '{clave}' debe ser true o false")

    cond = d.get("condiciones", {})
    if not isinstance(cond, dict):
        e.append("documento: 'condiciones' debe ser un objeto")
    else:
        for clave in ("pago", "entrega", "notas"):
            texto(e, cond, clave, "condiciones", maximo=2000)

    if d.get("tipo") == "propuesta":
        p = d.get("propuesta")
        if not isinstance(p, dict):
            e.append("propuesta: faltan los contenidos de la propuesta")
        else:
            texto(e, p, "titulo", "propuesta", requerido=True, maximo=120)
            for clave in ("contexto", "solucion", "por_que_nosotros", "proximos_pasos"):
                texto(e, p, clave, "propuesta", maximo=4000)
            lista_textos(e, p, "incluye", "propuesta")
            lista_textos(e, p, "no_incluye", "propuesta")
            etapas = p.get("etapas", [])
            if not isinstance(etapas, list) or len(etapas) > 20:
                e.append("propuesta: 'etapas' debe ser una lista de hasta 20")
            else:
                for i, et in enumerate(etapas, 1):
                    if not isinstance(et, dict):
                        e.append(f"etapa {i}: formato inválido")
                        continue
                    texto(e, et, "nombre", f"etapa {i}", requerido=True, maximo=120)
                    texto(e, et, "duracion", f"etapa {i}", maximo=60)
                    texto(e, et, "descripcion", f"etapa {i}", maximo=1000)
    return e


def completar_documento(d, negocio):
    """Rellena condiciones vacías con las del negocio. No inventa nada más."""
    d = json.loads(json.dumps(d))
    defecto = negocio.get("condiciones_por_defecto", {})
    cond = d.setdefault("condiciones", {})
    for clave in ("pago", "entrega", "notas"):
        if not cond.get(clave) and defecto.get(clave):
            cond[clave] = defecto[clave]
    d.setdefault("validez_dias", defecto.get("validez_dias", 15))
    return d


# ------------------------------------------------------- archivos y folios

def nombre_seguro(texto_libre, maximo=60):
    t = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", texto_libre or "")
    t = re.sub(r"\.{2,}", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" .")[:maximo].strip(" .")
    if not t or t.upper() in RESERVADOS_WINDOWS:
        t = f"cliente {t}".strip()
    return t


def folios_existentes(tipo):
    usados = []
    for ruta in CARPETA_DOCS.glob("*/documento.json"):
        try:
            d = leer_json(ruta)
        except (OSError, ValueError):
            continue
        if d.get("tipo") == tipo and isinstance(d.get("folio"), int):
            usados.append(d["folio"])
    return usados


def _contador():
    ruta = CARPETA_DOCS / "folios.json"
    return ruta, (leer_json(ruta) if ruta.exists() else {})


def proximo_folio(tipo):
    """El folio que tendría el documento, sin reservarlo (para la vista previa)."""
    _, contador = _contador()
    return max([contador.get(tipo, 0), *folios_existentes(tipo)]) + 1


def siguiente_folio(tipo):
    """Reserva el folio. Mira el contador Y los documentos existentes: si alguien
    borra folios.json, igual no se repite un número."""
    ruta, contador = _contador()
    folio = proximo_folio(tipo)
    contador[tipo] = folio
    escribir_json(ruta, contador)
    return folio


def codigo_documento(d):
    return f"{PREFIJOS[d['tipo']]}-{d['folio']:04d}"


def carpeta_documento(d):
    return CARPETA_DOCS / f"{codigo_documento(d)} {nombre_seguro(d['cliente']['nombre'])}"


# ------------------------------------------------------------------- colores

def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def mezclar(h, con, t):
    a, b = _rgb(h), _rgb(con)
    return _hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


def luminancia(h):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def legible_sobre_blanco(h, minimo=4.5):
    """Oscurece un color hasta que se lea como texto sobre fondo blanco."""
    t = 0.0
    color = h
    while contraste(color, "#ffffff") < minimo and t < 1:
        t += 0.05
        color = mezclar(h, "#000000", t)
    return color


def paleta(negocio):
    p = negocio["color_principal"].lower()
    a = (negocio.get("color_acento") or p).lower()
    texto_sobre_p = "#ffffff" if contraste(p, "#ffffff") >= contraste(p, "#161616") else "#161616"
    return {
        "principal": p,
        "sobre_principal": texto_sobre_p,
        "principal_texto": legible_sobre_blanco(p),
        "acento": a,
        "acento_texto": legible_sobre_blanco(a, 3.0),
        "tinte": mezclar(p, "#ffffff", 0.93),
        "tinte_fuerte": mezclar(p, "#ffffff", 0.84),
        "tinta": "#1f2328",
        "tinta_2": "#4a5260",
        "tinta_3": "#747b88",
        "borde": "#e3e5e8",
    }
