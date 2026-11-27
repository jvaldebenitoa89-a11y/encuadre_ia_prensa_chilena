"""
Scraper CNN Chile - Corpus IA Chile
Estrategia: buscador interno /buscador/inteligencia artificial/page/N/ →
filtrar por fecha desde tarjetas → scraping de artículos vía HTML.
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

MEDIO = "CNN Chile"
FECHA_MIN = date(2019, 1, 1)
FECHA_MAX = date(2026, 9, 30)

BASE_URL = "https://www.cnnchile.com"
SEARCH_URL = f"{BASE_URL}/buscador/inteligencia%20artificial/page/{{page}}/"

OUTPUT_DIR = Path("datos/cnn")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/buscador/inteligencia%20artificial/",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "es-CL,es;q=0.9",
}


def fecha_desde_datetime(dt_str):
    """Convierte 'YYYY-MM-DDTHH:MM:SS-03:00' a objeto date. Retorna None si falla."""
    if not dt_str:
        return None
    try:
        # isoformat con zona horaria
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).date()
    except Exception:
        try:
            return date.fromisoformat(dt_str[:10])
        except Exception:
            return None


def get_search_page(page_num):
    """Obtiene una página de resultados. Retorna lista de (url, fecha) y total_paginas."""
    url = SEARCH_URL.format(page=page_num)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        results = []
        for card in soup.select(".main-card"):
            link_el = card.select_one(".main-card__title a")
            time_el = card.select_one("time[datetime]")
            if not link_el:
                continue
            href = link_el.get("href", "")
            if href.startswith("/"):
                href = BASE_URL + href
            dt_str = time_el.get("datetime", "") if time_el else ""
            fecha = fecha_desde_datetime(dt_str)
            results.append((href, fecha))

        # Detectar total de páginas
        total_pags = None
        match = re.search(r'Página\s+\d+\s+de\s+(\d+)', r.text)
        if match:
            total_pags = int(match.group(1))

        return results, total_pags

    except Exception as e:
        print(f"  ERROR página {page_num}: {e}")
        return [], None


def scrape_articulo(url):
    """Extrae contenido de un artículo de CNN Chile."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        article = soup.select_one(".main-article")
        if not article:
            return None

        header = article.select_one(".main-article__header")
        body = article.select_one(".main-article__body")

        # Título
        headline = (header.select_one("h1") or header.select_one("h2") or soup.select_one("h1"))
        headline = headline.get_text(strip=True) if headline else ""

        # Fecha
        time_el = header.select_one("time[datetime]") if header else None
        date_published = time_el.get("datetime", "") if time_el else ""

        # Autor
        author_el = header.select_one(".main-article-heading__author") if header else None
        if author_el:
            # Eliminar el texto "Por" y juntar nombres
            names = [el.get_text(strip=True) for el in author_el.select("a, span") if el.get_text(strip=True) and el.get_text(strip=True) != "Por"]
            author = ", ".join(names)
        else:
            author = ""

        # Descripción (meta description como bajada)
        meta_desc = soup.select_one('meta[name="description"]')
        bajada = meta_desc.get("content", "") if meta_desc else ""

        # Texto del artículo (párrafos del body)
        if body:
            # Eliminar publicidad y elementos relacionados
            for rem in body.select(".ad, .publicidad, .rtb_slot, [id*='ad_'], .related, .more-news, script, style"):
                rem.decompose()
            paragraphs = [p.get_text(separator=" ", strip=True) for p in body.select("p") if len(p.get_text(strip=True)) > 20]
            texto = " ".join(paragraphs)
        else:
            texto = ""

        # Sección desde URL: /{seccion}/{slug}/
        path_parts = [p for p in r.url.replace(BASE_URL, "").split("/") if p]
        seccion = path_parts[0] if len(path_parts) > 0 else ""

        return {
            "headline": headline,
            "datePublished": date_published,
            "dateModified": date_published,
            "author": author,
            "bajada": bajada,
            "texto": texto,
            "seccion": seccion,
        }

    except Exception as e:
        print(f"    ERROR artículo: {e}")
        return None


def scrape_cnn():
    print("[CNN Chile] Paso 1: Obteniendo URLs de búsqueda...")

    # Primera página para conocer el total
    _, total_pags = get_search_page(0)
    if total_pags:
        print(f"[CNN Chile] Total páginas: {total_pags} (~{total_pags * 12} artículos)")
    else:
        total_pags = 50
        print(f"[CNN Chile] No se pudo leer total; usando {total_pags} páginas estimadas")

    urls_en_rango = []
    urls_fuera_rango = 0

    for page in range(0, total_pags):
        if page % 5 == 0:
            print(f"  Página {page+1}/{total_pags} | URLs en rango: {len(urls_en_rango)}")

        resultados, _ = get_search_page(page)
        if not resultados:
            print(f"  Página {page} vacía — deteniendo")
            break

        all_old = True
        for url, fecha in resultados:
            if fecha is None:
                urls_en_rango.append(url)
                all_old = False
            elif FECHA_MIN <= fecha <= FECHA_MAX:
                urls_en_rango.append(url)
                all_old = False
            elif fecha < FECHA_MIN:
                urls_fuera_rango += 1
            else:
                # fecha > FECHA_MAX (muy reciente, después de sept 2026)
                all_old = False

        # Parar si todos son anteriores a 2019
        if all_old and urls_fuera_rango > 5:
            print(f"  Todos los artículos en página {page} son anteriores a 2019. Deteniendo.")
            break

        time.sleep(0.4)

    print(f"\n[CNN Chile] URLs en rango 2019-2026: {len(urls_en_rango)}")
    print(f"[CNN Chile] URLs fuera de rango: {urls_fuera_rango}")

    # Guardar lista de URLs
    with open(OUTPUT_DIR / "urls_cnn.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls_en_rango))

    # Paso 2: Scrapear cada artículo
    print("\n[CNN Chile] Paso 2: Scrapeando artículos...")
    articulos = []
    errores = []

    for i, url in enumerate(urls_en_rango):
        if i % 50 == 0:
            print(f"  Artículo {i+1}/{len(urls_en_rango)}...")

        data = scrape_articulo(url)
        if data:
            art_id = f"CNN_{i+1:06d}"
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
                "sub_seccion": "",
                "url": url,
                "fecha_scraping": datetime.now().isoformat(),
                "fuente_busqueda": "inteligencia artificial",
            })
        else:
            errores.append(url)

        time.sleep(0.35)

    print(f"\n[CNN Chile] Artículos scrapeados: {len(articulos)}")
    print(f"[CNN Chile] Errores: {len(errores)}")

    if articulos:
        df = pd.DataFrame(articulos)
        csv_path = OUTPUT_DIR / "cnn_raw.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[CNN Chile] Guardado: {csv_path}")

        jsonl_path = OUTPUT_DIR / "cnn_raw.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for art in articulos:
                f.write(json.dumps(art, ensure_ascii=False) + "\n")
        print(f"[CNN Chile] Guardado: {jsonl_path}")

    if errores:
        with open(OUTPUT_DIR / "cnn_errores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(errores))
        print(f"[CNN Chile] Errores guardados: {len(errores)}")

    return articulos


if __name__ == "__main__":
    scrape_cnn()
