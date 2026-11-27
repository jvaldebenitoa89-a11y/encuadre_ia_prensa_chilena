"""
Selección de citas candidatas por código y valoración - Corpus IA Chile
Uso: python candidatas_citas.py <prefijo_codigos> [pool_por_celda]
Lee <prefijo>_codigos.csv; arma un pool diverso (períodos y medios) por celda (código x valoración),
agrega el contexto de la nota y escribe un archivo por código en citas_trabajo/candidatas/.
"""

import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
SALIDA = RAIZ / "citas_trabajo" / "candidatas"
PERIODOS = ["P1_2019-2021", "P2_2022", "P3_2023", "P4_2024", "P5_2025-2026"]
SEMILLA = 2026


def puntaje(fila, rng):
    palabras = len(fila["cita"].split())
    largo = 0 if 10 <= palabras <= 42 else -2 if palabras < 10 else -1
    return int(fila["calidad"] or 0) * 10 + largo + rng.random()


def contexto(fuente, cita, radio=350):
    i = fuente.find(cita)
    if i < 0:
        return ""
    a, b = max(0, i - radio), min(len(fuente), i + len(cita) + radio)
    return ("..." if a > 0 else "") + fuente[a:b] + ("..." if b < len(fuente) else "")


def main():
    prefijo = sys.argv[1]
    pool = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    rng = random.Random(SEMILLA)
    pob = {}
    for l in open(COD / "poblacion.jsonl", encoding="utf-8"):
        n = json.loads(l)
        pob[n["id"]] = n
    celdas = defaultdict(list)
    for fila in csv.DictReader(open(COD / f"{prefijo}_codigos.csv", encoding="utf-8-sig")):
        if fila["cita_estado"] not in ("exacta", "reparada") or not fila["cita"].strip():
            continue
        if fila["c1"] not in ("central", "secundaria"):
            continue
        fila["_p"] = puntaje(fila, rng)
        celdas[(fila["cod"], fila["v"])].append(fila)

    SALIDA.mkdir(parents=True, exist_ok=True)
    for f in SALIDA.glob("*.json"):
        f.unlink()
    por_codigo = defaultdict(list)
    resumen = {}
    for (cod, v), filas in sorted(celdas.items()):
        por_periodo = defaultdict(list)
        for f in sorted(filas, key=lambda x: -x["_p"]):
            por_periodo[f["periodo"]].append(f)
        elegidas, notas_usadas, ultimo_medio = [], set(), None
        cursor = {p: 0 for p in PERIODOS}
        while len(elegidas) < pool and any(cursor[p] < len(por_periodo[p]) for p in PERIODOS):
            for p in PERIODOS:
                if len(elegidas) >= pool:
                    break
                lista = por_periodo[p]
                while cursor[p] < len(lista) and lista[cursor[p]]["id"] in notas_usadas:
                    cursor[p] += 1
                if cursor[p] >= len(lista):
                    continue
                # prefiere un medio distinto del último elegido
                k = cursor[p]
                for j in range(cursor[p], min(len(lista), cursor[p] + 4)):
                    if lista[j]["id"] not in notas_usadas and lista[j]["medio_codigo"] != ultimo_medio:
                        k = j
                        break
                f = lista.pop(k)
                notas_usadas.add(f["id"])
                ultimo_medio = f["medio_codigo"]
                elegidas.append(f)
        resumen[f"{cod}|{v}"] = {"disponibles": len(filas), "candidatas": len(elegidas)}
        for f in elegidas:
            n = pob[f["id"]]
            fuente = f'{n["titulo"]} {n["bajada"]} {n["texto"]}'
            cid = hashlib.sha1(f'{f["id"]}|{cod}|{f["cita"]}'.encode("utf-8")).hexdigest()[:10]
            por_codigo[cod].append({
                "id_cita": cid, "id_nota": f["id"], "cod": cod, "v": v, "voz": f["voz"], "marca": f["marca"],
                "calidad": int(f["calidad"] or 0), "medio": f["medio"], "fecha": f["fecha"], "periodo": f["periodo"],
                "url": f["url"], "mod": f["mod"], "titulo_nota": n["titulo"], "cita": f["cita"],
                "contexto": contexto(fuente, f["cita"]),
            })
    for cod, lista in por_codigo.items():
        (SALIDA / f"{cod}.json").write_text(json.dumps({"cod": cod, "candidatas": lista}, ensure_ascii=False, indent=1), encoding="utf-8")
    (RAIZ / "citas_trabajo" / "resumen_celdas.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(por_codigo)} códigos con candidatas; {sum(len(v) for v in por_codigo.values())} citas candidatas en {len(resumen)} celdas")


if __name__ == "__main__":
    main()
