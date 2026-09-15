# Coleta de Dados

**Etapas realizadas:** 2, 3 e 11  
**Realizado por:** Vitória Alessandra das Neves  
**RGM:** 41812182  
**Realização:** 12/09/26  

---

## Etapa 2

| Decisão | Escolha da Equipe | Justificativa |
|---------|-------------------|---------------|
| **ID da medição** | 2000000 | Esta porta atende a todos os requisitos |
| **Intervalo Consultado** | Duas horas antes da execução | Um intervalo breve de execução para reduzir o volume de dados |
| **Duração do intervalo** | 2Hr | O período reduz o volume da coleta e é suficiente para validar o pipeline. |
| **Tipo de medição** | Ping | O tipo foi identificado na resposta de detalhes da medição. |
| **Formato de saída: CSV ou Parquet** | CSV | Escolhido por sua simplicidade de validação, abertura e compartilhamento |

---

## Etapa 3

A biblioteca executa com êxito.

---

## Etapa 11
**Responsável:** Vitória Alessandra das Neves  

### Atividade realizada:
Nesta etapa da atividade foi pesquisada e reforçado o que é uma API, o que é a “RIPE Atlas”, o entendimento do “measurements” e entender qual o tipo da ID, se é pública e se está aberta ou finalizada. Também foi validado como realizar o import das bibliotecas.

---

## Relatório de Contribuição e Evidências

* **Parte do trabalho relacionada:** Realizada a seção 2 juntamente do teste de adicionar as bibliotecas da seção 3. Também feito a etapa 11 com os registros da atividade feita por este usuário.
* **Tempo dedicado (aproximado):** 2 horas.

### Evidência da contribuição:

| Decisão | Escolha da Equipe | Justificativa |
|---------|-------------------|---------------|
| **ID da medição** | 1007 | Esta porta atende a todos os requisitos |
| **Intervalo Consultado** | Última hora antes da execução | Um intervalo breve de execução para reduzir o volume de dados |
| **Duração do intervalo** | 1Hr | O período reduz o volume da coleta e é suficiente para validar o pipeline. |
| **Tipo de medição** | Ping | O tipo foi identificado na resposta de detalhes da medição. |
| **Formato de saída: CSV ou Parquet** | CSV | Escolhido por sua simplicidade de validação, abertura e compartilhamento |

### Código de Importação das Bibliotecas:

```python
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

print("Bibliotecas carregadas.")
```

**Explicação da evidência:**  
Essas evidências mostram a realização da tarefa, demonstrando o preenchimento da tabela junto com as justificativas e o import com êxito das bibliotecas.
