# Planejamento de Sprints

Cronograma sugerido de **5 sprints de 1 semana** (ajustar datas conforme o
calendário real da disciplina). Cada sprint entrega algo demonstrável,
priorizando sempre o RF de maior valor primeiro (regra: sempre ter um
fluxo ponta-a-ponta funcionando, mesmo que simplificado, desde o Sprint 2).

## Sprint 0 — Preparação (opcional, antes do início oficial)
**Objetivo:** alinhar escopo e ambiente.
- Definir stack final (linguagem, framework de chat, LLM a usar).
- Criar repositório e estrutura de pastas.
- Escrever os documentos de planejamento e requisitos (este material).

**Entrega:** repositório inicializado + docs de planejamento/requisitos.

---

## Sprint 1 — Scraping e extração de estratégias
**Objetivo:** conseguir transformar um link de concorrente em uma lista de
estratégias qualitativas.
- RF01 — receber link do concorrente via chat.
- RF02 — scraping do conteúdo textual da página.
- RF14 — fallback: entrada manual de texto se o scraping falhar.
- RF03 — prompt de extração de estratégias via LLM, com justificativa
  baseada em trechos do texto.

**Entrega:** dado um link, o sistema retorna uma lista de estratégias
prováveis do concorrente com trecho de evidência.

**Critério de pronto:** testado com 3 sites reais de concorrentes de saúde
digital.

---

## Sprint 2 — Modelagem do jogo e payoffs
**Objetivo:** montar a matriz de payoff, com as duas formas de entrada.
- RF04 — usuário informa suas próprias estratégias.
- RF05 — montagem da matriz (2 jogadores x N estratégias, começando 2x2).
- RF06 — escolha entre payoff heurístico automático ou valor manual.
- RF11 — marcação visual de quais payoffs são heurísticos vs. reais.
- RD02 — definição e documentação da escala heurística.

**Entrega:** dado o resultado do Sprint 1 + estratégias do usuário, o
sistema gera e exibe a matriz de payoff completa.

**Critério de pronto:** matriz gerada corretamente nos dois modos (heurístico
e manual) e exibida de forma legível (RF10).

---

## Sprint 3 — Solver de teoria dos jogos
**Objetivo:** calcular o resultado estratégico da matriz.
- RF07 — cálculo de estratégia(s) dominante(s).
- RF08 — cálculo de equilíbrio(s) de Nash em estratégia pura.
- Testes com matrizes de referência conhecidas da literatura (dilema do
  prisioneiro, jogo de entrada) para validar o solver.

**Entrega:** dada uma matriz de payoff, o sistema retorna corretamente
estratégia dominante (se houver) e equilíbrio(s) de Nash.

**Critério de pronto:** solver validado contra pelo menos 3 exemplos
clássicos com resultado conhecido.

---

## Sprint 4 — Recomendação e integração ponta-a-ponta
**Objetivo:** fechar o fluxo completo com explicação em linguagem natural.
- RF09 — geração da recomendação textual final via LLM, a partir do
  resultado do solver.
- RNF02 — reforço de transparência sobre heurística vs. dado real na
  recomendação.
- RNF06 — revisão de linguagem para usuário leigo em teoria dos jogos.
- Integração de todo o pipeline: link → estratégias → matriz → solver →
  recomendação, tudo dentro da interface de chat.

**Entrega:** fluxo completo funcional de ponta a ponta, demonstrável com o
caso de uso de saúde digital.

**Critério de pronto:** um usuário consegue, sem intervenção manual no
código, ir do link do concorrente até a recomendação final.

---

## Sprint 5 — Polimento, testes e apresentação
**Objetivo:** estabilizar e preparar entrega/apresentação.
- RF12 — permitir refazer análise com novos payoffs sem repetir scraping.
- RF13 — histórico simples de análises (se houver tempo).
- Testes end-to-end com o caso real de saúde digital da empreendedora.
- Ajustes de UI/UX do chat.
- Preparação de roteiro de demonstração/apresentação para a disciplina.

**Entrega:** versão final estável + roteiro de demo.

---

## Backlog (pós-entrega / fora do prazo da disciplina)
- Jogos sequenciais (árvore de decisão / jogos de Stackelberg).
- Suporte a mais de 2 jogadores no mesmo jogo.
- Equilíbrio de Nash em estratégias mistas.
- Scraping de sites dinâmicos (JS-heavy).
- Módulo de aprendizado de payoffs a partir de dados históricos reais.
