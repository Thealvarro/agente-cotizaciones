# Configurar el negocio — una sola vez

Lo que se guarda acá aparece en todos los documentos. Encuádralo en una frase:

> *"Antes de la primera cotización, necesito los datos de tu negocio para que salgan con tu marca.
> Se hace una sola vez."*

Una pregunta por turno. Al final se guarda en `mi-negocio/negocio.json` con el formato de
`formato.md`.

---

## 1. Nombre

*"¿Cómo se llama tu negocio, tal como quieres que aparezca en los documentos?"*

## 2. País

*"¿En qué país está?"*

Corre `generar.py pais "<país>"`. Si hay valores sugeridos, tienes moneda, impuesto, nombre de la
identificación tributaria y cómo se llama el documento (en España y Argentina se dice
*Presupuesto*). Si no hay, pregunta la moneda y sigue.

## 3. El impuesto — confírmalo siempre

Los valores del país son **sugerencias**: cambian, y hay negocios exentos o con regímenes
especiales. Nunca guardes una tasa sin confirmarla:

> *"En [país] lo normal es [IVA 19%]. ¿Tu negocio cobra eso? Y cuando das un precio, ¿el
> impuesto ya viene incluido o se suma aparte?"*

| Respuesta | Qué guardas |
|---|---|
| Cobra y se suma aparte | `tasa` del país, `incluido_en_precios: false` |
| Cobra y ya viene incluido | `tasa` del país, `incluido_en_precios: true` |
| No cobra impuesto / exento | `tasa: 0` |
| No sabe | Guarda lo del país con `incluido_en_precios: false` y dile que puede cambiarlo cuando lo confirme con su contador |

## 4. Identificación tributaria

*"¿Tu [RUT / RFC / NIT] para que aparezca en los documentos? Si prefieres no ponerlo, lo dejamos
fuera."*

Es opcional. No lo inventes ni lo completes.

## 5. Contacto

*"¿Qué datos de contacto quieres que aparezcan? Correo, teléfono, dirección y sitio web: los que
quieras."*

Esta sí se responde de corrido.

## 6. Logo

*"¿Tienes tu logo como imagen? Dime cómo se llama el archivo y dónde está, por ejemplo en
Descargas o en el Escritorio."*

- Búscalo en la ubicación que diga (Descargas, Escritorio, Documentos, Imágenes) y **cópialo** a
  `mi-negocio/` con el nombre `logo.png` o `logo.jpg` según corresponda.
- **Solo PNG o JPG.** Si es SVG, PDF o de Word, explícale que necesitas el logo como imagen PNG
  o JPG, y que puede pedírselo a quien le hizo el diseño. Mientras tanto, sigue sin logo: el
  nombre del negocio aparece en su lugar.
- Si no tiene logo, sigue sin logo. No es un problema.

## 7. Colores

**Si hay logo, míralo** (abre la imagen) y propón los colores a partir de él:

> *"Vi tu logo. Te propongo usar este [verde] como color principal y este [naranjo] para los
> detalles. ¿Te gusta así?"*

Elige un color principal con presencia (no blanco, no casi negro) y, si el logo lo tiene, un
segundo color para acentos. El generador se encarga de que el texto se lea bien sobre ellos.

**Si no hay logo**, ofrece opciones con nombre, no códigos:

| Opción | Principal | Acento |
|---|---|---|
| Azul | `#1d4e89` | `#e07a2f` |
| Verde | `#2d6a4f` | `#d4a017` |
| Turquesa | `#0f766e` | `#e07a2f` |
| Grafito | `#343a40` | `#e0a82f` |
| Vino | `#7b2d3b` | `#c9a227` |
| Naranjo | `#b85418` | `#1d4e89` |

## 8. Datos para el pago *(opcional)*

*"¿Quieres que en las cotizaciones aparezcan tus datos para transferencia? Si es así, dime el
banco, tipo y número de cuenta, y a nombre de quién."*

## 9. Condiciones de siempre

*"¿Cómo trabajas normalmente el pago? Por ejemplo: 50% al inicio y 50% al entregar."*

Y guarda una validez de 15 días salvo que diga otra cosa.

---

## Cerrar

1. Guarda `mi-negocio/negocio.json`.
2. Corre `generar.py negocio` para validarlo. Si algo falla, corrígelo sin molestar al usuario
   salvo que falte un dato suyo.
3. Resume en dos líneas qué quedó y ofrece seguir:

> *"Listo, quedó configurado [nombre]. Si algún día cambias el logo, los colores o tus datos,
> me lo dices y lo actualizo. ¿Hacemos la primera cotización?"*
