"""
Preparación de lotes ciegos para codificación - Corpus IA Chile
Uso:
  python preparar_lotes.py poblacion
  python preparar_lotes.py piloto
  python preparar_lotes.py completo
  python preparar_lotes.py confiabilidad
Los lotes no contienen año, medio, autor ni URL. Los alias son aleatorios (semilla fija).
"""

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
MAESTRO = RAIZ / "corpus_maestro.jsonl"
MAX_PALABRAS = 3500
SEMILLA = 2026


def periodo(anio):
    if anio <= 2021:
        return "P1_2019-2021"
    return {2022: "P2_2022", 2023: "P3_2023", 2024: "P4_2024"}.get(anio, "P5_2025-2026")


def senal_baja(n):
    return n["n_ia_nucleo"] <= 1 and not n["ia_en_titulo_bajada"]


def cargar():
    return [json.loads(l) for l in open(MAESTRO, encoding="utf-8")]


def construir_poblacion():
    notas = cargar()
    embudo = Counter()
    pob = []
    for n in notas:
        embudo["corpus_maestro"] += 1
        tiene_texto = n["n_palabras"] >= 30
        if n["n_ia_amplio"] == 0:
            embudo["excluida_sin_mencion_ia"] += 1
            continue
        if not tiene_texto and not n["ia_en_titulo_bajada"]:
            embudo["excluida_sin_texto_y_sin_ia_en_titular"] += 1
            continue
        n["solo_titular_bajada"] = not tiene_texto
        pob.append(n)
    embudo["poblacion_a_codificar"] = len(pob)
    rng = random.Random(SEMILLA)
    alias = rng.sample(range(10000, 99999), len(pob))
    for n, a in zip(sorted(pob, key=lambda x: x["id"]), alias):
        n["alias"] = f"N{a}"
    with open(COD / "poblacion.jsonl", "w", encoding="utf-8") as f:
        for n in sorted(pob, key=lambda x: x["id"]):
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    mapa = {n["alias"]: n["id"] for n in pob}
    (COD / "mapa_alias.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=0), encoding="utf-8")
    por = defaultdict(Counter)
    for n in pob:
        por[n["medio_codigo"]][n["anio"]] += 1
    informe = {"embudo": dict(embudo),
               "poblacion_por_medio_anio": {m: dict(sorted(c.items())) for m, c in por.items()},
               "solo_titular_bajada": sum(1 for n in pob if n["solo_titular_bajada"]),
               "patrocinadas": sum(1 for n in pob if n["patrocinada"] if "patrocinada" in n) if False else sum(1 for n in pob if n.get("patrocinado"))}
    (COD / "informe_poblacion.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    return pob


def poblacion():
    return [json.loads(l) for l in open(COD / "poblacion.jsonl", encoding="utf-8")]


def registro_ciego(n):
    palabras = n["texto"].split()
    truncada = len(palabras) > MAX_PALABRAS
    texto = " ".join(palabras[:MAX_PALABRAS]) + (" [... texto truncado ...]" if truncada else "")
    return {"alias": n["alias"], "titulo": n["titulo"], "bajada": n["bajada"],
            "texto": texto, "solo_titular_bajada": n["solo_titular_bajada"]}, truncada


def escribir_lotes(notas, fase, tam, prefijo, semilla):
    carpeta = COD / "lotes" / fase
    carpeta.mkdir(parents=True, exist_ok=True)
    for f in carpeta.glob("*.json"):
        f.unlink()
    rng = random.Random(semilla)
    notas = list(notas)
    rng.shuffle(notas)
    manifiesto, trunc = [], 0
    for i in range(0, len(notas), tam):
        grupo = notas[i:i + tam]
        lote_id = f"{prefijo}{i // tam + 1:03d}"
        regs = []
        for n in grupo:
            r, t = registro_ciego(n)
            trunc += t
            regs.append(r)
        (carpeta / f"{lote_id}.json").write_text(json.dumps({"lote": lote_id, "notas": regs}, ensure_ascii=False), encoding="utf-8")
        manifiesto.append({"lote": lote_id, "aliases": [n["alias"] for n in grupo], "n": len(grupo)})
    (COD / "lotes" / f"manifiesto_{fase}.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{fase}: {len(notas)} notas en {len(manifiesto)} lotes ({trunc} truncadas a {MAX_PALABRAS} palabras)")
    return manifiesto


def muestra_estratificada(pob, por_periodo, semilla, excluir=frozenset(), min_palabras=0):
    rng = random.Random(semilla)
    celdas = defaultdict(lambda: defaultdict(list))
    for n in pob:
        if n["alias"] in excluir or n["n_palabras"] < min_palabras:
            continue
        celdas[periodo(n["anio"])][n["medio_codigo"]].append(n)
    elegidas = []
    for per, medios in sorted(celdas.items()):
        for lst in medios.values():
            rng.shuffle(lst)
        cuota, k = por_periodo, 0
        ciclo = sorted(medios)
        pos = {m: 0 for m in ciclo}
        while k < cuota and any(pos[m] < len(medios[m]) for m in ciclo):
            for m in ciclo:
                if k >= cuota:
                    break
                if pos[m] < len(medios[m]):
                    elegidas.append(medios[m][pos[m]])
                    pos[m] += 1
                    k += 1
    return elegidas


def main():
    fase = sys.argv[1]
    if fase == "poblacion":
        construir_poblacion()
        return
    pob = poblacion()
    if fase == "piloto":
        m = muestra_estratificada(pob, 32, SEMILLA + 1, min_palabras=60)
        escribir_lotes(m, "piloto", 8, "P", SEMILLA + 2)
        (COD / "piloto_aliases.json").write_text(json.dumps([n["alias"] for n in m]), encoding="utf-8")
        print(Counter((periodo(n["anio"]), n["medio_codigo"]) for n in m))
    elif fase == "completo":
        principal = [n for n in pob if not senal_baja(n)]
        escribir_lotes(principal, "completo", 10, "C", SEMILLA + 3)
        (COD / "completo_aliases.json").write_text(json.dumps([n["alias"] for n in principal]), encoding="utf-8")
    elif fase == "triaje":
        bajas = [n for n in pob if senal_baja(n)]
        escribir_lotes(bajas, "triaje", 25, "T", SEMILLA + 7)
        (COD / "triaje_aliases.json").write_text(json.dumps([n["alias"] for n in bajas]), encoding="utf-8")
    elif fase == "escalada":
        esc = set()
        for f in sorted((COD / "salidas" / "triaje").glob("*_X.json")):
            for n in json.load(open(f, encoding="utf-8"))["notas"]:
                if n["c1"] != "tangencial":
                    esc.add(n["alias"])
        sel = [n for n in pob if n["alias"] in esc]
        escribir_lotes(sel, "escalada", 10, "E", SEMILLA + 8)
        (COD / "escalada_aliases.json").write_text(json.dumps([n["alias"] for n in sel]), encoding="utf-8")
    elif fase == "confiabilidad":
        base = [n for n in pob if not senal_baja(n)]
        m = muestra_estratificada(base, 48, SEMILLA + 4, min_palabras=60)
        escribir_lotes(m, "confiabilidad", 10, "R", SEMILLA + 5)
        (COD / "confiabilidad_aliases.json").write_text(json.dumps([n["alias"] for n in m]), encoding="utf-8")
        print(Counter((periodo(n["anio"]), n["medio_codigo"]) for n in m))
    elif fase == "validacion_humana":
        m = muestra_estratificada(pob, 24, SEMILLA + 6, min_palabras=150)
        (COD / "validacion_humana_ids.json").write_text(json.dumps([n["id"] for n in m]), encoding="utf-8")
        print(len(m), "notas para validación humana")


if __name__ == "__main__":
    main()
