"""
Scraper T13 (Canal 13) - Corpus IA Chile
Estrategia: buscador interno /search?q=inteligencia+artificial&offset=N →
recolectar URLs únicas de /noticia/ → scraping de artículos vía JSON-LD + .cuerpo-content.
Cobertura estimada: ~2023-2026 (T13 no indexa artículos anteriores en su búsqueda).
Período objetivo: 2019-01-01 a 2026-09-30
"""

import requests
import pandas as pd
import json
import time
import re
from datetime import datetime, date
from pathlib import Path
from bs4 import BeautifulSoup

MEDIO = "T13"
FECHA_MIN = date(2019, 1, 1)
FECHA_MAX = date(2026, 9, 30)

BASE_URL = "https://www.t13.cl"
SEARCH_URL = f"{BASE_URL}/search"

OUTPUT_DIR = Path("datos/t13")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/etiqueta/inteligencia-artificial",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "es-CL,es;q=0.9",
}

# Fecha al final de la URL: -D-M-YYYY
RE_FECHA_URL = re.compile(r'-(\d{1,2})-(\d{1,2})-(\d{4})$')


def fecha_desde_url(url):
    """Extrae fecha de URL tipo .../slug-D-M-YYYY. Retorna date o None."""
    path = url.split('?')[0].rstrip('/')
    m = RE_FECHA_URL.search(path)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def parse_t13_date(date_str):
    """Parsea el formato peculiar de T13: '2024-12-30 03:30:00T2024-12-30 03:30:00' o ISO."""
    if not date_str:
        return ""
    # T13 duplica la fecha: "YYYY-MM-DD HH:MM:SS T YYYY-..."
    clean = date_str.split("T")[0].strip()
    return clean[:10] if len(clean) >= 10 else clean


def get_search_page(offset):
    """Obtiene resultados de búsqueda para 'inteligencia artificial'. Retorna (urls, has_next)."""
    params = {"q": "inteligencia artificial", "offset": offset, "limit": 10}
    try:
        r = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Artículos del bloque de resultados de búsqueda (buscador)
        urls = []
        for a in soup.find_all("a", href=re.compile(r'/noticia/')):
            href = a.get("href", "")
            if href.startswith("/"):
                href = BASE_URL + href
            if href not in urls:
                urls.append(href)

        has_next = bool(soup.find("a", string=re.compile(r"Siguiente", re.I)))
        return urls, has_next

    except Exception as e:
        print(f"  ERROR offset {offset}: {e}")
        return [], False


def scrape_articulo(url):
    """Extrae contenido completo de un artículo T13."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # JSON-LD
        headline = ""
        date_published = ""
        date_modified = ""
        description = ""
        article_section = ""

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") in ("NewsArticle", "Article"):
                        headline = item.get("headline", "")
                        date_published = parse_t13_date(item.get("datePublished", ""))
                        date_modified = parse_t13_date(item.get("dateModified", ""))
                        description = item.get("description", "")
                        article_section = item.get("articleSection", "")
                        break
            except Exception:
                continue

        # Autor: está en el DOM, no en JSON-LD
        author_el = soup.select_one("[class*='autor'], [class*='author'], .byline, .reporter")
        if author_el:
            author = author_el.get_text(separator=" ", strip=True).replace("Por ", "")
        else:
            author = ""

        # Texto del artículo: .cuerpo-content o .cuerpo.article-component__main
        body_el = soup.select_one(".cuerpo-content, .cuerpo.article-component__main, .row.articulo-detalle-content")
        if body_el:
            for rem in body_el.select(".ad, .publicidad, script, style, [class*='ad_'], [class*='related']"):
                rem.decompose()
            paragraphs = [p.get_text(separator=" ", strip=True) for p in body_el.find_all("p") if len(p.get_text(strip=True)) > 20]
            texto = " ".join(paragraphs)
        else:
            texto = ""

        # Sección desde URL: /noticia/{seccion}/{slug}
        path_parts = [p for p in r.url.replace(BASE_URL, "").split("/") if p]
        seccion = path_parts[1] if len(path_parts) > 1 else ""

        return {
            "headline": headline,
            "datePublished": date_published,
            "dateModified": date_modified,
            "author": author,
            "bajada": description,
            "texto": texto,
            "seccion": seccion,
            "articleSection": article_section,
        }

    except Exception as e:
        print(f"    ERROR artículo: {e}")
        return None


def fecha_en_rango(fecha_str):
    """Verifica si una fecha ISO string ('YYYY-MM-DD') está en el rango."""
    try:
        f = date.fromisoformat(fecha_str[:10])
        return FECHA_MIN <= f <= FECHA_MAX
    except Exception:
        return True  # si no se puede parsear, incluir


def scrape_t13():
    print("[T13] Paso 1: Recolectando URLs desde buscador...")
    print("[T13] Nota: cobertura estimada 2023-2026 (búsqueda interna no indexa contenido anterior)")

    todas_urls = set()
    offset = 0

    while True:
        if offset % 30 == 0:
            print(f"  Offset {offset} | URLs únicas: {len(todas_urls)}")

        urls, has_next = get_search_page(offset)
        if not urls:
            print(f"  Offset {offset}: sin resultados. Deteniendo.")
            break

        for u in urls:
            todas_urls.add(u)

        if not has_next:
            print(f"  Offset {offset}: última página.")
            break

        offset += 10
        time.sleep(0.4)

    print(f"\n[T13] URLs únicas recolectadas: {len(todas_urls)}")

    # Guardar lista
    with open(OUTPUT_DIR / "urls_t13.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(todas_urls)))

    # Paso 2: Scrapear artículos
    print("\n[T13] Paso 2: Scrapeando artículos...")
    articulos = []
    errores = []
    excluidos = []

    for i, url in enumerate(sorted(todas_urls)):
        if i % 20 == 0:
            print(f"  Artículo {i+1}/{len(todas_urls)}...")

        # Pre-filtro por fecha en URL
        fecha_url = fecha_desde_url(url)
        if fecha_url is not None and not (FECHA_MIN <= fecha_url <= FECHA_MAX):
            excluidos.append(url)
            continue

        data = scrape_articulo(url)
        if data:
            # Filtro por fecha publicación
            if data["datePublished"] and not fecha_en_rango(data["datePublished"]):
                excluidos.append(url)
                continue

            art_id = f"T13_{i+1:06d}"
            articulos.append({
                "id": art_id,
                "medio": MEDIO,
                "fecha_publicacion": data["datePublished"],
                "fecha_modificacion": data["dateModified"],
                "titulo": data["headline"],
                "bajada": data["bajada"],
                "texto": data["texto"],
                "autor": data["author"],
                "seccion": data["seccion"],
                "sub_seccion": data["articleSection"],
                "url": url,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": "inteligencia artificial",
            })
        else:
            errores.append(url)

        time.sleep(0.35)

    print(f"\n[T13] Artículos scrapeados: {len(articulos)}")
    print(f"[T13] Excluidos por rango: {len(excluidos)}")
    print(f"[T13] Errores: {len(errores)}")

    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "t13_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[T13] Guardado: {csv_path}")

        jsonl_path = OUTPUT_DIR / "t13_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[T13] Guardado: {jsonl_path}")

    if errores:
        with open(OUTPUT_DIR / "t13_errores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(errores))

    return articulos


if __name__ == "__main__":
    scrape_t13()
