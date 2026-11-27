"""
Construcción del libro de códigos final - Corpus IA Chile
Uso: python construir_libro_codigos.py <prefijo_codigos>
Parte I: texto operativo v1.0. Anexos: frecuencias por código con ejemplo real, confiabilidad, emergentes y versiones.
Salida: 04 codigo/libro_de_codigos.md
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_nombres import CODIGOS, DIMENSIONES, INDICADORES  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
SALIDA = RAIZ / "04 codigo"
ORDEN_V = ["+", "-", "A", "C", "D", "NA"]


def f2(x):
    return "—" if x is None else f"{x:.2f}"


def main():
    prefijo = sys.argv[1]
    filas = list(csv.DictReader(open(COD / f"{prefijo}_codigos.csv", encoding="utf-8-sig")))
    notas = [json.loads(l) for l in open(COD / f"{prefijo}_notas.jsonl", encoding="utf-8")]
    activas = [f for f in filas if f["c1"] in ("central", "secundaria")]
    n_activas = len({f["id"] for f in activas})
    n_notas = defaultdict(set)
    dist_v = defaultdict(Counter)
    for f in activas:
        n_notas[f["cod"]].add(f["id"])
        dist_v[f["cod"]][f["v"]] += 1

    sel = {}
    p = RAIZ / "citas_trabajo" / "seleccion_final.json"
    if p.exists():
        sel = json.load(open(p, encoding="utf-8"))

    def ejemplo(cod):
        cel = sel.get(cod, {})
        mejor = None
        for v, lista in cel.items():
            for c in lista:
                clave = (c.get("repr", 1), c.get("calidad", 0), -len(c["cita"]))
                if mejor is None or clave > mejor[0]:
                    mejor = (clave, c)
        return mejor[1] if mejor else None

    acu_pil = json.load(open(COD / "acuerdo_piloto_v02.json", encoding="utf-8")) if (COD / "acuerdo_piloto_v02.json").exists() else None
    acu_val = json.load(open(COD / "acuerdo_validacion_v10.json", encoding="utf-8")) if (COD / "acuerdo_validacion_v10.json").exists() else None

    texto = (COD / "libro_codigos_operativo_v1.0.md").read_text(encoding="utf-8")
    cuerpo = texto.split("\n", 1)[1]
    cuerpo = cuerpo.replace("(instrucciones para el codificador)", "")

    L = []
    L.append("# Libro de códigos: encuadre mediático de la inteligencia artificial en la prensa chilena (v1.0)\n")
    L.append(f"Proyecto FONDECYT Pluralismo. Versión generada el {date.today().isoformat()}. Corpus: Emol, La Tercera, BioBioChile, Cooperativa, CNN Chile y T13, enero de 2019 a septiembre de 2026.\n")
    L.append("## Estructura de la variable\n")
    L.append("Variable: **encuadre mediático de la inteligencia artificial en la prensa** → Dimensión → Indicador → Código (con valoración, voz, marca y cita). Las categorías se plantearon como hipótesis orientadoras (ver `operacionalizacion_encuadre_IA.md`), se ajustaron con un piloto y el corpus mismo, y quedan abiertas a categorías emergentes.\n")
    L.append("| Dimensión | Indicador | Códigos |")
    L.append("|---|---|---|")
    por_ind = defaultdict(list)
    for c in CODIGOS:
        por_ind[c.rsplit(".", 1)[0]].append(c.rsplit(".", 1)[1])
    for ind, cs in por_ind.items():
        dim = "D" + ind.split(".")[0]
        L.append(f"| {dim} {DIMENSIONES[dim]} | {ind} {INDICADORES[ind]} | {', '.join(cs)} |")
    L.append("")
    L.append(f"El libro tiene {len(CODIGOS)} códigos, cinco variables de contexto (c1 a c5) y cuatro campos por código aplicado (valoración, voz, marca, cita). La unidad de codificación es la nota.\n")
    L.append("---\n")
    L.append("# Parte I. Reglas de codificación\n")
    L.append(cuerpo.replace("\n## ", "\n## ").replace("\n# ", "\n# "))

    L.append("\n---\n")
    L.append("# Parte II. Anexos\n")
    L.append("## Anexo A. Frecuencia de los códigos y ejemplo del corpus\n")
    L.append(f"Notas con codificación sustantiva (centrales o secundarias): **{n_activas}**. La columna *Notas* cuenta notas en las que el código aparece al menos una vez; los porcentajes son sobre esas {n_activas} notas. Los códigos por defecto (1.3.SIN, 3.1.NIN, 3.2.NEX, 3.3.NIN) indican ausencia del contenido correspondiente. El ejemplo es una cita real verificada del corpus.\n")
    L.append("| Código | Nombre | Notas | % | Valoraciones | Ejemplo (verificado) |")
    L.append("|---|---|---:|---:|---|---|")
    for cod, (nombre, _def) in CODIGOS.items():
        n = len(n_notas.get(cod, ()))
        dv = ", ".join(f"{v} {dist_v[cod][v]}" for v in ORDEN_V if dist_v[cod][v]) or "—"
        e = ejemplo(cod)
        ej = f"«{e['cita']}» ({e['medio']}, {e['fecha']})".replace("|", "/") if e else "—"
        L.append(f"| `{cod}` | {nombre} | {n} | {100 * n / max(1, n_activas):.1f} | {dv} | {ej} |")
    L.append("")

    bajos = [(c, len(n_notas.get(c, ()))) for c in CODIGOS if len(n_notas.get(c, ())) < 10 and c not in ("1.3.SIN", "3.1.NIN", "3.2.NEX", "3.3.NIN")]
    L.append("**Códigos sin uso o con muy poco uso en el corpus**: " + ", ".join(f"`{c}` ({n} nota{'' if n == 1 else 's'})" for c, n in bajos) + ". Que un código casi no aparezca es un resultado empírico (la prensa rara vez construye esa atribución) y no un defecto del libro; se mantienen porque corresponden a hipótesis teóricas del diseño, pero se recomienda no analizarlos de forma cuantitativa por separado.\n")
    L.append("**Cobertura de los códigos por defecto.** Los indicadores 1.3 (origen), 3.1 (futuro proyectado), 3.2 (modalidad) y 3.3 (acción) quedan en su valor por defecto en la mayoría de las notas (ver filas `1.3.SIN`, `3.1.NIN`, `3.2.NEX`, `3.3.NIN`). D1 y parte de D3 discriminan, por tanto, solo en una minoría de notas.\n")
    L.append("## Anexo B. Confiabilidad\n")
    L.append("**Advertencia.** El acuerdo se midió entre dos codificadores independientes que son instancias del mismo modelo de IA, con el mismo libro y sin comunicación entre sí. Mide la **replicabilidad del procedimiento**, no la validez frente a un codificador humano, y puede sobrestimar el acuerdo que alcanzarían personas con formaciones distintas. Se recomienda validar una submuestra con codificadores humanos (ver `validacion_humana_ids.json`).\n")

    def tabla_acuerdo(a, titulo):
        L.append(f"### {titulo}\n")
        L.append(f"Notas comparadas: {a['n_notas_comunes']} (con codificación sustantiva para al menos un codificador: {a['n_notas_activas']}).\n")
        L.append(f"- Centralidad (c1): kappa de Cohen {f2(a['c1']['cohen'])}, acuerdo {a['c1']['acuerdo']:.0%}.")
        L.append(f"- Ámbito (c3): kappa {f2(a['c3']['cohen'])}; género (c5): kappa {f2(a['c5']['cohen'])}.")
        v = a["valoracion"]
        L.append(f"- Valoración (v) en códigos presentes en ambos: {v['n_pares']} pares, acuerdo {v['acuerdo']:.0%}, alfa de Krippendorff {f2(v['alfa_krippendorff'])}.")
        if a.get("valoracion_dicotomica_signo"):
            s = a["valoracion_dicotomica_signo"]
            L.append(f"- Signo (+/-) cuando ambos asignan positivo o negativo: acuerdo {s['acuerdo']:.0%} (n = {s['n']}).")
        m = a["modificadores_2_3"]
        L.append(f"- Modificadores de 2.3: intensidad `g` {m['g']['acuerdo']:.0%}, responsable `resp` {m['resp']['acuerdo']:.0%}.\n")
        L.append("| Indicador | Códigos evaluados | Kappa medio | AC1 de Gwet medio | Acuerdo medio |")
        L.append("|---|---:|---:|---:|---:|")
        for ind, m in a["por_indicador"].items():
            L.append(f"| {ind} {INDICADORES.get(ind, '')} | {m['n_codigos']} | {f2(m['kappa_medio'])} | {f2(m['ac1_medio'])} | {m['acuerdo_medio']:.2f} |")
        L.append("")
        L.append("Códigos con kappa inferior a 0,70 (y al menos 4 usos entre ambos codificadores):\n")
        malos = [(c, m) for c, m in a["por_codigo"].items() if m["kappa"] is not None and m["kappa"] < 0.70 and (m["n_A"] + m["n_B"]) >= 4]
        if malos:
            for c, m in sorted(malos, key=lambda x: x[1]["kappa"]):
                L.append(f"- `{c}` {CODIGOS.get(c, ('',))[0]}: kappa {m['kappa']:.2f} (A = {m['n_A']}, B = {m['n_B']}, ambos = {m['n_ambos']}).")
        else:
            L.append("- Ninguno.")
        L.append("")

    if acu_pil:
        tabla_acuerdo(acu_pil, "B.1 Piloto con el libro v0.2 (160 notas, codificadores A y B)")
    if acu_val:
        tabla_acuerdo(acu_val, "B.2 Validación con el libro v1.0 (submuestra estratificada, codificadores X e Y)")

    L.append("### B.3 Cómo leer estas cifras\n")
    L.append("- **Paradoja del kappa.** En los indicadores 1.3 y 3.2, y en los códigos por defecto, un valor domina el 90 % o más de las notas. Con esa prevalencia, el kappa de Cohen cae aunque el acuerdo observado sea muy alto (acuerdo medio de 0,97 a 0,99, AC1 de Gwet de 0,97 a 0,98). Para estos códigos conviene leer AC1 y acuerdo, no solo kappa.")
    L.append("- **Puntos débiles reales.** Los códigos poco frecuentes de los indicadores 3.2 (DEC), 2.4 (DIS, CTX) y 1.3 (IRR) tienen pocos casos compartidos y kappa bajo; sus definiciones dependen de fórmulas lingüísticas explícitas y deben revisarse con codificadores humanos antes de analizarlos cuantitativamente.")
    L.append("- **Comparación entre versiones.** Entre el piloto (v0.2) y la validación (v1.0) el kappa medio sube en 2.1 (de 0,82 a 0,87), 2.3 (de 0,85 a 0,93) y 3.4 (de 0,70 a 0,87), y baja en 1.3 y 3.2. La comparación es orientativa: las muestras y los libros son distintos.")
    L.append("- **Valoración.** El signo (+ o -) coincide en el 100 % de los pares en ambas mediciones; las discrepancias de valoración se concentran en distinguir `D` (descriptiva) de `+` o `-`, que depende del umbral de marca valorativa (3.1).\n")
    L.append("## Anexo C. Categorías emergentes\n")
    ep = RAIZ / "emergentes_consolidados.json"
    if ep.exists():
        e = json.load(open(ep, encoding="utf-8"))
        L.append("| Etiqueta | Definición | Notas | Recomendación |")
        L.append("|---|---|---:|---|")
        for it in e.get("categorias", []):
            L.append(f"| {it['etiqueta']} | {it['definicion']} | {it.get('n_notas', '?')} | {it.get('recomendacion', '')} |")
        L.append("")
    else:
        L.append("_Pendiente de consolidar._\n")

    L.append("## Anexo D. Control de versiones\n")
    L.append("| Versión | Cambios |")
    L.append("|---|---|")
    L.append("| 0.1 | Traducción de la operacionalización a instrucciones de codificación: 63 códigos base, variables de contexto c1 a c5, campos v, voz, marca y cita. |")
    L.append("| 0.2 | Seis aclaraciones tras una prueba de humo con un lote (c1, c5, voz, 1.3.IRR, 2.1.LIM, 3.3 y 3.4, citas con puntos suspensivos). |")
    L.append("| 1.0 | Tras el piloto de doble codificación (160 notas, 244 desacuerdos diagnosticados: 82 % por ambigüedad del libro, 11 % por juicio legítimo, 7 % por error): unidad de registro (5.1); test de dos condiciones; umbrales de marca valorativa; alcance de D1; umbrales de HER e INN; delimitación de 3.3 y 3.4; nuevos ámbitos 2.2.SEG, 2.2.AMB, 2.3.SAL, 2.3.AMB, 2.3.EST; `resp` = RUS; c3 `consumo_cotidiano`; seis emergentes promovidos a códigos provisionales (2.6.REC, 2.6.IMI, 2.6.PCH, 2.6.FAH, 2.6.ACT, 3.5.REZ); lista cerrada de etiquetas emergentes. |")
    L.append("")
    L.append("**Decisiones de diseño tomadas al pasar de v0.2 a v1.0** (propuestas opuestas en el piloto): una entrada por código y objeto en lugar de una por fragmento; REG coexiste con CON o PRO cuando el texto detalla la restricción; `global` significa agente extranjero o transnacional; 1.1 admite modelos o sistemas de IA propios con verbo de agencia, pero 1.2 y 1.3 solo la IA como tecnología o campo; 2.2 y 2.3 admiten `D` solo en registro puramente informativo; `contenido_patrocinado` se define por fuente única más lenguaje promocional; el campo `seccion` no se entrega a los codificadores; en 3.3.ADA el actor es el ofertante y el individuo solo con exhortación expresa; la adopción de IA por una institución es 3.3.ADO pero la inversión de una empresa en su propio negocio no. **Fusiones no aplicadas** (HER con INN, CON con PRO, 3.2 como modificador, eliminación de 2.5.AMB y de los códigos sin uso en el piloto): se reevalúan con los datos de la validación.\n")
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "libro_de_codigos.md").write_text("\n".join(L), encoding="utf-8")
    print("Libro de códigos escrito:", SALIDA / "libro_de_codigos.md")


if __name__ == "__main__":
    main()
