"""
Scraper Cooperativa - Corpus IA Chile
Estrategia: búsqueda vía Prontus CGI (paginada) → filtrar por fecha desde URL →
scraping de artículos vía JSON-LD + selectores CSS.
Período: 2019-01-01 a 2026-09-30
"""

import requests
import pandas as pd
import json
import time
import re
from datetime import datetime, date
from pathlib import Path
from bs4 import BeautifulSoup

MEDIO = "Cooperativa"
FECHA_MIN = date(2019, 1, 1)
FECHA_MAX = date(2026, 9, 30)

SEARCH_URL = "https://www.cooperativa.cl/cgi-bin/prontus_search.cgi"
SEARCH_PARAMS_BASE = {
    "search_prontus": "noticias",
    "search_idx": "noticias",
    "search_tmp": "search_cooperativa_2018.html",
    "search_form": "no",
    "search_resxpag": "15",
    "search_maxpags": "10000",
    "search_orden": "cro",
    "search_texto": "inteligencia artificial",
    "search_modo": "and",
    "search_comodines": "no",
    "vista": "",
}

OUTPUT_DIR = Path("datos/cooperativa")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": "https://www.cooperativa.cl/",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "es-CL,es;q=0.9",
}

# Fecha en URL: /YYYY-MM-DD/HHMMSS.html
RE_FECHA_URL = re.compile(r'/(\d{4}-\d{2}-\d{2})/\d+\.html$')


def fecha_desde_url(url):
    """Extrae la fecha de la URL del artículo. Retorna objeto date o None."""
    m = RE_FECHA_URL.search(url)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            return None
    return None


def get_search_page(page_num):
    """Obtiene una página de resultados de búsqueda. Retorna lista de URLs de artículos."""
    params = dict(SEARCH_PARAMS_BASE)
    params["search_pag"] = str(page_num)
    try:
        r = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Buscar todos los links a artículos (/noticias/...YYYY/MM/DD/HHMMSS.html)
        links = []
        for a in soup.find_all("a", href=RE_FECHA_URL):
            href = a.get("href", "")
            if href.startswith("/"):
                href = "https://www.cooperativa.cl" + href
            if href not in links:
                links.append(href)
        # Detectar total de resultados en página 1
        total = None
        if page_num == 1:
            match = re.search(r'Resultados\s+\d+\s+al\s+\d+\s+de\s+([\d\.]+)', r.text)
            if match:
                total = int(match.group(1).replace(".", ""))
        return links, total
    except Exception as e:
        print(f"  ERROR página {page_num}: {e}")
        return [], None


def scrape_articulo(url):
    """Extrae contenido de un artículo de Cooperativa."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # JSON-LD
        headline = ""
        date_published = ""
        date_modified = ""
        author = ""
        keywords = []

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "NewsArticle":
                        headline = item.get("headline", "")
                        date_published = item.get("datePublished", "")
                        date_modified = item.get("dateModified", "")
                        # Autor: usar creator[0] (más específico que author: "Cooperativa.cl")
                        creators = item.get("creator", [])
                        if isinstance(creators, list) and creators:
                            # Evitar "Cooperativa.cl" genérico si hay otro
                            names = [c for c in creators if "cooperativa" not in c.lower()]
                            author = names[0] if names else creators[0]
                        kw = item.get("keywords", [])
                        keywords = kw if isinstance(kw, list) else [kw]
                        break
            except Exception:
                continue

        # Bajada
        bajada_el = soup.select_one(".texto-bajada")
        bajada = bajada_el.get_text(separator=" ", strip=True) if bajada_el else ""

        # Cuerpo del artículo
        cuerpo_el = soup.select_one(".cuerpo-articulo")
        if cuerpo_el:
            # Eliminar elementos de "leer más" y anuncios
            for rem in cuerpo_el.select(".leermas, .publicidad, .ad, script, style"):
                rem.decompose()
            texto = cuerpo_el.get_text(separator=" ", strip=True)
        else:
            texto = ""

        # Sección desde URL: /noticias/{seccion}/{sub_seccion}/...
        partes = url.replace("https://www.cooperativa.cl/noticias/", "").split("/")
        seccion = partes[0] if len(partes) > 0 else ""
        sub_seccion = partes[1] if len(partes) > 1 else ""

        return {
            "headline": headline,
            "datePublished": date_published,
            "dateModified": date_modified,
            "author": author,
            "bajada": bajada,
            "texto": texto,
            "seccion": seccion,
            "sub_seccion": sub_seccion,
            "keywords": "; ".join(keywords),
        }

    except Exception as e:
        print(f"    ERROR artículo: {e}")
        return None


def scrape_cooperativa():
    print("[Cooperativa] Paso 1: Obteniendo URLs de búsqueda...")

    # Obtener total de resultados
    _, total_resultados = get_search_page(1)
    if total_resultados:
        print(f"[Cooperativa] Total resultados: {total_resultados}")
        total_paginas = (total_resultados + 14) // 15
    else:
        total_paginas = 138  # estimado conservador
        print(f"[Cooperativa] No se pudo leer total; usando {total_paginas} páginas estimadas")

    # Recolectar todos los URLs dentro del rango de fecha
    urls_en_rango = []
    urls_fuera_rango = 0
    detenido_por_fecha = False

    for page in range(1, total_paginas + 1):
        if page % 10 == 0 or page == 1:
            print(f"  Página {page}/{total_paginas} | URLs en rango: {len(urls_en_rango)}")

        links, _ = get_search_page(page)
        if not links:
            print(f"  Página {page} vacía — deteniendo")
            break

        for url in links:
            f = fecha_desde_url(url)
            if f is None:
                urls_en_rango.append(url)  # sin fecha en URL, incluir por las dudas
            elif FECHA_MIN <= f <= FECHA_MAX:
                urls_en_rango.append(url)
            elif f < FECHA_MIN:
                urls_fuera_rango += 1
                detenido_por_fecha = True

        # Si todos los artículos de esta página son anteriores al rango, parar
        if detenido_por_fecha and urls_fuera_rango > 5 and len(links) > 0:
            fechas = [fecha_desde_url(u) for u in links]
            all_old = all(f is not None and f < FECHA_MIN for f in fechas)
            if all_old:
                print(f"  Todos los artículos en página {page} son anteriores a 2019. Deteniendo.")
                break

        time.sleep(0.4)

    print(f"\n[Cooperativa] URLs en rango 2019-2026: {len(urls_en_rango)}")
    print(f"[Cooperativa] URLs fuera de rango: {urls_fuera_rango}")

    # Guardar lista de URLs
    with open(OUTPUT_DIR / "urls_cooperativa.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls_en_rango))

    # Paso 2: Scrapear cada artículo
    print("\n[Cooperativa] Paso 2: Scrapeando artículos...")
    articulos = []
    errores = []

    for i, url in enumerate(urls_en_rango):
        if i % 50 == 0:
            print(f"  Artículo {i+1}/{len(urls_en_rango)}...")

        data = scrape_articulo(url)
        if data:
            art_id = f"COOP_{i+1:06d}"
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
                "sub_seccion": data["sub_seccion"],
                "keywords": data["keywords"],
                "url": url,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": "inteligencia artificial",
            })
        else:
            errores.append(url)

        time.sleep(0.35)

    print(f"\n[Cooperativa] Artículos scrapeados: {len(articulos)}")
    print(f"[Cooperativa] Errores: {len(errores)}")

    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "cooperativa_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[Cooperativa] Guardado: {csv_path}")

        jsonl_path = OUTPUT_DIR / "cooperativa_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[Cooperativa] Guardado: {jsonl_path}")

    if errores:
        with open(OUTPUT_DIR / "cooperativa_errores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(errores))
        print(f"[Cooperativa] Errores guardados: {len(errores)}")

    return articulos


if __name__ == "__main__":
    scrape_cooperativa()
