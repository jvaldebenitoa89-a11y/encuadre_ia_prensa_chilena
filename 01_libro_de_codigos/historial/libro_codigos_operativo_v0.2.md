# Libro de códigos operativo v0.2 (instrucciones para el codificador)

*v0.2 incorpora seis aclaraciones surgidas de una prueba de humo con un lote (c1, c5, voz, 1.3.IRR, 2.1.LIM, 3.3 y 3.4, citas con puntos suspensivos).*

Proyecto FONDECYT Pluralismo. Variable: **encuadre mediático de la inteligencia artificial (IA) en la prensa chilena**. Dimensiones: **D1 Origen**, **D2 Carácter**, **D3 Horizonte**.

## 0. Principios

1. **Codificas lo que el texto construye, no las palabras que aparecen.** Mencionar "regulación" o "innovación" no implica ninguna valoración.
2. **Presencia y valoración son cosas distintas.** Primero decides si un elemento está presente; después decides cómo se valora.
3. **Ante la duda, no codifiques**, salvo en los códigos "por defecto" (1.3.SIN, 3.1.NIN, 3.2.NEX, 3.3.NIN) que son obligatorios cuando no hay otro.
4. **Todo código aplicado necesita una cita textual literal** que lo sostenga (salvo los códigos por defecto).
5. **Codificas a ciegas del período y del medio.** No sabes el año ni el medio y no debes inferirlos para decidir un código. Codifica solo con lo que dice la nota.
6. **No sobrecodifiques.** Una nota central suele tener entre 3 y 10 códigos. Una nota secundaria, entre 0 y 3. Una nota tangencial, ninguno.
7. **Una nota puede combinar encuadres distintos.** Si hay fragmentos distintos que sustentan dos códigos, aplica ambos.

## 1. Procedimiento por nota

1. Lee el titular, la bajada y el texto completo.
2. Decide **C1 (centralidad)**. Si es *tangencial*, registra solo C1 a C5 y pasa a la siguiente nota.
3. Registra **C2 a C5**.
4. Recorre **D1, D2 y D3** indicador por indicador. Para cada código que el texto construya con claridad, registra: `cod`, `v`, `voz`, `marca`, `cita`, `calidad` y, si corresponde, los modificadores.
5. Asigna los códigos por defecto que falten (1.3, 3.1, 3.2, 3.3).
6. Si el texto construye algo relevante que **ningún código recoge**, regístralo como **emergente** (máximo 2 por nota).
7. Si dudaste de una decisión importante, anótalo en `dudas` en una línea.

**Notas con texto inexistente o muy corto** (solo titular y bajada): codifica solo lo que el titular y la bajada construyen, anótalo en `dudas` ("solo titular y bajada") y no inventes lo que no está.

**Residuos del scraper.** Pueden aparecer fragmentos que no son parte de la nota: titulares de otras notas insertados después de la marca `[Lea también]`, pies de foto con `| AFP`, `| EFE` y similares, o avisos como "Este es un contenido presentado por…". **No cites ni codifiques esos fragmentos.**

## 2. Variables de contexto (una por nota; no son el encuadre)

| Campo | Valores | Regla |
|---|---|---|
| `c1` Centralidad | `central` / `secundaria` / `tangencial` | **Central**: la IA es el tema de la nota (aparece en el titular o articula el argumento). **Secundaria**: la IA es un elemento importante, pero no el eje (uno de varios temas, o un apartado relevante). **Tangencial**: mención de paso, o "con IA" como adjetivo de un producto o evento, sin discurso sobre la IA. Si la IA aparece solo en el titular o la bajada, es *secundaria* únicamente cuando ese titular construye un sentido sobre la IA (la caracteriza, la valora, anuncia qué hacer con ella); si solo la nombra, es *tangencial*. |
| `c2` Referente tecnológico | lista, uno o más: `generica` / `generativa` / `sistemas_especificos` / `agi_superinteligencia` | `generativa`: chatbots, ChatGPT y similares, generación de texto, imagen, audio o video. `sistemas_especificos`: reconocimiento facial, vehículos autónomos, algoritmos de recomendación, aprendizaje automático aplicado a un fin concreto. `agi_superinteligencia`: IA general, superinteligencia, singularidad. `generica`: "la IA" sin especificar. |
| `c3` Ámbito temático | `educacion` / `trabajo_economia` / `politica_estado` / `salud_ciencia` / `seguridad_justicia` / `cultura_medios` / `otro` | El ámbito donde la nota ubica a la IA. Uno solo, el predominante. |
| `c4` Actores nombrados | lista de hasta 3 textos | Los actores más relevantes para el discurso sobre la IA (empresas, personas, Estados, instituciones), escritos de forma normalizada ("OpenAI", "Sam Altman", "Gobierno de Chile"). |
| `c5` Género | `noticia` / `reportaje` / `entrevista` / `columna_opinion` / `editorial` / `contenido_patrocinado` / `otro` | Por la forma del texto. `contenido_patrocinado`: avisos de "contenido presentado por", o notas claramente promocionales de una empresa (comunicado reproducido con llamado a la acción comercial, aunque no declare ser patrocinado). Una nota con firma periodística y fuentes plurales no lo es, aunque trate de una empresa. |

## 3. Campos que acompañan a cada código

| Campo | Valores | Regla |
|---|---|---|
| `v` Valoración | `+` / `-` / `A` / `C` / `D` / `NA` | Ver sección 3.1. `NA` solo en los indicadores 1.3, 2.4, 2.5, 3.2 y 3.4. |
| `voz` | `P` / `FE` / `FC` / `FG` / `FS` / `FI` / `FM` | Quién enuncia el fragmento citado. `P`: periodista, medio o columnista (voz propia del texto; una columna firmada es `P` aunque quien firma sea académico, salvo que cite a otra fuente; si el texto transcribe a un chatbot, usa `P` y anótalo en `dudas`). `FE`: fuente experta o académica. `FC`: fuente corporativa o empresarial. `FG`: fuente gubernamental o política. `FS`: sociedad civil, trabajadores, gremios. `FI`: organismo internacional. `FM`: dos o más voces que se oponen sin que el texto resuelva. |
| `marca` | `explicita` / `implicita` / `na` | **Explícita**: hay adjetivo, verbo, promesa o juicio verbalizado. **Implícita**: la valoración se infiere de la selección, el orden o el titular. `na` cuando `v` es `D` o `NA`. |
| `cita` | texto | Ver sección 5. |
| `calidad` | `1` / `2` / `3` | Calidad de la cita como evidencia. 1: débil o ambigua. 2: clara. 3: paradigmática (úsala de forma excepcional, solo para citas ejemplares). |

### 3.1 Cómo decidir `v`

`v` valora **el objeto del código que estás aplicando**, no la IA en abstracto. En D3.3, `v` valora **la medida** (la regulación, la prohibición, la adopción), no la IA.

Procedimiento, en este orden:

1. ¿El fragmento tiene marcas valorativas sobre ese objeto (adjetivos, verbos, advertencias, promesas, selección sesgada)? **No** → `D` (descriptiva). Es el valor por defecto. **No infieras la valoración desde el tema**: "despidos" o "lanzamiento" no son valorativos por sí solos.
2. Sí → ¿todas las marcas son favorables? `+`. ¿Todas desfavorables? `-`.
3. Hay de ambos signos → ¿una **condición explícita** determina cuál se cumple ("depende de cómo se use", "según cómo se regule")? Sí → `C`. No → `A` (ambivalente: ambas valencias afirmadas y sin resolver).

`NA` se usa en 1.3, 2.4, 2.5, 3.2 y 3.4 (indicadores estructurales).

## 4. Códigos

Formato: `código` — definición. **I**: incluye. **E**: excluye o frontera.

### D1. Origen: ¿quién y por qué hizo surgir o impulsa la IA?

D1 trata de la **causa o intención atribuida a la génesis y expansión** de la IA. Los efectos de la IA van en D2.

**1.1 Agente impulsor** (¿quién?). `v` aplica. Modificador `escala`: `global` / `Chile` / `no_especificada` (todos excepto 1.1.DIF).

- `1.1.CIE` — La nota atribuye el surgimiento o avance a científicos, ingenieros, universidades o centros de investigación. **E**: "avances científicos" sin sujeto va en 1.1.DIF.
- `1.1.CORP` — Atribuye el desarrollo o impulso a empresas tecnológicas, nombradas o genéricas. **E**: ser usuaria de IA no es ser impulsora.
- `1.1.EST` — Atribuye el desarrollo a gobiernos o Estados-nación (financiamiento, estrategia). **E**: la regulación estatal no es agente impulsor, va en D3.
- `1.1.USU` — Atribuye la expansión a la adopción masiva o la demanda del público. **E**: no basta una cifra de usuarios. La masividad debe presentarse como causa.
- `1.1.DIF` — El surgimiento o avance se enuncia sin sujeto ("la IA irrumpió", "avanza", "llegó"). Es marcador de naturalización. Puede coexistir con otros 1.1 si hay fragmentos distintos.

**1.2 Motor atribuido** (¿por qué?). `v` aplica.

- `1.2.CON` — Se explica por el avance del conocimiento, la creatividad o el ingenio humano. Requiere causalidad explícita ("gracias a", "fruto de").
- `1.2.ECO` — Se explica por lucro, competencia de mercado, inversión o acumulación de capital. **E**: nombrar a la empresa sin explicar su interés es solo 1.1.CORP.
- `1.2.GEO` — Se explica por rivalidad entre Estados o bloques, o por seguridad nacional. **E**: un acuerdo cooperativo no es geopolítica.
- `1.2.CTR` — Se atribuye a la IA un propósito deliberado de vigilar, disciplinar, explotar o controlar. Exige **intención atribuida al diseño**. **E**: un riesgo de vigilancia sin atribución de intención va en 2.3.PRI.
- `1.2.NEC` — Se explica por responder a necesidades o problemas sociales (salud, productividad, educación).
- `1.2.INE` — El surgimiento se presenta como resultado inevitable de la evolución tecnológica o histórica ("era cuestión de tiempo"). **E**: no confundir con 3.2.INE, que trata el futuro.

**1.3 Narrativa temporal del origen.** `v` = `NA`. **Exactamente uno por nota central o secundaria.**

- `1.3.IRR` — El surgimiento *de la IA o de la tecnología* se narra como irrupción súbita ("de pronto", "irrumpió", un lanzamiento que lo cambió todo). **E**: la masividad rápida de un producto concreto no es irrupción del origen; si el texto no narra de dónde viene la IA, es 1.3.SIN.
- `1.3.TRA` — Se narra como trayectoria larga o acumulativa (años o décadas de desarrollo).
- `1.3.SIN` — La nota no aborda el origen. **Es el valor por defecto.** No necesita cita.

### D2. Carácter: ¿qué es la IA y qué efectos se le atribuyen hoy?

**2.1 Naturaleza atribuida.** `v` aplica.

- `2.1.HER` — Se enuncia como herramienta, asistente o medio al servicio de fines humanos.
- `2.1.INN` — Se enuncia como avance, hito, innovación o capacidad tecnológica. La valoración va en `v` (puede ser `D`).
- `2.1.AGE` — Se le atribuyen capacidades humanas o decisión propia ("piensa", "decide", "quiere"). Es antropomorfización. **E**: términos técnicos lexicalizados ("aprendizaje automático") no cuentan.
- `2.1.REV` — Se presenta como fuerza de cambio profundo de la sociedad, la economía o el trabajo ("revolución", "cambio de época"). Requiere alcance general.
- `2.1.MER` — Se presenta como mercancía, servicio comercial o activo de mercado (precio, inversión, valorización bursátil).
- `2.1.LIM` — Se enfatizan sus errores, límites, sesgos o fallas **técnicas** ("alucina", "se equivoca", "no entiende"). **E**: un juicio estético o de autenticidad ("suena artificial", "carece de alma") no es una falla técnica y no se codifica aquí.

**2.2 Oportunidad** (ámbito). `v` aplica. Requiere un beneficio atribuido a la IA, no solo mencionar el ámbito.

- `2.2.ECO` economía y productividad. `2.2.LAB` trabajo (aumento de capacidades, nuevos empleos). `2.2.EDU` educación. `2.2.SAL` salud y ciencia. `2.2.EST` Estado y servicios públicos. `2.2.CUL` cultura, creatividad y vida cotidiana. `2.2.OTR` otra (con etiqueta en `mod.etiqueta`).

**2.3 Riesgo o amenaza** (ámbito del daño). `v` aplica. Requiere un daño atribuido a la IA. **Modificadores obligatorios en cada código 2.3**: `g` y `resp`.

- Ámbitos: `2.3.EMP` empleo y condiciones de trabajo. `2.3.DEM` democracia, esfera pública, desinformación. `2.3.PRI` privacidad, autonomía, vigilancia. `2.3.SEG` seguridad (delito, ciberseguridad, militar). `2.3.DES` desigualdad, concentración de poder, sesgo o discriminación. `2.3.CUL` educación, creación, autoría, integridad académica. `2.3.HUM` humanidad o supervivencia. `2.3.OTR` otro (con etiqueta).
- `g` (intensidad; **excluyente**): `G1` riesgo (daño posible y manejable; verbos de posibilidad o mitigación). `G2` amenaza (daño grave, estructural o intencional; daño enmarcado como cierto o con un actor que lo impulsa). `G3` pérdida de control (tecnología autónoma o fuera de control, como proceso o desenlace).
- `resp` (a quién se atribuye el daño; uno): `RCO` corporaciones. `RMA` usos maliciosos (delincuentes, actores hostiles). `RES` Estado o falta de regulación. `RTE` la tecnología misma. `RDI` difuso o no atribuido.
- **E**: un hecho adverso (despidos, una falla) sin vínculo explícito con la IA no es 2.3.

**2.4 Condicionalidad** (de qué depende el efecto). `v` = `NA`. Requiere fórmula condicional explícita ("depende de", "según cómo", "siempre que").

- `2.4.USO` uso humano. `2.4.DIS` diseño o propietarios. `2.4.REG` regulación o instituciones. `2.4.CTX` contexto o implementación.

**2.5 Relativización** (contra-narrativa). `v` = `NA`. Requiere el movimiento discursivo de **cuestionar** una narrativa dominante ("se exagera", "no hay evidencia", "burbuja"). **E**: presentar pros y contras sin cuestionar no es relativización.

- `2.5.HYP` cuestiona el entusiasmo o las promesas. `2.5.ALA` cuestiona el alarmismo. `2.5.AMB` cuestiona ambos.

### D3. Horizonte: ¿qué futuro se proyecta y qué debe hacerse?

**3.1 Futuro proyectado.** `v` aplica y valora **el futuro proyectado**. El contenido es neutral en valencia.

- `3.1.CON` continuidad o aceleración. `3.1.EST` transformación estructural de un ámbito (anota el ámbito en `mod.ambito`). `3.1.RUP` ruptura o punto de no retorno (IA general, superinteligencia). `3.1.INC` incertidumbre abierta. `3.1.NIN` sin proyección (**por defecto**, sin cita).

**3.2 Modalidad del futuro.** `v` = `NA`.

- `3.2.INE` la existencia o expansión se presenta como irreversible ("llegó para quedarse", "no hay vuelta atrás"). `3.2.DEC` la dirección se presenta como objeto de decisión colectiva. **Pueden coexistir.** `3.2.NEX` ninguna de las dos (**por defecto**, sin cita).

**3.3 Acción prescrita.** Se codifica cuando la nota (a) **prescribe o exhorta** una acción frente a la IA, o (b) **presenta una medida adoptada o propuesta** (ley, acuerdo, prohibición, programa) como respuesta a la IA. Constatar que la IA existe o crece no es 3.3. `v` valora **la medida**: exigirla o defenderla puede ser `+`, criticarla `-`, solo reportarla `D`.

- Apropiación: `3.3.ADO` adopción y promoción (invertir, impulsar, incorporar). `3.3.ADA` adaptación social (capacitar, reconvertir, alfabetizar).
- Ordenamiento institucional: `3.3.REG` regulación estatal (leyes, normas vinculantes, fiscalización). `3.3.GOB` gobernanza (acuerdos, estándares, autorregulación, cooperación multiactor o internacional **para ordenar, estandarizar o limitar** la IA; una cooperación para **impulsarla** es 3.3.ADO). `3.3.LIB` no intervención: se **rechaza o descarta explícitamente** la regulación.
- Restricción: `3.3.CON` contención y control (límites, supervisión humana obligatoria, pausa, moratoria). `3.3.PRO` prohibición o detención (verbos de prohibir, vetar, detener, eliminar). En `3.3.PRO` el modificador `alcance` es `parcial` (un uso específico) o `total` (la IA o su desarrollo).
- `3.3.NIN` sin prescripción (**por defecto**, solo si no hay ningún otro 3.3; sin cita).
- **Frontera REG/GOB**: REG es norma estatal vinculante; GOB es acuerdo o estándar sin carácter de ley, o multiactor. Si la nota tiene ambos, aplica ambos.
- **Frontera CON/PRO**: CON limita, condiciona o pausa; PRO prohíbe, veta o detiene.
- Describir una norma existente sin posición es presencia con `v` = `D`. Exigirla o defenderla es prescripción.

**3.4 Actor responsable de actuar.** `v` = `NA`. Solo se codifica si hay un código 3.3 distinto de 3.3.NIN. El actor es **quien debe ejecutar la acción** (el que tiene que legislar, adoptar, capacitarse o supervisar), no el destinatario de un mensaje que no la ejecuta.

- `3.4.EST` Estado. `3.4.EMP` empresas. `3.4.ACA` academia y comunidad científica. `3.4.SOC` sociedad civil, trabajadores, gremios. `3.4.IND` individuos y usuarios. `3.4.INT` organismos internacionales. `3.4.NES` no especificado (solo si hay prescripción sin sujeto).

## 5. La cita

- Es un fragmento **literal y continuo** copiado de la nota (titular, bajada o texto), de **como máximo 50 palabras**.
- Cópialo **exactamente**: mismos caracteres, mayúsculas, tildes, puntuación y espacios. No corrijas errores y no agregues tú puntos suspensivos ni corchetes para saltarte palabras; si necesitas recortar, elige un tramo más corto que sea continuo. Si la nota original ya trae "[...]" o "..." dentro del fragmento, puedes copiarlos tal cual.
- Elige el tramo **mínimo** que muestre el código y su valoración.
- Cada código lleva su propia cita. Una misma cita puede sustentar varios códigos si de verdad los sustenta.
- No cites residuos del scraper (sección 1).
- Los códigos por defecto (1.3.SIN, 3.1.NIN, 3.2.NEX, 3.3.NIN, 3.4.NES) llevan `cita` vacía.

## 6. Reglas de desempate frecuentes

- **Fuente que valora vs. periodista que adopta.** Si la valoración la emite una fuente citada, `voz` es el tipo de fuente. Si el texto adopta esa valoración sin distancia (titular que la asume, sin contrapunto), mantén la voz de la fuente y marca `implicita` solo si la valoración no es verbal.
- **Daño futuro.** "Podría destruir empleos" es D2 (2.3.EMP con G1), no D3.
- **Una misma frase, varios objetos.** Una frase puede sustentar un código de D1 y otro de D2. Registra ambos si cada uno se sostiene.
- **Titular alarmista, cuerpo descriptivo.** Valora lo que construye el fragmento citado. Si el titular y el cuerpo difieren, registra ambos fragmentos con sus propios `v`.
- **Citas del tipo "expertos advierten".** La voz es `FE`. Si el texto no resuelve ni contrapone, no agregues `FM`.
- **`FM`.** Úsalo solo cuando la **misma** valoración sobre el **mismo** objeto aparece con signos opuestos en voces distintas.

## 7. Emergentes

Registra un emergente cuando el texto construye con claridad un significado relevante sobre el origen, el carácter o el horizonte de la IA que **ningún código recoge**. Campos: `indicador` (1, 2 o 3), `etiqueta` (hasta 4 palabras), `definicion` (una línea), `v`, `voz`, `cita`. Máximo 2 por nota. No uses `OTR` para casos que sí caben en un código existente.

## 8. Formato de salida (JSON)

Un objeto por nota, en una lista `notas`. Los códigos por defecto se incluyen como cualquier otro, con `v` = `NA`, `voz` y `marca` en `na` y `cita` vacía.

```json
{
  "alias": "N04127",
  "c1": "central",
  "c2": ["generativa"],
  "c3": "educacion",
  "c4": ["OpenAI", "Ministerio de Educación"],
  "c5": "noticia",
  "codigos": [
    {"cod": "1.1.CORP", "v": "D", "voz": "P", "marca": "na", "cita": "...", "calidad": 2, "mod": {"escala": "global"}},
    {"cod": "2.3.CUL", "v": "-", "voz": "FE", "marca": "explicita", "cita": "...", "calidad": 2, "mod": {"g": "G1", "resp": "RDI"}},
    {"cod": "3.3.REG", "v": "+", "voz": "P", "marca": "explicita", "cita": "...", "calidad": 2, "mod": {}},
    {"cod": "1.3.SIN", "v": "NA", "voz": "na", "marca": "na", "cita": "", "calidad": 0, "mod": {}}
  ],
  "emergentes": [],
  "dudas": ""
}
```
