"""
Genera 04 codigo/libro_de_codigos.xlsx (libro de códigos v1.0 con frecuencias, ejemplos y confiabilidad).
Uso (desde 20 PLURALISMO): python codificacion/xlsx_libro_codigos.py
"""

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_nombres import CODIGOS, DIMENSIONES, INDICADORES  # noqa: E402
from reglas_codigos import CAMPOS, CONTEXTO, PRINCIPIOS, REGLA_COD, REGLA_IND  # noqa: E402
from utilidades_codificacion import CATALOGO  # noqa: E402
from xlsx_comun import *  # noqa: E402,F403

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
SALIDA = RAIZ / "04 codigo" / "libro_de_codigos.xlsx"
DIM_TXT = {"D1": "D1 Origen", "D2": "D2 Carácter", "D3": "D3 Horizonte"}
POR_DEFECTO = ("1.3.SIN", "3.1.NIN", "3.2.NEX", "3.3.NIN")


def main():
    filas = list(csv.DictReader(open(COD / "completo_codigos.csv", encoding="utf-8-sig")))
    activas = [f for f in filas if f["c1"] in ("central", "secundaria")]
    n_act = len({f["id"] for f in activas})
    n_corpus = sum(1 for _ in open(RAIZ / "corpus_maestro.jsonl", encoding="utf-8"))
    n_notas, dist_v = defaultdict(set), defaultdict(Counter)
    for f in activas:
        n_notas[f["cod"]].add(f["id"])
        dist_v[f["cod"]][f["v"]] += 1
    sel = json.load(open(RAIZ / "citas_trabajo" / "seleccion_final.json", encoding="utf-8"))
    acu_p = json.load(open(COD / "acuerdo_piloto_v02.json", encoding="utf-8"))
    acu_v = json.load(open(COD / "acuerdo_validacion_v10.json", encoding="utf-8"))
    emerg = json.load(open(RAIZ / "emergentes_consolidados.json", encoding="utf-8"))

    def ejemplo(cod):
        mejor = None
        for lista in sel.get(cod, {}).values():
            for c in lista:
                k = (c.get("repr", 1), c.get("calidad", 0), -len(c["cita"]))
                if mejor is None or k > mejor[0]:
                    mejor = (k, c)
        return mejor[1] if mejor else None

    wb = Workbook()

    # ---------------- Léeme ----------------
    ws = wb.active
    ws.title = "Léeme"
    anchos(ws, [30, 110])
    titulo(ws, "Libro de códigos: encuadre mediático de la inteligencia artificial en la prensa chilena (v1.0)",
           f"Proyecto FONDECYT Pluralismo · generado el {date.today().isoformat()}")
    r = 4
    r = seccion(ws, r, "Qué es este libro")
    textos = [
        "Instrumento para codificar notas de prensa sobre inteligencia artificial (IA) en Emol, La Tercera, BioBioChile, Cooperativa, CNN Chile y T13, de enero de 2019 a septiembre de 2026. La variable es el encuadre mediático de la IA, con tres dimensiones: D1 Origen, D2 Carácter y D3 Horizonte. La unidad de codificación es la nota.",
        "Cada código aplicado lleva una valoración (+, -, A ambivalente, C contingente, D descriptiva, NA sin valoración), la voz que enuncia el fragmento, la marca de la valoración (explícita o implícita) y una cita literal de la nota. Presencia y valoración son cosas distintas: mencionar 'regulación' o 'innovación' no implica ninguna valoración.",
        f"Estructura: 3 dimensiones, {len(INDICADORES)} indicadores, {len(CODIGOS)} códigos, 5 variables de contexto (c1 a c5) y 5 campos por código. Las categorías se plantearon como hipótesis orientadoras, se ajustaron con un piloto de doble codificación y quedan abiertas a categorías emergentes.",
    ]
    for t in textos:
        c = ws.cell(row=r, column=1, value=t)
        c.font, c.alignment = F_BASE, AL_TXT
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = estimar_alto(t, 140)
        r += 1
    r += 1
    r = seccion(ws, r, "Hojas del libro")
    encabezado(ws, r, ["Hoja", "Contenido"], alto=20)
    hojas = [
        ("Estructura", "Dimensiones e indicadores con su regla general, si aplica valoración, modificadores y exigencia de cita."),
        ("Códigos", "Una fila por código: definición, regla de inclusión, exclusiones, modificadores, frecuencia en el corpus, distribución de valoraciones y un ejemplo real verificado. Tiene filtros."),
        ("Contexto y campos", "Variables de contexto c1 a c5 y campos que acompañan a cada código (valoración, voz, marca, cita, calidad)."),
        ("Principios", "Principios de codificación, unidad de registro y manejo de residuos del scraper."),
        ("Confiabilidad", "Acuerdo entre codificadores en el piloto (v0.2) y en la validación (v1.0): resumen, por indicador y por código."),
        ("Emergentes", "Categorías que los codificadores registraron y que ningún código recogía, con frecuencia, recomendación y una cita."),
        ("Versiones", "Historial de versiones y decisiones de diseño."),
    ]
    r = filas_tabla(ws, r + 1, hojas)
    r += 1
    r = seccion(ws, r, "Advertencias")
    adv = [
        "La codificación del corpus fue realizada por agentes de IA (Claude Sonnet 5.5) siguiendo este libro, no por codificadores humanos. El acuerdo entre codificadores se midió entre dos instancias del mismo modelo: mide la replicabilidad del procedimiento, no su validez frente a personas. Se recomienda validar una submuestra con codificadores humanos.",
        f"Las frecuencias de la hoja 'Códigos' se calcularon sobre {n_act:,} notas con codificación sustantiva (centrales o secundarias) de un corpus de {n_corpus:,} notas.".replace(",", ".") + " La cobertura por medio y año es desigual (T13 solo desde fines de 2023, pocas notas entre 2019 y 2022). Las fechas de CNN Chile se corrigieron con su fecha real de publicación.",
        "Los porcentajes y los recuentos de la hoja 'Estructura' son fórmulas que se recalculan al abrir el archivo; el resto de las cifras son valores calculados desde el corpus codificado (archivo completo_codigos.csv).",
    ]
    for t in adv:
        c = ws.cell(row=r, column=1, value=t)
        c.font, c.alignment = F_BASE, AL_TXT
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = estimar_alto(t, 140)
        r += 1
    for rr in range(1, ws.max_row + 1):
        if ws.cell(row=rr, column=2).value and ws.cell(row=rr, column=2).alignment.wrap_text and not ws.cell(row=rr, column=2).font.bold:
            ws.row_dimensions[rr].height = max(ws.row_dimensions[rr].height or 15, estimar_alto(ws.cell(row=rr, column=2).value, 110))

    # ---------------- Códigos ----------------
    wc = wb.create_sheet("Códigos")
    cab = ["Dimensión", "Indicador", "Código", "Nombre", "Definición", "Regla de codificación (incluye)", "Excluye / frontera",
           "Valoración", "Modificadores obligatorios", "¿Cita?", "Notas (n)", "% de notas", "+", "-", "A", "C", "D", "NA",
           "Ejemplo del corpus (cita verificada)", "Medio", "Fecha", "ID de la nota"]
    anchos(wc, [11, 9, 10, 26, 44, 52, 44, 11, 22, 11, 9, 9, 6, 6, 6, 6, 6, 6, 64, 13, 11, 19])
    titulo(wc, "Códigos", "Una fila por código. Frecuencias sobre las notas con codificación sustantiva (centrales o secundarias).")
    wc.cell(row=3, column=1, value="Notas con codificación sustantiva:").font = F_NEG
    wc.merge_cells("A3:C3")
    n_cell = wc.cell(row=3, column=4, value=n_act)
    n_cell.font, n_cell.number_format, n_cell.alignment = F_NEG, "#,##0", Alignment(horizontal="left")
    encabezado(wc, 5, cab, alto=34)
    datos = []
    MAP = mapa_ids()
    for cod, (nombre, definicion) in CODIGOS.items():
        ind = CATALOGO[cod]["ind"]
        dim = DIM_TXT["D" + ind.split(".")[0]]
        regla, excl = REGLA_COD.get(cod, ("", ""))
        mods = ", ".join(CATALOGO[cod]["mods"]) or "—"
        val = "Aplica" if CATALOGO[cod]["aplica_v"] else "NA"
        if ind == "3.3":
            val = "Aplica (valora la medida)" if CATALOGO[cod]["aplica_v"] else "NA"
        cita = "Sí" if CATALOGO[cod]["cita"] else "No (por defecto)"
        e = ejemplo(cod)
        dv = dist_v.get(cod, Counter())
        datos.append([dim, ind, cod, nombre, definicion, regla, excl or "—", val, mods, cita, len(n_notas.get(cod, ())), None,
                      dv["+"], dv["-"], dv["A"], dv["C"], dv["D"], dv["NA"],
                      e["cita"] if e else "—", e["medio"] if e else "—", e["fecha"] if e else "—", MAP.get(e["id_nota"], e["id_nota"]) if e else "—"])
    r0 = 6
    filas_tabla(wc, r0, datos, alineacion={2: AL_CEN, 3: AL_CEN, 8: AL_CEN, 10: AL_CEN, 11: AL_NUM, 12: AL_NUM,
                                          13: AL_NUM, 14: AL_NUM, 15: AL_NUM, 16: AL_NUM, 17: AL_NUM, 18: AL_NUM, 21: AL_CEN},
                formatos={11: "#,##0", 12: "0.0%", 13: "#,##0", 14: "#,##0", 15: "#,##0", 16: "#,##0", 17: "#,##0", 18: "#,##0"})
    for i, fila in enumerate(datos):
        r = r0 + i
        wc.cell(row=r, column=12, value=f"=IFERROR(K{r}/$D$3,0)")
        wc.cell(row=r, column=3).font = F_NEG
        h = max(estimar_alto(fila[4], 44), estimar_alto(fila[5], 52), estimar_alto(fila[6], 44), estimar_alto(fila[18], 64), estimar_alto(fila[3], 26))
        wc.row_dimensions[r].height = min(h, 220)
    ultimo = r0 + len(datos) - 1
    wc.freeze_panes = "E6"
    wc.auto_filter.ref = f"A5:V{ultimo}"

    # ---------------- Estructura ----------------
    we = wb.create_sheet("Estructura", 1)
    anchos(we, [13, 10, 40, 80, 18, 40, 16, 12])
    titulo(we, "Estructura de la variable", "Variable → Dimensión → Indicador → Código")
    encabezado(we, 4, ["Dimensión", "Indicador", "Nombre del indicador", "Regla general", "Valoración", "Modificadores", "¿Cita?", "N.º de códigos"], alto=30)
    est = []
    for ind, nombre in INDICADORES.items():
        regla, val, mod, cita = REGLA_IND[ind]
        est.append([DIM_TXT["D" + ind.split(".")[0]], ind, nombre, regla, val, mod, cita, None])
    filas_tabla(we, 5, est, alineacion={2: AL_CEN, 5: AL_CEN, 7: AL_CEN, 8: AL_NUM})
    for i, fila in enumerate(est):
        r = 5 + i
        we.cell(row=r, column=8, value=f"=COUNTIF('Códigos'!$C$6:$C${ultimo},B{r}&\".*\")")
        we.row_dimensions[r].height = max(estimar_alto(fila[3], 80), estimar_alto(fila[5], 40))
    rr = 5 + len(est)
    we.cell(row=rr, column=7, value="Total").font = F_NEG
    c = we.cell(row=rr, column=8, value=f"=SUM(H5:H{rr - 1})")
    c.font, c.alignment = F_NEG, AL_NUM
    we.freeze_panes = "A5"

    # ---------------- Contexto y campos ----------------
    wx = wb.create_sheet("Contexto y campos")
    anchos(wx, [10, 24, 46, 120])
    titulo(wx, "Variables de contexto y campos de cada código", "Las variables de contexto describen la nota; no son parte del encuadre.")
    wx.cell(row=4, column=1, value="Variables de contexto (una por nota)").font = F_SEC
    encabezado(wx, 5, ["Campo", "Variable", "Valores", "Regla"], alto=20)
    rr = filas_tabla(wx, 6, [list(x) for x in CONTEXTO])
    for i, x in enumerate(CONTEXTO):
        wx.row_dimensions[6 + i].height = max(estimar_alto(x[3], 120), estimar_alto(x[2], 46))
    rr += 1
    wx.cell(row=rr, column=1, value="Campos que acompañan a cada código").font = F_SEC
    encabezado(wx, rr + 1, ["Campo", "Nombre", "Valores", "Regla"], alto=20)
    filas_tabla(wx, rr + 2, [list(x) for x in CAMPOS])
    for i, x in enumerate(CAMPOS):
        wx.row_dimensions[rr + 2 + i].height = max(estimar_alto(x[3], 120), estimar_alto(x[2], 46))

    # ---------------- Principios ----------------
    wp = wb.create_sheet("Principios")
    anchos(wp, [12, 140])
    titulo(wp, "Principios de codificación")
    encabezado(wp, 3, ["N.º", "Principio"], alto=20)
    filas_tabla(wp, 4, [list(x) for x in PRINCIPIOS], alineacion={1: AL_CEN})
    for i, x in enumerate(PRINCIPIOS):
        wp.row_dimensions[4 + i].height = estimar_alto(x[1], 140)

    # ---------------- Confiabilidad ----------------
    wf = wb.create_sheet("Confiabilidad")
    anchos(wf, [34, 18, 18, 18, 18, 18, 18, 18, 40])
    titulo(wf, "Confiabilidad entre codificadores",
           "Dos codificadores independientes, instancias del mismo modelo de IA: miden replicabilidad, no validez frente a codificadores humanos.")
    r = 4
    wf.cell(row=r, column=1, value="1. Resumen").font = F_SEC
    encabezado(wf, r + 1, ["Medida", "Piloto v0.2 (A y B)", "Validación v1.0 (X e Y)"], alto=30)

    def g(a, *ks):
        for k in ks:
            a = a[k] if a is not None and k in a else None
        return a

    resumen = [
        ("Notas comparadas", acu_p["n_notas_comunes"], acu_v["n_notas_comunes"], "#,##0"),
        ("Notas con codificación sustantiva", acu_p["n_notas_activas"], acu_v["n_notas_activas"], "#,##0"),
        ("Centralidad c1: kappa de Cohen", g(acu_p, "c1", "cohen"), g(acu_v, "c1", "cohen"), "0.00"),
        ("Centralidad c1: acuerdo observado", g(acu_p, "c1", "acuerdo"), g(acu_v, "c1", "acuerdo"), "0.0%"),
        ("Ámbito c3: kappa de Cohen", g(acu_p, "c3", "cohen"), g(acu_v, "c3", "cohen"), "0.00"),
        ("Género c5: kappa de Cohen", g(acu_p, "c5", "cohen"), g(acu_v, "c5", "cohen"), "0.00"),
        ("Valoración: pares comparados", g(acu_p, "valoracion", "n_pares"), g(acu_v, "valoracion", "n_pares"), "#,##0"),
        ("Valoración: acuerdo observado", g(acu_p, "valoracion", "acuerdo"), g(acu_v, "valoracion", "acuerdo"), "0.0%"),
        ("Valoración: alfa de Krippendorff", g(acu_p, "valoracion", "alfa_krippendorff"), g(acu_v, "valoracion", "alfa_krippendorff"), "0.00"),
        ("Signo (+/-): acuerdo cuando ambos asignan + o -", g(acu_p, "valoracion_dicotomica_signo", "acuerdo"), g(acu_v, "valoracion_dicotomica_signo", "acuerdo"), "0.0%"),
        ("2.3 intensidad (g): acuerdo", g(acu_p, "modificadores_2_3", "g", "acuerdo"), g(acu_v, "modificadores_2_3", "g", "acuerdo"), "0.0%"),
        ("2.3 responsable (resp): acuerdo", g(acu_p, "modificadores_2_3", "resp", "acuerdo"), g(acu_v, "modificadores_2_3", "resp", "acuerdo"), "0.0%"),
    ]
    r_ini = r + 2
    filas_tabla(wf, r_ini, [list(x[:3]) for x in resumen], alineacion={2: AL_NUM, 3: AL_NUM})
    for k, x in enumerate(resumen):
        for col in (2, 3):
            wf.cell(row=r_ini + k, column=col).number_format = x[3]
    r = r_ini + len(resumen)
    r += 1
    wf.cell(row=r, column=1, value="2. Por indicador (medias de los códigos con al menos 4 usos entre ambos codificadores)").font = F_SEC
    encabezado(wf, r + 1, ["Indicador", "Kappa piloto", "Kappa validación", "AC1 piloto", "AC1 validación", "Acuerdo piloto", "Acuerdo validación", "Códigos (validación)"], alto=30)
    pi, vi = acu_p["por_indicador"], acu_v["por_indicador"]
    filas_ind = []
    for ind in INDICADORES:
        a, b = pi.get(ind), vi.get(ind)
        if not a and not b:
            continue
        filas_ind.append([f"{ind} {INDICADORES[ind]}", a["kappa_medio"] if a else None, b["kappa_medio"] if b else None,
                          a["ac1_medio"] if a else None, b["ac1_medio"] if b else None,
                          a["acuerdo_medio"] if a else None, b["acuerdo_medio"] if b else None, b["n_codigos"] if b else None])
    r = filas_tabla(wf, r + 2, filas_ind, alineacion={j: AL_NUM for j in range(2, 9)}, formatos={j: "0.00" for j in range(2, 8)})
    r += 1
    wf.cell(row=r, column=1, value="3. Por código (validación v1.0)").font = F_SEC
    encabezado(wf, r + 1, ["Código", "Usos X", "Usos Y", "En ambos", "Kappa", "AC1 de Gwet", "Acuerdo", "Acuerdo en valoración", "Lectura"], alto=30)
    filas_cod = []
    for cod, m in acu_v["por_codigo"].items():
        lectura = ""
        if m["kappa"] is not None and m["kappa"] < 0.70 and (m["n_A"] + m["n_B"]) >= 4:
            lectura = "Revisar (kappa < 0,70)" + ("; AC1 alto: efecto de prevalencia" if (m["ac1"] or 0) >= 0.90 and (m["n_A"] + m["n_B"]) > 100 else "")
        filas_cod.append([f"{cod} {CODIGOS[cod][0]}", m["n_A"], m["n_B"], m["n_ambos"], m["kappa"], m["ac1"], m["acuerdo"], m["v_acuerdo"], lectura])
    r = filas_tabla(wf, r + 2, filas_cod, alineacion={j: AL_NUM for j in range(2, 9)},
                    formatos={2: "0", 3: "0", 4: "0", 5: "0.00", 6: "0.00", 7: "0.00", 8: "0.00"})
    r += 1
    wf.cell(row=r, column=1, value="4. Cómo leer estas cifras").font = F_SEC
    notas_lect = [
        "Paradoja del kappa: en los indicadores 1.3 y 3.2 y en los códigos por defecto un valor domina el 90 % o más de las notas. Con esa prevalencia el kappa cae aunque el acuerdo sea muy alto (0,97 a 0,99); conviene leer AC1 y acuerdo observado.",
        "Puntos débiles reales: los códigos poco frecuentes de 3.2 (DEC), 2.4 (DIS, CTX) y 1.3 (IRR) tienen pocos casos compartidos y kappa bajo; se recomienda revisarlos con codificadores humanos antes de analizarlos cuantitativamente.",
        "La comparación entre el piloto y la validación es orientativa: las muestras y las versiones del libro son distintas.",
        "El signo de la valoración (+ o -) coincide en el 100 % de los pares; las discrepancias de valoración se concentran en distinguir D (descriptiva) de + o -, que depende del umbral de marca valorativa.",
    ]
    for t in notas_lect:
        r += 1
        c = wf.cell(row=r, column=1, value=t)
        c.font, c.alignment = F_BASE, AL_TXT
        wf.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
        wf.row_dimensions[r].height = estimar_alto(t, 170)
    wf.freeze_panes = "B4"

    # ---------------- Emergentes ----------------
    wm = wb.create_sheet("Emergentes")
    anchos(wm, [28, 52, 9, 11, 10, 22, 34, 20, 64, 13, 11, 19])
    titulo(wm, "Categorías emergentes", "Significados que los codificadores registraron y que ningún código recogía. Umbrales: 40 o más notas = promover a código; 10 a 39 = vigilar; menos de 10 = registrar sin promover.")
    encabezado(wm, 4, ["Etiqueta", "Definición", "Notas", "% notas analíticas", "Registros", "Valoraciones", "Períodos", "Recomendación", "Cita ilustrativa (verificada)", "Medio", "Fecha", "ID de la nota"], alto=34)
    filas_em = []
    MAP = mapa_ids()
    for it in emerg["categorias"]:
        q = it["citas"][0] if it.get("citas") else None
        filas_em.append([it["etiqueta"], it["definicion"], it["n_notas"], it["n_notas"] / emerg["n_notas_analiticas"], it["n_registros"],
                         ", ".join(f"{k} {v}" for k, v in it["valoracion"].items()),
                         ", ".join(f"{k.split('_')[0]} {v}" for k, v in it["periodos"].items()),
                         it["recomendacion"], q["cita"] if q else "—", q["medio"] if q else "—", q["fecha"] if q else "—", MAP.get(q["id_nota"], q["id_nota"]) if q else "—"])
    filas_tabla(wm, 5, filas_em, alineacion={3: AL_NUM, 4: AL_NUM, 5: AL_NUM, 11: AL_CEN}, formatos={3: "0", 4: "0.0%", 5: "0"})
    for i, fila in enumerate(filas_em):
        wm.row_dimensions[5 + i].height = max(estimar_alto(fila[1], 52), estimar_alto(fila[8], 64), estimar_alto(fila[6], 34))
    wm.freeze_panes = "B5"
    wm.auto_filter.ref = f"A4:L{4 + len(filas_em)}"

    # ---------------- Versiones ----------------
    wv = wb.create_sheet("Versiones")
    anchos(wv, [10, 130])
    titulo(wv, "Historial de versiones y decisiones de diseño")
    encabezado(wv, 3, ["Versión", "Cambios"], alto=20)
    vers = [
        ["0.1", "Traducción de la operacionalización a instrucciones de codificación: 63 códigos base, variables de contexto c1 a c5, campos v, voz, marca y cita."],
        ["0.2", "Seis aclaraciones tras una prueba de humo con un lote (c1, c5, voz, 1.3.IRR, 2.1.LIM, 3.3 y 3.4, citas con puntos suspensivos)."],
        ["1.0", "Tras el piloto de doble codificación (160 notas, 244 desacuerdos diagnosticados: 82 % por ambigüedad del libro, 11 % por juicio legítimo, 7 % por error): unidad de registro; test de dos condiciones; umbrales de marca valorativa; alcance de D1; umbrales de HER e INN; delimitación de 3.3 y 3.4; nuevos ámbitos 2.2.SEG, 2.2.AMB, 2.3.SAL, 2.3.AMB, 2.3.EST; resp = RUS; c3 consumo_cotidiano; seis emergentes promovidos a códigos provisionales (2.6.REC, 2.6.IMI, 2.6.PCH, 2.6.FAH, 2.6.ACT, 3.5.REZ); lista cerrada de etiquetas emergentes."],
        ["", ""],
        ["Decisiones", "Tomadas al pasar de v0.2 a v1.0 (los adjudicadores del piloto proponían soluciones opuestas): (1) una entrada por código y objeto, no una por fragmento; (2) REG coexiste con CON o PRO cuando el texto detalla la restricción; (3) 'global' significa agente extranjero o transnacional; (4) 1.1 admite modelos o sistemas de IA propios con verbo de agencia, pero 1.2 y 1.3 solo la IA como tecnología o campo; (5) 2.2 y 2.3 admiten D solo en registro puramente informativo; (6) contenido_patrocinado se define por fuente única más lenguaje promocional; (7) el campo 'sección' no se entrega a los codificadores; (8) en 3.3.ADA el actor es el ofertante, y el individuo solo con exhortación expresa; (9) la adopción de IA por una institución es 3.3.ADO, pero no la inversión de una empresa en su propio negocio; (10) se agregan los ámbitos y el responsable que faltaban (2.2.SEG, 2.2.AMB, 2.3.SAL, 2.3.AMB, 2.3.EST, resp = RUS)."],
        ["Pendiente", "Fusiones propuestas y no aplicadas, a la espera de validación humana: HER con INN, CON con PRO, 3.2 como modificador, eliminación de 2.5.AMB y de los códigos sin uso."],
        ["Corrección de datos", "Las fechas de las notas de CNN Chile se corrigieron con la fecha real de publicación (el scraper había tomado la fecha de re-indexación del sitio en 328 de 428 notas). Se excluyeron 23 notas de CNN anteriores a 2019. Las frecuencias de este libro ya incluyen la corrección."],
    ]
    filas_tabla(wv, 4, vers, alineacion={1: AL_CEN}, cebra=False)
    for i, x in enumerate(vers):
        wv.row_dimensions[4 + i].height = estimar_alto(x[1], 130)

    for hoja in wb.worksheets:
        hoja.sheet_view.zoomScale = 100
        hoja.sheet_properties.tabColor = "1F3864"
    wb.calculation.fullCalcOnLoad = True
    SALIDA.parent.mkdir(exist_ok=True)
    wb.save(SALIDA)
    print("Guardado:", SALIDA, "| hojas:", wb.sheetnames)


if __name__ == "__main__":
    main()
