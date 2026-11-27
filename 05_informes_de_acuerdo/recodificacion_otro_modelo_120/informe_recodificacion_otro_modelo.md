# Recodificación ciega de 120 notas y concordancia con la codificación original

Informe elaborado el 8 de octubre de 2026. Las cifras se calculan desde los archivos que acompañan este informe.

> Versión pública del 27 de noviembre de 2026. Se reemplazaron referencias a archivos internos de trabajo y se actualizó el solapamiento con las submuestras de control. Los métodos y las cifras no cambian.

## 1. Qué es y qué no es

Se codificaron de nuevo, a ciegas, 120 notas del corpus con el libro de códigos v1.0 (parte I) y se comparó el resultado con la codificación original del registro de citas. La segunda codificación la hicieron doce agentes (uno por lote de diez notas) con el modelo Claude Fable 5.1. La original la hicieron agentes con Claude Sonnet 5.5.

Esto mide **replicabilidad entre dos modelos distintos con el mismo libro**. No es doble codificación humana ni reemplaza una validación con codificadores humanos. Sirve para dos cosas. Cuantifica cuánto cambia el resultado según el codificador y señala las notas donde conviene mirar primero.

## 2. Muestra y procedimiento

La muestra no es la lista de 120 notas reservada para codificadores humanos. Se extrajo una muestra nueva con semilla fija (2026) en dos estratos. El estrato A reúne 100 notas con al menos una cita en el registro, repartidas en proporción a cada combinación de período y medio con un mínimo de 2 por celda. El estrato B reúne 20 notas sin citas en el registro, repartidas en proporción al medio.

| Período | Con citas en el registro | Sin citas en el registro |
|---|---|---|
| P1_2019-2021 | 10 | 0 |
| P2_2022 | 10 | 3 |
| P3_2023 | 17 | 3 |
| P4_2024 | 17 | 3 |
| P5_2025-2026 | 46 | 11 |

Por medio. La Tercera 40, Cooperativa 34, Emol 17, CNN Chile 13, BioBioChile 11 y T13 5. Los 13 casos de CNN se asignaron a su período con la fecha de publicación corregida y ninguno cambia de período respecto de la muestra.

Cada lote llevó diez notas barajadas, con alias y sin medio ni fecha. Cada agente leyó las instrucciones y el libro, y devolvió por nota las variables c1 a c5, los códigos con valoración, voz, marca, cita literal, calidad y modificadores, los emergentes y una línea de dudas. Seis lotes (03, 04, 05, 06, 09 y 11) se codificaron antes de la interrupción del trabajo y seis (01, 02, 07, 08, 10 y 12) después, con el mismo encargo y el mismo modelo.

**Control automático.** Las 12 salidas son JSON válidos. Las 633 citas aparecen literalmente en la nota y tienen 50 palabras o menos, todos los códigos existen en el libro, los campos obligatorios están completos, las notas tangenciales no llevan códigos y los códigos por defecto están asignados donde corresponde. No hubo incidencias.

## 3. Resultados

| Medida | Base | Resultado |
|---|---|---|
| Centralidad (c1) | 100 notas con códigos en el original | acuerdo 90,0 %, kappa 0,73 |
| Nota con al menos un código | 120 notas | acuerdo 96,7 %, kappa 0,87 |
| Presencia de código (nota por código) | 8.280 celdas | Dice 0,80, kappa 0,79 |
| Valoración en códigos comunes | 379 pares | acuerdo 86,8 %, kappa 0,80, alfa 0,80 |
| Voz en códigos comunes | 455 pares | acuerdo 82,9 %, kappa 0,75 |
| Valoración, si ambos citan el mismo fragmento | 306 pares | acuerdo 91,2 %, kappa 0,87 |
| Voz, si ambos citan el mismo fragmento | 366 pares | acuerdo 90,2 %, kappa 0,86 |
| Emergentes | 120 notas | 2 en el original frente a 29 en la nueva, 1 coincidencia |

El coeficiente de Dice vale 1 cuando ambas codificaciones asignan los mismos códigos a una nota y 0 cuando no coinciden en ninguno. Un par es una combinación nota por código. La unidad de comparación es la presencia del código en la nota, sin considerar cuántas veces se repite por objeto.

### 3.1 Qué códigos aparecen

La codificación original tiene 516 pares nota-código y la nueva 619. Coinciden 455, lo que equivale al 88,2 % de los originales. La nueva agrega 164 pares ausentes del original (26,5 % de sus pares) y omite 61. En total la nueva produce 633 entradas frente a 529, un 20 % más. La asimetría se concentra en pocos códigos.

| Código | Notas original | Notas nueva | En ambas | Dice |
|---|---|---|---|---|
| 2.1.HER | 34 | 50 | 33 | 0,79 |
| 3.1.EST | 4 | 11 | 4 | 0,53 |
| 2.1.MER | 12 | 19 | 12 | 0,77 |
| 3.4.EMP | 14 | 19 | 13 | 0,79 |
| 3.3.ADA | 12 | 17 | 12 | 0,83 |
| 2.1.AGE | 13 | 18 | 13 | 0,84 |
| 3.3.REG | 12 | 16 | 12 | 0,86 |
| 1.2.ECO | 4 | 8 | 4 | 0,67 |
| 2.2.SAL | 15 | 12 | 12 | 0,89 |
| 3.1.CON | 10 | 7 | 7 | 0,82 |
| 1.1.EST | 6 | 3 | 3 | 0,67 |
| 2.5.HYP | 7 | 5 | 5 | 0,83 |

Por indicador, según haya al menos un código de ese indicador en la nota.

| Indicador | Notas original | Notas nueva | En ambas | Acuerdo | Kappa |
|---|---|---|---|---|---|
| 1.1 | 52 | 54 | 46 | 88,3 % | 0,76 |
| 1.2 | 8 | 12 | 8 | 96,7 % | 0,78 |
| 1.3 | 2 | 5 | 2 | 97,5 % | 0,56 |
| 2.1 | 72 | 79 | 71 | 92,5 % | 0,84 |
| 2.2 | 50 | 49 | 46 | 94,2 % | 0,88 |
| 2.3 | 39 | 44 | 39 | 95,8 % | 0,91 |
| 2.4 | 12 | 13 | 9 | 94,2 % | 0,69 |
| 2.5 | 12 | 14 | 11 | 96,7 % | 0,83 |
| 2.6 | 16 | 23 | 14 | 90,8 % | 0,67 |
| 3.1 | 18 | 21 | 16 | 94,2 % | 0,79 |
| 3.2 | 10 | 12 | 8 | 95,0 % | 0,70 |
| 3.3 | 40 | 46 | 39 | 93,3 % | 0,86 |
| 3.4 | 40 | 46 | 39 | 93,3 % | 0,86 |
| 3.5 | 3 | 4 | 3 | 99,2 % | 0,85 |
| D1 | 53 | 56 | 47 | 87,5 % | 0,75 |
| D2 | 96 | 99 | 95 | 95,8 % | 0,86 |
| D3 | 45 | 53 | 43 | 90,0 % | 0,79 |

### 3.2 Centralidad

Las filas son la codificación original y las columnas la nueva.

| original \ nueva | central | secundaria | tangencial |
|---|---|---|---|
| central | 71 | 6 | 0 |
| secundaria | 4 | 19 | 0 |

De las 20 notas sin citas en el original, la nueva codificación clasificó 14 como tangenciales y 6 como secundarias. Cuatro de ellas recibieron códigos (ver sección 5).

### 3.3 Valoración

Se comparan los 379 pares con valoración (se excluyen 3.4, que no valora, y 26 pares sin valoración en ambas codificaciones). Filas original, columnas nueva.

| original \ nueva | + | - | A | C | D |
|---|---|---|---|---|---|
| + | 130 | 0 | 1 | 0 | 13 |
| - | 0 | 80 | 0 | 0 | 6 |
| A | 1 | 0 | 2 | 0 | 3 |
| C | 1 | 0 | 0 | 0 | 0 |
| D | 19 | 6 | 0 | 0 | 117 |

No hay ninguna inversión de signo entre positivo y negativo en 210 pares polares. De las 50 discrepancias, 44 son entre descriptivo y valorativo, es decir, una codificación ve una marca de valoración y la otra solo registra el hecho. Van en ambos sentidos. En 25 casos el original describe y la nueva valora, y en 19 ocurre lo inverso.

### 3.4 Voz

Filas original, columnas nueva, sobre 455 pares comunes.

| original \ nueva | P | FE | FC | FG | FS | FI | FM |
|---|---|---|---|---|---|---|---|
| P | 205 | 7 | 5 | 3 | 1 | 0 | 0 |
| FE | 8 | 73 | 4 | 1 | 11 | 1 | 0 |
| FC | 15 | 1 | 52 | 0 | 0 | 0 | 0 |
| FG | 3 | 0 | 0 | 23 | 0 | 1 | 1 |
| FS | 0 | 1 | 0 | 11 | 22 | 0 | 0 |
| FI | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| FM | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Hay 78 discrepancias. Las cuatro confusiones más frecuentes, de la codificación original a la nueva, son FC (corporativa) a P (medio) en 15 pares de 10 notas, FE (experta) a FS (sociedad civil) en 11 pares de 2 notas (N062, N070), FS (sociedad civil) a FG (autoridad) en 11 pares de 1 nota (N114) y FE (experta) a P (medio) en 8 pares de 7 notas. Algunas se concentran en muy pocas notas con fuentes ambiguas.

### 3.5 Valoración y voz según el fragmento citado

Valoración y voz se asignan al fragmento que cita cada codificador. Si para un mismo código eligieron tramos distintos, pueden diferir sin que haya desacuerdo sobre el mismo texto. Se consideró el mismo fragmento cuando uno contiene al otro o comparten al menos la mitad de sus palabras distintas.

| Pares comunes | Pares | Voz, acuerdo | Voz, kappa | Pares con valoración | Valoración, acuerdo | Valoración, kappa |
|---|---|---|---|---|---|---|
| Mismo fragmento | 366 | 90,2 % | 0,86 | 306 | 91,2 % | 0,87 |
| Fragmento distinto | 89 | 52,8 % | 0,31 | 73 | 68,5 % | 0,52 |

Cuando ambos citan el mismo fragmento, voz y valoración coinciden en alrededor del 90 %. Con fragmentos distintos el acuerdo cae a 53 % en voz y 68 % en valoración. Esos 89 pares son el 20 % de los comunes y concentran 42 de las 78 discrepancias de voz y 23 de las 50 de valoración.

### 3.6 Emergentes y género

La nueva codificación registró 29 emergentes en 9 etiquetas (fuente_consultable 9, democratizadora_acceso 6, ia_superior_humano 5, infraestructura_cotidiana 3, autoevolucion_ia 2, referente_ficcional 1, confianza_publica_legitimidad 1, regulacion_habilitante 1, vigilancia_normalizada 1), todas de la lista en vigilancia del libro. El registro original contiene 2 emergentes en estas notas, y 1 coincide en nota y etiqueta. Es el punto de menor acuerdo y reproduce la limitación del anclaje en la lista de etiquetas en vigilancia.

La nueva codificación incluye el género periodístico (c5) de las 120 notas (noticia 88, columna_opinion 11, reportaje 7, contenido_patrocinado 6, otro 5, entrevista 3). No hay contraparte original porque el registro entregado no trae c2 a c5.

### 3.7 Por período y por centralidad

Coincidencia media (Dice) por nota entre las 100 notas con citas.

| Período | Notas | Dice medio |
|---|---|---|
| P1_2019-2021 | 10 | 0,85 |
| P2_2022 | 10 | 0,71 |
| P3_2023 | 17 | 0,78 |
| P4_2024 | 17 | 0,81 |
| P5_2025-2026 | 46 | 0,78 |

Las notas centrales coinciden más (Dice medio 0,83) que las secundarias (0,65). Con pocos códigos por nota cada discrepancia pesa más en el Dice. Con 10 a 46 notas por período no se interpretan diferencias entre períodos.

### 3.8 Referencia con el piloto

| Medida | Piloto (160 notas, libro v0.2, dos instancias del mismo modelo) | Esta recodificación (120 notas, libro v1.0, dos modelos distintos) |
|---|---|---|
| Centralidad c1, kappa | 0,90 | 0,73 (sobre 100 notas) |
| Valoración, alfa de Krippendorff | 0,89 | 0,80 (sobre 379 pares) |
| Signo positivo o negativo cuando ambos asignan signo | 100 % (n = 294) | 100 % (n = 210) |
| Kappa por indicador | media por indicador entre 0,70 y 0,96 | presencia por indicador entre 0,56 y 0,91 |

Las medidas no se definen igual y las muestras difieren, por lo que la comparación es solo orientativa. Las cifras de esta recodificación son más bajas en centralidad y valoración. Una parte puede deberse al cambio de modelo, pero con estas muestras no puede separarse de otras causas, como el paso del libro v0.2 al v1.0.

## 4. Lectura

**Dato.** La segunda codificación reproduce el 88 % de los pares nota-código originales y agrega otros 164. En los códigos comunes no hay inversiones de signo y la discrepancia en valoración se da en su mayor parte entre descriptivo y valorativo, en ambos sentidos. La voz coincide en 83 %. Cuando ambos citan el mismo fragmento, voz y valoración coinciden en cerca de 90 %, y con fragmentos distintos el acuerdo cae a 53 % y 68 %. Los emergentes casi no coinciden.

**Interpretación (hipótesis).** La diferencia parece de umbral y no de sentido. El segundo codificador aplica con más frecuencia unos pocos códigos (2.1.HER, 3.1.EST, 2.1.MER, 3.4.EMP, 3.3.ADA), y la ausencia de inversiones de signo apunta a que ambos codificadores entienden los códigos de modo semejante. En voz y valoración, la elección del fragmento explica buena parte de la diferencia, de modo que la regla de selección de la cita (secciones 5 y 5.1 del libro) sería el punto a afinar si se quiere que estas variables sean estables entre codificadores. Se puede contrastar revisando las 164 citas de `codigos_en_una_sola_codificacion.csv`. Hay una explicación alternativa que los materiales no permiten descartar. El registro original pasó por una verificación posterior de citas que pudo eliminar entradas, y parte del exceso de la nueva codificación sería entonces un efecto de esa depuración.

**Límites.**

- Es replicabilidad entre modelos con el mismo libro, no validez frente a codificadores humanos.
- La muestra no es la lista reservada para humanos.
- La muestra comparte 2 notas con el piloto de 160 notas con que se ajustó el libro y 5 con la validación de 240 notas. El solapamiento con el piloto puede aumentar el acuerdo.
- El registro original no trae c2 a c5 ni los códigos por defecto. Solo se compararon c1, presencia de códigos, valoración y voz.
- La voz y la valoración dependen del fragmento citado. Por eso su acuerdo se informa también separando los pares con el mismo fragmento (sección 3.5). El criterio de "mismo fragmento" es operativo y lo definió este análisis.
- Hay 19 pares con entradas repetidas por objeto. Se compararon por su primera entrada.
- Con 5 a 40 notas por medio no se interpretan diferencias entre medios.

## 5. Notas para revisar primero

Las diez notas con menor coincidencia entre las que tienen citas en el original.

| Alias | ID | Medio | c1 original | c1 nueva | Códigos original | Códigos nueva | Comunes | Dice |
|---|---|---|---|---|---|---|---|---|
| N012 | EMOL_20220412_001 | Emol | secundaria | secundaria | 2 | 1 | 0 | 0,00 |
| N107 | LT_20260903_003 | La Tercera | secundaria | secundaria | 1 | 2 | 0 | 0,00 |
| N109 | LT_20260602_002 | La Tercera | secundaria | central | 2 | 4 | 1 | 0,33 |
| N068 | CNN_20190815_001 | CNN Chile | secundaria | central | 1 | 5 | 1 | 0,33 |
| N036 | COOP_20240619_001 | Cooperativa | central | secundaria | 6 | 4 | 2 | 0,40 |
| N086 | COOP_20251029_003 | Cooperativa | secundaria | central | 2 | 7 | 2 | 0,44 |
| N032 | COOP_20260116_002 | Cooperativa | secundaria | secundaria | 1 | 3 | 1 | 0,50 |
| N067 | COOP_20260727_001 | Cooperativa | secundaria | secundaria | 1 | 3 | 1 | 0,50 |
| N091 | BBC_20230608_001 | BioBioChile | secundaria | secundaria | 1 | 3 | 1 | 0,50 |
| N052 | LT_20230723_001 | La Tercera | central | central | 3 | 5 | 2 | 0,50 |

Cuatro notas sin citas en el original recibieron códigos en la nueva.

| Alias | ID | Medio | c1 nueva | Códigos nueva | Códigos |
|---|---|---|---|---|---|
| N028 | T13_20240202_001 | T13 | secundaria | 1 | 2.1.AGE |
| N035 | LT_20260408_002 | La Tercera | secundaria | 3 | 1.2.GEO 1.3.IRR 2.6.ACT |
| N073 | EMOL_20260924_001 | Emol | secundaria | 1 | 2.6.IMI |
| N087 | LT_20251208_001 | La Tercera | secundaria | 2 | 2.1.HER 2.1.INN |

## 6. Archivos

| Archivo | Contenido |
|---|---|
| `recodificacion_ciega_120_notas.json` | Codificación completa de las 120 notas (c1 a c5, códigos, emergentes, dudas) con ID vigente |
| `recodificacion_ciega_codigos.csv` | Un registro por código aplicado, con cita |
| `recodificacion_ciega_emergentes.csv` | Los 29 emergentes |
| `comparacion_por_nota.csv` | Por nota. Códigos originales y nuevos, diferencias, Dice y dudas del codificador |
| `pares_codigos_comunes.csv` | Los 455 pares comunes con valoración, voz y cita de cada codificación e indicador de mismo fragmento |
| `codigos_en_una_sola_codificacion.csv` | Los 225 pares presentes en una sola codificación, con su cita |
| `concordancia_por_codigo.csv`, `concordancia_por_indicador.csv`, `metricas.json` | Medidas de acuerdo |
| `clave_alias_id.csv` | Alias de las notas con el ID original y el vigente |
| `INSTRUCCIONES_codificador.md` | Encargo entregado a los codificadores |
