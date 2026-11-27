"""
Complemento La Tercera - Corpus IA Chile
scraper_latercera.py guardó titulo y bajada pero dejó 'texto' vacío. Este script visita cada URL
con una petición HTTP normal (sin credenciales) y extrae el cuerpo desde el JSON-LD (articleBody)
que el servidor entrega en el HTML público. Es reanudable.
Salida: datos/latercera/latercera_texto.jsonl  (id, url, texto, n_palabras, estado)
"""

import json
import re
import sys
import time
import html as htmllib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pandas as pd
import requests

BASE_URL = "https://www.latercera.com"
SRC = Path("datos/latercera/latercera_raw.csv")
MODO_B = len(sys.argv) > 1 and sys.argv[1] == "B"
OUT = Path("datos/latercera/latercera_texto_b.jsonl" if MODO_B else "datos/latercera/latercera_texto.jsonl")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/etiqueta/inteligencia-artificial/",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "es-CL,es;q=0.9",
}
RE_LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.S)
lock = Lock()


def limpiar(t):
    t = re.sub(r'<[^>]+>', ' ', t or '')
    t = htmllib.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


def extraer(url):
    r = requests.get(url, headers=HEADERS, timeout=40)
    r.raise_for_status()
    for m in RE_LD.findall(r.text):
        try:
            j = json.loads(m)
        except Exception:
            continue
        for it in (j if isinstance(j, list) else [j]):
            if isinstance(it, dict) and it.get("articleBody"):
                return limpiar(it["articleBody"])
    return ""


def tarea(fila):
    time.sleep(0.3)
    try:
        texto = extraer(fila["url"])
        estado = "ok" if texto else "sin_articleBody"
    except Exception as e:
        texto, estado = "", f"error:{type(e).__name__}"
    reg = {"id": fila["id"], "url": fila["url"], "texto": texto, "n_palabras": len(texto.split()), "estado": estado}
    with lock:
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    return estado


def main():
    df = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False)
    hechos = set()
    if OUT.exists():
        for linea in OUT.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(linea)
                if r["estado"] == "ok":
                    hechos.add(r["id"])
            except Exception:
                pass
    filas = df.to_dict("records")
    if MODO_B:
        filas = filas[1000:][::-1]
    pend = [r for r in filas if r["id"] not in hechos]
    print(f"[LT texto] total {len(df)} | ya listos {len(hechos)} | pendientes {len(pend)}", flush=True)
    cuenta = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        for i, estado in enumerate(ex.map(tarea, pend), 1):
            cuenta[estado] = cuenta.get(estado, 0) + 1
            if i % 100 == 0:
                print(f"  {i}/{len(pend)} {cuenta}", flush=True)
    print("[LT texto] fin", cuenta, flush=True)


if __name__ == "__main__":
    main()
