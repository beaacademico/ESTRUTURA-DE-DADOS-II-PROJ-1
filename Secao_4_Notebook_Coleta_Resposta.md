## 4. Montar o Google Drive e preparar a pasta `raw`

**Realizado por:** Breno Brasil de Souza (RGM: 48365963)

**Execução:**

```python
from google.colab import drive

drive.mount("/content/drive")

PASTA_PROJETO = Path("/content/drive/MyDrive/ripe_atlas")
PASTA_RAW = PASTA_PROJETO / "raw"
PASTA_RAW.mkdir(parents=True, exist_ok=True)

print("Arquivos raw serão salvos em:", PASTA_RAW)
```

**Saída obtida:**

```
Mounted at /content/drive
Arquivos raw serão salvos em: /content/drive/MyDrive/ripe_atlas/raw
```

**Resultado:** o Google Drive foi montado com sucesso e a pasta `ripe_atlas/raw` foi criada dentro do `MyDrive` da minha conta. Esse é o caminho onde os arquivos `.json`, `.csv`/`.parquet` e os metadados da coleta (Seção 9 do notebook) serão salvos.

**Caminho gerado:** `MyDrive/ripe_atlas/raw`

---

### Como o grupo acessa essa pasta

**Decisão do grupo:** para evitar que cada integrante gere sua própria pasta `raw` isolada (o que aconteceria se cada um rodasse o notebook apontando pro próprio `MyDrive`), a pasta `ripe_atlas` criada nesta etapa (na minha conta) será usada como **fonte única** do projeto. O link já está liberado para qualquer pessoa com acesso — as próximas coletas devem ser salvas ali, em vez de cada pessoa criar a própria.

**Link:** https://drive.google.com/drive/folders/10LREhRohsM6TJAXghLiRgItydt5Qzyou?usp=sharing

**Instruções para o grupo (adicionar a pasta ao próprio Drive):**

1. Abra o link acima
2. No canto superior, clique no ícone do Google Drive (ou clique com o botão direito na pasta `ripe_atlas`) e selecione **"Adicionar atalho ao Drive"**
3. Escolha onde o atalho vai aparecer no seu Drive (ex: `Meu Drive`) e confirme
4. A pasta passa a aparecer no seu próprio Google Drive, sem duplicar os arquivos — qualquer coisa salva nela por qualquer integrante fica visível pra todos

---

## 11. Contribuições Individuais

### Integrante — Breno Brasil de Souza

- **Atividade realizada:**
  Executei a Seção 4 do notebook de ingestão (montagem do Google Drive via Colab e criação da pasta `raw`). Autorizei o acesso da minha conta Google, confirmei a criação do caminho `MyDrive/ripe_atlas/raw`, e defini essa pasta como fonte única de dados do grupo — evitando que cada integrante gerasse sua própria pasta isolada ao rodar o notebook na própria conta. Compartilhei o link de acesso e documentei o passo a passo para o restante do grupo adicionar essa pasta ao próprio Drive via atalho.

- **Parte do trabalho relacionada:**
  Seção 4 do notebook `2 - Coleta de dados.ipynb` (Montar o Google Drive e preparar a pasta `raw`).

- **Tempo dedicado (aproximado):**
  30min

- **Evidência da contribuição:**
  Print da execução da célula no Colab, mostrando a saída `Mounted at /content/drive` e `Arquivos raw serão salvos em: /content/drive/MyDrive/ripe_atlas/raw`. Link da pasta compartilhada: https://drive.google.com/drive/folders/10LREhRohsM6TJAXghLiRgItydt5Qzyou?usp=sharing

- **Explicação da evidência:**
  O print comprova que o Drive foi montado com sucesso e a pasta `raw` foi criada no caminho esperado. O link comprova que a pasta está compartilhada e acessível ao restante do grupo, servindo como repositório único da coleta.
