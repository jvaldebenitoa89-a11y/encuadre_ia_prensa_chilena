export const meta = {
  name: 'triaje-centralidad-ia',
  description: 'Triaje de centralidad (c1) de las notas con señal baja de menciones de IA; las no tangenciales pasan a codificación completa',
  phases: [{ title: 'Triaje', detail: 'un agente por lote de 25 notas' }],
}

const RAIZ = '<RUTA_DEL_PROYECTO>'
const COD = RAIZ + '\\codificacion'
const LIBRO = COD + '\\' + args.libro
const lotes = args.lotes

const STATUS = {
  type: 'object',
  properties: {
    lote: { type: 'string' },
    n_notas: { type: 'integer' },
    n_central: { type: 'integer' },
    n_secundaria: { type: 'integer' },
    n_tangencial: { type: 'integer' },
    observaciones: { type: 'string' },
  },
  required: ['lote', 'n_notas', 'n_central', 'n_secundaria', 'n_tangencial'],
}

function prompt(l) {
  const rLote = `${COD}\\lotes\\triaje\\${l}.json`
  const rSal = `${COD}\\salidas\\triaje\\${l}_X.json`
  return `Eres clasificador de centralidad en un estudio de análisis crítico del discurso (FONDECYT Pluralismo, encuadre mediático de la inteligencia artificial en prensa chilena). Tu única tarea es decidir la variable c1 (centralidad de la IA) de cada nota de un lote.

Rutas (Windows; usa comillas en el shell):
- Libro de códigos: ${LIBRO}  (lee el principio 8, la sección 1 y la fila c1 de la sección 2; el resto no es necesario)
- Lote: ${rLote}  (JSON con notas: alias, titulo, bajada, texto, solo_titular_bajada)
- Salida que debes escribir: ${rSal}

Pasos:
1. Lee las partes indicadas del libro de códigos.
2. Lee el lote y, nota por nota, lee el texto completo antes de decidir.
3. Decide c1 = central | secundaria | tangencial aplicando exactamente la regla de la fila c1 (preguntas P1 y P2). Estas notas fueron preseleccionadas porque mencionan la IA solo una vez o ninguna en titular o bajada; la mayoría será tangencial, pero no lo des por supuesto: lee el pasaje donde aparece la IA y decide qué construye el texto sobre ella.
4. Escribe un JSON UTF-8 válido: {"lote": "${l}", "coder": "X", "notas": [{"alias": "...", "c1": "...", "razon": "frase de hasta 20 palabras"}, ...]} con todas las notas del lote.
5. Comprueba que el archivo se parsea (por ejemplo con python -c "import json; json.load(open(r'<ruta>', encoding='utf-8'))").
6. Restricciones: clasificación ciega. No leas otros archivos de la carpeta codificacion salvo el libro y tu lote. No intentes averiguar el medio ni el año.

Responde SOLO con el estado estructurado.`
}

phase('Triaje')
const res = await parallel(lotes.map(l => () => agent(prompt(l), { label: `triaje ${l}`, phase: 'Triaje', schema: STATUS })))
const ok = res.filter(Boolean)
const fallidos = lotes.filter((l, i) => !res[i])
log(`Triaje completado: ${ok.length}/${lotes.length}; fallidos: ${fallidos.join(',') || 'ninguno'}`)
return { completados: ok.length, fallidos, central: ok.reduce((a, r) => a + r.n_central, 0), secundaria: ok.reduce((a, r) => a + r.n_secundaria, 0), tangencial: ok.reduce((a, r) => a + r.n_tangencial, 0) }
