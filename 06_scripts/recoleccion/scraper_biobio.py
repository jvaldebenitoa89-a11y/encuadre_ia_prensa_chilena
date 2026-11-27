"""
Scraper BioBioChile - Corpus IA Chile
Estrategia: sitemaps mensuales → filtrar URLs con 'inteligencia-artificial' →
scraping via JSON-LD (incluye texto completo).
Período: 2019-01 a 2026-09
"""

import requests
import pandas as pd
import json
import time
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

MEDIO = "BioBioChile"
FECHA_MIN = "2019-01-01"
FECHA_MAX = "2026-09-30"
SITEMAP_BASE = "https://www.biobiochile.cl/static/sitemap-{year}-{month:02d}.xml"
OUTPUT_DIR = Path("datos/biobio")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
}

def limpiar_html(texto):
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', texto)).strip()

def get_sitemap_urls(year, month):
    url = SITEMAP_BASE.format(year=year, month=month)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//sm:loc', ns)]
        return urls
    except Exception as e:
        print(f"  ERROR sitemap {year}-{month:02d}: {e}")
        return []

def scrape_articulo(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        # Extraer JSON-LD
        matches = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                articles = data if isinstance(data, list) else [data]
                for art in articles:
                    if art.get('@type') == 'NewsArticle':
                        return {
                            'headline': art.get('headline', ''),
                            'datePublished': art.get('datePublished', ''),
                            'dateModified': art.get('dateModified', ''),
                            'author': art.get('author', {}).get('name', '') if isinstance(art.get('author'), dict) else '',
                            'description': limpiar_html(art.get('description', '')),
                            'articleBody': limpiar_html(art.get('articleBody', '')),
                            'articleSection': art.get('articleSection', ''),
                        }
            except Exception:
                continue
    except Exception as e:
        print(f"    ERROR artículo: {e}")
    return None

def scrape_biobio():
    # Paso 1: Recolectar todas las URLs relevantes de los sitemaps
    print("[BioBioChile] Paso 1: Recolectando URLs de sitemaps...")
    urls_ia = []

    for year in range(2019, 2027):
        mes_fin = 10 if year == 2026 else 13
        for month in range(1, mes_fin):
            urls = get_sitemap_urls(year, month)
            ia_mes = [u for u in urls if 'inteligencia-artificial' in u.lower()]
            if ia_mes:
                print(f"  {year}-{month:02d}: {len(urls)} URLs → {len(ia_mes)} con IA")
            urls_ia.extend(ia_mes)
            time.sleep(0.2)

    print(f"\n[BioBioChile] Total URLs con 'inteligencia-artificial': {len(urls_ia)}")

    # Guardar lista de URLs como respaldo
    with open(OUTPUT_DIR / "urls_ia.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls_ia))
    print(f"[BioBioChile] URLs guardadas en datos/biobio/urls_ia.txt")

    # Paso 2: Scrapear cada artículo
    print("\n[BioBioChile] Paso 2: Scrapeando artículos...")
    articulos = []
    errores = []

    for i, url in enumerate(urls_ia):
        if i % 50 == 0:
            print(f"  Artículo {i+1}/{len(urls_ia)}...")
        data = scrape_articulo(url)
        if data:
            # Extraer sección y fecha desde URL: /noticias/seccion/subseccion/YYYY/MM/DD/slug.shtml
            partes = url.replace("https://www.biobiochile.cl/", "").split("/")
            seccion = partes[1] if len(partes) > 1 else ""
            sub_seccion = partes[2] if len(partes) > 2 else ""
            art_id = f"BBC_{i+1:06d}"

            articulos.append({
                "id": art_id,
                "medio": MEDIO,
                "fecha_publicacion": data['datePublished'],
                "fecha_modificacion": data['dateModified'],
                "titulo": data['headline'],
                "bajada": data['description'],
                "texto": data['articleBody'],
                "autor": data['author'],
                "seccion": seccion,
                "sub_seccion": sub_seccion,
                "url": url,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": "inteligencia artificial"
            })
        else:
            errores.append(url)
        time.sleep(0.3)

    print(f"\n[BioBioChile] Artículos scrapeados: {len(articulos)}")
    print(f"[BioBioChile] Errores: {len(errores)}")

    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "biobio_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[BioBioChile] Guardado: {csv_path}")

        jsonl_path = OUTPUT_DIR / "biobio_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[BioBioChile] Guardado: {jsonl_path}")

    if errores:
        with open(OUTPUT_DIR / "biobio_errores.txt", "w") as f:
            f.write("\n".join(errores))

    return articulos

if __name__ == "__main__":
    scrape_biobio()
