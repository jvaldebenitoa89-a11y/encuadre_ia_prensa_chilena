"""
Consolidación de categorías emergentes - Corpus IA Chile
Uso: python emergentes_consolidar.py preparar   -> citas_trabajo/candidatas_emergentes/*.json y emergentes_resumen.json
     python emergentes_consolidar.py cerrar     -> emergentes_consolidados.json (con citas verificadas)
"""

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "codificacion"
TRABAJO = RAIZ / "citas_trabajo"
FUS = {
    "ia_no_neutral_politica": "ia_no_neutral",
    "analogia_nuclear_oppenheimer": "momento_oppenheimer",
    "ia_industria_extractiva": "ia_industria_material",
}
DEFINICIONES = {
    "compania_afectiva": "La IA aparece como interlocutor afectivo, refugio o remedio frente a la soledad, al que se confían problemas personales.",
    "fuente_consultable": "Un chatbot es consultado como informante o pronosticador y su respuesta se publica como contenido noticioso, con autoridad.",
    "democratizadora_acceso": "La IA se presenta como capacidad puesta al alcance de todos o hecha accesible por una institución o empresa.",
    "referente_ficcional": "El texto ancla a la IA en un referente de ciencia ficción (Terminator, Matrix, Skynet) para activar o desactivar el temor.",
    "motivo_politico_atribuido": "Se atribuye a un actor un motivo político, de imagen o ulterior no declarado para impulsar o adoptar la IA.",
    "infraestructura_cotidiana": "La IA se presenta como sustrato ya presente y normalizado de lo cotidiano, sin carácter propio diferenciado.",
    "entretenimiento_viral": "La IA se presenta como juguete, curiosidad o moda de consumo que se difunde por redes, sin beneficio ni riesgo atribuidos.",
    "crisis_acelerador": "Un choque externo (p. ej. la pandemia) se presenta como lo que impulsa o abre una ventana a la adopción de la IA.",
    "ia_superior_humano": "La IA se presenta como capaz de lo que ningún humano puede, o como decisor más objetivo por carecer de sesgos emocionales.",
    "vigilancia_normalizada": "La IA se enuncia como dispositivo que evalúa o vigila a trabajadores o ciudadanos, presentado sin tensión ni daño.",
    "ia_sujeto_derechos": "La IA se presenta como persona sintiente con derecho a representación u otro estatus moral o jurídico.",
    "regulacion_habilitante": "La regulación se presenta como condición o palanca que habilita la inversión y la innovación.",
    "confianza_publica_legitimidad": "El horizonte deseable se define como una IA segura y confiable ante el público, con la confianza o la ética como criterio de legitimidad.",
    "autoevolucion_ia": "La IA aparece como agente de su propia mejora o evolución; se perfecciona a sí misma.",
    "ia_coautora_politica": "La IA participa en la producción de textos políticos o normativos, incluida su propia regulación.",
    "fuerza_laboral_equivalente": "Los robots con IA se encuadran como equivalentes de trabajadores humanos, sin valorarlos como oportunidad ni amenaza al empleo.",
}


def periodo(a):
    return "P1_2019-2021" if a <= 2021 else {2022: "P2_2022", 2023: "P3_2023", 2024: "P4_2024"}.get(a, "P5_2025-2026")


def cargar():
    pob = {}
    for l in open(COD / "poblacion.jsonl", encoding="utf-8"):
        n = json.loads(l)
        pob[n["id"]] = n
    notas = [json.loads(l) for l in open(COD / "completo_notas.jsonl", encoding="utf-8")]
    grupos = defaultdict(list)
    for n in notas:
        for e in n.get("emergentes") or []:
            et = FUS.get(e.get("etiqueta", "").strip().lower(), e.get("etiqueta", "").strip().lower())
            if et:
                grupos[et].append((n, e))
    return pob, notas, grupos


def contexto(fuente, cita, radio=350):
    i = fuente.find(cita)
    if i < 0:
        return ""
    return fuente[max(0, i - radio): i + len(cita) + radio]


def preparar():
    pob, notas, grupos = cargar()
    (TRABAJO / "candidatas_emergentes").mkdir(parents=True, exist_ok=True)
    (TRABAJO / "curadas_emergentes").mkdir(parents=True, exist_ok=True)
    n_act = sum(1 for n in notas if n["c1"] in ("central", "secundaria"))
    resumen, rng = [], random.Random(2026)
    for et, regs in sorted(grupos.items(), key=lambda x: -len({n["id"] for n, _ in x[1]})):
        ids = {n["id"] for n, _ in regs}
        defin = DEFINICIONES.get(et) or next((e.get("definicion", "") for _, e in regs if e.get("definicion")), "")
        item = {
            "etiqueta": et, "definicion": defin, "n_notas": len(ids), "n_registros": len(regs),
            "pct_notas_analiticas": round(100 * len(ids) / n_act, 2),
            "valoracion": dict(Counter(e.get("v", "?") for _, e in regs)),
            "periodos": dict(sorted(Counter(n["periodo"] for n, _ in regs).items())),
            "medios": dict(Counter(n["medio_codigo"] for n, _ in regs)),
            "recomendacion": "promover a código" if len(ids) >= 40 else "vigilar" if len(ids) >= 10 else "registrar sin promover",
        }
        resumen.append(item)
        if len(ids) < 3:
            continue
        cands = []
        por_p = defaultdict(list)
        for n, e in regs:
            if e.get("cita") and e.get("cita_estado") in ("exacta", "reparada"):
                por_p[n["periodo"]].append((n, e))
        for p in por_p:
            rng.shuffle(por_p[p])
        while len(cands) < 10 and any(por_p.values()):
            for p in sorted(por_p):
                if por_p[p] and len(cands) < 10:
                    n, e = por_p[p].pop()
                    src = pob[n["id"]]
                    fuente = f'{src["titulo"]} {src["bajada"]} {src["texto"]}'
                    cands.append({
                        "id_cita": f'{et}|{n["id"]}', "id_nota": n["id"], "cod": et, "v": e.get("v"), "voz": e.get("voz"),
                        "marca": "", "calidad": 0, "medio": n["medio"], "fecha": n["fecha"], "periodo": n["periodo"],
                        "url": src["url"], "titulo_nota": src["titulo"], "cita": e["cita"], "contexto": contexto(fuente, e["cita"]),
                    })
        (TRABAJO / "candidatas_emergentes" / f"{et}.json").write_text(
            json.dumps({"cod": et, "definicion": defin, "candidatas": cands}, ensure_ascii=False, indent=1), encoding="utf-8")
    (RAIZ / "emergentes_resumen.json").write_text(json.dumps({"n_notas_analiticas": n_act, "categorias": resumen}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(resumen)} categorías; {sum(1 for r in resumen if r['n_notas'] >= 3)} con candidatas")
    print(json.dumps([r["etiqueta"] for r in resumen if r["n_notas"] >= 3], ensure_ascii=False))


def cerrar():
    resumen = json.load(open(RAIZ / "emergentes_resumen.json", encoding="utf-8"))
    ver = {}
    for f in (TRABAJO / "curadas_emergentes").glob("*.json"):
        for v in json.load(open(f, encoding="utf-8")).get("veredictos", []):
            ver[v["id_cita"]] = v
    cats = []
    for it in resumen["categorias"]:
        citas = []
        p = TRABAJO / "candidatas_emergentes" / f'{it["etiqueta"]}.json'
        if p.exists():
            for c in json.load(open(p, encoding="utf-8"))["candidatas"]:
                v = ver.get(c["id_cita"])
                if v and v["veredicto"] in ("apta", "ajustar"):
                    c["repr"] = int(v.get("representatividad") or 1)
                    citas.append(c)
            citas.sort(key=lambda c: (-c["repr"], c["fecha"]))
        it["citas"] = [{k: c[k] for k in ("cita", "medio", "fecha", "id_nota", "url", "v", "voz")} for c in citas[:4]]
        cats.append(it)
    (RAIZ / "emergentes_consolidados.json").write_text(json.dumps({"n_notas_analiticas": resumen["n_notas_analiticas"], "categorias": cats}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("emergentes_consolidados.json escrito:", len(cats), "categorías")


if __name__ == "__main__":
    {"preparar": preparar, "cerrar": cerrar}[sys.argv[1]]()
