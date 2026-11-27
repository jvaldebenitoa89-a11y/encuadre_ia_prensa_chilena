"""
Corrección de fechas de CNN Chile.
El scraper original tomó la fecha de la cabecera (re-indexación del sitio, 2026-04-08) en 328 de 428 notas.
Las fechas reales (datePublished) están en datos/cnn/cnn_fechas_reales.json.
Uso (desde 20 PLURALISMO): python codificacion\corregir_fechas_cnn.py
Hace respaldo en _respaldo_fechas_cnn/, corrige fechas en todos los archivos derivados y excluye
las notas fuera del período 2019-01-01 a 2026-09-30.
"""

import csv
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
TR = RAIZ / "citas_trabajo"
RESP = RAIZ / "_respaldo_fechas_cnn"
MIN, MAX = "2019-01-01", "2026-09-30"

reales = json.load(open(RAIZ / "datos" / "cnn" / "cnn_fechas_reales.json", encoding="utf-8"))
corr = {i: v["fecha_real"] for i, v in reales.items() if v.get("fecha_real")}
fuera = {i for i, f in corr.items() if f < MIN or f > MAX}


def periodo(a):
    return "P1_2019-2021" if a <= 2021 else {2022: "P2_2022", 2023: "P3_2023", 2024: "P4_2024"}.get(a, "P5_2025-2026")


def respaldar(p):
    destino = RESP / p.relative_to(RAIZ)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copy2(p, destino)


def fix_rec(r, campo_id="id_nota"):
    """Actualiza fecha/anio/periodo de un registro dict. Devuelve False si debe excluirse."""
    i = r.get(campo_id) or r.get("id")
    if i in fuera:
        return False
    if i in corr:
        f = corr[i]
        if "fecha" in r:
            r["fecha"] = f
        if "anio" in r:
            r["anio"] = int(f[:4]) if isinstance(r["anio"], int) else f[:4]
        if "periodo" in r:
            r["periodo"] = periodo(int(f[:4]))
    return True


def jsonl(p, campo_id="id"):
    respaldar(p)
    filas = [json.loads(l) for l in open(p, encoding="utf-8")]
    nuevas = [r for r in filas if fix_rec(r, campo_id)]
    with open(p, "w", encoding="utf-8") as f:
        for r in nuevas:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(filas), len(nuevas)


# 1) corpus maestro, población, notas codificadas
print("corpus_maestro:", jsonl(RAIZ / "corpus_maestro.jsonl"))
print("poblacion:", jsonl(COD / "poblacion.jsonl"))
print("completo_notas:", jsonl(COD / "completo_notas.jsonl"))

# 2) filas de códigos (csv)
p = COD / "completo_codigos.csv"
respaldar(p)
rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
campos = list(rows[0].keys())
nuevas = []
for r in rows:
    if r["id"] in fuera:
        continue
    if r["id"] in corr:
        r["fecha"] = corr[r["id"]]
        r["anio"] = corr[r["id"]][:4]
        r["periodo"] = periodo(int(corr[r["id"]][:4]))
    nuevas.append(r)
with open(p, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    w.writerows(nuevas)
print("completo_codigos:", len(rows), "->", len(nuevas))

# 3) trabajo de citas
p = TR / "universo_citas.json"
respaldar(p)
u = json.load(open(p, encoding="utf-8"))
u2 = [c for c in u if fix_rec(c)]
json.dump(u2, open(p, "w", encoding="utf-8"), ensure_ascii=False)
print("universo_citas:", len(u), "->", len(u2))

n_cand = 0
for f in (TR / "candidatas").glob("*.json"):
    respaldar(f)
    d = json.load(open(f, encoding="utf-8"))
    antes = len(d["candidatas"])
    d["candidatas"] = [c for c in d["candidatas"] if fix_rec(c)]
    n_cand += antes - len(d["candidatas"])
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("candidatas excluidas por fuera de rango:", n_cand)

p = TR / "seleccion_final.json"
respaldar(p)
sel = json.load(open(p, encoding="utf-8"))
quitadas = 0
for cod in sel:
    for v in sel[cod]:
        antes = len(sel[cod][v])
        sel[cod][v] = [c for c in sel[cod][v] if fix_rec(c)]
        quitadas += antes - len(sel[cod][v])
json.dump(sel, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("seleccion_final: citas quitadas por fuera de rango:", quitadas)

# 4) emergentes: recalcula conteos y corrige citas
import sys
sys.path.insert(0, str(COD))
import emergentes_consolidar as ec  # noqa: E402

pc = RAIZ / "emergentes_consolidados.json"
pr = RAIZ / "emergentes_resumen.json"
respaldar(pc)
respaldar(pr)
old = json.load(open(pc, encoding="utf-8"))
_, notas, grupos = ec.cargar()
n_act = sum(1 for n in notas if n["c1"] in ("central", "secundaria"))
por_et = {it["etiqueta"]: it for it in old["categorias"]}
nuevas_cats = []
for et, regs in sorted(grupos.items(), key=lambda x: -len({n["id"] for n, _ in x[1]})):
    ids = {n["id"] for n, _ in regs}
    it = por_et.get(et, {"etiqueta": et, "definicion": ec.DEFINICIONES.get(et, ""), "citas": []})
    it.update({
        "n_notas": len(ids), "n_registros": len(regs), "pct_notas_analiticas": round(100 * len(ids) / n_act, 2),
        "valoracion": dict(Counter(e.get("v", "?") for _, e in regs)),
        "periodos": dict(sorted(Counter(n["periodo"] for n, _ in regs).items())),
        "medios": dict(Counter(n["medio_codigo"] for n, _ in regs)),
        "recomendacion": "promover a código" if len(ids) >= 40 else "vigilar" if len(ids) >= 10 else "registrar sin promover",
    })
    cs = []
    for q in it.get("citas", []):
        if q.get("id_nota") in fuera:
            continue
        if q.get("id_nota") in corr:
            q["fecha"] = corr[q["id_nota"]]
        cs.append(q)
    it["citas"] = cs
    nuevas_cats.append(it)
json.dump({"n_notas_analiticas": n_act, "categorias": nuevas_cats}, open(pc, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
res = [{k: v for k, v in it.items() if k != "citas"} for it in nuevas_cats]
json.dump({"n_notas_analiticas": n_act, "categorias": res}, open(pr, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("emergentes recalculados:", len(nuevas_cats), "categorías; notas analíticas:", n_act)

# 5) registro de exclusiones
json.dump({"criterio": f"fecha real de publicación fuera de {MIN} a {MAX}", "ids": sorted(fuera),
           "fechas": {i: corr[i] for i in sorted(fuera)}}, open(RAIZ / "datos" / "cnn" / "cnn_excluidas_fuera_de_rango.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("CNN excluidas por fecha fuera de rango:", len(fuera))
