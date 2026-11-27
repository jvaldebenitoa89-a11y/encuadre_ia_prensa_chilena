"""
Consolidación de codificaciones - Corpus IA Chile
Uso: python consolidar.py <carpeta_salidas> <sufijo> <prefijo_salida>
Lee <lote>_<sufijo>.json, valida cada nota contra su texto fuente, la une con los metadatos reales
(id, medio, fecha) y escribe:
  <prefijo_salida>_notas.jsonl   una fila por nota codificada
  <prefijo_salida>_codigos.csv   una fila por (nota, código)
  <prefijo_salida>_informe.json  problemas y notas faltantes
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utilidades_codificacion import CATALOGO, validar_nota  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"


def periodo(anio):
    if anio <= 2021:
        return "P1_2019-2021"
    return {2022: "P2_2022", 2023: "P3_2023", 2024: "P4_2024"}.get(anio, "P5_2025-2026")


def main():
    carpeta, sufijo, prefijo = sys.argv[1:4]
    pob = {}
    for l in open(COD / "poblacion.jsonl", encoding="utf-8"):
        n = json.loads(l)
        pob[n["alias"]] = n
    esperadas = None
    if len(sys.argv) > 4:
        esperadas = set(json.load(open(sys.argv[4], encoding="utf-8")))

    notas_out, filas, problemas, vistos = [], [], {}, set()
    archivos = sorted(Path(carpeta).glob(f"*_{sufijo}.json"))
    for f in archivos:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            problemas[f.name] = [f"JSON inválido: {e}"]
            continue
        for n in d.get("notas", []):
            alias = n.get("alias")
            if alias not in pob:
                problemas[f"{f.name}:{alias}"] = ["alias desconocido"]
                continue
            if alias in vistos:
                problemas[f"{f.name}:{alias}"] = ["alias repetido"]
                continue
            vistos.add(alias)
            src = pob[alias]
            fuente = f'{src["titulo"]} {src["bajada"]} {src["texto"]}'
            n2, probs = validar_nota(n, fuente)
            if probs:
                problemas[f"{f.name}:{alias}"] = probs
            fila_nota = {
                "id": src["id"], "alias": alias, "medio_codigo": src["medio_codigo"], "medio": src["medio"],
                "fecha": src["fecha"], "anio": src["anio"], "periodo": periodo(src["anio"]),
                "c1": n2.get("c1"), "c2": n2.get("c2"), "c3": n2.get("c3"), "c4": n2.get("c4"), "c5": n2.get("c5"),
                "n_codigos": len(n2.get("codigos", [])), "emergentes": n2.get("emergentes", []),
                "dudas": n2.get("dudas", ""), "solo_titular_bajada": src["solo_titular_bajada"],
                "n_problemas": len(probs), "lote": d.get("lote"),
            }
            notas_out.append({**fila_nota, "codigos": n2.get("codigos", [])})
            for c in n2.get("codigos", []):
                ind = CATALOGO[c["cod"]]["ind"]
                filas.append({
                    "id": src["id"], "alias": alias, "medio_codigo": src["medio_codigo"], "medio": src["medio"],
                    "fecha": src["fecha"], "anio": src["anio"], "periodo": periodo(src["anio"]),
                    "c1": n2.get("c1"), "dimension": f"D{ind.split('.')[0]}", "indicador": ind, "cod": c["cod"],
                    "v": c.get("v"), "voz": c.get("voz"), "marca": c.get("marca"), "cita": c.get("cita", ""),
                    "calidad": c.get("calidad"), "cita_estado": c.get("cita_estado"),
                    "mod": json.dumps(c.get("mod") or {}, ensure_ascii=False), "url": src["url"],
                })

    with open(COD / f"{prefijo}_notas.jsonl", "w", encoding="utf-8") as f:
        for n in notas_out:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    cols = ["id", "alias", "medio_codigo", "medio", "fecha", "anio", "periodo", "c1", "dimension", "indicador", "cod", "v", "voz",
            "marca", "cita", "calidad", "cita_estado", "mod", "url"]
    with open(COD / f"{prefijo}_codigos.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    faltantes = sorted(esperadas - vistos) if esperadas is not None else []
    informe = {
        "archivos": len(archivos), "notas_consolidadas": len(notas_out), "filas_codigos": len(filas),
        "notas_con_problemas": len(problemas), "faltantes": len(faltantes),
        "c1": dict(Counter(n["c1"] for n in notas_out)),
        "citas": dict(Counter(r["cita_estado"] for r in filas)),
        "problemas": problemas, "alias_faltantes": faltantes,
    }
    (COD / f"{prefijo}_informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in informe.items() if k not in ("problemas", "alias_faltantes")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
