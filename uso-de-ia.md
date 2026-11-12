# Declaração de uso de IA

Ferramenta: Claude (Anthropic), via Claude Code, em 2026-11-11.

- Estrutura do repositório e arquivo de dados vazio (`dados/parametros.csv`): aproveitado como base.
- Código do modelo, ponto de equilíbrio, sensibilidade e gráficos (`src/modelo.py`): aproveitado e revisado pela dupla.
- Scripts de coleta (`src/medir.py`, `src/medir_windows.ps1`) e leitura de logs (`src/potencia.py`): aproveitados.
- Script que roda os 3 regimes em sequência (`src/medir_tudo.py`): aproveitado.
- Script de carga `src/carga.py` (SHA-256 em todos os núcleos por 600 s, conforme a descrição do roteiro), gerado porque o oficial não estava disponível: aproveitado.
- Consulta à API Boavizta (`src/boavizta.py`): aproveitado.
- Testes de conferência das contas (`tests/`): aproveitados.
- Rascunho da estrutura do README: aproveitado. Resultados, limitações e conclusão escritos pela dupla.
- Busca e extração dos dados documentais (MCTI, Ember, Dell LCA, Boavizta) com URL e data: aproveitado; valores conferidos pela dupla nos arquivos de `dados/fontes/`.
- A IA não gerou valores de medição (potência, massa), não inventou fontes, nem escreveu o caderno de bordo.
