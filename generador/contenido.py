"""
Arma una sola "vista" del documento: los textos ya formateados y los montos
ya calculados. El PDF, el Word y el Excel leen de acá y de ningún otro lado,
así que no pueden mostrar cifras distintas entre sí.
"""
from calculos import (calcular, fechas, fecha_larga, formato_moneda,
                      formato_cantidad, formato_pct, precios_incluyen_impuesto)
from datos import codigo_documento, paleta

AVISO = "Documento comercial. No constituye factura ni documento tributario."


def parrafos(texto):
    if not texto:
        return []
    return [p.strip() for p in texto.replace("\r\n", "\n").split("\n\n") if p.strip()]


def armar(documento, negocio):
    moneda = negocio["moneda"]
    imp = negocio["impuesto"]
    calc = calcular(documento, negocio)
    emision, vence = fechas(documento)
    dinero = lambda v: formato_moneda(v, moneda)

    items = []
    hay_desc_linea = False
    for n, l in enumerate(calc["lineas"], 1):
        desc = l.get("descuento_pct", 0) or 0
        hay_desc_linea = hay_desc_linea or desc > 0
        items.append({
            "n": n,
            "descripcion": l["descripcion"],
            "detalle": l.get("detalle", ""),
            "unidad": l.get("unidad", ""),
            "cantidad": l["cantidad"],
            "precio_unitario": l["precio_unitario"],
            "descuento_pct": desc,
            "total": l["total"],
            "cantidad_txt": formato_cantidad(l["cantidad"], moneda),
            "precio_txt": dinero(l["precio_unitario"]),
            "descuento_txt": formato_pct(desc, moneda) if desc else "",
            "total_txt": dinero(l["total"]),
        })

    exento = documento.get("exento", False)
    incluido = precios_incluyen_impuesto(documento, negocio)
    con_impuesto = not exento and imp["tasa"] > 0
    desc_global = documento.get("descuento_global_pct", 0) or 0

    totales = []
    # Subtotal solo cuando hay descuento: sin descuento repetiría la línea de abajo.
    if desc_global:
        totales.append({"clave": "subtotal", "etiqueta": "Subtotal", "valor": calc["subtotal"]})
        totales.append({"clave": "descuento", "etiqueta": f"Descuento {formato_pct(desc_global, moneda)}",
                        "valor": -calc["descuento"]})
    if con_impuesto:
        totales.append({"clave": "neto", "etiqueta": "Neto", "valor": calc["neto"]})
        etiqueta_imp = f"{imp['nombre']} {formato_pct(imp['tasa'], moneda)}" + (" incluido" if incluido else "")
        totales.append({"clave": "impuesto", "etiqueta": etiqueta_imp, "valor": calc["impuesto"]})
    totales.append({"clave": "total", "etiqueta": "Total", "valor": calc["total"]})
    for t in totales:
        t["texto"] = dinero(abs(t["valor"])) if t["valor"] >= 0 else "−" + dinero(-t["valor"])

    cond = documento.get("condiciones", {})
    condiciones = [(et, cond[k]) for k, et in
                   (("pago", "Forma de pago"), ("entrega", "Plazo de entrega"), ("notas", "Notas"))
                   if cond.get(k)]
    if negocio.get("datos_pago"):
        condiciones.append(("Datos para el pago", negocio["datos_pago"]))

    tipo = documento["tipo"]
    nombre_doc = "Propuesta" if tipo == "propuesta" else (negocio.get("nombre_documento") or "Cotización")
    idt = negocio.get("id_tributario", {})

    vista = {
        "tipo": tipo,
        "codigo": codigo_documento(documento),
        "nombre_documento": nombre_doc,
        "emision": fecha_larga(emision),
        "vence": fecha_larga(vence),
        "negocio": {
            "nombre": negocio["nombre"],
            "id_etiqueta": idt.get("etiqueta", ""),
            "id_valor": idt.get("valor", ""),
            **{k: negocio.get(k, "") for k in ("direccion", "email", "telefono", "web")},
        },
        "cliente": documento["cliente"],
        "lineas": items,
        "hay_desc_linea": hay_desc_linea,
        "totales": totales,
        "total_txt": dinero(calc["total"]),
        "exento": exento,
        "incluido": incluido,
        "nota_impuesto": f"Exento de {imp['nombre']}" if exento else "",
        "nota_total": (f"Exento de {imp['nombre']}" if exento else
                       f"Incluye {imp['nombre']} {formato_pct(imp['tasa'], moneda)}" if con_impuesto else ""),
        "condiciones": condiciones,
        "aviso": AVISO,
        "moneda": moneda,
        "impuesto": imp,
        "descuento_global_pct": desc_global,
        "calc": calc,
        "colores": paleta(negocio),
    }

    if tipo == "propuesta":
        p = documento["propuesta"]
        vista["propuesta"] = {
            "titulo": p["titulo"],
            "contexto": parrafos(p.get("contexto")),
            "solucion": parrafos(p.get("solucion")),
            "incluye": p.get("incluye", []),
            "no_incluye": p.get("no_incluye", []),
            "etapas": p.get("etapas", []),
            "por_que_nosotros": parrafos(p.get("por_que_nosotros")),
            "proximos_pasos": parrafos(p.get("proximos_pasos")),
        }
    return vista
