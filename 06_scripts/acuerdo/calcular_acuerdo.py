"""
Acuerdo entre dos codificadores - Corpus IA Chile
Uso: python calcular_acuerdo.py <carpeta_salidas> <sufijoA> <sufijoB> <salida.json> [aliases.json]
Lee <lote>_<sufijoA>.json y <lote>_<sufijoB>.json y calcula:
  - kappa de Cohen, AC1 de Gwet y % de acuerdo en presencia de cada código
  - acuerdo de valoración (V) en los códigos presentes en ambos
  - acuerdo en C1, C3, C5 y en los modificadores de 2.3 (g, resp)
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utilidades_codificacion import CATALOGO  # noqa: E402


def cargar(carpeta, sufijo):
    out = {}
    for f in sorted(Path(carpeta).glob(f"*_{sufijo}.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for n in d.get("notas", []):
            out[n["alias"]] = n
    return out


def kappa_ac1(a, b):
    """a, b: listas de 0/1 emparejadas. Devuelve (kappa, ac1, acuerdo)."""
    n = len(a)
    if n == 0:
        return None, None, None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    p1a, p1b = sum(a) / n, sum(b) / n
    pe_k = p1a * p1b + (1 - p1a) * (1 - p1b)
    kappa = (po - pe_k) / (1 - pe_k) if pe_k < 1 else None
    pi = (p1a + p1b) / 2
    pe_g = 2 * pi * (1 - pi)
    ac1 = (po - pe_g) / (1 - pe_g) if pe_g < 1 else None
    return kappa, ac1, po


def cohen_categorico(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    return (po - pe) / (1 - pe) if pe < 1 else None


def alfa_krippendorff_nominal(pares):
    """pares: lista de (x, y) de dos codificadores."""
    if not pares:
        return None
    coincid = defaultdict(float)
    for x, y in pares:
        coincid[(x, y)] += 1
        coincid[(y, x)] += 1
    n = sum(coincid.values())
    marg = defaultdict(float)
    for (x, _y), v in coincid.items():
        marg[x] += v
    do = sum(v for (x, y), v in coincid.items() if x != y) / n
    de = sum(marg[x] * marg[y] for x in marg for y in marg if x != y) / (n * (n - 1))
    return 1 - do / de if de > 0 else None


def main():
    carpeta, sa, sb, salida = sys.argv[1:5]
    filtro = None
    if len(sys.argv) > 5:
        filtro = set(json.load(open(sys.argv[5], encoding="utf-8")))
    A, B = cargar(carpeta, sa), cargar(carpeta, sb)
    comunes = sorted(set(A) & set(B))
    if filtro is not None:
        comunes = [x for x in comunes if x in filtro]
    res = {"n_notas_comunes": len(comunes)}

    res["c1"] = {"cohen": cohen_categorico([A[x]["c1"] for x in comunes], [B[x]["c1"] for x in comunes]),
                 "acuerdo": sum(A[x]["c1"] == B[x]["c1"] for x in comunes) / max(1, len(comunes))}
    res["c3"] = {"cohen": cohen_categorico([A[x]["c3"] for x in comunes], [B[x]["c3"] for x in comunes]),
                 "acuerdo": sum(A[x]["c3"] == B[x]["c3"] for x in comunes) / max(1, len(comunes))}
    res["c5"] = {"cohen": cohen_categorico([A[x]["c5"] for x in comunes], [B[x]["c5"] for x in comunes]),
                 "acuerdo": sum(A[x]["c5"] == B[x]["c5"] for x in comunes) / max(1, len(comunes))}

    # conjunto restringido: notas que al menos un codificador considera central o secundaria
    activas = [x for x in comunes if A[x]["c1"] != "tangencial" or B[x]["c1"] != "tangencial"]
    res["n_notas_activas"] = len(activas)

    def cods(n):
        return {c["cod"]: c for c in n.get("codigos", [])}

    por_codigo = {}
    for cod in CATALOGO:
        a = [1 if cod in cods(A[x]) else 0 for x in activas]
        b = [1 if cod in cods(B[x]) else 0 for x in activas]
        if sum(a) + sum(b) == 0:
            continue
        k, g, po = kappa_ac1(a, b)
        ambos = [x for x in activas if cod in cods(A[x]) and cod in cods(B[x])]
        vs = [(cods(A[x])[cod].get("v"), cods(B[x])[cod].get("v")) for x in ambos]
        por_codigo[cod] = {"n_A": sum(a), "n_B": sum(b), "n_ambos": len(ambos), "kappa": k, "ac1": g, "acuerdo": po,
                           "v_acuerdo": (sum(1 for p, q in vs if p == q) / len(vs)) if vs else None}
    res["por_codigo"] = por_codigo

    # por indicador (media de kappa y AC1 de sus códigos con prevalencia suficiente)
    por_ind = defaultdict(list)
    for cod, m in por_codigo.items():
        if m["n_A"] + m["n_B"] >= 4 and m["kappa"] is not None:
            por_ind[CATALOGO[cod]["ind"]].append((m["kappa"], m["ac1"], m["acuerdo"]))
    res["por_indicador"] = {i: {"kappa_medio": sum(k for k, _, _ in v) / len(v), "ac1_medio": sum(g for _, g, _ in v) / len(v),
                                "acuerdo_medio": sum(p for _, _, p in v) / len(v), "n_codigos": len(v)} for i, v in sorted(por_ind.items())}

    pares_v = []
    for x in activas:
        ca, cb = cods(A[x]), cods(B[x])
        for cod in set(ca) & set(cb):
            if CATALOGO[cod]["aplica_v"]:
                pares_v.append((ca[cod].get("v"), cb[cod].get("v")))
    res["valoracion"] = {"n_pares": len(pares_v), "acuerdo": (sum(1 for p, q in pares_v if p == q) / len(pares_v)) if pares_v else None,
                         "alfa_krippendorff": alfa_krippendorff_nominal(pares_v)}
    res["valoracion_dicotomica_signo"] = None
    signo = [(p, q) for p, q in pares_v if p in ("+", "-") and q in ("+", "-")]
    if signo:
        res["valoracion_dicotomica_signo"] = {"n": len(signo), "acuerdo": sum(1 for p, q in signo if p == q) / len(signo)}

    mods = {"g": [], "resp": []}
    for x in activas:
        ca, cb = cods(A[x]), cods(B[x])
        for cod in set(ca) & set(cb):
            if cod.startswith("2.3."):
                for m in mods:
                    mods[m].append(((ca[cod].get("mod") or {}).get(m), (cb[cod].get("mod") or {}).get(m)))
    res["modificadores_2_3"] = {m: {"n": len(v), "acuerdo": (sum(1 for p, q in v if p == q) / len(v)) if v else None} for m, v in mods.items()}

    Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("n_notas_comunes", "n_notas_activas", "c1", "valoracion", "por_indicador", "modificadores_2_3")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
