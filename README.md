<p align="center">
  <img src=".github/portada.png" width="100%" alt="Agente Cotizaciones: conversas, personalizas, generas y descargas tu cotización en PDF, Word y Excel">
</p>

# Cotizaciones y propuestas con tu marca

Un asistente que arma tus cotizaciones y propuestas **conversando contigo**. Le cuentas a quién
le vas a cotizar y qué, y te entrega el documento listo en **PDF, Word y Excel**, con tu nombre,
tu logo y tus colores.

No necesitas saber de tecnología. No hay que llenar planillas ni aprender un programa.

<p align="center">
  <img src="ejemplos/muestra-cotizacion.png" width="31%" alt="Cotización de ejemplo">
  <img src="ejemplos/muestra-propuesta-portada.png" width="31%" alt="Portada de una propuesta">
  <img src="ejemplos/muestra-propuesta-inversion.png" width="31%" alt="Inversión de una propuesta">
</p>

---

## Lo que necesitas

- **Un computador** con Windows o Mac. Desde el celular no se puede.
- **Internet.**
- **Una cuenta de Claude de pago** (plan **Pro** o superior). El plan gratuito no incluye esta
  función. Revisa el precio actual en [claude.com/pricing](https://claude.com/pricing).

Nada más. Lo demás que haga falta lo instala el asistente, y te pide permiso antes.

---

## Instalación — se hace una sola vez

Son cinco pasos. Hazlos en orden; si ya tienes alguno listo, sáltatelo.

### Paso 1 · Crea tu cuenta de Claude

1. Entra a [claude.ai](https://claude.ai) y crea tu cuenta con tu correo.
2. Contrata el plan **Pro** en [claude.com/pricing](https://claude.com/pricing).

### Paso 2 · Instala la aplicación de Claude

1. Descárgala desde [claude.ai/download](https://claude.ai/download). Elige Windows o Mac.
2. Abre el archivo que se descargó (queda en tu carpeta *Descargas*):
   - **Windows:** doble clic y sigue el instalador.
   - **Mac:** doble clic y arrastra el ícono de Claude a la carpeta *Aplicaciones*.
3. Abre Claude (en Windows, desde el menú Inicio; en Mac, desde *Aplicaciones*) e **inicia
   sesión** con la cuenta del paso 1.

### Paso 3 · Descarga el asistente

1. En esta misma página de GitHub, arriba de la lista de archivos, hay un botón verde que dice
   **Code**. Haz clic y después en **Download ZIP**. Se descarga en tu carpeta *Descargas*.
2. Sácalo del ZIP:
   - **Windows:** clic derecho sobre el archivo → **Extraer todo** → **Extraer**.
   - **Mac:** doble clic sobre el archivo.
3. Al extraer queda **una carpeta dentro de otra con el mismo nombre**. Entra a la primera: la
   que sirve es **la de adentro**, la que tiene las carpetas `generador` y `ejemplos`.
4. **Arrastra esa carpeta de adentro a *Documentos*.** Así la encuentras fácil y no la borras
   sin querer al limpiar *Descargas*.

### Paso 4 · Abre el asistente en Claude

1. En la aplicación de Claude, arriba al centro, haz clic en **Code**. (Es distinto al botón
   verde de GitHub, aunque se llamen igual.) Si te pide contratar un plan, te falta el paso 1.
2. Donde te pregunta dónde trabajar, elige **Local** (no *Cloud*).
3. Haz clic en **Select folder** y elige la carpeta que dejaste en *Documentos* en el paso 3.
4. Si te pregunta si confías en la carpeta, di que sí.
5. **Recomendado:** al lado del botón de enviar hay un selector de modo. Si aparece **Auto**,
   elígelo: así Claude te pide menos permisos mientras trabaja.

### Paso 5 · Salúdalo

Escribe **hola** y presiona Enter.

El asistente te explica cómo funciona, deja listo lo necesario y te hace **unas pocas preguntas
de tu negocio**: el nombre, cómo das tus precios y cómo te contactan. Se hace una sola vez, y
después sigue directo con tu primera cotización.

> **Sobre los permisos:** Claude puede pedirte autorización antes de hacer cosas en tu
> computador, como instalar lo necesario o crear los archivos. Es normal: aprieta el botón para
> permitir. Si la aplicación te pide instalar algo más, también acepta.

> **¿Te responde algo que no tiene nada que ver con cotizaciones?** Casi siempre es porque
> elegiste la carpeta de afuera. Vuelve al paso 4 y elige la de adentro: la que tiene
> `generador` y `ejemplos`.

---

## Cómo se usa — todas las demás veces

1. Abre Claude y haz clic en **Code**.
2. Elige **Local** y la misma carpeta del asistente.
3. Dile lo que necesitas, con tus palabras:
   - *"Cotización para la señora Rosa: cambio de tablero eléctrico 180 mil, y 6 enchufes
     instalados a 25 mil cada uno."*
   - *"Hazme una cotización para la panadería La Espiga: un logo a 450 mil y 12 piezas para
     redes a 18 mil cada una."*
   - *"Arma una propuesta para la clínica veterinaria."*
   - *"Cambia el precio de los enchufes en la cotización de la señora Rosa."*
4. Responde lo que te pregunte. Antes de crear nada te muestra el total: si está bien, dile que
   sí y crea el PDF, el Word y el Excel.

> **¿Te perdiste?** Escríbele *"¿qué hago?"* o *"ayuda"* y te explica de nuevo.

> **Si prefieres hablar en vez de escribir:** en Windows aprieta **tecla Windows + H** y dicta.
> En Mac, aprieta dos veces la tecla **fn**.

Puedes parar cuando quieras: si algo queda a medias, la próxima vez te ofrece retomarlo.

---

## Tus documentos

Quedan dentro de la carpeta que elegiste, en **`mis-documentos`**, cada uno con su número y el
nombre del cliente:

```
mis-documentos/
  COT-0001 Señora Rosa/
    COT-0001 Señora Rosa.pdf      ← este es el que le mandas al cliente
    COT-0001 Señora Rosa.docx
    COT-0001 Señora Rosa.xlsx
```

**Al cliente se le manda el PDF.** El Word y el Excel son por si te los piden.

Los números de cotización son correlativos y **nunca se repiten**.

### Mandarla por WhatsApp desde el computador

1. En el computador, abre **web.whatsapp.com**.
2. En tu celular: WhatsApp → los tres puntos (en iPhone, Configuración) → **Dispositivos
   vinculados** → **Vincular un dispositivo**, y apunta la cámara al código de la pantalla.
3. Abre el chat del cliente y **arrastra el PDF** a la conversación.

Se hace una vez; después queda vinculado. Si te complica, pídele ayuda al asistente.

---

## Lo que tienes que saber

**Una cotización no es una factura.** Los documentos lo dicen al pie. La factura o boleta la
sigues haciendo donde siempre.

**Revisa antes de enviar.** El asistente no se equivoca en las sumas, pero el precio que le
dictaste y los datos del cliente tienen que estar bien de tu lado.

**El impuesto.** El asistente te pregunta cómo das tus precios. Si no sabes si te corresponde
cobrar impuesto, deja tus precios tal cual y confírmalo con tu contador: después se cambia en un
minuto.

**Tus documentos quedan en tu computador.** Lo que le cuentas al asistente pasa por Claude, como
cualquier conversación con Claude.

---

## Preguntas frecuentes

**¿Puedo agregar mi logo o cambiar los colores?**
Sí. Después de tu primera cotización te lo ofrece, y en cualquier momento puedes decirle
*"quiero poner mi logo"*.

**¿Puedo editar el Word o el Excel?**
Sí, son archivos normales. En el Excel, si cambias una cantidad o un precio, los totales se
recalculan solos. Pero el PDF no se entera: si quieres que los tres coincidan, pídele el cambio
al asistente y te rehace los tres.

**¿Funciona en mi país?**
Trae los valores de 18 países de habla hispana. Si el tuyo no está, igual funciona: te pregunta
la moneda.

**¿Qué diferencia hay entre una cotización y una propuesta?**
La cotización es la lista de precios y condiciones. La propuesta además explica el proyecto: qué
necesita el cliente, qué incluye y qué no, y en qué etapas se hace.

**¿Cuánto cuesta?**
El asistente es gratis. Lo que se paga es tu cuenta de Claude.

---

<details>
<summary><strong>Para desarrolladores</strong></summary>

### Cómo funciona

```
CLAUDE.md                   Hace que un simple "hola" active el agente, sin saber de /cotizar
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

La skill vive en `.claude/skills/` de la carpeta, así que Claude Code la carga al abrirla, sin
copiar nada a la configuración del usuario.

### Decisiones de seguridad

- Todo texto del usuario pasa por escape automático antes de llegar al HTML del PDF.
- Los colores se validan como `#rrggbb` estricto: se insertan en CSS, donde el escape de HTML no
  protege.
- En Excel, el texto se escribe siempre como texto: una celda que empieza con `=`, `+`, `-` o `@`
  nunca se convierte en fórmula.
- Logos solo PNG o JPG, verificados por su contenido y no por la extensión. Los SVG pueden traer
  código.
- Los nombres de archivo se limpian de rutas y nombres reservados de Windows.
- `mi-negocio/` y `mis-documentos/` están en `.gitignore`: si alguien sube su copia a GitHub, sus
  datos y los de sus clientes quedan fuera.

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
