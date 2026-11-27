"""
Autochequeo para codificadores.
Uso: python validar_lote.py <lote.json> <salida.json> [--reparar]
Verifica formato, códigos válidos y que cada cita sea literal. Con --reparar reemplaza las citas casi
exactas por el tramo literal de la nota. Imprime los problemas que quedan por corregir.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utilidades_codificacion import validar_nota  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    ruta_salida = Path(sys.argv[2])
    reparar = "--reparar" in sys.argv
    try:
        salida = json.load(open(ruta_salida, encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: la salida no es JSON válido: {e}")
        sys.exit(1)
    fuentes = {n["alias"]: f'{n["titulo"]} {n["bajada"]} {n["texto"]}' for n in lote["notas"]}
    por_alias = {n.get("alias"): n for n in salida.get("notas", [])}
    problemas_total = 0
    for alias in fuentes:
        if alias not in por_alias:
            print(f"{alias}: FALTA la nota en la salida")
            problemas_total += 1
    corregidas = []
    for n in salida.get("notas", []):
        if n.get("alias") not in fuentes:
            print(f"{n.get('alias')}: alias que no está en el lote")
            problemas_total += 1
            continue
        n2, probs = validar_nota(n, fuentes[n["alias"]])
        for p in probs:
            print(f"{n['alias']}: {p}")
        problemas_total += len(probs)
        corregidas.append(n2 if reparar else n)
    if reparar:
        salida["notas"] = corregidas
        for n in salida["notas"]:
            for c in n.get("codigos", []):
                c.pop("cita_estado", None)
            for e in n.get("emergentes", []) or []:
                e.pop("cita_estado", None)
        ruta_salida.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Notas en lote: {len(fuentes)} | notas en salida: {len(salida.get('notas', []))} | problemas: {problemas_total}")
    sys.exit(0 if problemas_total == 0 else 2)


if __name__ == "__main__":
    main()
