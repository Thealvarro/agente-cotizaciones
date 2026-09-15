"""
Montos, impuestos, formato de moneda y fechas.

Toda cifra que aparece en un documento sale de acá. El agente conversacional
nunca calcula ni formatea montos: si lo hiciera, un error de redondeo quedaría
como compromiso comercial con el cliente, y el PDF, el Word y el Excel podrían
mostrar totales distintos.

Se usa Decimal y redondeo "half up" en cada paso, igual que la función ROUND de
Excel, para que las fórmulas del .xlsx den exactamente los mismos valores.
"""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def redondear(valor, decimales):
    return Decimal(valor).quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)


def precios_incluyen_impuesto(documento, negocio):
    """El documento puede decidir distinto que el negocio: si el usuario dicta
    precios con impuesto, se marca acá en vez de que el modelo haga la división."""
    return documento.get("precios_incluyen_impuesto", negocio["impuesto"].get("incluido_en_precios", False))


def calcular(documento, negocio):
    """Devuelve las líneas y los totales ya redondeados."""
    dec = negocio["moneda"]["decimales"]
    tasa = Decimal(str(negocio["impuesto"]["tasa"])) / 100
    exento = documento.get("exento", False)
    incluido = precios_incluyen_impuesto(documento, negocio)

    lineas = []
    for item in documento["items"]:
        cantidad = Decimal(str(item["cantidad"]))
        # El precio se redondea a la moneda ANTES de multiplicar: así lo que se ve
        # ("3 × $1.501") es exactamente lo que se calcula, y cualquiera lo puede verificar.
        precio = redondear(Decimal(str(item["precio_unitario"])), dec)
        desc = Decimal(str(item.get("descuento_pct", 0))) / 100
        total_linea = redondear(cantidad * precio * (1 - desc), dec)
        lineas.append({**item, "precio_unitario": precio, "total": total_linea})

    subtotal = sum((l["total"] for l in lineas), Decimal(0))
    desc_global_pct = Decimal(str(documento.get("descuento_global_pct", 0))) / 100
    descuento = redondear(subtotal * desc_global_pct, dec)
    base = subtotal - descuento

    if exento or tasa == 0:
        neto, impuesto, total = base, Decimal(0), base
    elif incluido:
        # Los precios ya traen el impuesto: se desglosa hacia atrás.
        total = base
        neto = redondear(total / (1 + tasa), dec)
        impuesto = total - neto
    else:
        neto = base
        impuesto = redondear(neto * tasa, dec)
        total = neto + impuesto

    return {
        "lineas": lineas,
        "subtotal": subtotal,
        "descuento": descuento,
        "neto": neto,
        "impuesto": impuesto,
        "total": total,
    }


def formato_numero(valor, moneda):
    dec = moneda["decimales"]
    texto = f"{redondear(valor, dec):,.{dec}f}"          # 1,234,567.89
    entero, _, fraccion = texto.partition(".")
    entero = entero.replace(",", moneda["miles"])
    return entero + (moneda["decimal"] + fraccion if dec else "")


def formato_moneda(valor, moneda):
    numero = formato_numero(valor, moneda)
    if moneda.get("simbolo_despues"):
        return f"{numero} {moneda['simbolo']}"
    return f"{moneda['simbolo']}{numero}" if len(moneda["simbolo"]) == 1 else f"{moneda['simbolo']} {numero}"


def formato_cantidad(valor, moneda):
    """2 -> '2' · 2.5 -> '2,5' o '2.5' según el separador decimal del país."""
    texto = f"{Decimal(str(valor)).normalize():f}"
    return texto.replace(".", moneda["decimal"])


def formato_pct(valor, moneda):
    return formato_cantidad(valor, moneda) + "%"


def decimales_de(valor):
    """Cuántos decimales tiene un número tal como se escribió: 12.5 -> 1."""
    return max(0, -Decimal(str(valor)).normalize().as_tuple().exponent)


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def fechas(documento):
    emision = date.fromisoformat(documento["fecha"])
    vence = emision + timedelta(days=int(documento.get("validez_dias", 15)))
    return emision, vence
