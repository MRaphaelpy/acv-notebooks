# ACV — substituir agora ou prolongar o uso de um notebook

Prática 4 — Gestão Ambiental (PROD2222), UNIVASF, 2026.2. **Dupla 2**: Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.

> **Roteiro da defesa:** [`APRESENTACAO.md`](APRESENTACAO.md) — o que abrir, a ordem e onde está a resposta de cada pergunta.

**Objetivo.** Trocar agora o Samsung RV415 (2011, AMD E-300; Cenário B) pelo VAIO FE15
(Ryzen 7 5700U; Cenário A) reduz ou aumenta o impacto ambiental em 4 anos?

**Unidade funcional.** Disponibilizar 2.200 h/ano de computação pessoal (perfil estagiário em
desenvolvimento) durante 4 anos. A unidade é o serviço, não "um notebook": os dois cenários entregam
as mesmas horas e por isso são comparáveis.

**Fronteira.** Berço ao túmulo: fabricação, distribuição, uso e fim de vida. Ficam excluídos
periféricos, rede e nuvem, que são iguais nos dois cenários. Cenário A: compra do novo e descarte do
RV415 no ano 0. Cenário B: RV415 por 2 anos, descarte e compra do novo no ano 2.
**A fabricação do RV415 não entra:** já foi emitida, e nenhuma decisão tomada hoje a evita. Ela é
idêntica nos dois cenários; somá-la a B responderia outra pergunta (custo afundado).

**Dados.** Medidos: potência do VAIO na bateria (`power_now`, 1 Hz, 600 s × 3 regimes), uso de CPU
do RV415 (1 Hz, 600 s × 3) e massa do RV415 (2,2 kg). Documentais, com fonte e data em
`dados/parametros.csv`: C_novo = 252 kg CO2-eq (Dell Inspiron 15 3535: 15,6", AMD, 1,9 kg, o modelo
mais parecido com o VAIO FE15 entre os relatórios encontrados), FE_BR = 0,0461 (MCTI, 2025) e
FE_França = 0,0412 (Ember, 2025), em kg CO2-eq/kWh.

**Reproduzir:** `pip install -r requirements.txt && python3 src/modelo.py` (saída em `resultados/`).

## Resultados
| | RV415 (antigo) | VAIO (novo) |
|---|---|---|
| R1 / R2 / R3 (W) | 8,2 / 16,3 / 25,9 (estimado pela CPU medida) | 10,4 / 11,0 / 27,2 (medido) |
| **P média ponderada** | **16,67 W** | **14,90 W** |

- ΔP = 1,77 W → economia de 3,9 kWh/ano → 0,18 kg CO2-eq/ano no SIN.
- **t\* (SIN) = 1.403 anos; t\* (França) = 1.570 anos**, muito acima da vida útil de 4 anos.
- Em 4 anos, com o carbono alocado pela vida útil: A = 260,0 e **B = 134,2 kg CO2-eq** (SIN).
  Energia primária: A = 1.227 e B = 797 kWh. Resíduo eletrônico: 2,2 kg nos dois cenários (A no ano 0, B no ano 2).
- Conferência de cabeça: 2 W × 2.200 h = 4 kWh/ano × 0,05 = 0,2 kg/ano; 250 ÷ 0,2 ≈ 1.250 anos. ✔
- **Sensibilidade:** a conclusão só se inverteria com FE > 16,2 kg CO2-eq/kWh (27 vezes a matriz da
  Polônia, à base de carvão) ou com h > 771.683 h/ano (o ano tem 8.760 h). Não se inverte em nenhum
  ponto da varredura: ΔP é pequeno e as duas matrizes são limpas, então a economia nunca paga a fabricação.
  Com outros relatórios de carbono, B continua melhor: Dell Inspiron 14 5440 (79 kg, t\* = 439 anos) e
  Positivo Master N1110 (108 kg, t\* = 602 anos; mesmo fabricante do VAIO, mas 11,6" e Celeron).
- Na leitura literal (carbono integral na compra também em B, no ano 2), B termina 0,3 kg acima de A,
  porque B compra o mesmo notebook e ainda usa o RV415 por 2 anos. Isso ignora que o novo de B segue
  em uso após o ano 4; por isso a conclusão usa a leitura alocada, coerente com t\* × vida útil.

## Limitações
- **P_ant é estimado:** a bateria do RV415 tem 9% da capacidade e ele não tem sensor de potência.
  P = 8 W (base indicada pelo professor) + 18 W (TDP do E-300) × uso de CPU medido.
- C_novo vem do Dell Inspiron 15 3535, não do VAIO: não há pegada por unidade publicada para o FE15
  (buscas em 12/11 no site da VAIO, no relatório de sustentabilidade da Positivo e no cadastro EPEAT).
  O relatório da Dell tem incerteza grande (167 a 614 kg) e o transporte foi calculado para a Europa.
- O indicador de carga do VAIO está descalibrado (82 W pela queda da bateria no R3, contra 27 W do sensor);
  usou-se o `power_now`, que só se atualiza a cada ~2 s.
- O fator do MCTI cobre só a combustão; o da Ember é de ciclo de vida. A energia primária incorporada
  foi estimada por proporção dos componentes (Boavizta).

## Conclusão
**Prolongar o uso do RV415 (Cenário B) emite cerca de 48% menos CO2-eq em 4 anos** no Brasil e
na França. O novo é só 1,8 W mais eficiente, e com eletricidade de baixa emissão essa economia levaria
cerca de 1.400 anos para pagar a fabricação. A decisão não muda em nenhum ponto da sensibilidade.
