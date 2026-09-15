# Cotizaciones y propuestas con tu marca

Un asistente que arma tus cotizaciones y propuestas **conversando contigo**. Le cuentas a quién
le vas a cotizar y qué, y te entrega el documento con tu logo y tus colores en **PDF, Word y
Excel**.

No necesitas saber de tecnología. No hay que llenar planillas ni aprender un programa.

<p align="center">
  <img src="ejemplos/muestra-cotizacion.png" width="31%" alt="Cotización de ejemplo">
  <img src="ejemplos/muestra-propuesta-portada.png" width="31%" alt="Portada de una propuesta">
  <img src="ejemplos/muestra-propuesta-inversion.png" width="31%" alt="Inversión de una propuesta">
</p>

---

## Lo que necesitas

- **Una cuenta de Claude de pago** (Pro o superior). La cuenta gratuita no incluye esta función.
- **La aplicación de Claude para tu computador**, Windows o Mac. Se descarga desde
  [claude.ai/download](https://claude.ai/download).
- **Google Chrome o Microsoft Edge.** Si usas Windows, ya tienes Edge.

Nada más. Lo que falte, el asistente lo instala por ti y te pide permiso antes.

---

## Cómo empezar — la primera vez

1. **Descarga esta carpeta.** Arriba en esta página, botón verde **Code** y después
   **Download ZIP**. Descomprímela en un lugar que recuerdes, por ejemplo en *Documentos*.
2. **Abre la aplicación de Claude** y entra a la pestaña **Code**.
3. **Elige la carpeta** que descomprimiste como carpeta del proyecto.
4. Si te pregunta **si confías en la carpeta, di que sí.**
5. Escribe **`/cotizar`** y presiona Enter.

La primera vez, el asistente prepara lo necesario y te pide los datos de tu negocio: nombre,
país, logo y colores. Eso se hace **una sola vez**.

> **Sobre los permisos:** Claude te va a pedir autorización antes de hacer cosas en tu
> computador, como instalar lo necesario o crear los archivos. Es normal y puedes aceptar. Si te
> ofrece no volver a preguntar para esta carpeta, también puedes elegirlo.

---

## Cómo se usa — todas las demás veces

Abre la carpeta en Claude, escribe **`/cotizar`** y dile lo que necesitas:

- *"Hazme una cotización para la panadería La Espiga: un logo a 450 mil y 12 piezas para redes
  a 18 mil cada una."*
- *"Arma una propuesta para la clínica veterinaria."*
- *"Cambia el precio del logo en la cotización de La Espiga."*

Te va a hacer las preguntas que falten, te muestra el resumen con los totales, y cuando le
dices que está bien, crea los tres archivos.

Puedes parar cuando quieras: si una cotización queda a medias, la próxima vez te ofrece
retomarla.

---

## Dónde quedan tus documentos

En la carpeta **`mis-documentos`**, cada uno en su propia carpeta con el número y el cliente:

```
mis-documentos/
  COT-0001 Panadería La Espiga/
    COT-0001 Panadería La Espiga.pdf
    COT-0001 Panadería La Espiga.docx
    COT-0001 Panadería La Espiga.xlsx
```

Los números de cotización y de propuesta son correlativos y **nunca se repiten**.

---

## Lo que tienes que saber

**Una cotización no es una factura.** Los documentos lo dicen al pie. La factura o boleta se
sigue haciendo en el sistema de impuestos de tu país.

**Revisa siempre antes de enviar.** El asistente calcula los montos con un sistema que no se
equivoca en las sumas, pero el precio que le dictaste y los datos del cliente tienen que estar
bien de tu lado.

**Confirma tu impuesto.** El asistente sugiere el de tu país, pero siempre te pregunta. Si no
estás seguro de si te corresponde cobrarlo o no, consúltalo con tu contador.

**Tus documentos quedan en tu computador.** Lo que le cuentas al asistente pasa por Claude, como
cualquier conversación con Claude. Si algún día subes esta carpeta a internet, las carpetas con
tus datos y los de tus clientes quedan fuera automáticamente.

---

## Preguntas frecuentes

**¿Puedo cambiar el logo, los colores o mis datos?**
Sí. Escribe `/cotizar` y dile *"quiero cambiar mi logo"* o lo que sea.

**¿Puedo editar el Word o el Excel después?**
Sí, son archivos normales. En el Excel, si cambias una cantidad o un precio, los totales se
recalculan solos. Pero ojo: el PDF no se va a enterar del cambio. Si quieres que los tres
coincidan, pídele el cambio al asistente y te rehace los tres.

**¿Funciona en mi país?**
Trae los valores de moneda e impuesto de 18 países de habla hispana. Si el tuyo no está, igual
funciona: te pregunta la moneda y el impuesto.

**¿Qué diferencia hay entre una cotización y una propuesta?**
La cotización es la lista de precios y condiciones. La propuesta además explica el proyecto: qué
entendiste del cliente, qué incluye y qué no, y en qué etapas se hace.

**¿Cuánto cuesta?**
El asistente es gratis. Lo que necesitas es tu cuenta de Claude de pago.

---

<details>
<summary><strong>Para desarrolladores</strong></summary>

### Cómo funciona

```
.claude/skills/cotizar/     El agente: conversación, reglas y formato de datos
generador/
  generar.py                Punto de entrada que usa el agente
  calculos.py               Montos con Decimal y redondeo igual al ROUND de Excel
  contenido.py              Una sola vista de datos para los tres formatos
  datos.py                  Validación y seguridad de la entrada
  pdf.py                    HTML con escape automático + Chrome/Edge headless
  word.py                   python-docx
  excel.py                  XlsxWriter: fórmulas con el valor ya calculado guardado
  plantillas/               HTML y CSS del PDF
  paises.json               Moneda, impuesto e identificación tributaria por país
ejemplos/                   Negocio, cotización y propuesta de ejemplo
tests/                      Pruebas
```

El agente conversa y escribe los datos; **nunca calcula montos**. Los tres formatos salen de la
misma vista calculada, así que no pueden mostrar totales distintos.

### Decisiones de seguridad

- Todo texto del usuario pasa por escape automático antes de llegar al HTML del PDF.
- Los colores se validan como `#rrggbb` estricto: se insertan en CSS, donde el escape de HTML no
  protege.
- En Excel, el texto se escribe siempre como texto: una celda que empieza con `=`, `+`, `-` o `@`
  nunca se convierte en fórmula.
- Logos solo PNG o JPG, verificados por su contenido y no por la extensión. Los SVG pueden traer
  código.
- Los nombres de archivo se limpian de rutas y nombres reservados de Windows.
- `mi-negocio/` y `mis-documentos/` están en `.gitignore` desde el primer commit.

### Pruebas

```bash
python generador/preparar.py
.venv/Scripts/python -m pip install -r tests/requirements.txt    # en Mac: .venv/bin/python
cd tests
../.venv/Scripts/python -m unittest
```

`test_excel_real.py` abre cada Excel con Microsoft Excel, fuerza el recálculo de todas las
fórmulas y compara contra el valor guardado. Solo corre en Windows con Excel instalado.

</details>

---

Desarrollado por [SICS](https://alvarocofre.dev)
