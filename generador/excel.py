"""
Excel (.xlsx) con fórmulas reales y el valor ya calculado guardado en cada una.

Por qué las dos cosas: las vistas previas del correo y del celular no
recalculan fórmulas y mostrarían los totales vacíos. Con el valor guardado se
ve bien en cualquier lado, y si alguien cambia una cantidad en Excel el total
se recalcula igual.

Seguridad: todo texto del usuario se escribe como texto con write_string. Una
celda que empiece con "=" jamás se convierte en fórmula.
"""
import math
import re
import struct
from decimal import Decimal

import xlsxwriter

FUENTE = "Arial"


def tamano_imagen(ruta):
    datos = ruta.read_bytes()
    if datos.startswith(b"\x89PNG"):
        return struct.unpack(">II", datos[16:24])
    i = 2
    while i < len(datos) - 9:
        if datos[i] != 0xFF:
            i += 1
            continue
        marca = datos[i + 1]
        if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):
            alto, ancho = struct.unpack(">HH", datos[i + 5:i + 9])
            return ancho, alto
        i += 2 + struct.unpack(">H", datos[i + 2:i + 4])[0]
    return 200, 60


def formato_moneda(moneda):
    s = moneda["simbolo"].replace('"', "")
    cuerpo = "#,##0" + ("." + "0" * moneda["decimales"] if moneda["decimales"] else "")
    pos = f'{cuerpo} "{s}"' if moneda.get("simbolo_despues") else (f'"{s}"{cuerpo}' if len(s) == 1 else f'"{s} "{cuerpo}')
    return f"{pos};-{pos}"


def filas_de(texto, caracteres_por_linea):
    if not texto:
        return 1
    return sum(max(1, math.ceil(len(linea) / caracteres_por_linea)) for linea in texto.split("\n"))


class Libro:
    def __init__(self, destino, vista):
        self.v = vista
        self.c = vista["colores"]
        self.wb = xlsxwriter.Workbook(str(destino), {
            "strings_to_formulas": False,
            "strings_to_urls": False,
            "strings_to_numbers": False,
        })
        self.dec = vista["moneda"]["decimales"]
        self.fmt_dinero = formato_moneda(vista["moneda"])
        self._cache = {}

    def f(self, **props):
        clave = tuple(sorted(props.items()))
        if clave not in self._cache:
            base = {"font_name": FUENTE, "font_size": 9.5, "valign": "top", "font_color": self.c["tinta"]}
            base.update(props)
            self._cache[clave] = self.wb.add_format(base)
        return self._cache[clave]

    def hoja(self, nombre, anchos):
        ws = self.wb.add_worksheet(nombre)
        ws.hide_gridlines(2)
        ws.set_paper(9)
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_margins(left=0.5, right=0.5, top=0.6, bottom=0.7)
        ws.center_horizontally()
        ws.set_footer(f"&L&8{self.v['codigo']}&R&8Página &P de &N")
        for col, ancho in enumerate(anchos):
            ws.set_column(col, col, ancho)
        return ws

    # ------------------------------------------------------------ bloques

    def encabezado(self, ws, ruta_logo, ultima_col):
        n, c = self.v["negocio"], self.c
        ws.set_row(0, 22)
        if ruta_logo:
            ancho, alto = tamano_imagen(ruta_logo)
            escala = 58 / alto if alto else 1
            if ancho * escala > 230:
                escala = 230 / ancho
            ws.insert_image(0, 0, str(ruta_logo), {"x_scale": escala, "y_scale": escala,
                                                   "x_offset": 2, "y_offset": 4, "object_position": 3})
        else:
            ws.write_string(0, 0, n["nombre"], self.f(bold=True, font_size=16, font_color=c["principal_texto"]))

        lineas = [(n["nombre"], True)] if ruta_logo else []
        if n["id_valor"]:
            lineas.append((f"{n['id_etiqueta']} {n['id_valor']}", False))
        for dato in (n["direccion"], " · ".join(x for x in (n["email"], n["telefono"]) if x), n["web"]):
            if dato:
                lineas.append((dato, False))
        for i, (texto, negrita) in enumerate(lineas):
            ws.merge_range(i, ultima_col - 2, i, ultima_col, "", self.f())
            ws.write_string(i, ultima_col - 2, texto,
                            self.f(align="right", bold=negrita, font_size=9.5 if negrita else 8,
                                   font_color=c["tinta"] if negrita else c["tinta_2"]))
        fila = max(len(lineas), 4) + 1
        ws.set_row(fila, 3)
        for col in range(ultima_col + 1):
            ws.write_blank(fila, col, None, self.f(bg_color=c["principal"]))
        return fila + 2

    def titulo(self, ws, fila, titulo, subtitulo, ultima_col):
        c = self.c
        ws.set_row(fila, 30)
        ws.merge_range(fila, 0, fila, 3, "", self.f())
        ws.write_string(fila, 0, titulo, self.f(bold=True, font_size=20, valign="bottom"))
        ws.write_string(fila + 1, 0, subtitulo, self.f(bold=True, font_size=9, font_color=c["acento_texto"]))
        for i, (etiqueta, fecha, alineacion) in enumerate((("EMISIÓN", self.v["emision"], "bottom"),
                                                          ("VÁLIDA HASTA", self.v["vence"], "top"))):
            ws.write_string(fila + i, ultima_col - 2, etiqueta,
                            self.f(bold=True, font_size=7, font_color=c["acento_texto"], align="right",
                                   valign=alineacion))
            valor = self.f(align="right", valign=alineacion, font_size=9)
            ws.merge_range(fila + i, ultima_col - 1, fila + i, ultima_col, "", valor)
            ws.write_string(fila + i, ultima_col - 1, fecha, valor)
        return fila + 3

    def rotulo(self, ws, fila, col, texto):
        ws.write_string(fila, col, texto.upper(), self.f(bold=True, font_size=7, font_color=self.c["acento_texto"]))

    def cliente_y_total(self, ws, fila, ultima_col):
        cl, c = self.v["cliente"], self.c
        self.rotulo(ws, fila, 0, "Para")
        ws.merge_range(fila + 1, 0, fila + 1, 2, "", self.f())
        ws.write_string(fila + 1, 0, cl["nombre"], self.f(bold=True, font_size=11))
        datos = [cl.get("empresa")]
        if cl.get("id_tributario"):
            datos.append(f"{self.v['negocio']['id_etiqueta'] or 'ID'} {cl['id_tributario']}")
        if cl.get("contacto"):
            datos.append(f"Atención: {cl['contacto']}")
        datos += [" · ".join(x for x in (cl.get("email"), cl.get("telefono")) if x), cl.get("direccion")]
        datos = [d for d in datos if d]
        for i, d in enumerate(datos):
            ws.merge_range(fila + 2 + i, 0, fila + 2 + i, 2, "", self.f())
            ws.write_string(fila + 2 + i, 0, d, self.f(font_size=8.5, font_color=c["tinta_2"]))

        caja = self.f(bg_color=c["tinte"])
        for r in range(fila, fila + 4):
            for col in range(ultima_col - 1, ultima_col + 1):
                ws.write_blank(r, col, None, caja)
        ws.write_string(fila, ultima_col - 1, "TOTAL", self.f(bold=True, font_size=7, font_color=c["acento_texto"],
                                                             bg_color=c["tinte"]))
        ws.set_row(fila + 1, 26)
        self.celda_total_resumen = (fila + 1, ultima_col - 1, ultima_col)
        nota = self.v["nota_total"]
        if nota:
            ws.merge_range(fila + 2, ultima_col - 1, fila + 2, ultima_col, "", caja)
            ws.write_string(fila + 2, ultima_col - 1, nota, self.f(font_size=7.5, font_color=c["tinta_3"],
                                                                  bg_color=c["tinte"]))
        return fila + max(len(datos) + 2, 4) + 2

    def items(self, ws, fila):
        c = self.c
        cab = self.f(bold=True, font_size=7.5, font_color=c["sobre_principal"], bg_color=c["principal"],
                     valign="vcenter")
        cab_der = self.f(bold=True, font_size=7.5, font_color=c["sobre_principal"], bg_color=c["principal"],
                         valign="vcenter", align="right")
        ws.set_row(fila, 20)
        for col, (titulo, derecha) in enumerate((("#", False), ("DESCRIPCIÓN", False), ("UNIDAD", False),
                                                 ("CANT.", True), ("PRECIO UNIT.", True), ("DESC.", True),
                                                 ("TOTAL", True))):
            ws.write_string(fila, col, titulo, cab_der if derecha else cab)

        borde = {"bottom": 1, "bottom_color": c["borde"]}
        dinero = self.f(num_format=self.fmt_dinero, align="right", **borde)
        primera = fila + 1
        for i, it in enumerate(self.v["lineas"]):
            r = primera + i
            ws.write_number(r, 0, it["n"], self.f(font_color=c["tinta_3"], font_size=8.5, align="left", **borde))
            celda_desc = self.f(text_wrap=True, **borde)
            if it["detalle"]:
                ws.write_rich_string(r, 1, self.f(bold=True), it["descripcion"], "\n",
                                     self.f(font_size=8, font_color=c["tinta_3"]), it["detalle"], celda_desc)
            else:
                ws.write_string(r, 1, it["descripcion"], self.f(bold=True, text_wrap=True, **borde))
            ws.write_string(r, 2, it["unidad"], self.f(font_color=c["tinta_3"], **borde))
            ws.write_number(r, 3, float(it["cantidad"]), self.f(align="right", **borde))
            ws.write_number(r, 4, float(it["precio_unitario"]), dinero)
            pct = float(it["descuento_pct"]) / 100
            ws.write_number(r, 5, pct, self.f(num_format='0%;-0%;""' if float(it["descuento_pct"]).is_integer()
                                              else '0.0%;-0.0%;""', align="right", **borde))
            ws.write_formula(r, 6, f"=ROUND(D{r + 1}*E{r + 1}*(1-F{r + 1}),{self.dec})", dinero,
                             float(it["total"]))
            lineas = filas_de(it["descripcion"], 48) + (filas_de(it["detalle"], 56) if it["detalle"] else 0)
            ws.set_row(r, max(18, 13 * lineas + 5))
        return primera, primera + len(self.v["lineas"]) - 1

    def totales(self, ws, fila, desde, hasta):
        v, c = self.v, self.c
        imp = v["impuesto"]
        tasa = Decimal(str(imp["tasa"])) / 100
        incluido = v["incluido"]
        pct = Decimal(str(v["descuento_global_pct"] or 0)) / 100
        ref, d = {}, self.dec
        items = f"SUM(G{desde + 1}:G{hasta + 1})"

        for i, t in enumerate(v["totales"]):
            r = fila + i
            ref[t["clave"]] = f"G{r + 1}"
            base = ref.get("subtotal", items) + (f"+{ref['descuento']}" if "descuento" in ref else "")
            formula = {
                "subtotal": f"={items}",
                "descuento": f"=-ROUND({ref.get('subtotal')}*{pct},{d})",
                "neto": f"=ROUND(({base})/(1+{tasa}),{d})" if incluido else f"={base}",
                "impuesto": f"=({base})-{ref.get('neto')}" if incluido else f"=ROUND({ref.get('neto')}*{tasa},{d})",
                "total": f"={base}" if (incluido or "impuesto" not in ref) else f"={ref['neto']}+{ref['impuesto']}",
            }[t["clave"]]

            es_total = t["clave"] == "total"
            if es_total:
                ws.set_row(r, 22)
                eti = self.f(bold=True, font_size=11, font_color=c["sobre_principal"], bg_color=c["principal"],
                             valign="vcenter")
                num = self.f(bold=True, font_size=11, font_color=c["sobre_principal"], bg_color=c["principal"],
                             valign="vcenter", align="right", num_format=self.fmt_dinero)
            else:
                borde = {"bottom": 1, "bottom_color": c["borde"]}
                eti = self.f(font_color=c["tinta_2"], **borde)
                num = self.f(align="right", num_format=self.fmt_dinero, **borde)
            ws.merge_range(r, 4, r, 5, "", eti)
            ws.write_string(r, 4, t["etiqueta"], eti)
            ws.write_formula(r, 6, formula, num, float(t["valor"]))

        fr, c1, c2 = self.celda_total_resumen
        ws.merge_range(fr, c1, fr, c2, "", self.f())
        ws.write_formula(fr, c1, f"={ref['total']}",
                         self.f(bold=True, font_size=16, font_color=c["principal_texto"], bg_color=c["tinte"],
                                num_format=self.fmt_dinero, align="left", valign="vcenter"),
                         float(v["calc"]["total"]))
        return fila + len(v["totales"])

    def condiciones(self, ws, fila, ultima_fila_totales):
        c = self.c
        bloques = [("Validez", f"Esta oferta es válida hasta el {self.v['vence']}.")] + list(self.v["condiciones"])
        for etiqueta, texto in bloques:
            self.rotulo(ws, fila, 0, etiqueta)
            ws.merge_range(fila + 1, 0, fila + 1, 3, "", self.f())
            ws.write_string(fila + 1, 0, texto, self.f(text_wrap=True, font_size=8.8, font_color=c["tinta_2"]))
            ws.set_row(fila + 1, max(15, 12.5 * filas_de(texto, 80) + 4))
            fila += 3
        return max(fila, ultima_fila_totales + 1)

    def cierre(self, ws, fila):
        c = self.c
        fila += 2
        linea = self.f(top=1, top_color=c["tinta_3"], font_size=7.5, font_color=c["tinta_3"])
        ws.merge_range(fila, 0, fila, 2, "", linea)
        ws.write_string(fila, 0, "Nombre y firma de aceptación", linea)
        ws.merge_range(fila, 4, fila, 6, "", linea)
        ws.write_string(fila, 4, "Fecha", linea)
        ws.merge_range(fila + 2, 0, fila + 2, 6, "", self.f())
        ws.write_string(fila + 2, 0, self.v["aviso"], self.f(font_size=7.5, font_color=c["tinta_3"], align="center"))

    def bloque_texto(self, ws, fila, titulo, parrafos):
        self.rotulo(ws, fila, 0, titulo)
        fila += 1
        for p in parrafos:
            ws.merge_range(fila, 0, fila, 3, "", self.f())
            ws.write_string(fila, 0, p, self.f(text_wrap=True, font_size=9.3, font_color=self.c["tinta_2"]))
            ws.set_row(fila, max(15, 13 * filas_de(p, 95) + 4))
            fila += 1
        return fila + 1

    # --------------------------------------------------------- hojas

    def hoja_economica(self, nombre, ruta_logo, titulo, subtitulo):
        ws = self.hoja(nombre, [4.5, 44, 8, 8, 15, 8, 17])
        fila = self.encabezado(ws, ruta_logo, 6)
        fila = self.titulo(ws, fila, titulo, subtitulo, 6)
        fila = self.cliente_y_total(ws, fila, 6)
        desde, hasta = self.items(ws, fila)
        fin_totales = self.totales(ws, hasta + 2, desde, hasta)
        fila = self.condiciones(ws, hasta + 2, fin_totales)
        self.cierre(ws, fila)
        ws.activate()

    def hoja_detalle(self, ruta_logo):
        p = self.v["propuesta"]
        ws = self.hoja("Detalle", [26, 26, 26, 26])
        fila = self.encabezado(ws, None, 3)
        ws.write_string(fila, 0, p["titulo"], self.f(bold=True, font_size=16))
        fila += 2
        if p["contexto"]:
            fila = self.bloque_texto(ws, fila, "Contexto", p["contexto"])
        if p["solucion"]:
            fila = self.bloque_texto(ws, fila, "Nuestra propuesta", p["solucion"])
        for titulo, lista in (("Incluye", p["incluye"]), ("No incluye", p["no_incluye"])):
            if lista:
                fila = self.bloque_texto(ws, fila, titulo, [f"•  {x}" for x in lista])
        if p["etapas"]:
            self.rotulo(ws, fila, 0, "Etapas y plazos")
            fila += 1
            cab = self.f(bold=True, font_size=7.5, font_color=self.c["sobre_principal"],
                         bg_color=self.c["principal"], valign="vcenter")
            ws.write_string(fila, 0, "ETAPA", cab)
            ws.merge_range(fila, 1, fila, 2, "", cab)
            ws.write_string(fila, 1, "DESCRIPCIÓN", cab)
            ws.write_string(fila, 3, "DURACIÓN", cab)
            fila += 1
            borde = {"bottom": 1, "bottom_color": self.c["borde"], "text_wrap": True}
            for et in p["etapas"]:
                ws.write_string(fila, 0, et["nombre"], self.f(bold=True, **borde))
                ws.merge_range(fila, 1, fila, 2, "", self.f(**borde))
                ws.write_string(fila, 1, et.get("descripcion", ""), self.f(font_color=self.c["tinta_2"], **borde))
                ws.write_string(fila, 3, et.get("duracion", ""), self.f(bold=True, font_color=self.c["acento_texto"],
                                                                        **borde))
                ws.set_row(fila, max(18, 13 * max(filas_de(et.get("descripcion", ""), 50),
                                                  filas_de(et["nombre"], 25)) + 5))
                fila += 1
            fila += 1
        if p["por_que_nosotros"]:
            fila = self.bloque_texto(ws, fila, "Por qué nosotros", p["por_que_nosotros"])
        if p["proximos_pasos"]:
            self.bloque_texto(ws, fila, "Próximos pasos", p["proximos_pasos"])


def generar(vista, ruta_logo, destino):
    libro = Libro(destino, vista)
    if vista["tipo"] == "propuesta":
        libro.hoja_economica("Inversión", ruta_logo, vista["propuesta"]["titulo"], f"Propuesta N° {vista['codigo']}")
        libro.hoja_detalle(ruta_logo)
        libro.wb.worksheets()[0].activate()
    else:
        hoja = re.sub(r"[\[\]:*?/\\]", "", vista["nombre_documento"])[:31] or "Cotización"
        libro.hoja_economica(hoja, ruta_logo, vista["nombre_documento"], f"N° {vista['codigo']}")
    libro.wb.set_properties({"title": f"{vista['nombre_documento']} {vista['codigo']}",
                             "author": vista["negocio"]["nombre"]})
    libro.wb.close()
    return destino
