# Configurar el negocio

Dos partes, y el orden importa:

1. **Lo mínimo**, antes de la primera cotización. Son tres o cuatro preguntas.
2. **Lo que mejora el documento** — logo, colores, identificación, datos de pago —, que se
   ofrece **después** de que la persona ya tiene su primera cotización en la mano.

**Por qué así:** si alguien llegó a cotizarle a un cliente que está esperando y le haces diez
preguntas sobre su marca antes, se va. Primero que vea que funciona.

Una pregunta por turno. Todo se guarda en `mi-negocio/negocio.json` con el formato de
`formato.md`.

---

# Parte 1 — Lo mínimo

Encuádralo en una frase:

> *"Antes de la primera, necesito tres datos de tu negocio. Se hace una sola vez."*

## 1. Nombre

*"¿Cómo se llama tu negocio, tal como quieres que aparezca en la cotización? Puede ser tu
nombre."*

## 2. País

Si ya lo dijo o se deduce ("en Puente Alto", "en Monterrey"), **no preguntes**. Si no:
*"¿En qué país trabajas?"*

Corre `generar.py pais "<país>"` para tener moneda, impuesto e identificación. Si no hay valores
para ese país, pregunta la moneda.

## 3. El precio y el impuesto

🚫 **No preguntes "¿cobras IVA?".** Mucha gente no sabe responder eso — trabaja con boleta de
honorarios, con monotributo, o lo ve su contador — y un "no sé" mal manejado le suma un impuesto
que nunca cobra.

Pregunta lo práctico:

> *"Cuando le das un precio a un cliente, ¿ese es lo que te paga al final, o después le sumas
> el [IVA]?"*

| Responde | Qué haces |
|---|---|
| "Le sumo el IVA" | Guarda la tasa del país con `incluido_en_precios: false` |
| "Ese es el precio final" | Pregunta en el turno siguiente: *"¿Y ese precio ya trae el [IVA] adentro, o no cobras [IVA]? Si no estás seguro, no pasa nada."* |
| → "Trae el IVA adentro" | Tasa del país con `incluido_en_precios: true` |
| → "No cobro IVA", boleta de honorarios, monotributo, exento | `tasa: 0` |
| → "No sé" | `tasa: 0` |
| "No sé" desde el principio | `tasa: 0` |

⚠️ **La regla que manda: ante la duda, el total del documento es exactamente el precio que dijo
la persona.** Nunca sumes un impuesto que no confirmó. Con `tasa: 0` el documento muestra el total
tal cual.

Si quedó en `tasa: 0` por no saber, díselo sin alarmar:

> *"Dejé tus precios tal cual me los das, sin sumar impuesto. Si después tu contador te dice que
> corresponde agregarlo, me avisas y lo cambio."*

## 4. Cómo lo contactan

*"¿Qué teléfono o correo quieres que aparezca para que el cliente te ubique?"*

## Guardar y seguir

Guarda con el **color Azul** de la tabla de más abajo y validez de 15 días. Corre
`generar.py negocio` para validar.

**Y sigue directo con lo que la persona vino a hacer.** Si al empezar ya había dicho qué quería
cotizar, retómalo sin volver a pedírselo:

> *"Listo. Vamos con la cotización para [cliente] que me contaste."*

---

# Parte 2 — Lo que mejora el documento

**Ofrécelo una sola vez, justo después de entregar la primera cotización:**

> *"Tu cotización ya está. Si quieres que las próximas salgan con tu logo, tus colores, tu
> [RUT] o tus datos para transferencia, lo agregamos ahora o cuando quieras."*

Si dice que no, no insistas. Si dice que sí, ve por lo que elija, de a uno.

## Logo

*"Deja la imagen de tu logo en el Escritorio o en Descargas y avísame cuando esté."*

No le pidas el nombre del archivo: busca **la imagen más reciente** en esas dos carpetas (JPG,
JPEG o PNG), ábrela para verla y confirma: *"¿Es este?"*. Si la confirma, cópiala a
`mi-negocio/` como `logo.png` o `logo.jpg`.

| Pasa esto | Qué haces |
|---|---|
| **Es una foto, no un logo** (una camioneta, un local, una persona) | Recomiéndale seguir sin logo: en el documento se vería chica y no se leería. *"Esa foto no se va a lucir en la cotización; mejor dejamos tu nombre bien grande, que se ve más profesional."* |
| Es un PDF, un archivo de diseño o viene dentro de un Word | *"Necesito el logo como imagen. Quien te lo hizo te puede mandar una versión en imagen."* Mientras, sin logo |
| Pesa demasiado (el generador lo rechaza) | *"Esa imagen es muy pesada. ¿Tienes una versión más liviana, como la que usas en WhatsApp?"* |
| Está en el celular | Que se la mande por WhatsApp o correo a sí mismo, la descargue en el computador, y la deje en Descargas |

## Colores

**Si hay logo, míralo** y propón a partir de él:

> *"Vi tu logo. Te propongo este [verde] como color principal y este [naranjo] para los
> detalles. ¿Te gusta?"*

Elige un principal con presencia (ni blanco ni casi negro) y, si el logo lo tiene, un segundo
color. El generador se encarga de que el texto se lea sobre ellos.

**Si no hay logo**, ofrece nombres, nunca códigos:

| Opción | Principal | Acento |
|---|---|---|
| Azul | `#1d4e89` | `#e07a2f` |
| Verde | `#2d6a4f` | `#d4a017` |
| Turquesa | `#0f766e` | `#e07a2f` |
| Grafito | `#343a40` | `#e0a82f` |
| Vino | `#7b2d3b` | `#c9a227` |
| Naranjo | `#b85418` | `#1d4e89` |

## Identificación tributaria

*"¿Tu [RUT] para que aparezca? Sirve el tuyo personal si no tienes empresa."*

Opcional. Nunca lo inventes ni lo completes.

## Dirección y sitio web

Solo si quiere que aparezcan.

## Datos para el pago

*"¿Quieres que aparezcan tus datos para transferencia? Dime banco, tipo y número de cuenta, y a
nombre de quién."*

## Condiciones de siempre

*"¿Cómo trabajas normalmente el pago? Por ejemplo: la mitad al empezar y la mitad al terminar."*

Y si es un oficio o un servicio en terreno, pregunta una vez por lo que suele aclarar:
*"¿Hay algo que siempre dejas por escrito, como la garantía o que el precio puede cambiar al ver
el trabajo?"* Eso va en `notas`.

---

## Cambiar algo después

Si más adelante dice *"cambia mi logo"*, *"ahora tengo RUT de empresa"* o *"sí cobro IVA"*,
actualizas `negocio.json`, validas con `generar.py negocio`, y le confirmas en una frase qué
cambió. Las cotizaciones que ya hizo no se tocan.
