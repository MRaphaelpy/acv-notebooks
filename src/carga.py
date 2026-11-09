#!/usr/bin/env python3
"""Carga pesada para o regime R3: SHA-256 em todos os núcleos por 600 s.

Reimplementação conforme a descrição do roteiro (seção 4), feita porque o arquivo
do professor não estava disponível. Se o professor fornecer o carga.py oficial,
use o dele: é o que garante comparabilidade entre as duplas.

Uso:
    python3 src/carga.py                 # 600 s, todos os núcleos
    python3 src/carga.py --duracao 600 --log dados/logs/carga_antigo_R3.log
"""
import argparse
import datetime as dt
import hashlib
import multiprocessing as mp
import os
import socket
import time


def trabalhador(fim, contador):
    bloco = os.urandom(1024 * 1024)  # 1 MiB
    h = hashlib.sha256()
    n = 0
    while time.time() < fim:
        h.update(bloco)
        bloco = h.digest() * 32768  # realimenta para não otimizar
        n += 1
    with contador.get_lock():
        contador.value += n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracao", type=int, default=600)
    ap.add_argument("--log", default=os.path.join(os.path.dirname(__file__), "..", "dados", "logs", "carga.log"))
    a = ap.parse_args()

    nucleos = os.cpu_count() or 1
    inicio = dt.datetime.now()
    fim = time.time() + a.duracao
    print(f"[{inicio:%Y-%m-%d %H:%M:%S}] carga.py: {nucleos} núcleos, {a.duracao} s, máquina {socket.gethostname()}")

    contador = mp.Value("q", 0)
    procs = [mp.Process(target=trabalhador, args=(fim, contador)) for _ in range(nucleos)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    termino = dt.datetime.now()
    dur = (termino - inicio).total_seconds()
    linha = (f"maquina={socket.gethostname()};nucleos={nucleos};inicio={inicio.isoformat(timespec='seconds')};"
             f"fim={termino.isoformat(timespec='seconds')};duracao_s={dur:.1f};"
             f"MiB_hasheados={contador.value};MiB_por_s={contador.value / dur:.1f}")
    print(f"[{termino:%Y-%m-%d %H:%M:%S}] fim. {linha}")
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    with open(a.log, "a") as f:
        f.write(linha + "\n")


if __name__ == "__main__":
    main()
