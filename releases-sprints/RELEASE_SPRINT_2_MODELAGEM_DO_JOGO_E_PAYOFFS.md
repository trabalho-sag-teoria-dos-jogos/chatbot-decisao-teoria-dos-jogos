# Release — Sprint 2: Modelagem do Jogo e Payoffs

**Data:** 2026-07-19
**Sprint:** 2 de 5
**Status:** Concluído

## Objetivo do Sprint

Montar a matriz de payoff do jogo (usuário x concorrente), suportando as
duas formas de entrada previstas no planejamento: heurística automática e
valor manual informado pelo usuário.

## O que foi feito

- Foi criado o módulo `payoff.py`, responsável por toda a modelagem do
  jogo:
  - Foi definida a escala ordinal heurística fixa e documentada (RD02):
    1 (baixo), 2 (médio) e 3 (alto).
  - Foi implementado um classificador de estratégias por categoria
    (`custo`, `diferenciação`, `nicho`, `geral`), baseado em
    correspondência de palavras-chave sobre o texto da estratégia.
  - Foi implementada a regra heurística de payoff: estratégias na mesma
    categoria foram tratadas como concorrência direta pelo mesmo público
    (payoff baixo para os dois lados); estratégias em categorias
    diferentes foram tratadas como de menor sobreposição (payoff alto);
    estratégias não classificadas geraram payoff médio (incerteza). Essa
    regra foi documentada no próprio código para manter o critério
    auditável.
  - Foram criadas as estruturas `Game` e `PayoffCell`, guardando, por
    célula da matriz, o payoff do usuário, o payoff do concorrente e uma
    marcação explícita de heurístico vs. manual (RF11).
  - Foi implementada a renderização da matriz como tabela Markdown,
    exibindo cada célula com o par de payoffs e a etiqueta de origem
    (RF10).
- O fluxo de chat (`app.py`) foi estendido para cobrir o restante do
  Sprint 2:
  - Após a extração das estratégias do concorrente (Sprint 1), o usuário
    passou a ser solicitado a informar suas próprias estratégias, com
    validação de no mínimo 2 (RF04, RD01).
  - Foi adicionada uma pergunta com botões de ação (heurística automática
    x valor manual) para a escolha do modo de payoff (RF06).
  - No modo heurístico, a matriz completa foi calculada e exibida
    imediatamente, acompanhada de um aviso explícito de que os valores são
    estimativas ordinais, com o critério da heurística descrito na própria
    mensagem (RNF02).
  - No modo manual, o sistema passou a perguntar, célula a célula, o par
    de payoffs (`seu_valor,valor_do_concorrente`), validando o formato
    antes de aceitar, até completar toda a matriz.
  - A matriz final foi exibida de forma tabular no chat em ambos os modos
    (RF10), com marcação visual por célula indicando se o valor é
    heurístico ou manual (RF11).
- Foi validado manualmente, via smoke test isolado do módulo `payoff.py`,
  que a regra heurística produz os resultados esperados: mesma categoria
  → payoff (1, 1); categorias diferentes → payoff (3, 3).
- A aplicação Chainlit foi validada novamente após as mudanças, subindo
  sem erros de inicialização.
- Foi criado o `README.md` do projeto, com descrição do trabalho, stack
  técnica, instruções de configuração do ambiente e passo a passo de uso
  do chatbot.

## Requisitos atendidos neste sprint

RF04, RF05, RF06, RF10, RF11, RD01, RD02, RNF02 (reforçado na própria
matriz, além da recomendação final que virá no Sprint 4).

## Riscos observados

- O classificador heurístico por palavras-chave é intencionalmente simples
  e pode não capturar nuances de estratégias fora do vocabulário mapeado —
  nesses casos, o sistema já assume o valor médio (incerteza) em vez de
  arriscar uma classificação errada, mantendo o comportamento conservador.
- A entrada manual célula a célula funciona bem para matrizes pequenas
  (2–4 estratégias por lado); para matrizes maiores o fluxo ficaria
  repetitivo, mas isso está alinhado ao escopo do projeto (jogo 2x2
  simultâneo como prioridade).

## Próximos passos (Sprint 3)

Implementar o solver de teoria dos jogos (estratégia dominante e
equilíbrio de Nash em estratégia pura) sobre a matriz já montada, validado
contra exemplos clássicos da literatura.
