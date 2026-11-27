export const meta = {
  name: 'curar-citas-ia',
  description: 'Verificación adversarial de las citas candidatas del libro de citas: un agente por código juzga si cada cita, leída en su contexto, sustenta el código, la valoración y la voz asignados',
  phases: [{ title: 'Verificar', detail: 'un agente por código' }],
}

const RAIZ = '<RUTA_DEL_PROYECTO>'
const COD = RAIZ + '\\codificacion'
const LIBRO = COD + '\\' + args.libro
const codigos = args.codigos

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

function prompt(cod) {
  const rIn = `${RAIZ}\\citas_trabajo\\candidatas\\${cod}.json`
  const rOut = `${RAIZ}\\citas_trabajo\\curadas\\${cod}.json`
  return `Eres verificador adversarial del libro de citas de un estudio de análisis crítico del discurso (FONDECYT Pluralismo, encuadre mediático de la IA en prensa chilena). Un codificador asignó a cada cita candidata el código ${cod}, una valoración (v) y una voz. Tu trabajo es intentar REFUTAR esas asignaciones: una cita solo entra al libro si resiste tu escrutinio.

Archivos (Windows; usa comillas en el shell):
- Libro de códigos con las definiciones y reglas: ${LIBRO}  (lee la sección 3 sobre v, voz y marca, y la definición del código ${cod} en la sección 4 con sus exclusiones)
- Citas candidatas: ${rIn}  (JSON {cod, candidatas:[{id_cita, id_nota, cod, v, voz, marca, calidad, medio, fecha, titulo_nota, cita, contexto}]}; "contexto" son unos 350 caracteres antes y después de la cita en la nota)
- Archivo de salida que debes escribir: ${rOut}

Para cada candidata, leyendo la cita y su contexto, decide:
- veredicto = "apta": leída por sí sola (con el contexto) la cita sustenta el código ${cod} según su definición y sus exclusiones, la valoración v asignada es la que corresponde según las reglas de 3.1, y la voz asignada es correcta.
- veredicto = "ajustar": sustenta el código pero la valoración o la voz asignada es incorrecta; entrega v_correcta y/o voz_correcta.
- veredicto = "rechazar": no sustenta el código (la cita no nombra el objeto, es residuo del scraper como "Lee también" o un pie de foto, el fragmento es de otro hablante o refuta lo que se le atribuye, el código no corresponde por una exclusión del libro, o la cita es tan fragmentaria que no se entiende).
Además puntúa representatividad: 3 = cita ejemplar y autosuficiente para ilustrar el código en un informe, 2 = clara, 1 = aceptable pero débil. Da una razón de una línea (razon).

Escribe un JSON UTF-8 válido {"cod": "${cod}", "veredictos": [{"id_cita": "...", "veredicto": "...", "v_correcta": "...", "voz_correcta": "...", "representatividad": 1, "razon": "..."}, ...]} con una entrada por cada candidata (v_correcta y voz_correcta solo si veredicto es "ajustar"). Comprueba que el archivo se parsea.
Sé estricto: ante la duda sobre el sustento, rechaza o ajusta. No leas otros archivos de la carpeta codificacion. Responde SOLO con el estado estructurado.`
}

phase('Verificar')
const res = await parallel(codigos.map(c => () => agent(prompt(c), { label: `verificar ${c}`, phase: 'Verificar', schema: STATUS })))
const ok = res.filter(Boolean)
const fallidos = codigos.filter((c, i) => !res[i])
log(`Verificación completada: ${ok.length}/${codigos.length}; fallidos: ${fallidos.join(',') || 'ninguno'}`)
return { completados: ok.length, fallidos, aptas: ok.reduce((a, r) => a + r.n_aptas, 0), ajustar: ok.reduce((a, r) => a + r.n_ajustar, 0), rechazadas: ok.reduce((a, r) => a + r.n_rechazadas, 0) }
