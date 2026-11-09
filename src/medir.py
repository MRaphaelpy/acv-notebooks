#!/usr/bin/env python3
"""Amostra a potência da bateria a 1 Hz no Linux e grava um log CSV carimbado.

Uso (rodar NA BATERIA, brilho 50%, sem USB, modo equilibrado):
    python3 src/medir.py antigo_R1 --palavra PALAVRA_DA_SEMANA
    python3 src/medir.py antigo_R3 --palavra PALAVRA --duracao 600   # junto com carga.py

Lê power_now (µW); se não existir, usa current_now (µA) × voltage_now (µV).
Também registra energy_now/charge_now e o percentual da bateria, para permitir
o método alternativo (energia inicial − final ÷ duração).
"""
import argparse
import datetime as dt
import glob
import os
import socket
import sys
import time


def ler(caminho):
    try:
        with open(caminho) as f:
            return f.read().strip()
    except OSError:
        return None


def achar_bateria():
    bats = sorted(glob.glob("/sys/class/power_supply/BAT*"))
    if not bats:
        sys.exit("Nenhuma bateria em /sys/class/power_supply. Registre no caderno de bordo e "
                 "use o método alternativo (Wh início/fim) ou um wattímetro de tomada.")
    return bats[0]


def amostra(bat):
    p_uw = ler(f"{bat}/power_now")
    v_uv = ler(f"{bat}/voltage_now")
    if p_uw is not None:
        p = int(p_uw) / 1e6
    else:
        i_ua = ler(f"{bat}/current_now")
        p = (int(i_ua) * int(v_uv)) / 1e12 if i_ua and v_uv else float("nan")
    e = ler(f"{bat}/energy_now")
    if e is not None:
        e_wh = int(e) / 1e6
    else:
        c = ler(f"{bat}/charge_now")
        e_wh = int(c) * int(v_uv) / 1e12 if c and v_uv else float("nan")
    return p, e_wh, ler(f"{bat}/capacity"), ler(f"{bat}/status")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nome", help="ex.: antigo_R1, novo_R3")
    ap.add_argument("--palavra", required=True, help="palavra-chave da semana dada em aula")
    ap.add_argument("--duracao", type=int, default=600)
    ap.add_argument("--saida", default=os.path.join(os.path.dirname(__file__), "..", "dados", "logs"))
    a = ap.parse_args()

    bat = achar_bateria()
    os.makedirs(a.saida, exist_ok=True)
    arq = os.path.join(a.saida, f"{a.nome}.csv")
    host = socket.gethostname()
    modelo = ler("/sys/class/dmi/id/product_name") or "?"
    fabricante = ler("/sys/class/dmi/id/sys_vendor") or "?"
    print(f"Máquina: {host} | {fabricante} {modelo} | palavra-chave: {a.palavra}")
    print(f"Gravando {arq} por {a.duracao} s ...")

    with open(arq, "w") as f:
        f.write(f"# maquina={host};fabricante={fabricante};modelo={modelo};"
                f"palavra={a.palavra};bateria={bat};inicio={dt.datetime.now().isoformat()}\n")
        f.write("timestamp,epoch,potencia_w,energia_wh,bateria_pct,status\n")
        t0 = time.monotonic()
        for k in range(a.duracao):
            p, e, cap, st = amostra(bat)
            agora = dt.datetime.now()
            f.write(f"{agora.isoformat(timespec='seconds')},{agora.timestamp():.3f},"
                    f"{p:.3f},{e:.4f},{cap},{st}\n")
            f.flush()
            if k % 30 == 0:
                print(f"{agora:%H:%M:%S}  {p:6.2f} W  bateria {cap}%  [{a.palavra}]")
            time.sleep(max(0.0, t0 + k + 1 - time.monotonic()))
    print("Fim.", arq)


if __name__ == "__main__":
    main()
