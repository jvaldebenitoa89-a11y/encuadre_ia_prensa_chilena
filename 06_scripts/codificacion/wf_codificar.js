export const meta = {
  name: 'codificacion-ia-corpus',
  description: 'Codificación ciega del corpus de prensa chilena sobre IA con el libro de códigos vigente, por lotes de 10 notas; incluye lotes de confiabilidad con un segundo codificador independiente',
  phases: [
    { title: 'Codificar', detail: 'un agente por lote, con autochequeo de citas literales' },
  ],
}

const RAIZ = '<RUTA_DEL_PROYECTO>'
const COD = RAIZ + '\\codificacion'
const LIBRO = COD + '\\' + args.libro
const VALIDADOR = COD + '\\validar_lote.py'
// args.tareas: [{lote:'C001', fase:'completo', coder:'X', salida:'completo'}]
// args.rangos: [{prefijo:'C', n:444, fase:'completo', coder:'X', salida:'completo'}] se expande a tareas
const tareas = (args.tareas || []).concat((args.rangos || []).flatMap(r =>
  Array.from({ length: r.n }, (_, i) => ({
    lote: r.prefijo + String(i + 1).padStart(3, '0'), fase: r.fase, coder: r.coder, salida: r.salida || 'completo',
  }))))

const STATUS = {
  type: 'object',
  properties: {
    lote: { type: 'string' },
    coder: { type: 'string' },
    n_notas: { type: 'integer' },
    n_codigos: { type: 'integer' },
    problemas_pendientes: { type: 'integer' },
    observaciones: { type: 'string' },
  },
  required: ['lote', 'coder', 'n_notas', 'problemas_pendientes'],
}

function prompt(t) {
  const rLote = `${COD}\\lotes\\${t.fase}\\${t.lote}.json`
  const rSal = `${COD}\\salidas\\${t.salida}\\${t.lote}_${t.coder}.json`
  return `Eres el codificador ${t.coder} de un estudio de análisis crítico del discurso (FONDECYT Pluralismo). Debes codificar un lote de notas de prensa chilena sobre inteligencia artificial siguiendo EXACTAMENTE el libro de códigos.

Rutas (Windows; usa comillas en el shell):
- Libro de códigos: ${LIBRO}
- Lote a codificar: ${rLote}
- Archivo de salida que debes escribir: ${rSal}
- Validador: ${VALIDADOR}

Pasos:
1. Lee completo el libro de códigos.
2. Lee el lote (JSON con notas: alias, seccion, titulo, bajada, texto, solo_titular_bajada).
3. Codifica cada nota, una por una, leyendo antes todo su texto. Aplica el procedimiento de la sección 1 del libro.
4. Escribe la salida como JSON válido UTF-8 con la forma {"lote": "${t.lote}", "coder": "${t.coder}", "notas": [ ... ]} y los campos de la sección 8 del libro. Incluye todas las notas del lote.
5. Autochequeo obligatorio: ejecuta  python "${VALIDADOR}" "${rLote}" "${rSal}" --reparar  (con PYTHONIOENCODING=utf-8 si hace falta). Corrige a mano todo problema que informe y repite hasta que diga "problemas: 0". Si queda uno irresoluble, déjalo y descríbelo en observaciones.
6. Restricciones: codificación ciega e independiente. No leas ningún otro archivo de la carpeta codificacion salvo el libro de códigos y tu lote. En particular NO leas salidas de otros codificadores, ni poblacion.jsonl, ni mapa_alias.json, ni corpus_maestro.jsonl, ni los .md del corpus. No intentes averiguar el medio ni el año de las notas, ni uses esa información para decidir.
7. Codifica lo que el texto construye, no las palabras. Ante la duda, no codifiques (salvo los códigos por defecto). No inventes códigos fuera del libro.

Responde SOLO con el estado estructurado (lote, coder, n_notas, n_codigos, problemas_pendientes, observaciones brevísimas).`
}

phase('Codificar')
const resultados = await parallel(tareas.map(t => () =>
  agent(prompt(t), Object.assign({ label: `${t.coder} ${t.lote}`, phase: 'Codificar', schema: STATUS }, t.effort ? { effort: t.effort } : {}))))

const ok = resultados.filter(Boolean)
const fallidos = tareas.filter((t, i) => !resultados[i]).map(t => t.lote + '_' + t.coder)
const conProblemas = ok.filter(r => r.problemas_pendientes > 0).map(r => r.lote + '_' + r.coder)
log(`Completados ${ok.length}/${tareas.length}; fallidos: ${fallidos.length}; con problemas pendientes: ${conProblemas.length}`)
return { completados: ok.length, fallidos, conProblemas }
