# Release — Sprint 1: Scraping e Extração de Estratégias

**Data:** 2026-07-19
**Sprint:** 1 de 5
**Status:** Concluído

## Objetivo do Sprint

Transformar o link de um concorrente em uma lista de estratégias
competitivas qualitativas, com evidência textual, dentro de uma interface
de chat funcional.

## O que foi feito

- Foi definida e criada a estrutura inicial do projeto (`src/gamebot/`,
  `tests/`, `releases-sprints/`, `public/`), junto com `.gitignore`,
  `.env.example` e `requirements.txt`.
- Foi criado o módulo `config.py`, responsável por carregar a chave da
  Groq API e os nomes dos modelos a partir de variáveis de ambiente
  (`.env`), sem expor segredos no código-fonte (RNF04).
- Foi implementado o módulo `scraping.py`, que:
  - Validou a URL informada e verificou permissão de coleta consultando o
    `robots.txt` do domínio antes de acessar a página (RNF05).
  - Aplicou um intervalo mínimo entre requisições para não sobrecarregar
    os sites dos concorrentes (RNF05).
  - Baixou e limpou o HTML com `requests` + `BeautifulSoup`, removendo
    scripts, estilos e elementos de navegação/rodapé, retornando apenas o
    texto visível (RF02).
  - Levantou uma exceção específica (`ScrapingError`) em qualquer falha
    (rede, bloqueio por robots.txt, página sem texto legível), permitindo
    que a camada de chat oferecesse a entrada manual como alternativa
    (RF14).
- Foi implementado o módulo `llm.py`, integrando com a **Groq API**
  (modelo `llama-3.3-70b-versatile`, com fallback automático para
  `llama-3.1-8b-instant` em caso de falha):
  - Foi escrito um prompt restrito ao texto efetivamente coletado,
    exigindo que cada estratégia identificada viesse acompanhada de um
    trecho literal do texto como evidência — mitigação direta do risco de
    alucinação do LLM documentado no planejamento (RF03).
  - A resposta do modelo foi forçada a JSON estruturado (`response_format:
    json_object`) para facilitar o parsing confiável.
  - Foi reforçado, em comentário no código, que o LLM é usado somente para
    tarefas de interpretação/redação de texto — o cálculo de teoria dos
    jogos (Sprint 3) é e continuará sendo feito por um módulo determinístico
    separado.
- Foi construída a primeira versão da interface de chat com **Chainlit**
  (`app.py`), cobrindo o fluxo de ponta a ponta deste sprint:
  - O usuário foi recebido com uma mensagem de boas-vindas que já deixa
    explícito o escopo do sistema (consultor de estratégia competitiva,
    não avaliador de viabilidade geral do negócio).
  - O usuário pôde enviar o link de um concorrente pelo chat (RF01).
  - As etapas de coleta e extração foram exibidas como *Steps* visíveis na
    conversa, mostrando o que o sistema está fazendo em cada momento.
  - As estratégias extraídas foram exibidas com o trecho de evidência
    correspondente.
  - Foi implementado o fluxo de fallback: quando o scraping falhou, o
    sistema pediu ao usuário que colasse manualmente um trecho de texto do
    site do concorrente, e a extração seguiu normalmente a partir desse
    texto (RF14).
- Foram feitos testes manuais de fumaça (smoke tests) confirmando que:
  - A extração via Groq retornou estratégias plausíveis com evidência a
    partir de um texto sintético.
  - O scraping funcionou corretamente contra um site real do domínio de
    saúde digital.
  - A aplicação Chainlit subiu sem erros de inicialização.

## Requisitos atendidos neste sprint

RF01, RF02, RF03, RF14, RNF04, RNF05 (parcial — modularidade completa do
RNF07 será consolidada conforme os próximos módulos forem adicionados).

## Riscos observados

- A qualidade da extração depende da qualidade do texto coletado; páginas
  fortemente dependentes de JavaScript continuam fora do escopo (conforme
  já previsto em "Fora de Escopo v1").
- A chave de API usada durante o desenvolvimento foi compartilhada em
  texto plano em um canal de conversa; foi recomendado à dupla revogá-la e
  gerar uma nova antes da apresentação.

## Próximos passos (Sprint 2)

Coletar as estratégias da própria empresa do usuário, montar a matriz de
payoff (heurística ou manual) e exibi-la de forma tabular na conversa.
