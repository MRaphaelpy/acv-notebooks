#!/usr/bin/env python3
"""Consulta a API aberta do Boavizta para o carbono e a energia primária incorporados.

Uso:
    python3 src/boavizta.py                       # lista arquétipos de laptop
    python3 src/boavizta.py <arquetipo>           # impactos de fabricação (embedded)

Copie o resultado para dados/parametros.csv citando a URL impressa e a data de hoje.
Energia primária vem em MJ; divida por 3,6 para kWh (o script já mostra os dois).
"""
import datetime as dt
import json
import sys
import urllib.request

BASE = "https://api.boavizta.org/v1/terminal"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "acv-pratica4"}), timeout=30) as r:
        return json.load(r)


def main():
    if len(sys.argv) < 2:
        url = f"{BASE}/laptop/archetypes"
        print(url)
        print(json.dumps(get(url), indent=1, ensure_ascii=False))
        return
    url = f"{BASE}/laptop?archetype={sys.argv[1]}&verbose=false&criteria=gwp&criteria=pe"
    d = get(url)
    print(f"Fonte: {url}\nConsulta: {dt.date.today().isoformat()}")
    imp = d.get("impacts", d)
    for crit in ("gwp", "pe"):
        emb = imp.get(crit, {}).get("embedded", {})
        un = imp.get(crit, {}).get("unit", "")
        if not isinstance(emb, dict):  # ex.: "not implemented" para pe de terminais
            print(f"{crit}: embedded = {emb!r} -> buscar em PER do fabricante e registrar como limitação")
            continue
        print(f"{crit}: embedded = {emb.get('value')} {un} (min {emb.get('min')}, max {emb.get('max')})")
        if crit == "pe" and isinstance(emb.get("value"), (int, float)):
            print(f"     = {emb['value'] / 3.6:.1f} kWh")
    print(json.dumps(d, indent=1, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
