# Logs brutos de medição

Seis arquivos, gerados por `src/medir.py` (ou `powerstat`, ou `src/medir_windows.ps1`):

| equipamento | R1 ocioso | R2 típico | R3 carga pesada |
|---|---|---|---|
| antigo (Samsung RV415) | `antigo_R1.csv` | `antigo_R2.csv` | `antigo_R3.csv` |
| novo | `novo_R1.csv` | `novo_R2.csv` | `novo_R3.csv` |

Logs do `powerstat` podem ser salvos como `antigo_R1.log` etc.; o parser reconhece os dois formatos.
Não edite os arquivos. `src/modelo.py` calcula as médias e emite ALERTA se um log tiver menos
de ~600 amostras, potência constante ou carimbos repetidos.
