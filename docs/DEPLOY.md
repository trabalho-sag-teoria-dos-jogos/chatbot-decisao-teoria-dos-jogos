# Guia de Deploy — Render

> **Nota de histórico:** este guia originalmente indicava o Hugging Face
> Spaces. Ao tentar seguir os passos, a dupla descobriu que o SDK Docker do
> Hugging Face passou a exigir cadastro de pagamento em contas novas
> (mudança recente da plataforma — o nível "CPU Basic" gratuito deixou de
> estar disponível para o SDK Docker sem forma de pagamento cadastrada).
> Como alternativa 100% gratuita, sem cartão de crédito, migramos o guia
> para o **Render**, que também builda direto do `Dockerfile` do
> repositório sem exigir nenhuma mudança de código.

## O que já está pronto no repositório

- `Dockerfile` — builda a aplicação e escuta na porta definida pela
  variável de ambiente `PORT` (o Render injeta essa variável
  automaticamente; localmente cai no fallback `7860`).
- `requirements.txt` — todas as dependências Python.
- `app.py` + `src/gamebot/` — o código da aplicação.
- `.chainlit/config.toml` + `public/` — identidade visual.
- Repositório já publicado no GitHub:
  `https://github.com/CeciliaaPaiva/chatbot-teoriadosjogos`.

O único item que falta é específico de cada pessoa/conta: a **chave da
Groq API**, que nunca deve ir para o repositório.

## Passo a passo

### 1. Criar uma conta no Render

Acesse https://dashboard.render.com/register e crie uma conta — pode
entrar direto com a conta do GitHub (facilita o passo 3). **Não é pedido
cartão de crédito** para o tier gratuito.

### 2. Criar um novo Web Service

1. No dashboard, clique em **New** → **Web Service**.
2. Escolha **Build and deploy from a Git repository** e conecte a conta
   do GitHub (autorize o Render a acessar o repositório
   `chatbot-teoriadosjogos`).
3. Selecione o repositório na lista.

### 3. Configurar o serviço

Na tela de configuração:

- **Name:** por exemplo `consultor-teoria-dos-jogos`.
- **Region:** qualquer uma (ex.: Oregon ou a mais próxima do Brasil
  disponível).
- **Branch:** `main`.
- **Runtime:** o Render detecta automaticamente o `Dockerfile` na raiz do
  repositório — confirme que a opção **Docker** está selecionada (não
  "Python" nativo, pois queremos usar exatamente o mesmo Dockerfile já
  testado localmente).
- **Instance Type:** selecione **Free**.

### 4. Configurar a chave da Groq API como variável de ambiente

**Nunca** coloque a chave da Groq num arquivo do repositório (nem mesmo
`.env`, que já está no `.gitignore`).

Ainda na tela de criação do serviço (ou depois, em **Environment**):

1. Clique em **Add Environment Variable**.
2. Nome: `GROQ_API_KEY`. Valor: a chave atual da Groq (a chave que
   circulou antes em texto puro já foi tratada como comprometida — se
   ainda não geraram uma nova, façam isso em
   https://console.groq.com/keys antes de colar aqui).
3. (Opcional) Adicionem também `GROQ_MODEL` e `GROQ_MODEL_FALLBACK` se
   quiserem trocar os modelos padrão sem alterar código.

### 5. Criar o serviço e aguardar o build

Clique em **Create Web Service**. O Render vai clonar o repositório,
buildar a imagem a partir do `Dockerfile` e subir o container. Acompanhem
o progresso na aba **Logs** — o primeiro build costuma levar de 3 a 6
minutos.

Quando o status virar **Live**, o site estará disponível em uma URL como:

```
https://consultor-teoria-dos-jogos.onrender.com
```

### 6. Importante: "sono" do serviço gratuito

O tier gratuito do Render **hiberna o serviço após ~15 minutos sem
acesso**. O próximo acesso após esse período demora cerca de 1 minuto
para "acordar" o container — isso é esperado, não é bug.

**Antes da apresentação:** abram o link do site uns 5 minutos antes de
começar, para garantir que o container já esteja "acordado" quando a
professora for testar ao vivo.

**Plano B de segurança para o dia da apresentação:** tenham também a
aplicação rodando localmente (`chainlit run app.py`) como alternativa,
caso a internet da sala falhe ou o Render esteja instável — nesse caso é
só compartilhar a tela do computador com o `localhost:8000` aberto.

### 7. Testar o fluxo completo no ambiente publicado

Antes da apresentação, testem no link público (não só localmente):

1. Enviar um link de concorrente real.
2. Confirmar que a extração de estratégias funciona.
3. Informar estratégias próprias e escolher o modo heurístico.
4. Conferir se a matriz e a recomendação final aparecem corretamente.

### 8. Se algo der errado

- **Build falha:** confiram a aba "Logs" — geralmente é erro de
  dependência no `requirements.txt` ou de sintaxe no `Dockerfile`.
- **App sobe mas dá erro de "GROQ_API_KEY não configurada":** a variável
  de ambiente não foi salva corretamente — revisem o passo 4 em
  **Environment** no painel do serviço.
- **Deploy não atualiza depois de um novo `git push`:** confirmem que o
  **Auto-Deploy** está habilitado nas configurações do serviço (fica
  ligado por padrão ao conectar via GitHub).

## Segurança

- Usem sempre uma chave da Groq **nova** como variável de ambiente do
  Render — nunca a chave que já foi exposta em texto puro no histórico
  desta conversa.
- Nunca commitem o arquivo `.env` nem qualquer chave diretamente em
  código — o `.gitignore` do projeto já bloqueia o `.env`, mas vale
  sempre conferir com `git status` antes de um `git push`.
