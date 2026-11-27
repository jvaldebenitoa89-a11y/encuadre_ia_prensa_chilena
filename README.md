# Encuadre mediático de la inteligencia artificial en la prensa digital chilena (2019–2026). Instrumentos, registro de codificación y scripts

Versión 1.0 · 27 de noviembre de 2026

Material complementario del artículo:

> Valdebenito Allendes, J. (2026). La inteligencia artificial en la prensa digital chilena (2019–2026). Encuadres, voces y autoridad discursiva en seis medios. *Perspectivas de la Comunicación*. [Volumen, número, páginas y DOI del artículo por completar al publicarse.]

El paquete reúne lo que el artículo declara disponible. A saber, el libro de códigos, el libro de citas, el registro completo de entradas codificadas, la codificación por nota, el embudo del corpus, las instrucciones entregadas a los agentes, los informes de acuerdo y los scripts de recolección, muestreo, codificación y análisis.

## 1. Contenido

| Carpeta | Contenido |
|---|---|
| `01_libro_de_codigos/` | `libro_de_codigos.xlsx` (estructura, 76 códigos con definición, reglas, frecuencias y ejemplos, variables de contexto, principios, confiabilidad, emergentes y versiones). `libro_codigos_operativo_v1.0.md`, el texto del libro que recibieron los agentes en la corrida principal. `historial/` con las versiones 0.1 y 0.2 (la 0.2 se usó en el piloto). |
| `02_libro_de_citas/` | `libro_de_citas.xlsx` con 566 citas verificadas, un resumen por código, las citas de las categorías emergentes y el registro completo. |
| `03_registro/` | `registro_entradas_codificadas.csv` (17.235 entradas con cita literal en 3.762 notas), `codificacion_completa_codigos.csv` (30.368 filas, incluidos los códigos por defecto sin cita), `notas_codificadas.csv` (4.510 notas con las variables de contexto, emergentes y dudas) y `embudo_corpus.csv` (5.150 notas con su enlace, su etapa en el embudo y su pertenencia a las submuestras de control). |
| `04_instrucciones_agentes/` | `instrucciones_agentes.md`, con el texto literal de las instrucciones de codificación, triaje y verificación de citas, e `instrucciones_recodificacion_ciega.md`, con las de la recodificación hecha con otro modelo. |
| `05_informes_de_acuerdo/` | Piloto (v0.2), validación (v1.0) y recodificación con otro modelo (120 notas), con las codificaciones comparadas, las métricas, el diagnóstico de los desacuerdos del piloto y la prueba del parámetro de esfuerzo. |
| `06_scripts/` | Scripts de recolección, muestreo y lotes, codificación, verificación de citas, cálculo de acuerdo, análisis y armado del libro de códigos. |
| `07_resultados/` | Tablas que produce el análisis y las tres figuras del artículo. |

## 2. Corpus y embudo

El corpus reúne las notas con la expresión "inteligencia artificial" publicadas en Emol, La Tercera, BioBioChile, Cooperativa, CNN Chile y T13 entre el 1 de enero de 2019 y el 27 de septiembre de 2026. `embudo_corpus.csv` permite reproducir la Tabla 1 del artículo.

| Etapa | Notas |
|---|---|
| Universo recuperado, sin duplicados ni residuos de formato | 5.150 |
| Corpus en rango, tras excluir 23 notas de CNN Chile anteriores a 2019 | 5.127 |
| Población a codificar, tras excluir 75 notas sin mención de la IA y 11 sin texto ni mención en titular o bajada | 5.041 |
| Triaje de centralidad (531 tangenciales y 93 derivadas a la codificación completa) | 624 |
| Codificación completa | 4.510 |
| Notas tangenciales (531 del triaje y 581 de la codificación completa) | 1.112 |
| Corpus analítico (2.661 centrales y 1.268 secundarias) | 3.929 |
| Notas con codificación sustantiva (2.651 centrales y 1.111 secundarias) | 3.762 |

Las 23 notas de CNN Chile anteriores a 2019 se codificaron antes de recuperar su fecha de publicación y se excluyeron después. En `embudo_corpus.csv` figuran con la etapa `excluida_fuera_de_rango`.

## 3. Procedimiento

El corpus no fue codificado por personas. El autor fijó las tres dimensiones de la variable, el corpus y el período, y revisó y aprobó los ajustes que dieron origen a la versión 1.0 del libro de códigos. Entre ellos, las diez decisiones en que las propuestas de adjudicación del piloto eran opuestas y la promoción de seis categorías emergentes a códigos provisionales (indicadores 2.6 y 3.5).

La aplicación del libro la realizaron agentes del modelo de lenguaje Claude Sonnet 5.5 (Anthropic) el 7 de octubre de 2026, con el parámetro de esfuerzo en su valor por defecto. Una prueba con valores bajo y medio en dos lotes del piloto registró entre 18 % y 23 % menos códigos sustantivos que con el valor por defecto (`05_informes_de_acuerdo/piloto_v0.2/prueba_esfuerzo/`, sufijos L, M y Z, respectivamente). Cada agente recibió el libro completo y un lote de diez notas barajadas, con alias aleatorio y sin medio, fecha, autor, URL ni sección. Los lotes del piloto tenían ocho notas e incluían la sección. Las siete notas de más de 3.500 palabras se entregaron truncadas en ese límite. Las instrucciones pedían citas de no más de 50 palabras. Un validador exigió que cada cita fuera literal y rechazó las de más de 60, de modo que 3 de las 17.235 entradas con cita superan las 50 palabras (51, 56 y 56). La corrida principal sumó 478 lotes (444 principales, 10 de notas derivadas del triaje y 24 de confiabilidad), y el triaje 25 lotes.

El piloto aplicó la versión 0.2 a 160 notas estratificadas por período y medio, con dos instancias independientes del modelo (A y B). Un tercer agente diagnosticó los 244 desacuerdos (82 % por ambigüedad del libro, 11 % por juicio legítimo y 7 % por error). Sus informes por lote y la síntesis están en `diagnostico_desacuerdos/`. Las codificaciones del piloto no integran el registro final, porque sus 160 notas pasaron de nuevo por el procedimiento definitivo.

La validación aplicó la versión 1.0 a 240 notas estratificadas. La codificación que se conserva es la de la corrida principal (X), y la segunda (Y) solo se usó para medir el acuerdo. Veintisiete de esas notas habían formado parte del piloto. La recodificación con otro modelo (Claude Fable 5.1, 8 de octubre de 2026) aplicó la versión 1.0 a otras 120 notas, a ciegas, y comparte 2 notas con el piloto y 5 con la validación.

Todos los coeficientes de acuerdo se calcularon por script entre codificaciones automáticas. Miden la replicabilidad del procedimiento y no su validez. No hubo contrastación entre la codificación del modelo y la de codificadores humanos. Los coeficientes del piloto y de la validación se calcularon antes de excluir las 23 notas de CNN Chile anteriores a 2019, una de las cuales integraba la validación.

El libro de citas se armó con pools de candidatas por código y valoración, diversificados por período y medio. Agentes verificadores intentaron refutar cada candidata leyéndola en su contexto. De 1.545 candidatas, 1.106 resultaron aptas, 103 se corrigieron en valoración o voz y 336 se rechazaron. El libro conserva 566 citas.

## 4. Diccionario de datos

Valoración (`v`): `+` positiva, `-` negativa, `A` ambivalente, `C` contingente, `D` descriptiva, `NA` sin valoración. En el libro de citas y en el registro de la hoja Excel figuran con su nombre.

Voz (`voz`): `P` periodista o medio, `FE` fuente experta, `FC` fuente corporativa, `FG` fuente gubernamental, `FS` sociedad civil o ciudadanía, `FI` organismo internacional, `FM` voces en disputa, `na` códigos por defecto.

Centralidad (`c1`): central, secundaria o tangencial. Las demás variables de contexto (`c2` referente tecnológico, `c3` ámbito temático, `c4` actores nombrados y `c5` género) se definen en la hoja «Contexto y campos» del libro de códigos.

`registro_entradas_codificadas.csv`. Una fila por entrada con cita. `id` es el identificador vigente de la nota (`MEDIO_AAAAMMDD_NNN`) e `id_scraper` el original de CNN Chile antes de corregir su fecha. `dimension`, `indicador` y `cod` ubican el código. `marca` indica si la valoración es explícita o implícita. `calidad` va de 1 a 3. `cita` es el fragmento literal. `mod` reúne los modificadores del código en JSON. `url` enlaza a la nota.

`codificacion_completa_codigos.csv`. Mismas columnas, con todas las filas de la corrida principal en rango, incluidos los códigos por defecto (`cita_estado` = `no_requerida`).

`notas_codificadas.csv`. Una fila por nota con codificación completa. `c2` separa valores con punto y coma y `c4` con barra vertical. `emergentes` guarda en JSON las etiquetas que ningún código recogía. `dudas` registra la justificación del agente en las decisiones difíciles. `lote` identifica el lote de codificación.

`embudo_corpus.csv`. Una fila por nota del universo recuperado, con `etapa` (`excluida_fuera_de_rango`, `excluida_sin_mencion_ia`, `excluida_sin_texto_ni_ia_en_titular`, `triaje_tangencial`, `codificacion_completa_tras_triaje` o `codificacion_completa`), `c1`, `codificacion_sustantiva` y las marcas de pertenencia a las submuestras.

## 5. Qué no se incluye

Los textos completos de las notas no se distribuyen, porque son obras protegidas. Pueden recuperarse desde el enlace de cada nota y con los scripts de recolección. Por la misma razón no se incluyen los lotes que recibieron los agentes.

Tampoco se incluyen tres piezas que no se conservaron como archivos. El texto de las instrucciones del agente que diagnosticó los desacuerdos del piloto, cuyos informes sí se incluyen. El script que ensambló el libro de citas, cuyos pasos de selección y verificación sí se incluyen. Y el script de comparación de la recodificación con otro modelo, cuyos informes, métricas y tablas sí se incluyen.

## 6. Notas para reproducir

Los scripts de Python requieren pandas, numpy, scipy, statsmodels, matplotlib y openpyxl. Las rutas absolutas del equipo original se reemplazaron por `<RUTA_DEL_PROYECTO>`. Los scripts de análisis (`06_scripts/analisis/`) leen y escriben en las carpetas definidas por las variables `CORP`, `OUT`, `R` y `O`, que deben ajustarse. `analisis.py` construye el índice del corpus desde los archivos de texto. Ese índice se entrega en `07_resultados/tablas/corpus_indice_5127.csv`.

Los flujos `wf_*.js` orquestaron a los agentes en el entorno de Claude Code. Las funciones `agent`, `parallel`, `phase` y `log` pertenecen a ese entorno, de modo que los archivos documentan las instrucciones y la organización de los lotes, pero no se ejecutan como programas independientes.

Las frecuencias de las hojas «Códigos» y «Emergentes» del libro de códigos y del «Resumen por código» del libro de citas se regeneraron el 27 de noviembre de 2026 para el corpus en rango. Los porcentajes de los códigos se calculan sobre las 3.762 notas con codificación sustantiva y los de los códigos por defecto sobre las 3.929 del corpus analítico.

## 7. Avisos

La etiqueta «FONDECYT Pluralismo» que aparece en las instrucciones a los agentes y en algunos scripts era un nombre interno de trabajo. El estudio no recibió financiamiento específico.

Las citas son fragmentos breves de notas de prensa (de no más de 50 palabras, salvo tres entradas del registro, de hasta 56), que se incluyen con fines de investigación y con indicación de su fuente. Los derechos sobre esos textos pertenecen a sus medios y autores. Los nombres de personas y organizaciones que aparecen en las citas y en la variable `c4` provienen de notas publicadas.

## 8. Licencia y cita

Los instrumentos, la codificación, las tablas y la documentación se distribuyen bajo licencia Creative Commons Reconocimiento 4.0 Internacional (CC BY 4.0). Los scripts, bajo licencia MIT. La licencia no alcanza a las citas de terceros. Detalle en `LICENCIA.md`.

Para citar este material: Valdebenito Allendes, J. (2026). *Encuadre mediático de la inteligencia artificial en la prensa digital chilena (2019–2026). Instrumentos, registro de codificación y scripts* (versión 1.0) [Conjunto de datos]. [Repositorio y DOI por asignar.]
