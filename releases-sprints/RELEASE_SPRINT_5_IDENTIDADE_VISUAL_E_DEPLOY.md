# Release — Sprint 5: Identidade Visual, Deploy e Documentação Final

**Data:** 2026-07-19
**Sprint:** 5 de 5
**Status:** Concluído

## Objetivo do Sprint

Aplicar a identidade visual definida com a dupla ("tabuleiro estratégico
corporativo"), preparar o deploy em uma plataforma gratuita e finalizar a
documentação do projeto.

## O que foi feito

- Foi validada com a dupla, antes da implementação, a direção visual a
  ser aplicada: paleta grafite/azul-marinho com acento verde-esmeralda,
  grid sutil remetendo à matriz de payoff, ícone de peça de xadrez (torre)
  como identidade do bot, e tipografia serifada nos títulos para reforçar
  o tom formal de consultoria de negócios.
- Foi investigada a estrutura interna do bundle do Chainlit para
  identificar as variáveis CSS reais usadas pelo tema (`--background`,
  `--primary`, `--card`, etc., em formato HSL), permitindo uma
  customização de tema precisa em vez de tentativa e erro.
- Foi criado `public/style.css`, sobrescrevendo a paleta clara e escura do
  Chainlit com as cores definidas, e adicionando um padrão de grid sutil
  no cabeçalho.
- Foram criados os ícones da identidade visual em SVG
  (`public/favicon.svg`, `public/logo_dark.svg`, `public/logo_light.svg`),
  em formato de peça de torre/tabuleiro.
- O `.chainlit/config.toml` foi ajustado: nome do assistente, tema escuro
  como padrão, descrição e referência ao CSS customizado.
- Foi corrigido o `.gitignore`, que originalmente excluía toda a pasta
  `.chainlit/` — isso teria feito a configuração de tema/identidade visual
  não ser versionada. Passou a excluir apenas a subpasta de traduções
  geradas automaticamente.
- O `chainlit.md` (painel de boas-vindas) foi reescrito com a descrição
  formal do sistema, reforçando o escopo (estratégia competitiva, não
  viabilidade geral do negócio).
- Foi validado, via requisições HTTP diretas ao servidor local, que o CSS
  customizado, o favicon e o logo estão sendo servidos corretamente pelo
  Chainlit.
- Foi criado o `Dockerfile` do projeto, inicialmente seguindo o padrão de
  Spaces do tipo Docker na Hugging Face (porta `7860`).
- Foi criado `docs/DEPLOY.md`, um guia passo a passo para a dupla realizar
  o deploy por conta própria.
- **Correção de rota durante o sprint:** ao seguir o guia inicial, a
  dupla constatou que o SDK Docker do Hugging Face Spaces havia deixado
  de oferecer o tier gratuito ("CPU Basic") para contas novas, passando a
  exigir cadastro de pagamento — mudança recente da plataforma, não
  prevista no planejamento original. Diante disso, o `Dockerfile` foi
  ajustado para escutar na porta definida pela variável de ambiente
  `PORT` (compatível com múltiplas plataformas) e o `docs/DEPLOY.md` foi
  reescrito para o **Render**, que oferece Web Service gratuito via
  Docker sem exigir cartão de crédito, sem qualquer outra mudança de
  código necessária. O guia final cobre: criação de conta, conexão do
  repositório GitHub já existente, configuração da chave da Groq como
  variável de ambiente (nunca em arquivo versionado), e um alerta sobre a
  hibernação do serviço gratuito após inatividade — com orientação de
  "aquecer" o link alguns minutos antes da apresentação.
- Foi criado o `README.md` do projeto (registrado já no Sprint 2), agora
  também referenciando o guia de deploy.
- A suíte de testes automatizados foi executada novamente após todas as
  mudanças do sprint, permanecendo 100% passando (4/4).

## Requisitos atendidos neste sprint

Consolidação final de RNF06 (usabilidade/identidade visual coerente com o
domínio) e preparação de infraestrutura para a entrega/apresentação
(critério de pronto do Sprint 5 do planejamento original).

## Riscos observados e decisões tomadas

- Não foi possível validar o `Dockerfile` com um build local completo
  porque o Docker Desktop não estava em execução neste ambiente. A
  validação ficou por inspeção do Dockerfile e pelas convenções
  documentadas do Chainlit/Render; o build real acontece no servidor do
  Render durante o deploy — o `docs/DEPLOY.md` já orienta a dupla a
  acompanhar os logs desse build e reagir a eventuais erros.
- A escolha inicial de plataforma de deploy (Hugging Face Spaces) revelou
  uma mudança de política da própria plataforma apenas na hora de
  executar o passo a passo — um lembrete de que decisões de
  infraestrutura em serviços de terceiros devem ser validadas o mais
  próximo possível do momento de uso, não só no planejamento. A resposta
  foi rápida porque a arquitetura (Docker + variável de porta) já era
  portável entre plataformas.
- O deploy efetivo no Render depende de uma conta e de uma chave da Groq
  API válida (a chave anterior, compartilhada em texto puro no chat, já
  foi revogada e substituída) — por decisão conjunta com a dupla, essa
  etapa fica para ser executada por eles mesmos, seguindo o guia criado,
  como parte do aprendizado do processo.

## Estado final do projeto

Ao final deste sprint, o pipeline completo está funcional localmente:
link do concorrente → scraping/fallback manual → extração de estratégias
via LLM → estratégias do usuário → matriz de payoff (heurística ou
manual) → solver determinístico → recomendação final em linguagem
natural, tudo dentro de uma única interface de chat com identidade visual
própria, documentação de planejamento/requisitos/sprints atualizada, um
release por sprint, e um guia de deploy pronto para uso.
