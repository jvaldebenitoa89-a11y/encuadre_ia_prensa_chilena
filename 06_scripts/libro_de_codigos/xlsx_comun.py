"""Estilos y utilidades comunes para los libros en Excel."""

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FUENTE = "Arial"
AZUL = "1F3864"
GRIS = "F2F2F2"
CELESTE = "DDEBF7"
LINEA = Side(style="thin", color="BFBFBF")
BORDE = Border(left=LINEA, right=LINEA, top=LINEA, bottom=LINEA)

F_TITULO = Font(name=FUENTE, size=16, bold=True, color=AZUL)
F_SUB = Font(name=FUENTE, size=10, italic=True, color="595959")
F_ENC = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
F_BASE = Font(name=FUENTE, size=10)
F_NEG = Font(name=FUENTE, size=10, bold=True)
F_SEC = Font(name=FUENTE, size=12, bold=True, color=AZUL)
F_LINK = Font(name=FUENTE, size=10, color="0563C1", underline="single")
REL_ENC = PatternFill("solid", fgColor=AZUL)
REL_ALT = PatternFill("solid", fgColor=GRIS)
REL_SEC = PatternFill("solid", fgColor=CELESTE)
AL_ENC = Alignment(horizontal="center", vertical="center", wrap_text=True)
AL_TXT = Alignment(vertical="top", wrap_text=True)
AL_NUM = Alignment(horizontal="right", vertical="top")
AL_CEN = Alignment(horizontal="center", vertical="top", wrap_text=True)


def titulo(ws, texto, subtitulo=None, fila=1):
    ws.cell(row=fila, column=1, value=texto).font = F_TITULO
    if subtitulo:
        ws.cell(row=fila + 1, column=1, value=subtitulo).font = F_SUB


def seccion(ws, fila, texto, ncols=1):
    c = ws.cell(row=fila, column=1, value=texto)
    c.font = F_SEC
    return fila + 1


def anchos(ws, lista):
    for i, w in enumerate(lista, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def encabezado(ws, fila, cabeceras, alto=32):
    for j, h in enumerate(cabeceras, 1):
        c = ws.cell(row=fila, column=j, value=h)
        c.font, c.fill, c.alignment, c.border = F_ENC, REL_ENC, AL_ENC, BORDE
    ws.row_dimensions[fila].height = alto


def filas_tabla(ws, fila0, filas, alineacion=None, formatos=None, cebra=True):
    """Escribe filas bajo un encabezado. alineacion: dict col(1-based)->Alignment; formatos: dict col->number_format."""
    alineacion = alineacion or {}
    formatos = formatos or {}
    for i, fila in enumerate(filas):
        r = fila0 + i
        for j, v in enumerate(fila, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = F_BASE
            c.alignment = alineacion.get(j, AL_TXT)
            c.border = BORDE
            if j in formatos:
                c.number_format = formatos[j]
            if cebra and i % 2 == 1:
                c.fill = REL_ALT
    return fila0 + len(filas)


def parrafo(ws, fila, texto, col_fin=2, alto=None, negrita=False):
    c = ws.cell(row=fila, column=1, value=texto)
    c.font = F_NEG if negrita else F_BASE
    c.alignment = AL_TXT
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=col_fin)
    if alto:
        ws.row_dimensions[fila].height = alto
    return fila + 1


def estimar_alto(texto, ancho_chars, minimo=15, linea=12.5):
    if texto is None:
        return minimo
    n = 0
    for tramo in str(texto).split("\n"):
        n += max(1, -(-len(tramo) // max(1, int(ancho_chars))))
    return max(minimo, n * linea + 3)


def mapa_ids():
    """ID de CNN Chile: id_scraper -> id_nuevo (fecha real de publicación), según el mapa del 2026-10-08."""
    import csv
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "06 logs" / "cnn_fechas_e_ids_corregidos_2026-10-08.csv"
    out = {}
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        if str(r["en_rango"]).lower() in ("true", "1"):
            out[r["id_scraper"]] = r["id_nuevo"]
    return out
