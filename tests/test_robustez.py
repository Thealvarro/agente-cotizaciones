"""
Una prueba por cada falla que encontró la revisión de código. Si alguna vuelve
a aparecer, esto la detecta antes que un usuario.
"""
import json
import sys
import unittest

import apoyo
from casos import MXN, documento, negocio


def preparar(nombre, **cambios_negocio):
    carpeta = apoyo.carpeta_limpia(nombre)
    apoyo.guardar(carpeta / "mi-negocio" / "negocio.json", negocio(**cambios_negocio))
    return carpeta


def crear(carpeta, datos, archivo="doc.json"):
    ruta = carpeta / "mis-documentos" / "borradores" / archivo
    apoyo.guardar(ruta, datos)
    return apoyo.generar(carpeta, "crear", str(ruta.relative_to(apoyo.RAIZ)))


def carpetas(carpeta):
    return sorted(p.name for p in (carpeta / "mis-documentos").iterdir() if p.is_dir())


def item(**cambios):
    return {"descripcion": "Trabajo", "cantidad": 1, "precio_unitario": 1000, **cambios}


class NumerosYArchivos(unittest.TestCase):
    def test_borrador_llamado_documento_json_no_mueve_los_borradores(self):
        c = preparar("borrador_documento_json")
        apoyo.guardar(c / "mis-documentos" / "borradores" / "otro.json", documento([item()]))
        crear(c, documento([item()]), archivo="documento.json")
        self.assertTrue((c / "mis-documentos" / "borradores" / "otro.json").exists())
        self.assertIn("borradores", carpetas(c))

    def test_un_borrador_no_puede_elegir_un_numero_ya_usado(self):
        c = preparar("folio_en_borrador")
        crear(c, documento([item()], cliente={"nombre": "Primero"}))
        crear(c, documento([item()], cliente={"nombre": "Segundo"}, folio=1))
        self.assertEqual(carpetas(c), ["COT-0001 Primero", "COT-0002 Segundo", "borradores"])

    def test_cambiar_el_tipo_de_uno_existente_no_pisa_otro(self):
        c = preparar("cambiar_tipo")
        crear(c, documento([item()], cliente={"nombre": "Cliente"}))
        propuesta = documento([item()], tipo="propuesta", cliente={"nombre": "Cliente"},
                              propuesta={"titulo": "Original"})
        crear(c, propuesta)
        existente = c / "mis-documentos" / "COT-0001 Cliente" / "documento.json"
        datos = json.loads(existente.read_text(encoding="utf-8"))
        datos.update(tipo="propuesta", propuesta={"titulo": "Pisada"})
        existente.write_text(json.dumps(datos), encoding="utf-8")

        r = apoyo.generar(c, "crear", str(existente.relative_to(apoyo.RAIZ)))
        self.assertEqual(r.returncode, 2)
        original = json.loads((c / "mis-documentos" / "PROP-0001 Cliente" / "documento.json").read_text("utf-8"))
        self.assertEqual(original["propuesta"]["titulo"], "Original")

    def test_quitar_el_numero_a_uno_existente_no_lo_renumera(self):
        c = preparar("quitar_folio")
        crear(c, documento([item()], cliente={"nombre": "Cliente"}))
        existente = c / "mis-documentos" / "COT-0001 Cliente" / "documento.json"
        datos = json.loads(existente.read_text(encoding="utf-8"))
        del datos["folio"]
        existente.write_text(json.dumps(datos), encoding="utf-8")
        apoyo.generar(c, "crear", str(existente.relative_to(apoyo.RAIZ)))
        self.assertEqual(carpetas(c), ["COT-0001 Cliente", "borradores"])

    def test_carpeta_sin_datos_igual_reserva_su_numero(self):
        c = preparar("carpeta_sin_datos")
        crear(c, documento([item()], cliente={"nombre": "Cliente"}))
        (c / "mis-documentos" / "COT-0001 Cliente" / "documento.json").unlink()
        (c / "mis-documentos" / "folios.json").unlink()
        crear(c, documento([item()], cliente={"nombre": "Otro"}))
        self.assertIn("COT-0002 Otro", carpetas(c))

    def test_rehacer_no_borra_otros_archivos_de_la_carpeta(self):
        c = preparar("otros_archivos")
        crear(c, documento([item()], cliente={"nombre": "Cliente"}))
        doc = c / "mis-documentos" / "COT-0001 Cliente"
        (doc / "firmada por el cliente.pdf").write_bytes(b"%PDF-firmada")
        (doc / "mi version editada.xlsx").write_bytes(b"editada")
        apoyo.generar(c, "crear", str((doc / "documento.json").relative_to(apoyo.RAIZ)))
        self.assertEqual((doc / "firmada por el cliente.pdf").read_bytes(), b"%PDF-firmada")
        self.assertEqual((doc / "mi version editada.xlsx").read_bytes(), b"editada")

    def test_cambiar_el_nombre_del_cliente_renombra_y_limpia_solo_lo_suyo(self):
        c = preparar("renombrar")
        crear(c, documento([item()], cliente={"nombre": "Nombre viejo"}))
        doc = c / "mis-documentos" / "COT-0001 Nombre viejo"
        (doc / "firmada.pdf").write_bytes(b"firmada")
        datos = json.loads((doc / "documento.json").read_text(encoding="utf-8"))
        datos["cliente"]["nombre"] = "Nombre nuevo"
        (doc / "documento.json").write_text(json.dumps(datos), encoding="utf-8")
        apoyo.generar(c, "crear", str((doc / "documento.json").relative_to(apoyo.RAIZ)))

        nueva = c / "mis-documentos" / "COT-0001 Nombre nuevo"
        self.assertTrue((nueva / "COT-0001 Nombre nuevo.xlsx").exists())
        self.assertFalse((nueva / "COT-0001 Nombre viejo.xlsx").exists())
        self.assertTrue((nueva / "firmada.pdf").exists())

    @unittest.skipUnless(sys.platform == "win32", "el bloqueo de archivos abiertos es de Windows")
    def test_archivo_abierto_no_deja_el_documento_a_medias(self):
        c = preparar("archivo_abierto")
        crear(c, documento([item()], cliente={"nombre": "Cliente"}))
        doc = c / "mis-documentos" / "COT-0001 Cliente"
        excel_viejo = (doc / "COT-0001 Cliente.xlsx").read_bytes()
        with open(doc / "COT-0001 Cliente.xlsx", "rb"):
            r = apoyo.generar(c, "crear", str((doc / "documento.json").relative_to(apoyo.RAIZ)))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("abierto en otro programa", r.stdout)
        self.assertTrue((doc / "COT-0001 Cliente.docx").exists())
        self.assertEqual((doc / "COT-0001 Cliente.xlsx").read_bytes(), excel_viejo)
        self.assertEqual(list(doc.glob("*.nuevo.*")), [])


class EntradasRaras(unittest.TestCase):
    def test_null_en_campos_opcionales(self):
        c = preparar("nulls", nombre_documento=None)
        datos = documento([item(descuento_pct=None, unidad=None, detalle=None)],
                          descuento_global_pct=None, validez_dias=None, cliente={"nombre": "X", "email": None})
        r = crear(c, datos)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Cotización COT-0001", r.stdout)

    def test_caracteres_de_control_de_copiar_y_pegar(self):
        c = preparar("control")
        r = crear(c, documento([item(descripcion="Línea uno\x0bLínea dos\x01", detalle="con\x07campana")]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("CREADO", r.stdout)
        self.assertNotIn("NO SE PUDO", r.stdout)

    def test_nombre_de_documento_vacio(self):
        c = preparar("nombre_vacio", nombre_documento="")
        self.assertIn("Cotización COT-0001", crear(c, documento([item()])).stdout)

    def test_valores_mal_escritos_en_el_negocio(self):
        from datos import validar_negocio
        malos = [
            negocio(moneda={**negocio()["moneda"], "decimales": True}),
            negocio(impuesto={"nombre": "IVA", "tasa": 19, "incluido_en_precios": "false"}),
            negocio(condiciones_por_defecto={"validez_dias": "30 días"}),
        ]
        for n in malos:
            with self.subTest(n):
                self.assertTrue(validar_negocio(n))

    def test_fecha_fuera_de_rango(self):
        from datos import validar_documento
        self.assertTrue(validar_documento(documento([item()], fecha="9999-12-31")))

    def test_negocio_guardado_con_bom(self):
        c = apoyo.carpeta_limpia("bom")
        (c / "mi-negocio" / "negocio.json").write_bytes(b"\xef\xbb\xbf" + json.dumps(negocio()).encode("utf-8"))
        r = apoyo.generar(c, "negocio")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_negocio_danado_no_revienta_revisar(self):
        c = apoyo.carpeta_limpia("danado")
        (c / "mi-negocio" / "negocio.json").write_text("{ esto no es json", encoding="utf-8")
        r = apoyo.generar(c, "revisar")
        self.assertIn("PENDIENTE negocio", r.stdout)
        self.assertNotIn("Traceback", r.stderr)


class CifrasQueCuadranALaVista(unittest.TestCase):
    def test_precio_con_decimales_de_mas_se_redondea_antes_de_multiplicar(self):
        from calculos import calcular
        c = calcular(documento([item(cantidad=3, precio_unitario=1500.6)]), negocio())
        self.assertEqual(str(c["lineas"][0]["precio_unitario"]), "1501")
        self.assertEqual(str(c["lineas"][0]["total"]), "4503")

    def test_cantidad_con_el_separador_del_pais(self):
        from calculos import formato_cantidad
        clp = negocio()["moneda"]
        self.assertEqual(formato_cantidad(2.5, MXN), "2.5")
        self.assertEqual(formato_cantidad(2.5, clp), "2,5")

    def test_sin_impuesto_ni_descuento_no_repite_subtotal_y_total(self):
        from contenido import armar
        v = armar(documento([item()], folio=1), negocio(impuesto={"nombre": "IVA", "tasa": 0}))
        self.assertEqual([t["clave"] for t in v["totales"]], ["total"])

    def test_nombres_de_carpeta_sin_emoji_y_con_largo_acotado(self):
        from datos import carpeta_documento, nombre_seguro
        self.assertNotIn("😀", nombre_seguro("Cliente 😀😀😀"))
        largo = carpeta_documento({"tipo": "cotizacion", "folio": 1, "cliente": {"nombre": "x" * 500}})
        self.assertLess(len(str(largo / (largo.name + ".nuevo.docx"))), 260)


if __name__ == "__main__":
    unittest.main()
