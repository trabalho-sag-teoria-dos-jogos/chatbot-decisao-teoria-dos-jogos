# Planejamento de Implementação

## 1. Visão Geral

Chatbot de apoio à decisão gerencial que aplica **Teoria dos Jogos** para
recomendar estratégias de entrada e competição de mercado. O usuário
(gestor/empreendedor) informa os links das páginas dos concorrentes; o
sistema mapeia as estratégias prováveis de cada concorrente, monta um jogo
(matriz de payoff) e recomenda a melhor estratégia com base em conceitos
como estratégia dominante e equilíbrio de Nash.

Caso de uso motivador: entrada em um mercado de **saúde digital**, avaliando
concorrentes já estabelecidos (ex.: telemedicina, prontuário eletrônico).

**Delimitação importante:** o sistema é um **consultor de estratégia
competitiva**, não um avaliador de viabilidade de negócio. Ele assume que o
usuário já decidiu entrar no mercado e responde apenas "dado que vou
competir com estes concorrentes, qual estratégia devo adotar frente às
reações prováveis deles?". O sistema **não** avalia viabilidade financeira,
operacional ou de mercado do negócio como um todo — ver RNF08 em
`02-requisitos.md`.

## 2. Problema e Justificativa

Decisões de entrada/competição em mercado são frequentemente tomadas de
forma intuitiva, sem estruturação formal dos cenários e das reações
prováveis dos concorrentes. Um Sistema de Apoio à Gestão que formaliza essas
decisões como um jogo estratégico ajuda o gestor a visualizar
trade-offs e evitar decisões dominadas (piores em qualquer cenário).

## 3. Fluxo Funcional (alto nível)

```
Usuário informa:
  - Sua empresa/estratégias possíveis
  - Links dos concorrentes
        │
        ▼
[1] Coleta (scraping) do conteúdo das páginas dos concorrentes
        │
        ▼
[2] Extração de estratégias qualitativas (via LLM)
    ex.: "foco em baixo custo", "diferenciação por tecnologia",
         "nicho corporativo"
        │
        ▼
[3] Estruturação do jogo
    - Jogadores: usuário x concorrente(s)
    - Estratégias: extraídas no passo 2 (+ as do usuário)
    - Payoffs: heurística automática OU valor real inserido pelo usuário
        │
        ▼
[4] Solver de teoria dos jogos
    - Estratégia dominante (se existir)
    - Equilíbrio de Nash (puro; misto como extra se houver tempo)
        │
        ▼
[5] Chatbot traduz o resultado em recomendação textual,
    explicando o raciocínio
```

## 4. Decisões de Escopo (importantes para viabilidade)

- **Payoffs não são extraídos do site do concorrente.** Um site não revela
  números de lucro/market share. O sistema oferece duas opções ao usuário:
  1. **Heurística simples**: valores ordinais/relativos (ex.: alto=3,
     médio=2, baixo=1) atribuídos a partir de sinais textuais encontrados
     na página (preço mencionado, porte da empresa, funcionalidades,
     posicionamento de marketing).
  2. **Valor real inserido pelo usuário**: campo aberto para o gestor
     inserir números concretos quando tiver essa informação.
  - Isso deve ficar **explícito na interface**, sem prometer precisão que
    o sistema não tem.
- O jogo é modelado como **jogo estratégico simultâneo de 2 jogadores**
  (você x 1 concorrente por vez) para manter o escopo tratável no prazo da
  disciplina. Múltiplos concorrentes podem ser analisados em jogos
  separados (par a par) numa primeira versão.
- Scraping se limita a páginas públicas simples (HTML estático). Sites que
  exigem login/JS pesado ficam fora do escopo inicial.

## 5. Arquitetura Técnica

**Decisão de stack (definida em conjunto com a dupla):** aplicação **Python
monolítica** — sem backend/API separado — construída sobre **Chainlit**, que
já entrega a interface de chat web (site com URL pública) e suporta exibir
o raciocínio em etapas (scraping → extração → matriz → solver →
recomendação) e tabelas/elementos ricos (matriz de payoff) direto na
conversa. Essa escolha evita a complexidade de manter frontend e backend
separados (CORS, API REST, dois deploys), que não agrega valor aos
requisitos funcionais da disciplina.

| Camada | Tecnologia definida | Responsabilidade |
|---|---|---|
| Interface + orquestração | **Chainlit** (Python) | Chat web, coleta de links/payoffs, exibição da matriz e do raciocínio em etapas, tudo no mesmo processo (sem API separada) |
| Coleta de dados | `requests` + `BeautifulSoup` | Baixa e limpa o HTML das páginas dos concorrentes |
| Extração de estratégias | LLM (**Groq API, `llama-3.3-70b-versatile`**, fallback `llama-3.1-8b-instant`) | Interpreta o texto extraído e sugere estratégias prováveis |
| Heurística de payoff | Módulo Python próprio | Converte sinais textuais em valores ordinais |
| Solver de jogos | Módulo Python próprio (estratégia dominante + Nash puro), implementado pela dupla — **cálculo 100% determinístico, nunca delegado ao LLM** | Calcula estratégia dominante / equilíbrio de Nash |
| Validação do solver | `nashpy` (uso restrito a testes) | Confere, em testes automatizados, se o solver próprio bate com uma biblioteca de referência — não roda em produção |
| Explicação | LLM (**Groq API, `llama-3.3-70b-versatile`**) | Gera a recomendação final em linguagem natural a partir do resultado já calculado pelo solver, nomeando o conceito de teoria dos jogos usado (RF09) |
| Persistência | SQLite (opcional, RF13) | Histórico de análises do usuário |
| Deploy | **Render** (Web Service via Docker) | Hospedagem gratuita do site, com URL pública para demo/apresentação — substituiu o Hugging Face Spaces, cujo SDK Docker deixou de ter tier gratuito para contas novas |

## 6. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Sites de concorrentes bloqueiam scraping ou exigem JS | Fallback: usuário cola o texto manualmente |
| LLM "alucina" estratégias sem base no texto real | Prompt restrito ao conteúdo extraído; pedir citação do trecho que embasa cada estratégia |
| Payoffs heurísticos parecerem arbitrários | Deixar critério da heurística visível/transparente na resposta |
| Escopo grande para o prazo da disciplina | Priorizar jogo 2x2 simultâneo antes de qualquer extensão (N jogadores, jogos sequenciais, sinalização) |

## 7. Fora de Escopo (v1)

- Jogos sequenciais (árvore de decisão) e jogos de sinalização.
- Mais de 2 jogadores simultâneos no mesmo jogo.
- Scraping de sites com autenticação ou fortemente dependentes de JS.
- Machine learning para prever payoffs a partir de dados históricos.
