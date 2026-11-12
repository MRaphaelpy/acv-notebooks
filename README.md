# ACV — substituir agora ou prolongar o uso de um notebook

Prática 4 — Gestão Ambiental (PROD2222), UNIVASF, 2026.2. **Dupla 2**: Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.

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
`dados/parametros.csv`: C_novo = 79 kg CO2-eq (Dell Inspiron 14 5440, modelo mais próximo com
relatório), FE_BR = 0,0461 (MCTI, 2025), FE_França = 0,0412 (Ember, 2025), em kg CO2-eq/kWh.

**Reproduzir:** `pip install -r requirements.txt && python3 src/modelo.py` (saída em `resultados/`).

## Resultados
| | RV415 (antigo) | VAIO (novo) |
|---|---|---|
| R1 / R2 / R3 (W) | 8,2 / 16,3 / 25,9 (estimado pela CPU medida) | 10,4 / 11,0 / 27,2 (medido) |
| **P média ponderada** | **16,67 W** | **14,90 W** |

- ΔP = 1,77 W → economia de 3,9 kWh/ano → 0,18 kg CO2-eq/ano no SIN.
- **t\* (SIN) = 440 anos; t\* (França) = 492 anos**, ambos muito acima da vida útil de 4 anos.
- Em 4 anos, com o carbono alocado pela vida útil: A = 86,5 e **B = 47,3 kg CO2-eq** (SIN).
  Energia primária: A = 613 e B = 491 kWh. Resíduo eletrônico: 2,2 kg nos dois cenários (A no ano 0, B no ano 2).
- Conferência de cabeça: 2 W × 2.200 h = 4 kWh/ano × 0,05 = 0,2 kg/ano; 79 ÷ 0,2 ≈ 400 anos. ✔
- **Sensibilidade:** a conclusão só se inverteria com FE > 5,07 kg CO2-eq/kWh (mais de 8 vezes a
  matriz da Polônia, que é a base de carvão) ou com h > 241.725 h/ano (o ano tem 8.760 h). Ela não se inverte em nenhum ponto
  da varredura, porque ΔP é pequeno e as duas matrizes são limpas: a economia de energia nunca paga
  os 79 kg emitidos na fabricação.
- Na leitura literal (carbono integral na compra também em B, no ano 2), B termina 0,3 kg acima de A,
  porque B compra o mesmo notebook e ainda usa o RV415 por 2 anos. Isso ignora que o novo de B segue
  em uso após o ano 4; por isso a conclusão usa a leitura alocada, coerente com t\* × vida útil.


## Conclusão
**Prolongar o uso do RV415 (Cenário B) emite cerca de 45% menos CO2-eq em 4 anos** no Brasil e
na França. O novo é só 1,8 W mais eficiente, e com eletricidade de baixa emissão essa economia levaria
cerca de 440 anos para pagar a fabricação. A decisão não muda dentro da faixa de sensibilidade exigida.
