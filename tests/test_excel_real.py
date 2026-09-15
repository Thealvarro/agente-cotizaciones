"""
Abre cada Excel generado con Microsoft Excel de verdad, fuerza el recálculo de
todas las fórmulas y compara contra el valor que dejó guardado el generador.

Si no coinciden, un cliente que edite una celda vería un total distinto al del
PDF. Solo corre en Windows con Excel instalado; en otro caso se salta.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

import apoyo
from casos import CASOS

SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$salida = @{}
try {
  foreach ($ruta in ($env:ARCHIVOS_XLSX | ConvertFrom-Json)) {
    $wb = $xl.Workbooks.Open($ruta, 0, $true)
    try {
      $xl.CalculateFull()
      $valores = @{}
      foreach ($ws in $wb.Worksheets) {
        foreach ($celda in $ws.UsedRange.Cells) {
          if ($celda.HasFormula) { $valores[$ws.Name + '!' + $celda.Address(0,0)] = $celda.Value2 }
        }
      }
      $salida[$ruta] = $valores
    } finally { $wb.Close($false) }
  }
} finally {
  # Se cierra siempre: si falla a mitad, no queda un Excel invisible bloqueando archivos.
  $xl.Quit()
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
}
$salida | ConvertTo-Json -Depth 4 -Compress
"""


def hay_excel():
    if sys.platform != "win32" or not shutil.which("powershell"):
        return False
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "try { $x = New-Object -ComObject Excel.Application; $x.Quit(); 'si' } catch { 'no' }"],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip() == "si"


@unittest.skipUnless(hay_excel(), "requiere Windows con Microsoft Excel")
class FormulasExcel(unittest.TestCase):
    def test_excel_recalcula_los_mismos_montos(self):
        from openpyxl import load_workbook
        import excel
        from contenido import armar

        carpeta = apoyo.carpeta_limpia("excel_real")
        archivos = {}
        for nombre, (negocio, documento, _) in CASOS.items():
            documento = {**documento, "folio": 1}
            ruta = carpeta / f"{nombre}.xlsx"
            excel.generar(armar(documento, negocio), None, ruta)
            archivos[str(ruta)] = nombre

        entorno = {**os.environ, "ARCHIVOS_XLSX": json.dumps(list(archivos))}
        r = subprocess.run(["powershell", "-NoProfile", "-Command", SCRIPT],
                           capture_output=True, text=True, encoding="utf-8", timeout=300, env=entorno)
        self.assertEqual(r.returncode, 0, r.stderr)
        recalculados = json.loads(r.stdout)

        for ruta, nombre in archivos.items():
            guardados = load_workbook(ruta, data_only=True)
            for celda, valor_excel in recalculados[ruta].items():
                hoja, direccion = celda.split("!")
                with self.subTest(caso=nombre, celda=celda):
                    self.assertAlmostEqual(guardados[hoja][direccion].value, valor_excel, places=9)


if __name__ == "__main__":
    unittest.main()
