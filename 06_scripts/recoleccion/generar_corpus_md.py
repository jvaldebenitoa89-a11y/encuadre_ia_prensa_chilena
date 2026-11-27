"""
Generador de corpus .md por medio y año - Corpus IA Chile
Formato estándar del proyecto FONDECYT Pluralismo: {CODIGO}_{ANIO}.md
Lee corpus_maestro.jsonl (salida de preparar_corpus.py, ya limpio, deduplicado y con IDs estables).
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

MAESTRO = Path("corpus_maestro.jsonl")
OUTPUT_DIR = Path("corpus_md")
HOY = datetime.now().strftime("%Y-%m-%d")

CORRIENTE = {
    "EMOL": "liberal / centroderecha",
    "LT": "liberal / centroderecha",
    "BBC": "independiente / popular",
    "COOP": "independiente / centro",
    "CNN": "independiente / centro",
    "T13": "independiente / centro",
}
FUENTE = {
    "EMOL": "datos/emol/emol_raw.csv",
    "LT": "datos/latercera/latercera_raw.csv + latercera_texto.jsonl",
    "BBC": "datos/biobio/biobio_raw.csv",
    "COOP": "datos/cooperativa/cooperativa_raw.csv",
    "CNN": "datos/cnn/cnn_raw.csv",
    "T13": "datos/t13/t13_raw.csv",
}


def esc(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def bloque(n):
    lineas = [
        f"<!-- ===== {n['id']} | {n['fecha']} ===== -->", "",
        f"## {n['titulo']}", "",
        f"`{n['id']}` · {n['fecha']} · [fuente]({n['url']})", "",
        "---",
        f"id: {n['id']}",
        f"medio: {n['medio']}",
        f"corriente: {CORRIENTE[n['medio_codigo']]}",
        f"fecha: {n['fecha']}",
        f'titulo: "{esc(n["titulo"])}"',
        f'autor: "{esc(n["autor"])}"',
        f'url: "{n["url"]}"',
        "tipo: pendiente",
        "subtipo: pendiente",
        "palabras_clave: [inteligencia artificial]",
        "metodo_descubrimiento: scraping",
        f"fecha_captura: {HOY}",
        "---",
        f"# {n['titulo']}", "",
    ]
    if n["bajada"]:
        lineas += [n["bajada"], ""]
    if n["texto"]:
        lineas.append(n["texto"])
    lineas += ["", ""]
    return "\n".join(lineas)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for f in OUTPUT_DIR.glob("*.md"):
        f.unlink()
    grupos = defaultdict(list)
    for l in open(MAESTRO, encoding="utf-8"):
        n = json.loads(l)
        grupos[(n["medio_codigo"], n["anio"])].append(n)
    total = 0
    for (cod, anio), notas in sorted(grupos.items()):
        notas.sort(key=lambda x: x["id"])
        cab = [
            "---", f"medio: {cod}", f"medio_nombre: {notas[0]['medio'].replace(' ', '_')}", f"anio: {anio}",
            f"notas: {len(notas)}", f"generado: {HOY}", f"fuente: {FUENTE[cod]}", "---", "", "", "",
        ]
        contenido = "\n".join(cab) + "".join(bloque(n) for n in notas)
        (OUTPUT_DIR / f"{cod}_{anio}.md").write_text(contenido, encoding="utf-8")
        total += len(notas)
        print(f"{cod}_{anio}.md  {len(notas)} notas")
    print(f"Total: {total} notas en {len(grupos)} archivos")


if __name__ == "__main__":
    main()
