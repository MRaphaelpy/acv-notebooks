#!/usr/bin/env python3
"""Roda as 3 medições (R1, R2, R3) de um notebook em sequência, ~32 min no total.

    python3 src/medir_tudo.py antigo --palavra PALAVRA_DA_AULA     # no RV415
    python3 src/medir_tudo.py novo   --palavra PALAVRA_DA_AULA     # no outro notebook

O que ele faz sozinho:
  * R1: espera 10 min medindo, com a área de trabalho parada;
  * R2: abre 8 abas no navegador e um editor; você digita de vez em quando;
  * R3: dispara src/carga.py nos 10 min;
  * tira uma captura de tela no meio de cada regime (dados/evidencias/);
  * grava os logs brutos em dados/logs/<equip>_R1.csv ... _R3.csv.
Linux usa src/medir.py; Windows usa src/medir_windows.ps1.
Antes de começar: na bateria, brilho 50%, sem USB/fones, modo equilibrado.
"""
import argparse
import datetime as dt
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

SRC = Path(__file__).resolve().parent
RAIZ = SRC.parent
LOGS, EVID = RAIZ / "dados" / "logs", RAIZ / "dados" / "evidencias"
WIN = platform.system() == "Windows"
MODO_CPU = False  # --cpu: mede utilização de CPU (sem sensor de potência)
ABAS = ["https://www.gov.br/mcti", "https://ember-energy.org", "https://www.wikipedia.org",
        "https://docs.python.org/3/", "https://github.com", "https://www.univasf.edu.br",
        "https://www.ibge.gov.br", "https://www.youtube.com"]


def iniciar_medidor(nome, palavra, duracao):
    if WIN:
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(SRC / "medir_windows.ps1"),
               "-Nome", nome, "-Palavra", palavra, "-Duracao", str(duracao)]
    else:
        script = "medir_uso.py" if MODO_CPU else "medir.py"
        cmd = [sys.executable, str(SRC / script), nome, "--palavra", palavra,
               "--duracao", str(duracao)]
    return subprocess.Popen(cmd)


def captura(nome):
    EVID.mkdir(parents=True, exist_ok=True)
    arq = EVID / f"{nome}_{dt.datetime.now():%Y%m%d_%H%M%S}.png"
    if WIN:
        ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
              "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
              "$i=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
              "$g=[System.Drawing.Graphics]::FromImage($i);$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);"
              f"$i.Save('{arq}')")
        cmds = [["powershell", "-Command", ps]]
    else:
        cmds = [["gnome-screenshot", "-f", str(arq)], ["spectacle", "-b", "-n", "-o", str(arq)],
                ["grim", str(arq)], ["scrot", str(arq)], ["import", "-window", "root", str(arq)],
                ["xfce4-screenshooter", "-f", "-s", str(arq)]]
    for c in cmds:
        if shutil.which(c[0]) and subprocess.run(c, capture_output=True).returncode == 0 and arq.exists():
            print(f"   captura salva: {arq.relative_to(RAIZ)}")
            return
    print("   !! não consegui capturar a tela sozinho: tire a captura AGORA (PrintScreen) "
          f"e salve em dados/evidencias/{nome}.png")


def abrir_editor():
    for ed in (["code"], ["gedit"], ["kate"], ["mousepad"], ["notepad"]):
        if shutil.which(ed[0]):
            subprocess.Popen(ed + [str(SRC / "modelo.py")])
            return
    print("   abra um editor de código manualmente")


def regime(nome, palavra, duracao, carga=False):
    proc = iniciar_medidor(nome, palavra, duracao)
    time.sleep(3)
    cproc = None
    if carga:
        cmd = [sys.executable, str(SRC / "carga.py"), "--duracao", str(duracao - 3),
               "--log", str(LOGS / f"carga_{nome}.log")]
        cproc = subprocess.Popen(cmd)
    time.sleep(duracao / 2)
    print(f"\n   palavra-chave: {palavra} | {socket.gethostname()} | {dt.datetime.now():%Y-%m-%d %H:%M:%S}")
    captura(nome)
    proc.wait()
    if cproc:
        cproc.wait()
    arq = LOGS / f"{nome}.csv"
    n = sum(1 for l in arq.open(encoding="utf-8-sig") if l[:1].isdigit()) if arq.exists() else 0
    print(f"   {nome}: {n} amostras em {arq.relative_to(RAIZ)}" if n else f"   !! {nome}: log vazio")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("equip", choices=["antigo", "novo"])
    ap.add_argument("--palavra", required=True)
    ap.add_argument("--duracao", type=int, default=600)
    ap.add_argument("--pausa", type=int, default=60, help="s de descanso entre regimes")
    ap.add_argument("--cpu", action="store_true",
                    help="sem sensor de potência: mede utilização de CPU (potência estimada depois)")
    a = ap.parse_args()
    global MODO_CPU
    MODO_CPU = a.cpu
    LOGS.mkdir(parents=True, exist_ok=True)
    if not WIN and not MODO_CPU and not list(Path("/sys/class/power_supply").glob("BAT*")):
        sys.exit("Nenhuma bateria encontrada: rode no notebook, ou use --cpu se ele não expõe potência.")

    print(f"Máquina {socket.gethostname()} | equipamento: {a.equip} | palavra: {a.palavra}")
    print("Confira: NA BATERIA, brilho 50%, sem USB/fones, modo de energia equilibrado.")
    input("Enter para começar o R1 (ocioso)... ")

    print("\n== R1 ocioso: não mexa no notebook por 10 min ==")
    regime(f"{a.equip}_R1", a.palavra, a.duracao)

    print(f"\nPausa de {a.pausa} s. Vou abrir 8 abas e um editor para o R2.")
    time.sleep(a.pausa)
    for u in ABAS:
        webbrowser.open_new_tab(u)
        time.sleep(1)
    abrir_editor()
    input("Abas e editor abertos? Volte para ESTE terminal e dê Enter para começar o R2... ")
    print("\n== R2 típico: digite no editor de vez em quando, troque de aba às vezes ==")
    regime(f"{a.equip}_R2", a.palavra, a.duracao)

    input("\nFeche o navegador e o editor e dê Enter para o R3 (carga pesada)... ")
    print(f"Pausa de {a.pausa} s.")
    time.sleep(a.pausa)
    print("\n== R3 carga pesada: carga.py em todos os núcleos, não mexa ==")
    regime(f"{a.equip}_R3", a.palavra, a.duracao, carga=True)

    print("\nPronto. Logs em dados/logs/, capturas em dados/evidencias/.")
    print("Anote no caderno de bordo: data, % de bateria no início e no fim, e o que deu errado.")


if __name__ == "__main__":
    main()
