"""
Casos de prueba compartidos. Cada uno cubre una forma distinta de calcular
montos, que es donde un error cuesta plata.
"""
import copy
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NEGOCIO_BASE = json.loads((RAIZ / "ejemplos" / "negocio-ejemplo.json").read_text(encoding="utf-8"))

MXN = {"codigo": "MXN", "simbolo": "$", "decimales": 2, "miles": ",", "decimal": ".", "simbolo_despues": False}
EUR = {"codigo": "EUR", "simbolo": "€", "decimales": 2, "miles": ".", "decimal": ",", "simbolo_despues": True}


def negocio(**cambios):
    n = copy.deepcopy(NEGOCIO_BASE)
    n["logo"] = ""
    n.update(cambios)
    return n


def documento(items, **cambios):
    d = {"tipo": "cotizacion", "fecha": "2026-09-15", "validez_dias": 15,
         "cliente": {"nombre": "Cliente de prueba"}, "items": items}
    d.update(cambios)
    return d


# nombre -> (negocio, documento, total esperado calculado a mano)
CASOS = {
    "clp_descuento_linea": (
        negocio(),
        documento([{"descripcion": "A", "cantidad": 12, "precio_unitario": 18000, "descuento_pct": 10},
                   {"descripcion": "B", "cantidad": 1, "precio_unitario": 450000}]),
        # 194.400 + 450.000 = 644.400 · IVA 122.436 · total 766.836
        "766836",
    ),
    "clp_redondeo_medio": (
        negocio(),
        documento([{"descripcion": "Media unidad", "cantidad": 0.5, "precio_unitario": 1001}]),
        # 500,5 -> 501 · IVA 95,19 -> 95 · total 596
        "596",
    ),
    "clp_descuento_global": (
        negocio(),
        documento([{"descripcion": "A", "cantidad": 1, "precio_unitario": 1550000}], descuento_global_pct=5),
        # 1.550.000 - 77.500 = 1.472.500 · IVA 279.775 · total 1.752.275
        "1752275",
    ),
    "mxn_decimales": (
        negocio(moneda=MXN, impuesto={"nombre": "IVA", "tasa": 16}),
        documento([{"descripcion": "Horas", "cantidad": 2.5, "precio_unitario": 1234.567, "descuento_pct": 12.5},
                   {"descripcion": "Centavo", "cantidad": 1, "precio_unitario": 1.005}]),
        # 2,5×1234,567×0,875 = 2700,615... -> 2700,62 · 1,005 -> 1,01 · neto 2701,63
        # IVA 432,2608 -> 432,26 · total 3133,89
        "3133.89",
    ),
    "eur_impuesto_incluido": (
        negocio(moneda=EUR, impuesto={"nombre": "IVA", "tasa": 21, "incluido_en_precios": True}),
        documento([{"descripcion": "Con IVA", "cantidad": 3, "precio_unitario": 99.99}]),
        # total 299,97 · neto 299,97/1,21 = 247,909 -> 247,91 · IVA 52,06
        "299.97",
    ),
    "precio_dictado_con_iva": (
        negocio(),
        documento([{"descripcion": "Logo", "cantidad": 1, "precio_unitario": 300000}],
                  precios_incluyen_impuesto=True),
        # el negocio suma IVA aparte, pero este precio ya lo trae: total 300.000, neto 252.101
        "300000",
    ),
    "exento": (
        negocio(),
        documento([{"descripcion": "Exento", "cantidad": 2, "precio_unitario": 50000}], exento=True),
        "100000",
    ),
    "sin_impuesto": (
        negocio(moneda={**MXN, "codigo": "USD"}, impuesto={"nombre": "Sales tax", "tasa": 0}),
        documento([{"descripcion": "Servicio", "cantidad": 4, "precio_unitario": 125.5}], descuento_global_pct=10),
        # 502 - 50,20 = 451,80
        "451.80",
    ),
}
