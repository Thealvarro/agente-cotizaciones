import unittest
from decimal import Decimal

import apoyo  # noqa: F401  (agrega generador/ al path)
from calculos import calcular, formato_moneda
from casos import CASOS, EUR, MXN


class Montos(unittest.TestCase):
    def test_totales_calculados_a_mano(self):
        for nombre, (negocio, documento, esperado) in CASOS.items():
            with self.subTest(nombre):
                self.assertEqual(calcular(documento, negocio)["total"], Decimal(esperado))

    def test_impuesto_incluido_se_desglosa_sin_perder_un_centavo(self):
        negocio, documento, _ = CASOS["eur_impuesto_incluido"]
        c = calcular(documento, negocio)
        self.assertEqual(c["neto"], Decimal("247.91"))
        self.assertEqual(c["neto"] + c["impuesto"], c["total"])

    def test_redondeo_mitad_hacia_arriba_como_excel(self):
        negocio, documento, _ = CASOS["clp_redondeo_medio"]
        self.assertEqual(calcular(documento, negocio)["lineas"][0]["total"], Decimal("501"))

    def test_formato_por_pais(self):
        clp = {"simbolo": "$", "decimales": 0, "miles": ".", "decimal": ",", "simbolo_despues": False}
        self.assertEqual(formato_moneda(Decimal("1752275"), clp), "$1.752.275")
        self.assertEqual(formato_moneda(Decimal("3133.89"), MXN), "$3,133.89")
        self.assertEqual(formato_moneda(Decimal("1234.5"), EUR), "1.234,50 €")
        pen = {"simbolo": "S/", "decimales": 2, "miles": ",", "decimal": ".", "simbolo_despues": False}
        self.assertEqual(formato_moneda(Decimal("99"), pen), "S/ 99.00")


if __name__ == "__main__":
    unittest.main()
