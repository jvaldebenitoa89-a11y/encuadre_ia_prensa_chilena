"""
Scraper Emol - Corpus IA Chile
Extrae noticias sobre "inteligencia artificial" desde Emol via su API interna.
Período: 2019-01-01 a 2026-09-30
"""

import requests
import pandas as pd
import json
import time
import re
from datetime import datetime
from pathlib import Path

# Configuración
QUERY = "inteligencia artificial"
MEDIO = "emol"
FECHA_MIN = "2019-01-01"
FECHA_MAX = "2026-09-30"
API_BASE = "https://newsapi.ecn.cl/NewsApi/emol/buscador/emol"
SIZE = 10  # resultados por página
OUTPUT_DIR = Path("datos/emol")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def limpiar_html(texto):
    """Elimina etiquetas HTML del texto."""
    if not texto:
        return ""
    limpio = re.sub(r'<[^>]+>', ' ', texto)
    limpio = re.sub(r'\s+', ' ', limpio).strip()
    return limpio

def extraer_bajada(bajada_lista):
    """Extrae texto de la bajada (es una lista de dicts)."""
    if not bajada_lista:
        return ""
    textos = [b.get("texto", "") for b in bajada_lista if isinstance(b, dict)]
    return " ".join(textos).strip()

def fecha_en_rango(fecha_str, fecha_min, fecha_max):
    """Verifica si una fecha está en el rango definido."""
    try:
        fecha = datetime.fromisoformat(fecha_str.replace("Z", ""))
        min_d = datetime.fromisoformat(fecha_min)
        max_d = datetime.fromisoformat(fecha_max + "T23:59:59")
        return min_d <= fecha <= max_d
    except Exception:
        return True  # si no se puede parsear, incluir

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": "https://www.emol.com/buscador/?query=inteligencia+artificial",
    "Origin": "https://www.emol.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-CL,es;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}

def fetch_pagina(from_offset):
    """Llama a la API y retorna los hits de una página."""
    params = {
        "q": QUERY,
        "size": SIZE,
        "fechaPublicacion": "2026-10-08",
        "from": from_offset
    }
    try:
        r = requests.get(API_BASE, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data
    except Exception as e:
        print(f"  ERROR en offset {from_offset}: {e}")
        return None

def scrape_emol():
    articulos = []
    excluidos = []

    # Primera llamada para saber el total
    print(f"[Emol] Iniciando scraping: '{QUERY}'")
    primera = fetch_pagina(0)
    if not primera:
        print("Error en primera llamada. Abortando.")
        return

    total = primera["hits"]["total"]
    print(f"[Emol] Total de resultados en API: {total}")

    # Iterar por todas las páginas
    offset = 0
    while offset < total:
        print(f"  Página {offset//SIZE + 1}/{(total//SIZE) + 1} (offset {offset})...")

        if offset == 0:
            data = primera
        else:
            data = fetch_pagina(offset)
            time.sleep(0.5)  # pausa entre llamadas

        if not data or not data["hits"]["hits"]:
            break

        for hit in data["hits"]["hits"]:
            src = hit.get("_source", {})
            fecha_pub = src.get("fechaPublicacion", "")

            # Filtrar por rango de fechas
            if not fecha_en_rango(fecha_pub, FECHA_MIN, FECHA_MAX):
                excluidos.append({
                    "id": src.get("id"),
                    "fecha": fecha_pub,
                    "razon": "fuera de rango"
                })
                continue

            art_id = f"EMOL_{src.get('id', 'NA'):08}"
            titulo = src.get("titulo", "")
            bajada = extraer_bajada(src.get("bajada", []))
            texto_html = src.get("texto", "")
            texto = limpiar_html(texto_html)
            permalink = src.get("permalink", "")
            seccion = src.get("seccion", "")
            sub_seccion = src.get("subSeccion", "")
            autor = src.get("autor", "")
            fecha_mod = src.get("fechaModificacion", "")

            articulos.append({
                "id": art_id,
                "medio": "Emol",
                "fecha_publicacion": fecha_pub,
                "fecha_modificacion": fecha_mod,
                "titulo": titulo,
                "bajada": bajada,
                "texto": texto,
                "autor": autor,
                "seccion": seccion,
                "sub_seccion": sub_seccion,
                "url": permalink,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": QUERY
            })

        offset += SIZE

    print(f"\n[Emol] Artículos en rango: {len(articulos)}")
    print(f"[Emol] Artículos excluidos (fuera de rango): {len(excluidos)}")

    # Guardar CSV
    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "emol_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[Emol] Guardado: {csv_path} ({len(df)} filas)")

        # También guardar JSONL
        jsonl_path = OUTPUT_DIR / "emol_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[Emol] Guardado: {jsonl_path}")

    # Guardar log de excluidos
    if excluidos:
        exc_path = OUTPUT_DIR / "emol_excluidos.json"
        with open(exc_path, "w", encoding="utf-8") as f:
            json.dump(excluidos, f, ensure_ascii=False, indent=2)
        print(f"[Emol] Log excluidos: {exc_path}")

    return articulos

if __name__ == "__main__":
    scrape_emol()
