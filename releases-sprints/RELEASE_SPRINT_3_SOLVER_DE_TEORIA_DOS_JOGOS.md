# Release — Sprint 3: Solver de Teoria dos Jogos

**Data:** 2026-07-19
**Sprint:** 3 de 5
**Status:** Concluído

## Objetivo do Sprint

Calcular o resultado estratégico de uma matriz de payoff já montada:
estratégia(s) dominante(s) e equilíbrio(s) de Nash em estratégia pura.

## O que foi feito

- Foi implementado o módulo `solver.py`, de autoria da dupla, cobrindo:
  - **Estratégia dominante (RF07):** para cada jogador, o solver percorreu
    cada estratégia candidata e verificou se ela produz um payoff maior ou
    igual a todas as demais estratégias próprias, contra toda estratégia
    possível do oponente. Foi implementada a distinção entre dominância
    **estrita** (sempre estritamente melhor) e **fraca** (melhor ou igual,
    com pelo menos um empate), retornando `None` quando nenhuma estratégia
    domina as demais.
  - **Equilíbrio de Nash em estratégia pura (RF08):** o solver calculou,
    para cada estratégia do concorrente, a(s) melhor(es) resposta(s) do
    usuário, e vice-versa, retornando toda combinação em que nenhum dos
    dois jogadores melhora desviando sozinho — podendo haver zero, um ou
    múltiplos equilíbrios.
  - Foi reforçado, em docstring, que este módulo é **determinístico** e
    não depende de LLM nem de bibliotecas externas em produção.
- Foram escritos testes automatizados (`tests/test_solver.py`) validando o
  solver contra **4 exemplos clássicos da literatura**:
  - **Dilema do prisioneiro** — confirmando estratégia dominante estrita
    ("Delatar") para os dois jogadores e equilíbrio de Nash único em
    (Delatar, Delatar). Este caso também foi **validado cruzado com a
    biblioteca `nashpy`**, usada apenas como referência de teste.
  - **Batalha dos sexos** — confirmando ausência de estratégia dominante e
    dois equilíbrios de Nash distintos, caso clássico de coordenação.
  - **Matching pennies** — confirmando ausência de equilíbrio de Nash em
    estratégia pura, caso clássico que só tem solução em estratégia mista
    (fora do escopo da v1, conforme documentado).
  - Um caso sintético de **dominância fraca**, para garantir que a
    distinção entre dominância estrita e fraca funciona corretamente.
- Todos os 4 testes passaram na primeira execução completa da suíte.

## Requisitos atendidos neste sprint

RF07, RF08.

## Riscos observados

- O escopo da v1 cobre apenas equilíbrio de Nash em estratégia pura; jogos
  sem equilíbrio puro (como matching pennies) são tratados corretamente
  como "sem equilíbrio identificado nesta versão", sem gerar erro — isso
  precisará ficar claro na recomendação final (Sprint 4), para não passar
  a impressão de que o sistema falhou.

## Próximos passos (Sprint 4)

Gerar a recomendação final em linguagem natural via LLM a partir do
resultado do solver, nomeando explicitamente o conceito de Teoria dos
Jogos utilizado, e integrar todo o pipeline ponta a ponta dentro do chat.
