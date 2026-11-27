"""
Preparación del corpus maestro - Corpus IA Chile
Lee los CSV crudos de los 6 scrapers (+ cuerpo de La Tercera), limpia residuos de HTML/CSS,
elimina duplicados, normaliza fechas, asigna IDs estables y calcula rasgos de relevancia.
Salida: corpus_maestro.jsonl y informe_preparacion.json
"""

import html
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd

FECHA_MIN = date(2019, 1, 1)
FECHA_MAX = date(2026, 9, 30)

MEDIOS = {
    "EMOL": ("Emol", "datos/emol/emol_raw.csv"),
    "LT": ("La Tercera", "datos/latercera/latercera_raw.csv"),
    "BBC": ("BioBioChile", "datos/biobio/biobio_raw.csv"),
    "COOP": ("Cooperativa", "datos/cooperativa/cooperativa_raw.csv"),
    "CNN": ("CNN Chile", "datos/cnn/cnn_raw.csv"),
    "T13": ("T13", "datos/t13/t13_raw.csv"),
}

RE_CSS = re.compile(r'(?:[#.@][\w\-\s>,:\.#\[\]="\'\*\(\)\+~]*\{[^{}]*\}\s*)+')
RE_RELAC = re.compile(r'\{\s*RELACIONADAS?[^}]*\}', re.I)
RE_RELAC2 = re.compile(r'\{\s*RELACIONADAS?\s+https?://[^\s;}]+;?')
RE_CITA = re.compile(r'\{CITA\s+([^}]*)\}')
RE_JS = re.compile(r'\(function\s*\(|\$\(\s*document|function\s+\w+\s*\(')
RE_COMENT = re.compile(r'<!--|-->')
RE_TAG = re.compile(r'<[a-zA-Z/][^>]*>')
RE_TAIL_T13 = re.compile(r'\s*Inscríbete en nuestra lista de correo para recibir gratis las noticias más importantes del día, con la confianza de Teletrece\.?\s*$')
RE_TAIL_COOP = re.compile(r'\s*LEER ARTICULO COMPLETO\s*$')
RE_PATROCINADO = re.compile(r'(?i)este es un contenido presentado por|contenido patrocinado|contenido de marca|publirreportaje')

RE_IA_NUCLEO = re.compile(r'(?i:inteligencia\s+artificial)|\bIA\b|\bA\.?I\.?\b|\bIAs\b')
RE_IA_AMPLIO = re.compile(
    r'(?i:inteligencia\s+artificial|ia\s+generativa|chatgpt|openai|chatbot|machine\s+learning|aprendizaje\s+(?:autom[aá]tico|de\s+m[aá]quina|profundo)|deepfake|deepseek|midjourney|gemini|copilot|anthropic|algoritmo|rob[oó]t)|\bIA\b|\bGPT-?\d|\bLLM\b'
)


def limpiar_texto(medio, t):
    if not isinstance(t, str):
        return ""
    t = html.unescape(html.unescape(t)).replace("\xa0", " ")
    t = RE_RELAC.sub(" ", t)
    t = RE_RELAC2.sub(" ", t)
    t = RE_CITA.sub(lambda m: " " + m.group(1) + " ", t)
    m = RE_JS.search(t)
    if m and m.start() > len(t) * 0.5:
        t = t[:m.start()]
    t = RE_COMENT.sub(" ", t)
    t = RE_CSS.sub(" ", t)
    t = RE_TAG.sub(" ", t)
    if medio == "T13":
        t = RE_TAIL_T13.sub("", t)
    if medio == "COOP":
        t = RE_TAIL_COOP.sub("", t)
    return re.sub(r'\s+', ' ', t).strip()


def limpiar_simple(t):
    if not isinstance(t, str):
        return ""
    t = html.unescape(html.unescape(t)).replace("\xa0", " ")
    return re.sub(r'\s+', ' ', RE_TAG.sub(" ", t)).strip()


def fecha_local(medio, valor):
    if not isinstance(valor, str) or not valor.strip():
        return None
    try:
        ts = pd.Timestamp(valor.strip())
        if ts.tzinfo is not None and medio == "LT":
            ts = ts.tz_convert("America/Santiago")
        return ts.date()
    except Exception:
        m = re.match(r'(\d{4}-\d{2}-\d{2})', valor.strip())
        return date.fromisoformat(m.group(1)) if m else None


def fecha_desde_url(url):
    u = (url or "").split("?")[0].rstrip("/")
    m = re.search(r'-(\d{1,2})-(\d{1,2})-(\d{4})$', u)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    m = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', u)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def url_norm(u):
    u = (u or "").strip().lower().split("#")[0].split("?")[0].rstrip("/")
    return re.sub(r'^https?://(www\.)?', '', u)


def main():
    informe = {"por_medio": {}, "generado_con": "preparar_corpus.py"}
    registros = []

    lt_texto = {}
    for nombre_lt in ("latercera_texto.jsonl", "latercera_texto_b.jsonl"):
        p = Path("datos/latercera") / nombre_lt
        if not p.exists():
            continue
        for linea in p.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(linea)
            except Exception:
                continue
            if r.get("texto"):
                lt_texto[r["id"]] = r["texto"]

    for cod, (nombre, ruta) in MEDIOS.items():
        df = pd.read_csv(ruta, encoding="utf-8-sig", low_memory=False)
        inf = {"crudo": len(df)}
        vistos, filas = set(), []
        dup_url = fuera_rango = sin_fecha = fecha_recuperada = 0
        for r in df.to_dict("records"):
            un = url_norm(r.get("url"))
            if un in vistos:
                dup_url += 1
                continue
            vistos.add(un)
            f = fecha_local(cod, r.get("fecha_publicacion"))
            if f is None and cod in ("T13", "BBC"):
                f = fecha_desde_url(r.get("url"))
                if f is not None:
                    fecha_recuperada += 1
            if f is None:
                sin_fecha += 1
                continue
            if not (FECHA_MIN <= f <= FECHA_MAX):
                fuera_rango += 1
                continue
            texto_crudo = r.get("texto") if isinstance(r.get("texto"), str) and r.get("texto") else ""
            if cod == "LT" and not texto_crudo:
                texto_crudo = lt_texto.get(r["id"], "")
            texto = limpiar_texto(cod, texto_crudo)
            titulo = limpiar_simple(r.get("titulo"))
            bajada = limpiar_simple(r.get("bajada"))
            autor = limpiar_simple(r.get("autor")).replace("Por ", "", 1).strip()
            conjunto = f"{titulo} {bajada} {texto}"
            filas.append({
                "id_origen": r["id"], "medio_codigo": cod, "medio": nombre,
                "fecha": f.isoformat(), "anio": f.year,
                "titulo": titulo, "bajada": bajada, "texto": texto, "autor": autor,
                "seccion": limpiar_simple(r.get("seccion")), "url": (r.get("url") or "").strip(),
                "n_palabras": len(texto.split()),
                "n_ia_nucleo": len(RE_IA_NUCLEO.findall(conjunto)),
                "n_ia_amplio": len(RE_IA_AMPLIO.findall(conjunto)),
                "ia_en_titulo_bajada": bool(RE_IA_NUCLEO.search(f"{titulo} {bajada}")),
                "patrocinado": bool(RE_PATROCINADO.search(conjunto)),
            })
        # duplicados exactos por (titulo, fecha) dentro del medio
        clave, unicas = set(), []
        dup_tf = 0
        for x in filas:
            k = (x["titulo"].lower(), x["fecha"])
            if k in clave:
                dup_tf += 1
                continue
            clave.add(k)
            unicas.append(x)
        inf.update({"duplicadas_url": dup_url, "duplicadas_titulo_fecha": dup_tf,
                    "fuera_de_rango": fuera_rango, "sin_fecha": sin_fecha, "fecha_recuperada_desde_url": fecha_recuperada, "finales": len(unicas)})
        registros.extend(unicas)
        informe["por_medio"][cod] = inf

    # IDs estables: medio, fecha, url
    registros.sort(key=lambda x: (x["medio_codigo"], x["fecha"], url_norm(x["url"])))
    cont = Counter()
    for x in registros:
        k = (x["medio_codigo"], x["fecha"])
        cont[k] += 1
        x["id"] = f"{x['medio_codigo']}_{x['fecha'].replace('-', '')}_{cont[k]:03d}"

    with open("corpus_maestro.jsonl", "w", encoding="utf-8") as f:
        for x in registros:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    df = pd.DataFrame(registros)
    informe["total"] = len(df)
    informe["residuos_restantes"] = {
        "css": int(df["texto"].str.contains(r'\{[^}]*:[^}]*;').sum()),
        "relacionadas": int(df["texto"].str.contains('RELACIONADAS').sum()),
        "entidades": int(df["texto"].str.contains(r'&(?:quot|amp|nbsp|#\d+);').sum()),
        "texto_vacio": int((df["n_palabras"] == 0).sum()),
        "texto_menor_30": int((df["n_palabras"] < 30).sum()),
    }
    Path("informe_preparacion.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(informe, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
