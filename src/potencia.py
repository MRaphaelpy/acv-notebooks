"""Leitura e validação dos logs brutos de potência.

Formatos aceitos:
  * CSV de src/medir.py / src/medir_windows.ps1 (coluna potencia_w);
  * saída de `powerstat -d 0 1 600` (linhas HH:MM:SS ... com Watts na última coluna).
"""
import csv
import re
import statistics
from pathlib import Path

REGIMES = ("R1", "R2", "R3")
_HORA = re.compile(r"^\d{2}:\d{2}:\d{2}\s")


def ler_log(caminho, conv=None):
    """Retorna lista de (carimbo, potência_W).

    Logs de src/medir_uso.py trazem só a utilização de CPU medida; nesse caso a
    potência é ESTIMADA por P = P_plataforma + TDP × utilização, com conv = (P_plat, TDP).
    """
    caminho = Path(caminho)
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    pontos = []
    cab = next((l for l in linhas if l.startswith("timestamp,")), None)
    if cab is not None and "utilizacao" in cab:
        if conv is None:
            raise ValueError(f"{caminho}: log de utilização de CPU; preencha P_plat e TDP em parametros.csv")
        corpo = [l for l in linhas if l and not l.startswith("#")]
        for r in csv.DictReader(corpo):
            pontos.append((r["timestamp"], conv[0] + conv[1] * float(r["utilizacao"])))
    elif cab is not None:
        corpo = [l for l in linhas if l and not l.startswith("#")]
        for r in csv.DictReader(corpo):
            try:
                p = float(r["potencia_w"])
            except (ValueError, TypeError):
                continue
            if p == p:  # descarta NaN
                pontos.append((r["timestamp"], abs(p)))
    else:  # powerstat
        for l in linhas:
            if _HORA.match(l):
                campos = l.split()
                try:
                    pontos.append((campos[0], float(campos[-1])))
                except ValueError:
                    pass
    if not pontos:
        raise ValueError(f"{caminho}: nenhuma amostra de potência reconhecida")
    return pontos


def validar(pontos, nome, duracao_min=540):
    """Alertas de plausibilidade (os mesmos critérios do roteiro)."""
    alertas = []
    vals = [p for _, p in pontos]
    if len(vals) < duracao_min:
        alertas.append(f"{nome}: só {len(vals)} amostras (esperado ~600)")
    if len(set(vals)) <= 2 or statistics.pstdev(vals) == 0:
        alertas.append(f"{nome}: potência não varia ao longo do log")
    if len({t for t, _ in pontos}) < len(pontos) * 0.9:
        alertas.append(f"{nome}: carimbos de tempo repetidos")
    return alertas


def potencia_regimes(dir_logs, prefixo, conv=None):
    """Média de cada regime para um equipamento (prefixo 'antigo' ou 'novo')."""
    res, alertas = {}, []
    for r in REGIMES:
        arq = Path(dir_logs) / f"{prefixo}_{r}.csv"
        if not arq.exists():
            alt = Path(dir_logs) / f"{prefixo}_{r}.log"
            arq = alt if alt.exists() else arq
        if not arq.exists():
            raise FileNotFoundError(f"log ausente: {arq}")
        pts = ler_log(arq, conv)
        alertas += validar(pts, arq.name)
        vals = [p for _, p in pts]
        res[r] = {"media": statistics.fmean(vals), "min": min(vals),
                  "max": max(vals), "desvio": statistics.pstdev(vals), "n": len(vals)}
    return res, alertas


def potencia_ponderada(regimes, pesos):
    """P_média = w1·P(R1) + w2·P(R2) + w3·P(R3)."""
    return sum(pesos[r] * regimes[r]["media"] for r in REGIMES)
