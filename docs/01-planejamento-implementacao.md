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

| Camada | Tecnologia sugerida | Responsabilidade |
|---|---|---|
| Interface | Chat web simples (Streamlit ou frontend leve) | Conversa com o usuário, coleta de links e payoffs |
| Backend/API | Python (FastAPI) | Orquestra o fluxo, expõe endpoints |
| Coleta de dados | `requests` + `BeautifulSoup` | Baixa e limpa o HTML das páginas dos concorrentes |
| Extração de estratégias | LLM (API Claude) | Interpreta o texto extraído e sugere estratégias prováveis |
| Heurística de payoff | Módulo Python próprio | Converte sinais textuais em valores ordinais |
| Solver de jogos | Módulo Python próprio (ou `nashpy`) | Calcula estratégia dominante / equilíbrio de Nash |
| Explicação | LLM (API Claude) | Gera a recomendação final em linguagem natural |
| Persistência | SQLite (opcional) | Histórico de análises do usuário |

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
