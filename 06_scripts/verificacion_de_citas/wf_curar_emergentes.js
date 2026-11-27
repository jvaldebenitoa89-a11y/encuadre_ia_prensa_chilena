export const meta = {
  name: 'curar-emergentes-ia',
  description: 'Verificación adversarial de las citas de categorías emergentes: un agente por categoría juzga si cada cita sustenta la definición de la categoría',
  phases: [{ title: 'Verificar', detail: 'un agente por categoría emergente' }],
}

const RAIZ = '<RUTA_DEL_PROYECTO>'
const etiquetas = args.etiquetas

const STATUS = {
  type: 'object',
  properties: {
    cod: { type: 'string' },
    n_candidatas: { type: 'integer' },
    n_aptas: { type: 'integer' },
    n_ajustar: { type: 'integer' },
    n_rechazadas: { type: 'integer' },
    observaciones: { type: 'string' },
  },
  required: ['cod', 'n_candidatas', 'n_aptas', 'n_ajustar', 'n_rechazadas'],
}

function prompt(et) {
  const rIn = `${RAIZ}\\citas_trabajo\\candidatas_emergentes\\${et}.json`
  const rOut = `${RAIZ}\\citas_trabajo\\curadas_emergentes\\${et}.json`
  return `Eres verificador adversarial de un libro de citas (estudio de análisis crítico del discurso, FONDECYT Pluralismo, encuadre mediático de la IA en prensa chilena). Los codificadores registraron una categoría emergente llamada "${et}" que ningún código del libro recogía. Tu trabajo es intentar REFUTAR que cada cita candidata ejemplifica esa categoría.

Archivos (Windows; usa comillas en el shell):
- Citas candidatas y definición de la categoría: ${rIn}  (JSON {cod, definicion, candidatas:[{id_cita, id_nota, v, voz, medio, fecha, titulo_nota, cita, contexto}]}; "contexto" son unos 350 caracteres antes y después de la cita)
- Archivo de salida que debes escribir: ${rOut}

Para cada candidata, leyendo la cita y su contexto, decide:
- veredicto = "apta": leída con su contexto, la cita expresa con claridad el significado definido para la categoría.
- veredicto = "ajustar": la cita corresponde a la categoría pero la valoración v asignada es incorrecta (v_correcta: "+", "-", "A", "C" o "D"; "D" si el fragmento no tiene marca valorativa sobre el objeto).
- veredicto = "rechazar": la cita no expresa la categoría (no nombra la IA, la categoría se infiere con demasiado esfuerzo, es residuo del scraper, es de otro hablante o la refuta, o es demasiado fragmentaria).
Puntúa representatividad: 3 = ejemplar y autosuficiente, 2 = clara, 1 = aceptable pero débil. Da una razón de una línea.

Escribe un JSON UTF-8 válido {"cod": "${et}", "veredictos": [{"id_cita": "...", "veredicto": "...", "v_correcta": "...", "representatividad": 1, "razon": "..."}, ...]} con una entrada por candidata. Comprueba que el archivo se parsea.
Sé estricto. No leas otros archivos. Responde SOLO con el estado estructurado.`
}

phase('Verificar')
const res = await parallel(etiquetas.map(e => () => agent(prompt(e), { label: `emergente ${e}`, phase: 'Verificar', schema: STATUS })))
const ok = res.filter(Boolean)
log(`Verificación de emergentes: ${ok.length}/${etiquetas.length}`)
return { completados: ok.length, fallidos: etiquetas.filter((e, i) => !res[i]), aptas: ok.reduce((a, r) => a + r.n_aptas, 0), rechazadas: ok.reduce((a, r) => a + r.n_rechazadas, 0) }
