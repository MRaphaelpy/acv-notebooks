# Roteiro da defesa — Dupla 2

Dez minutos, sem slides. Abrir só o repositório e o gráfico `resultados/grafico_decisao.png`.
Cada integrante sorteia 2 perguntas e responde sozinho, então **os dois precisam saber tudo abaixo**.

## Antes de entrar (2 min)
- Abrir o repositório no GitHub ou no VS Code, já na pasta `acv-notebooks`.
- Rodar uma vez: `python3 src/modelo.py` (precisa terminar sem erro, em ~5 s).
- Deixar abertas as abas: `README.md`, `dados/parametros.csv`, `dados/logs/novo_R3.csv`,
  `resultados/grafico_decisao.png`, `resultados/sensibilidade.csv`.

## Sequência sugerida (se o professor pedir um resumo)
1. **Pergunta e unidade funcional** → `README.md`, primeiros parágrafos.
2. **Como medimos** → `dados/logs/` e `dados/evidencias/` (capturas com "pikachu").
3. **O que é medido e o que é consultado** → `dados/parametros.csv`, coluna `origem`.
4. **Resultado** → `resultados/grafico_decisao.png`: B (prolongar) termina em 134,2 kg e A em 260,0 kg.
5. **Por que não se inverte** → `resultados/sensibilidade.csv` e a linha "Inversão" da saída do modelo.
6. **Limitações** → P_ant estimado, bateria do VAIO descalibrada, C_novo de um modelo parecido (Dell Inspiron 15 3535).

## As 8 perguntas possíveis: onde mostrar e o que lembrar

**1. Por que a unidade funcional não é "um notebook"?** → `README.md`, "Unidade funcional".
- A unidade é o serviço (2.200 h/ano por 4 anos). Os dois cenários entregam as mesmas horas.
- Se fosse "um notebook", compararíamos produtos com vidas e usos diferentes, e o resultado deixaria
  de responder à pergunta da troca.

**2. Mostre o log de carga pesada e explique a variação.** → `dados/logs/novo_R3.csv` e `antigo_R3.csv`.
- VAIO: média de 27,2 W (de 6,0 a 30,0 W). O início é mais baixo porque os 16 processos do `carga.py`
  levam alguns segundos para subir; depois, oscila com a frequência do processador e a temperatura.
- **Os valores do VAIO se repetem de 2 em 2 linhas** (ex.: 5,971 / 5,971 / 8,835 / 8,835): o sensor
  `power_now` da bateria só se atualiza a cada ~2 s, e o script lê a 1 Hz. É uma limitação do hardware,
  não um dado repetido à mão: os valores mudam ao longo dos 600 s (desvio de 4,3 W).
- RV415: o log tem o **uso de CPU** (99,5% em média, 1.296 MHz, de 60 para 75,5 °C), não potência.
  A potência é estimada: 8 W + 18 W × uso.

**3. Por que a fabricação do antigo não entra no Cenário B?** → `README.md`, "Fronteira".
- Ela já aconteceu e é igual nos dois cenários. Nenhuma decisão de hoje a evita (custo afundado).
- Somá-la a B inverteria a conclusão e responderia outra pergunta: "comprar o RV415 valeu a pena?".

**4. De onde veio o fator de emissão e de quando ele é?** → `dados/parametros.csv`, linha `FE_BR`,
e `dados/fontes/MCTI_Inventario_2026_janset.xlsx`.
- MCTI, fator médio anual do SIN para inventários, **2025 = 0,0461 tCO2/MWh**, consultado em 11/11/2026.
- França: Ember, 2025 = 41,2 g/kWh. O fator do MCTI cobre só a combustão; o da Ember é de ciclo de vida.

**5. Em que ponto a conclusão se inverteria? Por que não se inverte no Brasil?** → saída do `modelo.py`.
- Só com FE > 16,2 kg CO2-eq/kWh (27 vezes a Polônia), ou com mais de 771.683 h/ano (o ano tem 8.760 h).
- Motivo: a diferença de consumo é de só 1,77 W e a matriz é limpa. A economia é de 0,18 kg/ano,
  contra 252 kg de fabricação, o que dá t* = 1.403 anos para uma vida útil de 4.

**6. Dobre as horas de uso. O que acontece com t\*, antes de rodar?** → `python3 src/modelo.py --horas 4400`.
- **t\* cai pela metade**, porque é inversamente proporcional às horas: 1.403 → ~702 anos.
- A conclusão não muda: 702 anos continua muito acima de 4.

**7. Qual foi o maior problema e como resolveram?** → `caderno-de-bordo.md`.
- A bateria do RV415 está com 9% da capacidade (2,96 de 32,56 Wh), ele desliga fora da tomada e não
  tem sensor de potência. Medimos o uso de CPU e estimamos a potência, com a base de 8 W indicada pelo professor.
- Outros: a bateria do VAIO chegou a 7% no R2 (recarregamos antes do R3); o indicador de carga dele
  está descalibrado (82 W pela queda da bateria contra 27 W do sensor; usamos o sensor).

**8. A outra dupla reproduziu o resultado? Se houve diferença, qual foi a causa?** → ficha da verificação cruzada.
- Preencher depois da aula 3. Causas prováveis de diferença: versão do Python ou do matplotlib,
  ou um parâmetro alterado. O `requirements.txt` fixa a versão do matplotlib.

## Números para saber de cor
| | Valor |
|---|---|
| P_ant (RV415, estimado) | 16,67 W |
| P_novo (VAIO, medido) | 14,90 W |
| ΔP | 1,77 W |
| C_novo | 252 kg CO2-eq (Dell Inspiron 15 3535); sensibilidade: 79 kg (Dell 14 5440) |
| FE_BR / FE França | 0,0461 / 0,0412 kg CO2-eq/kWh |
| t\* Brasil / França | 1.403 / 1.570 anos |
| 4 anos, A / B | 260,0 / 134,2 kg CO2-eq |
| Conta de cabeça | 2 W × 2.200 h = 4 kWh × 0,05 = 0,2 kg/ano → 250 ÷ 0,2 ≈ 1.250 anos |

## Pontos fracos (admita antes que perguntem)
- P_ant é **estimado**, não medido. Mesmo se o RV415 gastasse muito mais, a conclusão não mudaria:
  no Brasil, a troca só compensaria se o novo gastasse 622 W a menos.
- C_novo vem do Dell Inspiron 15 3535, o modelo mais parecido com o VAIO FE15 (15,6", AMD, 1,9 kg)
  entre os relatórios encontrados. Com o Dell 14 5440 (79 kg) a decisão é a mesma (t* = 440 anos).
