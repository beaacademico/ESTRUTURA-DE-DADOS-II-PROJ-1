# Parte 6 --- Recomendação Final, MLOps e Observações

**Projeto:** Preditor de Redes --- Grupo 5\
**Disciplina:** Estruturas de Dados II

## 6.1 Recomendação justificada

O projeto compara três modelos de classificação --- Árvore de Decisão,
Random Forest e XGBoost --- para classificar as condições de fluxos de
rede nos estados **OK, RISCO e FALHA**. A escolha do modelo final
considera o desempenho preditivo, o custo computacional e a viabilidade
de utilização no monitoramento de redes.

Conforme a definição adotada pelo grupo para a entrega, o **XGBoost é o
modelo campeão**. Sua escolha deve ser entendida no contexto do projeto:
o algoritmo combina árvores de decisão em sequência, buscando melhorar
as previsões, e oferece recursos de regularização para controlar a
complexidade. O roteiro do projeto informa que o arquivo do modelo ocupa
aproximadamente **372 KB**, característica favorável a uma implantação
leve.

Os resultados registrados na página do projeto reportam F1-Score macro
de **1,0000** para a Árvore de Decisão e para o XGBoost, e **0,9996**
para a Random Forest. Os tempos reportados são:

  --------------------------------------------------------------------------
  Modelo      Configuração    F1-Score macro     Treinamento        Predição
              reportada                                      
  ----------- -------------- --------------- --------------- ---------------
  Árvore de   Profundidade 7          1,0000          3,69 s         0,012 s
  Decisão                                                    

  Random      50 árvores              0,9996         22,29 s         0,145 s
  Forest                                                     

  XGBoost     100 árvores             1,0000          9,58 s         0,076 s
  --------------------------------------------------------------------------

Esses valores são os resultados reportados na versão atual da página do
projeto e devem ser reproduzidos a partir do notebook final antes de
serem tratados como resultados definitivos. Como a Árvore de Decisão
também apresenta F1-Score macro de 1,0000 e tempos menores na tabela, a
escolha do XGBoost deve ser justificada pelo critério de seleção
acordado pelo grupo e pelo conjunto completo de resultados --- não
apenas pelo F1-Score. O tamanho informado de 372 KB também deve ser
confirmado no artefato final.

A comparação deve utilizar os mesmos dados de avaliação e o mesmo
protocolo temporal para os três modelos. Antes da conclusão definitiva,
é necessário verificar possíveis vazamentos de dados e confirmar o
desempenho em um conjunto de teste separado. Um resultado perfeito pode
ser legítimo, mas também pode indicar que os rótulos ou informações do
futuro estão influenciando as previsões.

## 6.2 Limitações e Data Drift

O comportamento de uma rede pode mudar ao longo do tempo devido a
alterações de rotas, mudanças de operadora, variações de tráfego e
mudanças nas condições de conexão. Essas alterações podem modificar a
distribuição dos dados de entrada, fenômeno conhecido como *data drift*.
Se também mudar a relação entre as características observadas e o estado
que o modelo deve prever, pode ocorrer *concept drift*.

Essas mudanças são uma limitação importante porque o modelo aprende com
os dados utilizados no treinamento. Caso os dados reais passem a ser
diferentes dos dados de treinamento, a qualidade das previsões poderá
diminuir.

Para reduzir esse risco, recomenda-se:

1.  Monitorar continuamente as características de entrada, como RTT,
    jitter e perda de pacotes.
2.  Acompanhar as métricas de desempenho quando houver rótulos
    confiáveis disponíveis.
3.  Registrar as versões do conjunto de dados, do modelo, dos parâmetros
    e das bibliotecas utilizadas.
4.  Investigar mudanças relevantes nas rotas e na distribuição dos
    dados.
5.  Atualizar o conjunto de treinamento e treinar novamente o modelo
    quando houver evidências de perda de desempenho.
6.  Avaliar o modelo atualizado em dados separados e temporalmente
    posteriores antes de colocá-lo em uso.

O baseline por fluxo, calculado com medidas robustas como mediana e MAD,
ajuda a comparar cada medição com o comportamento esperado daquela rota.
Entretanto, o baseline também deve ser revisado quando as condições da
rede mudarem de forma persistente.

## 6.3 Quadro de observações

### Referências analisadas

1.  **RIPE NCC. RIPE Atlas Documentation.** Documentação da plataforma
    utilizada para obter medições de rede. Disponível em:
    https://atlas.ripe.net/docs/
2.  **XGBoost. XGBoost Documentation.** Documentação oficial do
    algoritmo utilizado como modelo campeão conforme a decisão do grupo.
    Disponível em: https://xgboost.readthedocs.io/

### Três decisões do grupo

1.  **Utilizar a Anchoring Mesh:** substituir a medição inicial de ID
    1001 por medições entre anchors, buscando destinos mais estáveis
    para construir a referência de cada fluxo.
2.  **Ampliar o período de coleta:** substituir a janela inicial de duas
    horas por dois períodos de sete dias, totalizando 14 dias de
    observação --- Período A para baseline e Período B para cálculo de
    atributos e rotulagem.
3.  **Separar os dados temporalmente:** preservar a ordem cronológica na
    divisão entre treino, validação e teste, reduzindo o risco de
    utilizar informações futuras durante o treinamento.

### Uma decisão de não fazer

**Não classificar a condição da rede exclusivamente por um limite
absoluto e fixo de RTT.** Um valor de RTT pode ser normal em uma rota
longa e representar uma anomalia em uma rota curta. Por isso, o projeto
considera métricas relativas ao baseline do fluxo, além de indicadores
como jitter e perda de pacotes.

## 6.4 Deploy e acesso

A página de apresentação do projeto está publicada no GitHub Pages e
pode ser acessada publicamente:

**Site do projeto:**
https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/\
**Repositório:**
https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1

A publicação permite consultar a descrição do problema, os modelos
avaliados, a metodologia, os resultados reportados, a conclusão, a
equipe e as referências. Antes da entrega, é necessário conferir se o
conteúdo publicado corresponde à versão final do trabalho e se os links
e recursos da página funcionam corretamente.

É importante distinguir a publicação do site da implantação do modelo. O
GitHub Pages disponibiliza a página estática de apresentação; isso, por
si só, não significa que o modelo esteja executando previsões em tempo
real. A implantação operacional exigiria também um serviço ou aplicação
que carregue o modelo, receba dados de entrada e produza previsões.

## Considerações finais

O projeto apresenta uma abordagem de monitoramento baseada em medições
reais, baseline por fluxo e classificação dos estados da rede. A
recomendação do XGBoost deve ser sustentada pelos resultados
reproduzidos e por uma avaliação independente, com separação temporal e
verificação de possíveis vazamentos. O monitoramento contínuo e a
análise de *data drift* são necessários para avaliar se o modelo
continua adequado quando as condições da rede mudam.

## Referências complementares

-   RIPE NCC. *RIPE Atlas Documentation*. https://atlas.ripe.net/docs/
-   XGBoost. *XGBoost Documentation*. https://xgboost.readthedocs.io/
-   scikit-learn. *Model evaluation: quantifying the quality of
    predictions*.
    https://scikit-learn.org/stable/modules/model_evaluation.html
-   scikit-learn. *TimeSeriesSplit*.
    https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
-   Grupo 5. *Preditor de Redes --- repositório do projeto*.
    https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1
-   Grupo 5. *Preditor de Redes --- página pública*.
    https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/
