# Consultor de Estratégia Competitiva — Teoria dos Jogos

Chatbot de apoio à decisão gerencial, desenvolvido para a disciplina
**Sistemas de Apoio à Gestão** (curso de Sistemas de Informação), sobre o
tema sorteado **Teoria dos Jogos**.

O sistema ajuda um gestor/empreendedor a decidir **qual estratégia
competitiva adotar frente a um concorrente específico**, formalizando a
decisão como um jogo estratégico simultâneo de 2 jogadores e aplicando
conceitos de Teoria dos Jogos — **estratégia dominante** e **equilíbrio de
Nash** — para chegar a uma recomendação.

> **Escopo importante:** este sistema é um **consultor de estratégia
> competitiva**, não um avaliador de viabilidade de negócio. Ele responde
> "dado que você vai competir com este concorrente, qual estratégia
> adotar?" — e não avalia viabilidade financeira, operacional ou de
> mercado do negócio como um todo. Ver `docs/01-planejamento-implementacao.md`.

Caso de uso motivador: entrada em um mercado de **saúde digital**,
avaliando concorrentes já estabelecidos (ex.: telemedicina, prontuário
eletrônico).

## Documentação do projeto

- [`docs/01-planejamento-implementacao.md`](docs/01-planejamento-implementacao.md) — visão geral, fluxo funcional, decisões de escopo e arquitetura técnica.
- [`docs/02-requisitos.md`](docs/02-requisitos.md) — requisitos funcionais, não funcionais, de dados e critérios de aceite.
- [`docs/03-sprints.md`](docs/03-sprints.md) — planejamento de sprints.
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — passo a passo de deploy no Render.
- [`releases-sprints/`](releases-sprints/) — um documento de release por sprint concluída, relatando o que foi entregue.

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Interface + orquestração | [Chainlit](https://docs.chainlit.io/) (Python) — chat web monolítico, sem backend separado |
| Coleta de dados | `requests` + `BeautifulSoup` |
| Extração de estratégias / recomendação final | Groq API, modelo `llama-3.3-70b-versatile` (fallback `llama-3.1-8b-instant`) |
| Solver de teoria dos jogos | Módulo Python próprio (determinístico), validado em testes com `nashpy` |
| Persistência (opcional) | SQLite |
| Deploy | Render (Web Service via Docker) |

O LLM é usado **apenas** para interpretar texto (extração de estratégias) e
redigir a explicação final. O cálculo de teoria dos jogos em si (estratégia
dominante / equilíbrio de Nash) é sempre feito de forma determinística pelo
módulo próprio — nunca delegado ao LLM.

## Pré-requisitos

- Python 3.10 ou superior (testado com 3.12).
- Uma chave de API da [Groq](https://console.groq.com/) (gratuita).

## Como configurar o ambiente

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows (Git Bash):
   source .venv/Scripts/activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Copie o arquivo de exemplo de variáveis de ambiente e preencha sua chave:

   ```bash
   cp .env.example .env
   ```

   Edite `.env` e substitua `your_groq_api_key_here` pela sua chave da
   Groq. **Nunca** commite o arquivo `.env` (ele já está no
   `.gitignore`).

## Como rodar localmente

```bash
chainlit run app.py
```

A aplicação sobe em `http://localhost:8000`.

## Como usar o chatbot (passo a passo)

1. **Envie o link de um concorrente.** Cole a URL de uma página pública do
   concorrente que você quer analisar (ex.: a home de um site de
   telemedicina).
   - Se o sistema não conseguir coletar o conteúdo automaticamente
     (bloqueio, site dependente de JavaScript, etc.), ele vai pedir que
     você **cole manualmente** um trecho de texto do site.
2. **Confira as estratégias identificadas.** O sistema extrai, via LLM,
   entre 2 e 4 estratégias prováveis do concorrente, cada uma com um
   trecho do texto original como evidência.
3. **Informe suas próprias estratégias.** Descreva, em texto livre,
   pelo menos 2 estratégias possíveis para o seu negócio — o sistema usa
   o LLM para identificar cada estratégia mencionada, mesmo que você
   escreva tudo em uma frase só.
4. **Escolha como definir os payoffs da matriz:**
   - **Heurística automática**: o sistema estima os payoffs (escala 1 a 3)
     a partir da categoria de cada estratégia — é uma estimativa, não um
     dado real de mercado, e isso fica explícito na resposta.
   - **Valor manual**: você informa, célula a célula, o payoff real (seu e
     do concorrente) no formato `seu_valor,valor_do_concorrente` (ex.:
     `3,2`).
5. **Veja a matriz de payoff** montada e exibida em formato de tabela, com
   cada célula marcada como heurística ou manual.
6. **Receba a recomendação final**, que nomeia explicitamente o conceito
   de Teoria dos Jogos utilizado (estratégia dominante e/ou equilíbrio de
   Nash) e explica o raciocínio em linguagem acessível.
7. Você pode enviar um **novo link de concorrente** a qualquer momento
   para repetir a análise com outro jogo.

## Estrutura do projeto

```
.
├── app.py                     # Ponto de entrada Chainlit (fluxo de chat)
├── src/gamebot/
│   ├── config.py               # Carregamento de variáveis de ambiente
│   ├── scraping.py             # Coleta de conteúdo (RF02, RF14, RNF05)
│   ├── llm.py                  # Integração com Groq/Llama 3 (RF03, RF09)
│   ├── payoff.py                # Modelagem do jogo e matriz de payoff (RF04-RF06, RF10-RF11)
│   └── solver.py                # Estratégia dominante / equilíbrio de Nash (RF07-RF08)
├── tests/                      # Testes automatizados (pytest)
├── docs/                       # Planejamento, requisitos e sprints
├── releases-sprints/           # Um release .md por sprint concluída
└── requirements.txt
```

## Testes

```bash
pytest
```

Os testes do solver validam o resultado contra exemplos clássicos da
literatura de Teoria dos Jogos (ex.: dilema do prisioneiro).

## Autoria

Trabalho desenvolvido em dupla para a disciplina Sistemas de Apoio à
Gestão — Sistemas de Informação.
