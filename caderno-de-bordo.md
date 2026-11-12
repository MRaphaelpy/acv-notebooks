# Caderno de Bordo

## 11/11/2026 — Sessão 1: preparação do ambiente e pesquisa inicial

- **Presentes:** Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.
- **Horário:** 14h30 às 16h (horário de Brasília).
- **O que foi feito:**
  - Criamos o repositório e os scripts de medição e do modelo.
  - Definimos as etapas de medição: R1 (ocioso), R2 (uso típico) e R3 (carga pesada).
  - Buscamos os dados documentais: fator de emissão do SIN (MCTI), fatores da Polônia e da França (Ember) e relatórios de pegada de carbono da Dell.
- **Problema:** As fontes de fator de emissão não medem a mesma coisa. O MCTI informa 0,0461 kg CO₂/kWh para o Brasil em 2025, considerando só a queima de combustível nas usinas; a Ember informa 0,109 para o Brasil, porque inclui o ciclo de vida das usinas.
- **Como resolvemos:** Usamos o MCTI no caso principal, como pede o roteiro, e a Ember para a França. Registramos a diferença de escopo nas limitações, porque ela favorece o Brasil na comparação.

## 11/11/2026 — Sessão 2: medição do Samsung RV415

- **Presentes:** Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.
- **Horário:** 16h16 às 16h49 (horário de Brasília).
- **O que foi feito:**
  - Medimos o Samsung RV415 nos três regimes, 10 minutos cada: R1 (ocioso), R2 (uso típico) e R3 (carga pesada, com o `carga.py`).
  - Registramos o uso do processador a cada segundo com o `medir_uso.py` (600 amostras por regime) e tiramos uma captura de tela por regime com a palavra-chave "pikachu".
  - Deixamos o brilho em 4 de 7 níveis (57%), o mais próximo de 50% que a tela permite.

- **Problema 1:** A bateria está praticamente morta: guarda 2,96 Wh de 32,56 Wh originais (9%), e o notebook desliga quando tiramos o carregador. O sistema também não informa a tensão (`voltage_now` dá erro), então não havia como medir a potência por software.

- **Como resolvemos:** O professor autorizou medir na tomada. Medimos o uso do processador e estimamos a potência como 8 W de base (valor indicado pelo professor) + 18 W (TDP do AMD E-300) × uso. Por isso o P_ant aparece como "estimado" no arquivo de dados.

- **Problema 2:** O notebook está sem HD interno, então o Linux Mint rodava de um pendrive. Havia ainda um segundo pendrive (Ventoy) conectado, e o roteiro pede medição sem periféricos USB.

- **Como resolvemos:** Retiramos o pendrive extra. O do sistema não pode sair com o notebook ligado, então ficou e foi registrado nas limitações.

- **Problema 3:** O relógio do Mint em pendrive estava em UTC, então os logs do RV415 mostram 19h para medições feitas às 16h (horário de Brasília).

- **Como resolvemos:** Mantivemos os logs como foram gerados (não se edita log bruto) e anotamos a diferença de 3 horas aqui.

- **Resultados obtidos:**
  - R1 (ocioso): utilização média da CPU de 1%.
  - R2 (uso típico): utilização média da CPU de 46%.
  - R3 (uso pesado): utilização média da CPU de 99,5%.

## 11/11/2026 — Sessão 3: medição do notebook VAIO

- **Presentes:** Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.
- **Horário:** 17h10 às 18h38, com intervalos para recarga.
- **O que foi feito:**
  - Medimos o VAIO FE15 na bateria, fora da tomada, no modo de energia equilibrado e com brilho de 50%.
  - Registramos a potência a cada segundo pelo sensor `power_now` (600 amostras por regime).
  - Bateria em cada regime: R1 das 17h10 às 17h20 (91% → 72%), R2 das 17h44 às 17h54 (25% → 5%) e R3 das 18h28 às 18h38 (58% → 8%).

- **Problema 4:** A bateria descarregou muito mais rápido que o esperado. No fim do R2 estava com 5%, insuficiente para os 10 minutos de carga pesada do R3.

- **Como resolvemos:** Concluímos a etapa R2, que terminou completa, e recarregamos o notebook até 58%. Depois, executamos a etapa R3 separadamente.

- **Problema 5:** A queda da bateria não bate com o sensor. No R3, a energia caiu 13,6 Wh em 10 minutos, o que daria 82 W, mas o sensor marcou 27 W em média. A bateria guarda 27,3 de 55,2 Wh originais (49%).

- **Como resolvemos:** 82 W é impossível para esse notebook, então concluímos que o indicador de carga está descalibrado pelo desgaste. Usamos o `power_now`, que é a leitura direta, e registramos a diferença nas limitações. Notamos também que o sensor só se atualiza a cada ~2 s, por isso os valores se repetem de duas em duas linhas no log.

- **Resultados obtidos:**
  - R1 (ocioso): potência média de 10,4 W.
  - R2 (uso típico): potência média de 11,0 W.
  - R3 (uso pesado): potência média de 27,2 W.

## 11/11/2026 — Sessão 4: pesagem do RV415 e revisão dos dados de fabricação

- **Presentes:** Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.
- **Horário:** Período da noite.
- **O que foi feito:**
  - Pesamos o Samsung RV415: 2,2 kg, sem o carregador.
  - Rodamos o modelo pela primeira vez e conferimos o resultado com a conta de cabeça.
  - Revisamos o relatório usado para a pegada de carbono de fabricação do notebook novo.
  - Analisamos os relatórios de pegada de carbono de produto (PCF) da Dell.
  - Atualizamos a referência utilizada para estimar o impacto da fabricação do notebook VAIO.

- **Problema 6:** Percebemos que o primeiro relatório escolhido para estimar a pegada de carbono do VAIO era referente ao Dell Inspiron 14 5440, um notebook de 14 polegadas com processador Intel e peso de aproximadamente 1,55 kg. Apesar de ser uma referência possível, ele apresentava diferenças em relação ao VAIO analisado.

- **Como resolvemos:** Substituímos a referência principal pelo Dell Inspiron 15 3535, que possui tela de 15,6 polegadas, processador AMD e peso aproximado de 1,9 kg, com pegada de carbono total informada de 295 kg de CO₂e, dos quais 252 kg correspondem à fabricação e ao transporte (81,3% + 4,2%), a parcela usada no modelo. Mantivemos o Dell Inspiron 14 5440, com 79 kg de CO₂e de fabricação e transporte, como referência de sensibilidade para avaliar a influência da escolha do equipamento comparável.

- **Resultado:** a decisão não mudou com a troca de relatório; com o 3535, o ponto de equilíbrio passou de 439 para 1.403 anos.

## 12/11/2026 — Sessão 5: pesquisa da pegada de carbono e consolidação das referências

- **Presentes:** Marcos Rafael Silvestri dos Santos e Jayme Gabriel Carvalho.
- **Horário:** 0h às 0h20 (horário de Brasília).
- **O que foi feito:**
  - Pesquisamos informações sobre a pegada de carbono de fabricação do notebook VAIO.
  - Consultamos o site da VAIO e o relatório de sustentabilidade da Positivo referente a 2024/2025.
  - Verificamos o cadastro EPEAT do modelo FE15.
  - Procuramos referências adicionais para estimar o impacto ambiental de notebooks semelhantes.
  - Analisamos um estudo referente ao Positivo Master N1110.
  - Revisamos a necessidade de incluir a pegada de carbono de fabricação do Samsung RV415 na comparação.

- **Problema 7:** Não encontramos valores públicos de pegada de carbono por unidade para o VAIO FE15 nas fontes consultadas. O site da VAIO, o relatório de sustentabilidade da Positivo e o cadastro EPEAT não apresentaram o valor específico que precisávamos.

- **Como resolvemos:** Ampliamos a pesquisa e encontramos um estudo referente ao Positivo Master N1110, que apresenta uma pegada de carbono de fabricação de aproximadamente 108 kg de CO₂e. Como esse equipamento possui tela de 11,6 polegadas e processador Celeron, decidimos utilizá-lo somente como referência de sensibilidade, e não como equivalente direto ao VAIO.

- **Problema 8:** Precisávamos decidir se a pegada de carbono de fabricação do Samsung RV415 deveria entrar na comparação, já que não encontramos um valor específico para esse modelo.

- **Como resolvemos:** Concluímos que não seria necessário incluir a fabricação do RV415 na comparação, pois ele já havia sido adquirido anteriormente. Seu custo ambiental de fabricação é considerado um custo afundado no contexto da decisão atual. Assim, a comparação inclui o uso dos dois equipamentos e a fabricação do notebook novo; apenas a fabricação do RV415 ficou de fora.

- **Resultados obtidos:**
  - Não encontramos um valor específico de carbono por unidade para o VAIO FE15.
  - Encontramos o valor de aproximadamente 108 kg de CO₂e para o Positivo Master N1110.
  - Mantivemos o N1110 apenas como referência de sensibilidade.
  - Definimos que a fabricação do RV415 ficaria fora da comparação principal.

---

## Observações finais

Os maiores problemas vieram dos equipamentos (duas baterias gastas e um notebook sem sensor de potência) e da falta de dados dos fabricantes (nenhuma pegada publicada para o VAIO FE15).

Nenhum deles muda a decisão. Mesmo com o consumo do RV415 estimado e com três relatórios diferentes para a fabricação do notebook novo, manter o RV415 emite menos em todos os casos, porque a diferença de consumo é de só 1,8 W e a energia do Brasil é limpa.
