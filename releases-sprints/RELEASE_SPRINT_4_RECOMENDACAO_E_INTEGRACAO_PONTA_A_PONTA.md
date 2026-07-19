# Release — Sprint 4: Recomendação e Integração Ponta a Ponta

**Data:** 2026-07-19
**Sprint:** 4 de 5
**Status:** Concluído

## Objetivo do Sprint

Gerar a recomendação final em linguagem natural a partir do resultado do
solver, e fechar o pipeline completo (link → estratégias → matriz →
solver → recomendação) dentro da interface de chat.

## O que foi feito

- Foi adicionada ao módulo `llm.py` a função `generate_recommendation`,
  responsável por redigir a recomendação final (RF09):
  - Foi escrito um prompt que deixa explícito ao LLM que os resultados
    (estratégia dominante e equilíbrio de Nash) **já vêm calculados** pelo
    solver determinístico, e que a única tarefa do modelo é **explicar**
    esse resultado — nunca recalculá-lo ou contestá-lo. Essa restrição
    reforça, na prática, a separação de responsabilidades definida desde o
    Sprint 1 entre cálculo (Python) e redação (LLM).
  - Foi exigido que a resposta nomeie explicitamente o conceito de Teoria
    dos Jogos utilizado (estratégia dominante e/ou equilíbrio de Nash) e
    explique o que ele significa em termos simples, atendendo à extensão
    de escopo feita no RF09 antes do início da implementação.
  - Foi tratado explicitamente o caso de **ausência** de estratégia
    dominante e/ou de equilíbrio de Nash em estratégia pura, instruindo o
    modelo a apresentar isso como um resultado válido, não como uma falha
    do sistema.
  - Foi reforçada, no próprio prompt, a obrigação de mencionar quando os
    payoffs usados são heurísticos (RNF02) e de deixar claro que a
    recomendação cobre apenas o aspecto estratégico/competitivo, não a
    viabilidade geral do negócio (RNF08).
- O fluxo de chat (`app.py`) foi integrado de ponta a ponta:
  - Após a matriz de payoff ser exibida (Sprint 2), o sistema passou a
    chamar automaticamente o solver (`find_dominant_strategies` e
    `find_pure_nash_equilibria`, do Sprint 3) e a exibir o resultado bruto
    como uma etapa visível no chat.
  - Em seguida, a recomendação em linguagem natural foi gerada e exibida
    ao usuário como a resposta final da análise.
  - Foi tratado o caso de falha na geração da recomendação (ex.:
    indisponibilidade da API): o sistema informa o ocorrido sem perder os
    resultados já calculados pelo solver, que continuam visíveis na etapa
    anterior.
- Foi validado, via smoke test isolado, o pipeline completo (matriz →
  solver → recomendação) fora da interface de chat, confirmando que a
  recomendação gerada nomeou corretamente o conceito de equilíbrio de
  Nash, explicou o raciocínio, mencionou a natureza heurística dos
  payoffs e reforçou a delimitação de escopo.
- A aplicação Chainlit foi validada novamente após a integração, subindo
  sem erros, e a suíte de testes automatizados (`pytest`) continuou
  passando integralmente (4/4).

## Requisitos atendidos neste sprint

RF09, RNF02 (reforço final), RNF06, RNF08 (reforço final).

## Critério de pronto

Um usuário consegue, sem intervenção manual no código, ir do link do
concorrente até a recomendação final — confirmado via teste manual do
fluxo completo.

## Próximos passos (Sprint 5)

Aplicar a identidade visual (tabuleiro estratégico corporativo), revisar
UX, preparar o deploy (Render) e o roteiro de apresentação.
