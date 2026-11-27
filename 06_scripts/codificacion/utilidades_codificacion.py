"""
Utilidades de codificación - Corpus IA Chile
Catálogo de códigos, validación de salidas de los codificadores y verificación/reparación de citas literales.
"""

import json
import re
from difflib import SequenceMatcher

# código -> (indicador, aplica_v, requiere_cita, modificadores_obligatorios)
CATALOGO = {}


def _reg(indicador, codigos, aplica_v=True, cita=True, mods=()):
    for c in codigos:
        CATALOGO[f"{indicador}.{c}"] = {"ind": indicador, "aplica_v": aplica_v, "cita": cita, "mods": tuple(mods)}


_reg("1.1", ["CIE", "CORP", "EST", "USU"], mods=("escala",))
_reg("1.1", ["DIF"])
_reg("1.2", ["CON", "ECO", "GEO", "CTR", "NEC", "INE"])
_reg("1.3", ["IRR", "TRA"], aplica_v=False)
_reg("1.3", ["SIN"], aplica_v=False, cita=False)
_reg("2.1", ["HER", "INN", "AGE", "REV", "MER", "LIM"])
_reg("2.2", ["ECO", "LAB", "EDU", "SAL", "EST", "CUL", "SEG", "AMB"])
_reg("2.2", ["OTR"], mods=("etiqueta",))
_reg("2.3", ["EMP", "DEM", "PRI", "SEG", "DES", "CUL", "HUM", "SAL", "AMB", "EST"], mods=("g", "resp"))
_reg("2.3", ["OTR"], mods=("g", "resp", "etiqueta"))
_reg("2.4", ["USO", "DIS", "REG", "CTX"], aplica_v=False)
_reg("2.5", ["HYP", "ALA", "AMB"], aplica_v=False)
_reg("2.6", ["REC", "IMI", "PCH", "FAH", "ACT"])
_reg("3.1", ["CON", "RUP", "INC"])
_reg("3.1", ["EST"], mods=("ambito",))
_reg("3.1", ["NIN"], aplica_v=False, cita=False)
_reg("3.2", ["INE", "DEC"], aplica_v=False)
_reg("3.2", ["NEX"], aplica_v=False, cita=False)
_reg("3.3", ["ADO", "ADA", "REG", "GOB", "LIB", "CON"])
_reg("3.3", ["PRO"], mods=("alcance",))
_reg("3.3", ["NIN"], aplica_v=False, cita=False)
_reg("3.5", ["REZ"])
_reg("3.4", ["EST", "EMP", "ACA", "SOC", "IND", "INT"], aplica_v=False)
_reg("3.4", ["NES"], aplica_v=False)

# los códigos por defecto no llevan cita
POR_DEFECTO = {"1.3.SIN", "3.1.NIN", "3.2.NEX", "3.3.NIN"}

V_VALIDOS = {"+", "-", "A", "C", "D"}
VOZ_VALIDAS = {"P", "FE", "FC", "FG", "FS", "FI", "FM", "na"}
MARCA_VALIDAS = {"explicita", "implicita", "na"}
C1_VALIDOS = {"central", "secundaria", "tangencial"}
C2_VALIDOS = {"generica", "generativa", "sistemas_especificos", "agi_superinteligencia"}
C3_VALIDOS = {"educacion", "trabajo_economia", "politica_estado", "salud_ciencia", "seguridad_justicia", "cultura_medios", "consumo_cotidiano", "otro"}
C5_VALIDOS = {"noticia", "reportaje", "entrevista", "columna_opinion", "editorial", "contenido_patrocinado", "otro"}
G_VALIDOS = {"G1", "G2", "G3"}
RESP_VALIDOS = {"RCO", "RMA", "RES", "RUS", "RTE", "RDI"}
ESCALA_VALIDAS = {"global", "Chile", "no_especificada"}
ALCANCE_VALIDOS = {"parcial", "total"}


# ---------- normalización y citas literales ----------

def _tokens_originales(texto):
    return texto.split()


def _norm_token(tok):
    return re.sub(r'[^0-9a-záéíóúüñ]', '', tok.lower())


def _tabla_tokens(texto):
    orig = _tokens_originales(texto)
    norm = [_norm_token(t) for t in orig]
    idx = [i for i, n in enumerate(norm) if n]
    return orig, [norm[i] for i in idx], idx


def localizar_cita(cita, texto_fuente, umbral_difuso=0.92):
    """Devuelve (estado, span_literal). estado: 'exacta' | 'reparada' | 'no_encontrada'."""
    if not cita or not cita.strip():
        return "vacia", ""
    orig, norm, idx = _tabla_tokens(texto_fuente)
    q = [_norm_token(t) for t in cita.split()]
    q = [t for t in q if t]
    if not q or not norm:
        return "no_encontrada", ""
    n = len(q)
    for i in range(0, len(norm) - n + 1):
        if norm[i:i + n] == q:
            a, b = idx[i], idx[i + n - 1]
            return "exacta", " ".join(orig[a:b + 1])
    # búsqueda difusa por ventana
    objetivo = " ".join(q)
    mejor, mejor_i, mejor_n = 0.0, -1, n
    for w in (n - 2, n - 1, n, n + 1, n + 2):
        if w < 3 or w > len(norm):
            continue
        for i in range(0, len(norm) - w + 1):
            if norm[i] != q[0] and norm[i + w - 1] != q[-1]:
                continue
            r = SequenceMatcher(None, " ".join(norm[i:i + w]), objetivo).ratio()
            if r > mejor:
                mejor, mejor_i, mejor_n = r, i, w
    if mejor >= umbral_difuso and mejor_i >= 0:
        a, b = idx[mejor_i], idx[mejor_i + mejor_n - 1]
        return "reparada", " ".join(orig[a:b + 1])
    return "no_encontrada", ""


def validar_nota(nota, texto_fuente):
    """Valida una nota codificada. Devuelve (nota_corregida, lista_de_problemas)."""
    problemas = []
    n = json.loads(json.dumps(nota))
    if n.get("c1") not in C1_VALIDOS:
        problemas.append(f"c1 inválido: {n.get('c1')}")
    for x in n.get("c2", []) or []:
        if x not in C2_VALIDOS:
            problemas.append(f"c2 inválido: {x}")
    if n.get("c3") not in C3_VALIDOS:
        problemas.append(f"c3 inválido: {n.get('c3')}")
    if n.get("c5") not in C5_VALIDOS:
        problemas.append(f"c5 inválido: {n.get('c5')}")
    codigos = n.get("codigos", []) or []
    if n.get("c1") == "tangencial" and codigos:
        problemas.append("nota tangencial con códigos")
    vistos = set()
    nuevos = []
    for c in codigos:
        cod = c.get("cod")
        if cod not in CATALOGO:
            problemas.append(f"código inexistente: {cod}")
            continue
        cat = CATALOGO[cod]
        previos = [x for x in nuevos if x["cod"] == cod]
        if previos:
            if len(previos) >= 2:
                problemas.append(f"{cod}: más de 2 entradas del mismo código")
            if not (c.get("mod") or {}).get("objeto") or not (previos[0].get("mod") or {}).get("objeto"):
                problemas.append(f"{cod}: código repetido sin mod.objeto en ambas entradas (5.1)")
        if cat["aplica_v"]:
            if c.get("v") not in V_VALIDOS:
                problemas.append(f"{cod}: v inválido ({c.get('v')})")
        else:
            if c.get("v") != "NA":
                c["v"] = "NA"
        if c.get("voz") not in VOZ_VALIDAS:
            problemas.append(f"{cod}: voz inválida ({c.get('voz')})")
        if c.get("marca") not in MARCA_VALIDAS:
            problemas.append(f"{cod}: marca inválida ({c.get('marca')})")
        mod = c.get("mod") or {}
        for m in cat["mods"]:
            if m not in mod or not mod[m]:
                problemas.append(f"{cod}: falta modificador {m}")
        if mod.get("g") and mod["g"] not in G_VALIDOS:
            problemas.append(f"{cod}: g inválido")
        if mod.get("resp") and mod["resp"] not in RESP_VALIDOS:
            problemas.append(f"{cod}: resp inválido")
        if mod.get("escala") and mod["escala"] not in ESCALA_VALIDAS:
            problemas.append(f"{cod}: escala inválida")
        if mod.get("alcance") and mod["alcance"] not in ALCANCE_VALIDOS:
            problemas.append(f"{cod}: alcance inválido")
        cita = c.get("cita", "") or ""
        if cat["cita"]:
            estado, span = localizar_cita(cita, texto_fuente)
            c["cita_estado"] = estado
            if estado in ("exacta", "reparada"):
                c["cita"] = span
                if len(span.split()) > 60:
                    problemas.append(f"{cod}: cita demasiado larga ({len(span.split())} palabras)")
            else:
                problemas.append(f"{cod}: cita no literal o vacía")
        else:
            c["cita_estado"] = "no_requerida"
        nuevos.append(c)
    n["codigos"] = nuevos
    cods = {c["cod"] for c in nuevos}
    if n.get("c1") in ("central", "secundaria"):
        if sum(1 for x in cods if x.startswith("1.3.")) != 1:
            problemas.append("1.3 debe tener exactamente un código")
        if not any(x.startswith("3.1.") for x in cods):
            problemas.append("falta 3.1")
        if not any(x.startswith("3.2.") for x in cods):
            problemas.append("falta 3.2")
        if not any(x.startswith("3.3.") for x in cods):
            problemas.append("falta 3.3")
        if "3.3.NIN" in cods and any(x.startswith("3.3.") and x != "3.3.NIN" for x in cods):
            problemas.append("3.3.NIN coexiste con otro 3.3")
        if any(x.startswith("3.4.") for x in cods) and not any(x.startswith("3.3.") and x != "3.3.NIN" for x in cods):
            problemas.append("hay 3.4 sin un 3.3 distinto de 3.3.NIN")
        if "3.1.NIN" in cods and any(x.startswith("3.1.") and x != "3.1.NIN" for x in cods):
            problemas.append("3.1.NIN coexiste con otro 3.1")
        if "3.2.NEX" in cods and ("3.2.INE" in cods or "3.2.DEC" in cods):
            problemas.append("3.2.NEX coexiste con INE o DEC")
    for e in n.get("emergentes", []) or []:
        if e.get("cita"):
            estado, span = localizar_cita(e["cita"], texto_fuente)
            e["cita_estado"] = estado
            if estado in ("exacta", "reparada"):
                e["cita"] = span
    return n, problemas
