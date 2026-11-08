#!/usr/bin/env python3
"""ACV simplificada: substituir agora (A) x prolongar o uso (B), horizonte de 4 anos.

Executar a partir da raiz do repositório:
    python3 src/modelo.py                # usa dados/ e grava em resultados/
    python3 src/modelo.py --dados X --saida Y

Nenhum valor numérico do estudo está neste arquivo: tudo vem de dados/.
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potencia  # noqa: E402

HORIZONTE_MESES = 48
TROCA_B_MESES = 24
DOCUMENTAIS = ("dupla", "C_novo", "EP_novo", "FE_BR", "FEP_BR", "fv_kg", "L_novo")


# ---------------------------------------------------------------- entrada ----
def _num(linhas, s):
    v = linhas.get(s, {}).get("valor", "").strip()
    return float(v.replace(",", ".")) if v else None


def carregar_documentais(dir_dados):
    """Parâmetros de fonte documental/atribuída (não dependem das medições)."""
    dir_dados = Path(dir_dados)
    with open(dir_dados / "parametros.csv", encoding="utf-8") as f:
        linhas = {r["simbolo"]: r for r in csv.DictReader(f)}
    faltando = [s for s in DOCUMENTAIS if _num(linhas, s) is None]
    if faltando:
        sys.exit("Preencha em dados/parametros.csv (valor e fonte): " + ", ".join(faltando))
    p = {s: _num(linhas, s) for s in DOCUMENTAIS}
    p["dupla"] = int(p["dupla"])

    with open(dir_dados / "perfis.csv", encoding="utf-8") as f:
        perfil = next(r for r in csv.DictReader(f) if int(r["dupla"]) == p["dupla"])
    pesos = {"R1": float(perfil["w_ocioso"]), "R2": float(perfil["w_tipico"]),
             "R3": float(perfil["w_pesado"])}
    if abs(sum(pesos.values()) - 1) > 1e-9:
        sys.exit("Pesos do perfil não somam 1")
    p["h"] = float(perfil["h_ano"])
    p["perfil"] = perfil["perfil"]
    p["matriz_alt"] = perfil["matriz_comparacao"]
    p["pesos"] = pesos
    cod = perfil["codigo_matriz"]
    p["FE_alt"], p["FEP_alt"] = _num(linhas, f"FE_{cod}"), _num(linhas, f"FEP_{cod}")
    if p["FE_alt"] is None or p["FEP_alt"] is None:
        sys.exit(f"Preencha FE_{cod} e FEP_{cod} em dados/parametros.csv")
    return p, linhas


def carregar(dir_dados):
    dir_dados = Path(dir_dados)
    p, linhas = carregar_documentais(dir_dados)
    p["m_ant"] = _num(linhas, "m_ant")
    if p["m_ant"] is None:
        sys.exit("Preencha m_ant (massa do RV415 pesada na balança) em dados/parametros.csv")
    p["CFV_ant"] = p["fv_kg"] * p["m_ant"]

    alertas, regimes = [], {}
    for simb, prefixo in (("P_ant", "antigo"), ("P_novo", "novo")):
        valor = linhas[simb]["valor"].strip()
        if valor == "logs":
            pp, tdp = _num(linhas, f"P_plat_{prefixo}"), _num(linhas, f"TDP_{prefixo}")
            conv = (pp, tdp) if pp is not None and tdp is not None else None
            regimes[prefixo], al = potencia.potencia_regimes(dir_dados / "logs", prefixo, conv)
            if conv:
                al.append(f"{prefixo}: potência ESTIMADA = {pp} W + {tdp} W × utilização de CPU medida")
            alertas += al
            p[simb] = potencia.potencia_ponderada(regimes[prefixo], p["pesos"])
        else:  # caso previsto no roteiro: potência declarada pelo fabricante
            p[simb] = float(valor.replace(",", "."))
    p["regimes"] = regimes
    return p, alertas


# ----------------------------------------------------------------- modelo ----
def energia_anual_kwh(P_w, h):
    return P_w / 1000.0 * h  # W -> kW


def t_estrela(C_novo, P_ant, P_novo, h, FE):
    """Anos para a economia na fase de uso pagar o carbono incorporado do novo."""
    economia = energia_anual_kwh(P_ant - P_novo, h) * FE  # kg CO2-eq / ano
    return float("inf") if economia <= 0 else C_novo / economia


def series(p, FE, FEP, h=None, alocar=False):
    """Impactos acumulados mês a mês (0..48) nos dois cenários.

    alocar=False: carbono incorporado do novo entra inteiro na compra (leitura literal).
    alocar=True : entra só a fração da vida útil usada dentro do horizonte
                  (A usa 4 anos do novo, B usa 2), o que evita penalizar B por um
                  equipamento cuja vida continua após o ano 4.
    """
    h = p["h"] if h is None else h
    Ea, En = energia_anual_kwh(p["P_ant"], h), energia_anual_kwh(p["P_novo"], h)
    L = p["L_novo"]
    fA = min(HORIZONTE_MESES / 12 / L, 1) if alocar else 1.0
    fB = min((HORIZONTE_MESES - TROCA_B_MESES) / 12 / L, 1) if alocar else 1.0
    out = {"mes": [], "A_co2": [], "B_co2": [], "A_ep": [], "B_ep": [], "A_res": [], "B_res": []}
    for m in range(HORIZONTE_MESES + 1):
        t = m / 12
        tb_ant, tb_novo = min(t, 2.0), max(t - 2.0, 0.0)
        trocou = m >= TROCA_B_MESES
        out["mes"].append(m)
        # mudança do clima (kg CO2-eq)
        out["A_co2"].append(p["C_novo"] * fA + p["CFV_ant"] + En * t * FE)
        out["B_co2"].append(Ea * tb_ant * FE + En * tb_novo * FE
                            + (p["C_novo"] * fB + p["CFV_ant"] if trocou else 0.0))
        # energia primária (kWh)
        out["A_ep"].append(p["EP_novo"] * fA + En * t * FEP)
        out["B_ep"].append(Ea * tb_ant * FEP + En * tb_novo * FEP
                           + (p["EP_novo"] * fB if trocou else 0.0))
        # resíduo eletrônico gerado (kg): descarte do antigo
        out["A_res"].append(p["m_ant"])
        out["B_res"].append(p["m_ant"] if trocou else 0.0)
    return out


def cruzamentos(s, a="A_co2", b="B_co2"):
    """Meses em que o sinal de (A − B) muda."""
    sinal = [(x > y) - (x < y) for x, y in zip(s[a], s[b])]
    meses, ant = [], sinal[0]
    for i in range(1, len(sinal)):
        if sinal[i] != 0 and ant != 0 and sinal[i] != ant:
            meses.append(s["mes"][i])
        if sinal[i] == 0 and ant != 0:
            meses.append(s["mes"][i])
        if sinal[i] != 0:
            ant = sinal[i]
    return meses


def vencedor(s, a="A_co2", b="B_co2"):
    da, db = s[a][-1], s[b][-1]
    return "A (substituir)" if da < db else "B (prolongar)" if db < da else "empate"


# ---------------------------------------------------------- sensibilidade ----
def sensibilidade(p, n=11):
    linhas = []
    for i in range(n):  # fator de emissão: SIN -> matriz de comparação
        FE = p["FE_BR"] + (p["FE_alt"] - p["FE_BR"]) * i / (n - 1)
        FEP = p["FEP_BR"] + (p["FEP_alt"] - p["FEP_BR"]) * i / (n - 1)
        linhas.append(_linha(p, "FE", FE, FE, FEP, p["h"]))
    for i in range(n):  # horas: 0,5h -> 2h
        h = p["h"] * (0.5 + 1.5 * i / (n - 1))
        linhas.append(_linha(p, "h", h, p["FE_BR"], p["FEP_BR"], h))
    return linhas


def _linha(p, var, valor, FE, FEP, h):
    s_lit, s_aloc = series(p, FE, FEP, h, False), series(p, FE, FEP, h, True)
    t = t_estrela(p["C_novo"], p["P_ant"], p["P_novo"], h, FE)
    return {"variavel": var, "valor": round(valor, 6), "FE": round(FE, 6), "h": round(h, 1),
            "t_estrela_anos": round(t, 2) if t != float("inf") else "inf",
            "t_dentro_vida_util": t <= p["L_novo"],
            "A_co2_4a": round(s_aloc["A_co2"][-1], 2), "B_co2_4a": round(s_aloc["B_co2"][-1], 2),
            "vencedor_alocado": vencedor(s_aloc),
            "vencedor_literal": vencedor(s_lit)}


def deltaP_inversao(p, FE, h):
    """ΔP (W) a partir do qual t* = vida útil."""
    return p["C_novo"] / (h * FE * p["L_novo"]) * 1000.0  # kW -> W


def fe_inversao(p, h=None):
    """FE a partir do qual t* = vida útil (a conclusão se inverte)."""
    h = p["h"] if h is None else h
    dE = energia_anual_kwh(p["P_ant"] - p["P_novo"], h)
    return float("inf") if dE <= 0 else p["C_novo"] / (dE * p["L_novo"])


# ---------------------------------------------------------------- gráficos ----
COR_A, COR_B, TINTA, TINTA2, GRADE = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"


def _estilo(ax, titulo, ylabel):
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    ax.set_xlabel("tempo (anos)", color=TINTA2)
    ax.set_ylabel(ylabel, color=TINTA2)
    ax.grid(True, color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRADE)
    ax.tick_params(colors=TINTA2)
    ax.set_xlim(0, 4)


def _curvas(ax, s, a, b, rotulo=True):
    t = [m / 12 for m in s["mes"]]
    ax.plot(t, s[a], color=COR_A, lw=2, label="A — substituir agora")
    ax.plot(t, s[b], color=COR_B, lw=2, label="B — prolongar o uso", drawstyle="default")
    for m in cruzamentos(s, a, b):
        y = s[a][m]
        ax.plot(m / 12, y, "o", ms=8, mfc="white", mec=TINTA, mew=1.5, zorder=5)
        if rotulo:
            ax.annotate(f"cruzamento\n{m/12:.2f} anos", (m / 12, y), xytext=(8, -28),
                        textcoords="offset points", fontsize=8, color=TINTA2)


def graficos(p, saida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lit = series(p, p["FE_BR"], p["FEP_BR"], alocar=False)
    alo = series(p, p["FE_BR"], p["FEP_BR"], alocar=True)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    _curvas(axs[0], lit, "A_co2", "B_co2")
    _estilo(axs[0], "Carbono incorporado integral na compra", "kg CO2-eq acumulado")
    _curvas(axs[1], alo, "A_co2", "B_co2")
    _estilo(axs[1], f"Carbono alocado pela vida útil ({p['L_novo']:g} anos)", "")
    axs[0].legend(frameon=False, loc="center right", fontsize=9)
    fig.suptitle(f"Mudança do clima — matriz SIN (FE = {p['FE_BR']} kg CO2-eq/kWh), "
                 f"{p['h']:g} h/ano", x=0.01, ha="left", fontsize=12, color=TINTA)
    fig.tight_layout()
    fig.savefig(saida / "impacto_acumulado.png", dpi=150)
    plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (a, b, tit, un) in zip(axs, (("A_co2", "B_co2", "Mudança do clima", "kg CO2-eq"),
                                         ("A_ep", "B_ep", "Energia primária", "kWh"),
                                         ("A_res", "B_res", "Resíduo eletrônico", "kg"))):
        _curvas(ax, alo, a, b, rotulo=False)
        _estilo(ax, tit, un + " acumulado")
    axs[0].legend(frameon=False, loc="center right", fontsize=9)
    fig.suptitle("Três categorias de impacto (carbono e energia incorporados alocados pela vida útil)",
                 x=0.01, ha="left", fontsize=12, color=TINTA)
    fig.tight_layout()
    fig.savefig(saida / "categorias.png", dpi=150)
    plt.close(fig)

    sens = sensibilidade(p, n=41)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, var, xl in ((axs[0], "FE", "fator de emissão (kg CO2-eq/kWh)"),
                        (axs[1], "h", "horas de uso por ano")):
        pts = [(r["valor"], r["t_estrela_anos"]) for r in sens if r["variavel"] == var
               and r["t_estrela_anos"] != "inf"]
        ax.plot([x for x, _ in pts], [y for _, y in pts], color=COR_A, lw=2, label="t*")
        ax.axhline(p["L_novo"], color=TINTA2, lw=1, ls="--")
        ax.annotate(f"vida útil = {p['L_novo']:g} anos", (pts[0][0], p["L_novo"]),
                    xytext=(0, 4), textcoords="offset points", fontsize=8, color=TINTA2)
        ax.set_yscale("log")
        _estilo(ax, f"t* em função de {var}", "t* (anos, escala log)")
        ax.set_xlim(min(x for x, _ in pts), max(x for x, _ in pts))
        ax.set_xlabel(xl, color=TINTA2)
    fig.tight_layout()
    fig.savefig(saida / "sensibilidade.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------- main ----
def main():
    raiz = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default=raiz / "dados", type=Path)
    ap.add_argument("--saida", default=raiz / "resultados", type=Path)
    ap.add_argument("--horas", type=float, help="sobrescreve h (teste da defesa)")
    ap.add_argument("--limiar", action="store_true",
                    help="só dados documentais: diferença de potência que faria a troca compensar")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)

    if a.limiar:
        p, _ = carregar_documentais(a.dados)
        if a.horas:
            p["h"] = a.horas
        print(f"Dupla {p['dupla']} — {p['perfil']}: {p['h']:g} h/ano; C_novo = {p['C_novo']:g} kg; "
              f"vida útil = {p['L_novo']:g} anos")
        print("ΔP mínimo (P_ant − P_novo) para t* ≤ vida útil:")
        linhas = []
        for nome, FE in (("SIN", p["FE_BR"]), (p["matriz_alt"], p["FE_alt"])):
            for fh in (0.5, 1.0, 2.0):
                h = p["h"] * fh
                dp = deltaP_inversao(p, FE, h)
                print(f"  {nome:8s} FE={FE:<7g} h={h:<6g} -> ΔP ≥ {dp:7.1f} W")
                linhas.append({"matriz": nome, "FE": FE, "h": h, "deltaP_min_W": round(dp, 2)})
        _csv(a.saida / "limiar_deltaP.csv", linhas)
        return

    p, alertas = carregar(a.dados)
    if a.horas:
        p["h"] = a.horas
    for al in alertas:
        print("ALERTA:", al)

    print(f"Dupla {p['dupla']} — {p['perfil']}: {p['h']:g} h/ano, pesos {p['pesos']}")
    for eq, reg in p["regimes"].items():
        for r, v in reg.items():
            print(f"  {eq:6s} {r}: média {v['media']:.2f} W (min {v['min']:.2f}, "
                  f"max {v['max']:.2f}, dp {v['desvio']:.2f}, n={v['n']})")
    print(f"P_ant = {p['P_ant']:.2f} W | P_novo = {p['P_novo']:.2f} W")

    # conferência de ordem de grandeza, com valores arredondados
    dP = p["P_ant"] - p["P_novo"]
    print("\nOrdem de grandeza (conta de cabeça):")
    print(f"  ΔP ≈ {dP:.0f} W = {dP/1000:.3f} kW; × {p['h']:.0f} h = {dP/1000*p['h']:.0f} kWh/ano")
    print(f"  × FE_BR {p['FE_BR']} = {dP/1000*p['h']*p['FE_BR']:.1f} kg CO2-eq/ano economizados")
    print(f"  C_novo {p['C_novo']:.0f} kg ÷ isso ≈ {t_estrela(p['C_novo'], p['P_ant'], p['P_novo'], p['h'], p['FE_BR']):.0f} anos")

    resumo = []
    for nome, FE, FEP in (("SIN", p["FE_BR"], p["FEP_BR"]), (p["matriz_alt"], p["FE_alt"], p["FEP_alt"])):
        t = t_estrela(p["C_novo"], p["P_ant"], p["P_novo"], p["h"], FE)
        lit, alo = series(p, FE, FEP, alocar=False), series(p, FE, FEP, alocar=True)
        dentro = "DENTRO" if t <= p["L_novo"] else "FORA"
        print(f"\n[{nome}] FE = {FE} kg CO2-eq/kWh")
        print(f"  t* = {t:.2f} anos -> {dentro} da vida útil ({p['L_novo']:g} anos)")
        print(f"  4 anos, alocado : A = {alo['A_co2'][-1]:.1f}  B = {alo['B_co2'][-1]:.1f} kg CO2-eq"
              f"  -> melhor: {vencedor(alo)}")
        print(f"  4 anos, literal : A = {lit['A_co2'][-1]:.1f}  B = {lit['B_co2'][-1]:.1f} kg CO2-eq"
              f"  -> melhor: {vencedor(lit)}; cruzamentos (meses): {cruzamentos(lit)}")
        print(f"  energia primária 4 anos (alocado): A = {alo['A_ep'][-1]:.0f}  B = {alo['B_ep'][-1]:.0f} kWh")
        print(f"  resíduo eletrônico: {p['m_ant']} kg nos dois cenários (A no ano 0, B no ano 2)")
        resumo.append({"matriz": nome, "FE": FE, "t_estrela_anos": round(t, 3),
                       "dentro_vida_util": t <= p["L_novo"],
                       "A_co2_4a_alocado": round(alo["A_co2"][-1], 2),
                       "B_co2_4a_alocado": round(alo["B_co2"][-1], 2),
                       "A_co2_4a_literal": round(lit["A_co2"][-1], 2),
                       "B_co2_4a_literal": round(lit["B_co2"][-1], 2),
                       "A_ep_4a_alocado": round(alo["A_ep"][-1], 1),
                       "B_ep_4a_alocado": round(alo["B_ep"][-1], 1)})

    fe_inv = fe_inversao(p)
    print(f"\nInversão: a troca passa a compensar se FE > {fe_inv:.3f} kg CO2-eq/kWh "
          f"(com {p['h']:g} h/ano) ou se h > "
          f"{p['h'] * fe_inversao(p) / p['FE_BR']:.0f} h/ano (com FE do SIN).")
    if p["h"] * fe_inversao(p) / p["FE_BR"] > 8760:
        print("  -> horas acima de 8760 h/ano são fisicamente impossíveis: no Brasil a conclusão não se inverte.")

    sens = sensibilidade(p)
    _csv(a.saida / "sensibilidade.csv", sens)
    _csv(a.saida / "resumo.csv", resumo)
    _csv(a.saida / "serie_mensal_SIN.csv", _linhas_series(series(p, p["FE_BR"], p["FEP_BR"], alocar=True)))
    graficos(p, a.saida)
    print(f"\nResultados gravados em {a.saida}")


def _linhas_series(s):
    return [dict(zip(s, v)) for v in zip(*s.values())]


def _csv(caminho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)


if __name__ == "__main__":
    main()
