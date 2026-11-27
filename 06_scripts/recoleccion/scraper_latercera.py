"""
Scraper La Tercera - Corpus IA Chile
Usa la API interna de Arc Publishing (story-feed-tag-fetch).
Etiqueta: inteligencia-artificial | Período: 2019-01-01 a 2026-09-30
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path

MEDIO = "La Tercera"
FECHA_MIN = "2019-01-01"
FECHA_MAX = "2026-09-30"
BASE_URL = "https://www.latercera.com"
API_URL = f"{BASE_URL}/pf/api/v3/content/fetch/story-feed-tag-fetch"
TAG_SLUG = "inteligencia-artificial"
SIZE = 24
OUTPUT_DIR = Path("datos/latercera")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/etiqueta/{TAG_SLUG}/",
    "Accept": "application/json, */*",
}

def fecha_en_rango(fecha_str):
    try:
        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00").replace("+00:00", ""))
        return datetime.fromisoformat(FECHA_MIN) <= fecha <= datetime.fromisoformat(FECHA_MAX + "T23:59:59")
    except Exception:
        return True

def fetch_pagina(offset):
    query = json.dumps({
        "feedOffset": offset,
        "feedSize": SIZE,
        "fromComponent": "result-list",
        "tagSlug": TAG_SLUG
    }, separators=(',', ':'))
    params = {"query": query, "d": "1277", "mxId": "00000000", "_website": "la-tercera"}
    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ERROR en offset {offset}: {e}")
        return None

def scrape_latercera():
    articulos = []
    excluidos = []

    print(f"[La Tercera] Iniciando scraping: '{TAG_SLUG}'")
    primera = fetch_pagina(0)
    if not primera:
        print("Error en primera llamada. Abortando.")
        return

    total = primera.get("count", 0)
    print(f"[La Tercera] Total en API: {total}")

    offset = 0
    while offset < total:
        print(f"  Lote offset {offset}/{total}...")

        data = primera if offset == 0 else fetch_pagina(offset)
        if not data:
            break

        elementos = data.get("content_elements", [])
        if not elementos:
            break

        for art in elementos:
            fecha_pub = art.get("first_publish_date", "") or art.get("publish_date", "")

            if not fecha_en_rango(fecha_pub):
                excluidos.append({"id": art.get("_id"), "fecha": fecha_pub, "razon": "fuera de rango"})
                continue

            # Extraer autor
            autores = art.get("credits", {}).get("by", [])
            autor = ", ".join([a.get("name", "") for a in autores]) if autores else ""

            # Extraer URL
            canonical = art.get("canonical_url", "")
            url = BASE_URL + canonical if canonical.startswith("/") else canonical

            art_id = f"LT_{art.get('_id', 'NA')}"

            articulos.append({
                "id": art_id,
                "medio": MEDIO,
                "fecha_publicacion": fecha_pub,
                "fecha_modificacion": art.get("last_updated_date", ""),
                "titulo": art.get("headlines", {}).get("basic", ""),
                "bajada": art.get("description", {}).get("basic", ""),
                "texto": "",  # requiere visitar cada artículo (paywall)
                "autor": autor,
                "seccion": art.get("taxonomy", {}).get("primary_section", {}).get("name", ""),
                "sub_seccion": "",
                "url": url,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": "inteligencia artificial"
            })

        offset += SIZE
        time.sleep(0.4)

    print(f"\n[La Tercera] Artículos en rango: {len(articulos)}")
    print(f"[La Tercera] Excluidos: {len(excluidos)}")

    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "latercera_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[La Tercera] Guardado: {csv_path}")

        jsonl_path = OUTPUT_DIR / "latercera_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[La Tercera] Guardado: {jsonl_path}")

    if excluidos:
        with open(OUTPUT_DIR / "latercera_excluidos.json", "w", encoding="utf-8") as f:
            json.dump(excluidos, f, ensure_ascii=False, indent=2)

    return articulos

if __name__ == "__main__":
    scrape_latercera()
