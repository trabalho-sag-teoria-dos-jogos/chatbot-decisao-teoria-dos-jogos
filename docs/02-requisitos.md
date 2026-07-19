# Documento de Requisitos

## 1. Requisitos Funcionais (RF)

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | O sistema deve permitir que o usuário informe, via chat, o link de uma ou mais páginas de concorrentes. | Alta |
| RF02 | O sistema deve coletar (scraping) o conteúdo textual das páginas informadas. | Alta |
| RF03 | O sistema deve extrair, via LLM, possíveis estratégias competitivas do concorrente a partir do texto coletado. | Alta |
| RF04 | O sistema deve permitir que o usuário informe suas próprias estratégias possíveis (ex.: preço baixo, diferenciação, nicho). | Alta |
| RF05 | O sistema deve montar uma matriz de payoff (jogo estratégico 2x2 ou maior) com base nas estratégias identificadas. | Alta |
| RF06 | O sistema deve oferecer ao usuário a escolha entre **payoff heurístico automático** ou **inserção manual de valor real** para cada célula da matriz. | Alta |
| RF07 | O sistema deve calcular estratégia(s) dominante(s), quando existir(em). | Alta |
| RF08 | O sistema deve calcular o(s) equilíbrio(s) de Nash em estratégia pura da matriz montada. | Alta |
| RF09 | O sistema deve apresentar ao usuário uma recomendação em linguagem natural, explicando o raciocínio por trás do resultado. A resposta deve nomear explicitamente qual(is) conceito(s) de Teoria dos Jogos foi(ram) usado(s) para chegar à recomendação (ex.: "estratégia dominante", "equilíbrio de Nash em estratégia pura") e explicar em termos simples o que esse conceito significa, para que o usuário entenda o "porquê" e não apenas o resultado. | Alta |
| RF10 | O sistema deve exibir a matriz de payoff de forma visual/tabular na conversa. | Média |
| RF11 | O sistema deve indicar claramente ao usuário quando um payoff é heurístico (estimado) vs. inserido manualmente. | Alta |
| RF12 | O sistema deve permitir editar/refazer a análise com novos valores de payoff sem repetir o scraping. | Média |
| RF13 | O sistema deve salvar o histórico de análises realizadas pelo usuário. | Baixa |
| RF14 | O sistema deve tratar falhas de scraping (site indisponível, bloqueio) oferecendo alternativas: entrada manual de texto ou envio de um print (imagem) da página do concorrente, interpretado por um modelo de visão. | Média |

## 2. Requisitos Não Funcionais (RNF)

| ID | Requisito | Categoria |
|---|---|---|
| RNF01 | O tempo de resposta entre o envio dos links e a apresentação da matriz de estratégias não deve ultrapassar ~30s em condições normais. | Desempenho |
| RNF02 | O sistema deve deixar explícito, em toda recomendação, que os payoffs heurísticos são estimativas e não dados de mercado reais. | Transparência |
| RNF03 | O sistema deve funcionar com no mínimo Python 3.10+. | Compatibilidade |
| RNF04 | As chaves de API (LLM) não devem ser expostas no código-fonte (uso de variáveis de ambiente). | Segurança |
| RNF05 | O sistema deve respeitar `robots.txt` e não sobrecarregar os sites dos concorrentes (rate limiting simples). | Ética/Legal |
| RNF06 | A interface deve ser utilizável por alguém sem conhecimento prévio de teoria dos jogos (linguagem acessível nas explicações). | Usabilidade |
| RNF07 | O código deve ser modular, separando claramente: scraping, extração via LLM, heurística de payoff, solver de jogos e geração de resposta. | Manutenibilidade |
| RNF08 | O sistema deve deixar claro, na interface e nas recomendações, que a análise se limita ao aspecto de estratégia competitiva (Teoria dos Jogos) e não constitui avaliação de viabilidade financeira, operacional ou de mercado do negócio como um todo. | Transparência |

## 3. Requisitos de Dados

| ID | Requisito |
|---|---|
| RD01 | Entrada mínima: link(s) do(s) concorrente(s) e ao menos 2 estratégias por jogador. |
| RD02 | Payoffs, quando manuais, devem ser numéricos (inteiros ou decimais); quando heurísticos, devem seguir escala ordinal fixa e documentada (ex.: 1 a 3). |
| RD03 | O texto extraído do scraping deve ser armazenado (ao menos temporariamente) para permitir auditoria da estratégia sugerida pelo LLM. |

## 4. Restrições

- Prazo limitado ao cronograma da disciplina de Sistemas de Apoio à Gestão (ver `03-sprints.md`).
- Sem tempo hábil para pesquisa/estimação de payoffs reais de mercado — por isso a heurística é parte central do requisito, não um extra.
- Escopo inicial restrito a jogos simultâneos de 2 jogadores (ver seção "Fora de Escopo" do documento de planejamento).

## 5. Critérios de Aceite (nível de projeto)

- Dado um link de concorrente válido, o sistema extrai ao menos 2 estratégias plausíveis com justificativa textual.
- Dada uma matriz de payoff (heurística ou manual), o sistema retorna corretamente a estratégia dominante e/ou o equilíbrio de Nash correspondente (validável manualmente com exemplos de referência de teoria dos jogos).
- A recomendação final é compreensível por alguém sem formação em teoria dos jogos e nomeia explicitamente o conceito de teoria dos jogos utilizado (RF09).
- A interface e a recomendação deixam claro que o escopo da análise é estratégico/competitivo, não uma avaliação de viabilidade geral do negócio (RNF08).
