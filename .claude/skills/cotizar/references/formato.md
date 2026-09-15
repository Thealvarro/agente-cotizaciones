# Formato de los datos *(solo para ti)*

Ejemplos completos y válidos en `ejemplos/`: úsalos como punto de partida.

---

## Reglas que el generador exige

- **Números sin separadores de miles:** `150000` o `1500.5`. Nunca `"150.000"` ni `"1.500,50"`:
  se rechazan, porque `1.500` es mil quinientos en Chile y uno coma cinco en México.
- **Fechas** como `AAAA-MM-DD`. La fecha de emisión es la de hoy salvo que el usuario diga otra.
- **Porcentajes** como número de 0 a 100: `10` es 10%.
- **Textos** con saltos de línea normales (`\n`). Un párrafo nuevo es una línea vacía (`\n\n`).
- **Nunca** pongas un `folio` en un borrador nuevo: el generador asigna el siguiente número.

---

## El negocio — `mi-negocio/negocio.json`

```json
{
  "nombre": "Estudio Aurora SpA",
  "pais": "Chile",
  "id_tributario": { "etiqueta": "RUT", "valor": "77.123.456-7" },
  "direccion": "Av. Providencia 1234, Santiago",
  "email": "hola@estudioaurora.cl",
  "telefono": "+56 9 8765 4321",
  "web": "estudioaurora.cl",
  "logo": "logo.png",
  "color_principal": "#0f766e",
  "color_acento": "#e07a2f",
  "moneda": { "codigo": "CLP", "simbolo": "$", "decimales": 0, "miles": ".", "decimal": ",", "simbolo_despues": false },
  "impuesto": { "nombre": "IVA", "tasa": 19, "incluido_en_precios": false },
  "nombre_documento": "Cotización",
  "datos_pago": "Banco de Chile · Cuenta corriente 00-123-45678-90",
  "condiciones_por_defecto": { "pago": "50% al inicio y 50% contra entrega.", "entrega": "", "notas": "", "validez_dias": 15 }
}
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `nombre` | sí | |
| `color_principal` | sí | Exactamente `#rrggbb` |
| `moneda`, `impuesto` | sí | Copia los del país con `generar.py pais` y ajusta lo que confirme el usuario |
| `logo` | no | Solo el nombre del archivo, que debe estar dentro de `mi-negocio/`. PNG o JPG |
| `color_acento` | no | Si falta, se usa el principal |
| `nombre_documento` | no | `Cotización` o `Presupuesto`, según el país |
| el resto | no | Si el usuario no lo da, se omite |

---

## Un documento — `mis-documentos/borradores/<cliente>.json`

Un borrador por documento, con el nombre del cliente en minúsculas y sin símbolos
(`panaderia-la-espiga.json`). Al crear, el generador lo mueve a su carpeta definitiva.

### Cotización

```json
{
  "tipo": "cotizacion",
  "fecha": "2026-09-15",
  "validez_dias": 15,
  "cliente": {
    "nombre": "Panadería La Espiga",
    "empresa": "Comercial La Espiga Ltda.",
    "id_tributario": "76.987.654-3",
    "contacto": "Carolina Muñoz",
    "email": "carolina@laespiga.cl",
    "telefono": "+56 2 2345 6789",
    "direccion": "Irarrázaval 3150, Ñuñoa"
  },
  "items": [
    { "descripcion": "Diseño de logo", "detalle": "Tres propuestas y manual", "cantidad": 1, "unidad": "proyecto", "precio_unitario": 450000 },
    { "descripcion": "Piezas para redes", "cantidad": 12, "unidad": "piezas", "precio_unitario": 18000, "descuento_pct": 10 }
  ],
  "descuento_global_pct": 0,
  "exento": false,
  "condiciones": { "pago": "", "entrega": "Tres semanas", "notas": "" }
}
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `tipo`, `fecha`, `cliente.nombre` | sí | |
| `items` | sí | Al menos uno. Cada uno con `descripcion`, `cantidad` y `precio_unitario` |
| `items[].detalle`, `unidad`, `descuento_pct` | no | |
| `descuento_global_pct` | no | Descuento sobre el subtotal |
| `exento` | no | `true` si esta venta no lleva impuesto |
| `precios_incluyen_impuesto` | no | Úsalo cuando el usuario dicte precios **con** impuesto y su negocio normalmente lo suma aparte. **Así no calculas tú** |
| `condiciones` | no | Lo que quede vacío se completa con las condiciones de siempre del negocio |

### Propuesta

Todo lo de la cotización, con `"tipo": "propuesta"`, más:

```json
"propuesta": {
  "titulo": "Nueva marca y lanzamiento digital",
  "contexto": "Párrafo uno.\n\nPárrafo dos.",
  "solucion": "…",
  "incluye": ["Logotipo y manual", "24 publicaciones"],
  "no_incluye": ["Pauta pagada", "Impresión"],
  "etapas": [ { "nombre": "Descubrimiento", "duracion": "1 semana", "descripcion": "…" } ],
  "por_que_nosotros": "…",
  "proximos_pasos": "…"
}
```

Solo `titulo` es obligatorio. Las secciones vacías no aparecen en el documento.

---

## Qué devuelve el generador

- `previa` y `crear` imprimen el resumen con los montos **ya formateados**. Esos son los que le
  muestras al usuario, tal cual.
- `crear` termina con `CREADO <archivo>` por cada formato. Si uno no se pudo, dice `NO SE PUDO`
  y el motivo; los otros se crean igual.
- Si los datos no pasan la validación: `NO SE PUDO. Datos a corregir:` y la lista. Arregla lo
  que puedas tú; pregunta al usuario solo lo que sea un dato suyo.
