#!/usr/bin/env python3
"""Gera um gráfico de destaque e um slide-resumo a partir de resultados/.

    python3 src/modelo.py && python3 src/slide.py

Lê resultados/resumo.csv e resultados/serie_mensal_SIN.csv (gerados pelo modelo);
nenhum resultado numérico é digitado aqui.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados"
COR_A, COR_B = "#2a78d6", "#eb6834"
TINTA, TINTA2, TINTA3, GRADE, FUNDO = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"


def br(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ler_csv(nome):
    with open(RES / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def eixos_limpos(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRADE)
    ax.tick_params(colors=TINTA2, labelsize=10)
    ax.grid(True, axis="y", color=GRADE, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_facecolor(FUNDO)


def grafico(ax, s, p):
    t = [int(m) / 12 for m in s["mes"]]
    A = [float(v) for v in s["A_co2"]]
    B = [float(v) for v in s["B_co2"]]
    ax.fill_between(t, B, A, color=COR_B, alpha=0.08, lw=0)
    ax.plot(t, A, color=COR_A, lw=2.5)
    ax.plot(t, B, color=COR_B, lw=2.5)
    ax.plot([4], [A[-1]], "o", ms=9, color=COR_A, mec=FUNDO, mew=2, zorder=5)
    ax.plot([4], [B[-1]], "o", ms=9, color=COR_B, mec=FUNDO, mew=2, zorder=5)
    ax.annotate(f"A — substituir agora\n{br(A[-1])} kg", (4, A[-1]), xytext=(10, 0),
                textcoords="offset points", va="center", fontsize=11, color=TINTA, fontweight="bold")
    ax.annotate(f"B — prolongar o uso\n{br(B[-1])} kg", (4, B[-1]), xytext=(10, 0),
                textcoords="offset points", va="center", fontsize=11, color=TINTA, fontweight="bold")
    i0 = 24
    ax.annotate(f"fabricação do novo\nlogo na compra ({br(p['C_novo'], 0)} kg)", (0, A[0]), xytext=(0.15, A[0] - 0.25 * max(A)),
                fontsize=9, color=TINTA2, arrowprops=dict(arrowstyle="-", color=TINTA3, lw=0.8))
    ax.annotate("B compra o novo no ano 2\n(metade da vida útil cai no horizonte)", (2, B[i0]),
                xytext=(2.25, B[i0] - 0.33 * max(A)), fontsize=9, color=TINTA2,
                arrowprops=dict(arrowstyle="-", color=TINTA3, lw=0.8))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, max(A) * 1.15)
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticklabels(["ano 0", "1", "2", "3", "4"])
    ax.set_ylabel("kg CO2-eq acumulado", color=TINTA2, fontsize=10)
    eixos_limpos(ax)


def grafico_relatorios(p):
    """Barras A × B em 4 anos para cada relatório de carbono incorporado (sensibilidade)."""
    casos = [("principal", p["C_novo"])] + list(p.get("C_novo_alts", {}).items())
    linhas = []
    for nome, c in casos:
        q = dict(p, C_novo=c)
        ss = modelo.series(q, p["FE_BR"], p["FEP_BR"], alocar=True)
        linhas.append({"relatorio": nome, "C_novo": c, "A_co2_4a": ss["A_co2"][-1], "B_co2_4a": ss["B_co2"][-1],
                       "t_estrela_SIN_anos": modelo.t_estrela(c, p["P_ant"], p["P_novo"], p["h"], p["FE_BR"])})
    nomes = {"principal": "Dell Inspiron 15 3535\n(caso principal)", "5440": "Dell Inspiron 14 5440",
             "N1110": "Positivo Master N1110\n(mesmo fabricante)"}
    fig, ax = plt.subplots(figsize=(11, 5.4), facecolor=FUNDO)
    y = [i * 1.55 for i in range(len(linhas))][::-1]
    alt = 0.36
    for yi, r in zip(y, linhas):
        A, B, t = float(r["A_co2_4a"]), float(r["B_co2_4a"]), float(r["t_estrela_SIN_anos"])
        ax.barh(yi + alt / 2 + 0.02, A, height=alt, color=COR_A)
        ax.barh(yi - alt / 2 - 0.02, B, height=alt, color=COR_B)
        ax.text(A + 4, yi + alt / 2 + 0.02, f"substituir {br(A)} kg", va="center", fontsize=10, color=TINTA)
        ax.text(B + 4, yi - alt / 2 - 0.02, f"prolongar {br(B)} kg", va="center", fontsize=10, color=TINTA,
                fontweight="bold")
        ax.text(0, yi - 0.66, f"fabricação do novo: {br(float(r['C_novo']), 0)} kg · t* = {br(t, 0)} anos",
                fontsize=9, color=TINTA2)
    ax.set_yticks(y)
    ax.set_yticklabels([nomes.get(r["relatorio"], r["relatorio"]) for r in linhas], fontsize=10.5, color=TINTA)
    ax.set_xlabel("kg CO2-eq em 4 anos (SIN, carbono alocado pela vida útil)", color=TINTA2, fontsize=10)
    ax.set_xlim(0, max(float(r["A_co2_4a"]) for r in linhas) * 1.28)
    ax.set_ylim(-0.95, max(y) + 0.55)
    eixos_limpos(ax)
    ax.grid(True, axis="x", color=GRADE, lw=0.8)
    ax.grid(False, axis="y")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    fig.text(0.02, 0.94, "A decisão não depende de qual relatório de fabricação usamos",
             fontsize=15, fontweight="bold", color=TINTA)
    fig.text(0.02, 0.885, f"Em todos os casos, prolongar o uso do RV415 emite menos · {br(p['h'], 0)} h/ano, "
             f"FE {br(p['FE_BR'], 4)} kg CO2-eq/kWh", fontsize=10, color=TINTA2)
    fig.subplots_adjust(left=0.20, right=0.97, top=0.80, bottom=0.14)
    fig.savefig(RES / "grafico_relatorios.png", dpi=180, facecolor=FUNDO)
    plt.close(fig)


def main():
    p, _ = modelo.carregar(RAIZ / "dados")
    s = {k: [r[k] for r in ler_csv("serie_mensal_SIN.csv")] for k in ler_csv("serie_mensal_SIN.csv")[0]}
    resumo = {r["matriz"]: r for r in ler_csv("resumo.csv")}
    sin = resumo["SIN"]
    alt = resumo[p["matriz_alt"]]
    A4, B4 = float(s["A_co2"][-1]), float(s["B_co2"][-1])
    reducao = (A4 - B4) / A4 * 100
    dP = p["P_ant"] - p["P_novo"]
    t_sin, t_alt = float(sin["t_estrela_anos"]), float(alt["t_estrela_anos"])

    # ---------- gráfico de destaque ----------
    fig, ax = plt.subplots(figsize=(11, 5.6), facecolor=FUNDO)
    grafico(ax, s, p)
    fig.text(0.06, 0.95, "Prolongar o uso do RV415 emite menos carbono em 4 anos",
             fontsize=16, fontweight="bold", color=TINTA)
    fig.text(0.06, 0.905, f"Mudança do clima acumulada — matriz SIN ({br(p['FE_BR'], 4)} kg CO2-eq/kWh), "
             f"{br(p['h'], 0)} h/ano, carbono incorporado alocado pela vida útil ({p['L_novo']:g} anos)",
             fontsize=10, color=TINTA2)
    fig.subplots_adjust(left=0.07, right=0.80, top=0.85, bottom=0.10)
    fig.savefig(RES / "grafico_decisao.png", dpi=180, facecolor=FUNDO)
    plt.close(fig)

    # ---------- slide 16:9 ----------
    fig = plt.figure(figsize=(13.33, 7.5), facecolor=FUNDO)
    fig.text(0.05, 0.92, "Trocar o notebook agora compensa?", fontsize=26, fontweight="bold", color=TINTA)
    fig.text(0.05, 0.875, f"ACV comparativa · Samsung RV415 (2011) × VAIO FE15 (Ryzen 7 5700U) · "
             f"Dupla {p['dupla']}, {br(p['h'], 0)} h/ano por 4 anos", fontsize=12, color=TINTA2)

    ax = fig.add_axes([0.06, 0.17, 0.42, 0.62])
    grafico(ax, s, p)

    def cartao(x, y, w, h, titulo, valor, sub, cor):
        fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                          transform=fig.transFigure, fc="white", ec=GRADE, lw=1))
        fig.patches.append(FancyBboxPatch((x, y), 0.006, h, boxstyle="square,pad=0",
                                          transform=fig.transFigure, fc=cor, ec="none"))
        fig.text(x + 0.02, y + h - 0.04, titulo, fontsize=10.5, color=TINTA2)
        fig.text(x + 0.02, y + 0.055, valor, fontsize=19, fontweight="bold", color=TINTA)
        fig.text(x + 0.02, y + 0.018, sub, fontsize=9, color=TINTA2)

    x0, w = 0.64, 0.32
    cartao(x0, 0.64, w, 0.14, "Consumo médio ponderado", f"{br(p['P_ant'], 1)} W × {br(p['P_novo'], 1)} W",
           f"RV415 (estimado) × VAIO (medido): só {br(dP, 1)} W de diferença", TINTA3)
    cartao(x0, 0.47, w, 0.14, "Ponto de equilíbrio t*", f"{br(t_sin, 0)} anos",
           f"Brasil · {br(t_alt, 0)} anos na {p['matriz_alt']} · vida útil: {p['L_novo']:g} anos", COR_A)
    cartao(x0, 0.30, w, 0.14, "Emissões em 4 anos (SIN)", f"−{br(reducao, 0)}% com B",
           f"A = {br(A4)} kg   ·   B = {br(B4)} kg CO2-eq", COR_B)

    fig.patches.append(FancyBboxPatch((x0, 0.12), w, 0.14, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, fc=COR_B, ec="none"))
    fig.text(x0 + 0.02, 0.215, "DECISÃO", fontsize=10.5, color="white", fontweight="bold")
    fig.text(x0 + 0.02, 0.165, "Prolongar o uso do RV415", fontsize=17, color="white", fontweight="bold")
    fig.text(x0 + 0.02, 0.135, "a conclusão não se inverte na sensibilidade", fontsize=9.5, color="white")

    fig.text(0.06, 0.065, "Por quê", fontsize=11, fontweight="bold", color=TINTA)
    fig.text(0.13, 0.065,
             f"Fabricar o novo emite {br(p['C_novo'], 0)} kg CO2-eq. A economia de {br(dP, 1)} W × {br(p['h'], 0)} h × "
             f"{br(p['FE_BR'], 4)} kg/kWh ≈ {br(dP / 1000 * p['h'] * p['FE_BR'], 2)} kg CO2-eq/ano nunca paga essa dívida",
             fontsize=10.5, color=TINTA)
    fig.text(0.13, 0.035,
             f"com eletricidade limpa. Só se inverteria com FE > {br(modelo.fe_inversao(p), 2)} kg/kWh "
             f"(a {p['matriz_alt']} tem {br(p['FE_alt'], 4)}; o Brasil, {br(p['FE_BR'], 4)}).",
             fontsize=10.5, color=TINTA)
    fig.savefig(RES / "slide_decisao.png", dpi=150, facecolor=FUNDO)
    plt.close(fig)

    if p.get("C_novo_alts"):
        grafico_relatorios(p)
    print("Gerados: resultados/grafico_decisao.png, slide_decisao.png e grafico_relatorios.png")


if __name__ == "__main__":
    main()
