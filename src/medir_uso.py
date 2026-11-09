#!/usr/bin/env python3
"""Mede, a 1 Hz, a utilização da CPU, a frequência e a temperatura (Linux).

Usado quando o notebook não expõe potência (ex.: RV415 sem bateria funcional).
O log registra apenas grandezas MEDIDAS. A conversão para watts é feita depois, em
src/potencia.py, com o modelo P = P_plataforma + TDP × utilização, cujos parâmetros
estão em dados/parametros.csv com origem "estimado".

    python3 src/medir_uso.py antigo_R1 --palavra PALAVRA
"""
import argparse
import datetime as dt
import glob
import os
import socket
import time


def ler(c):
    try:
        with open(c) as f:
            return f.read().strip()
    except OSError:
        return None


def cpu_tempos():
    with open("/proc/stat") as f:
        v = [int(x) for x in f.readline().split()[1:]]
    ocioso = v[3] + (v[4] if len(v) > 4 else 0)
    return sum(v), ocioso


def freq_mhz():
    fs = [ler(p) for p in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq")]
    fs = [int(f) for f in fs if f]
    return sum(fs) / len(fs) / 1000 if fs else float("nan")


def temp_c():
    for h in glob.glob("/sys/class/hwmon/hwmon*"):
        if ler(f"{h}/name") == "k10temp" and ler(f"{h}/temp1_input"):
            return int(ler(f"{h}/temp1_input")) / 1000
    return float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nome")
    ap.add_argument("--palavra", required=True)
    ap.add_argument("--duracao", type=int, default=600)
    ap.add_argument("--saida", default=os.path.join(os.path.dirname(__file__), "..", "dados", "logs"))
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    arq = os.path.join(a.saida, f"{a.nome}.csv")
    host = socket.gethostname()
    modelo = ler("/sys/class/dmi/id/product_name") or "?"
    fab = ler("/sys/class/dmi/id/sys_vendor") or "?"
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "?")
    print(f"Máquina: {host} | {fab} {modelo} | {cpu} | palavra-chave: {a.palavra}")
    print(f"Gravando {arq} por {a.duracao} s (utilização de CPU medida; potência será estimada)")

    with open(arq, "w") as f:
        f.write(f"# maquina={host};fabricante={fab};modelo={modelo};cpu={cpu};nucleos={os.cpu_count()};"
                f"palavra={a.palavra};grandeza=utilizacao_cpu_medida;inicio={dt.datetime.now().isoformat()}\n")
        f.write("timestamp,epoch,utilizacao,freq_mhz,temp_c,carga_1min\n")
        t0 = time.monotonic()
        tot0, oc0 = cpu_tempos()
        for k in range(a.duracao):
            time.sleep(max(0.0, t0 + k + 1 - time.monotonic()))
            tot1, oc1 = cpu_tempos()
            u = 1 - (oc1 - oc0) / (tot1 - tot0) if tot1 > tot0 else 0.0
            tot0, oc0 = tot1, oc1
            agora = dt.datetime.now()
            f.write(f"{agora.isoformat(timespec='seconds')},{agora.timestamp():.3f},{u:.4f},"
                    f"{freq_mhz():.0f},{temp_c():.1f},{os.getloadavg()[0]:.2f}\n")
            f.flush()
            if k % 30 == 0:
                print(f"{agora:%H:%M:%S}  CPU {u*100:5.1f}%  {freq_mhz():.0f} MHz  {temp_c():.1f} °C  [{a.palavra}]")
    print("Fim.", arq)


if __name__ == "__main__":
    main()
