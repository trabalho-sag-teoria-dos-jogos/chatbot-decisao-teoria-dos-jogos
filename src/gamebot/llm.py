"""Integração com o LLM (Groq / Llama 3) para extração de estratégias e
redação da recomendação final (RF03, RF09).

Importante: o LLM nunca calcula estratégia dominante ou equilíbrio de Nash.
Esse cálculo é feito de forma determinística pelo módulo `solver.py`. O LLM
só interpreta texto (extração) e redige texto (explicação) — ver RNF07 e a
mitigação de risco de alucinação documentada em
`docs/01-planejamento-implementacao.md`.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from groq import Groq

from . import config
from .payoff import Game
from .solver import DominantStrategyResult

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.require_groq_api_key())
    return _client


@dataclass
class StrategyCandidate:
    strategy: str
    evidence: str


EXTRACTION_SYSTEM_PROMPT = """\
Você é um analista de estratégia competitiva. Você recebe um trecho de texto
extraído do site de uma empresa concorrente e deve identificar possíveis
estratégias competitivas dessa empresa.

Regras estritas:
- Baseie-se SOMENTE no texto fornecido. Não invente informação que não
  esteja no texto.
- Para cada estratégia identificada, cite um trecho literal do texto
  (evidence) que embasa essa conclusão.
- Identifique entre 2 e 4 estratégias.
- Responda em português do Brasil.
- Responda EXCLUSIVAMENTE em JSON válido, no formato:
  {"strategies": [{"strategy": "nome curto da estratégia", "evidence": "trecho literal do texto"}]}
"""


def _chat_json(system_prompt: str, user_prompt: str) -> dict:
    client = _get_client()
    models_to_try = [config.GROQ_MODEL, config.GROQ_MODEL_FALLBACK]
    last_error: Exception | None = None
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001 - queremos tentar o fallback
            last_error = exc
            continue
    raise RuntimeError(
        f"Falha ao consultar o LLM (Groq) em todos os modelos configurados: {last_error}"
    ) from last_error


USER_STRATEGIES_SYSTEM_PROMPT = """\
Você é um assistente que organiza uma lista de estratégias competitivas
que um usuário descreveu em linguagem natural, em texto corrido.

Regras estritas:
- Identifique cada estratégia distinta mencionada pelo usuário, mesmo que
  ele tenha escrito tudo numa frase só, com vírgulas internas ou
  conectivos ("e", "além disso", "também").
- NÃO invente estratégias que o usuário não mencionou.
- NÃO inclua frases de preenchimento, exemplos ilustrativos ou conectivos
  como itens da lista (ex.: "por exemplo", "ou seja", "entre outros").
  Esses termos NUNCA devem virar um item da lista sozinhos.
- Reescreva cada estratégia de forma curta e clara (poucas palavras),
  preservando o sentido original do usuário.
- Se o usuário claramente listou os itens um por linha, apenas limpe e
  devolva a mesma lista.
- Responda em português do Brasil.
- Responda EXCLUSIVAMENTE em JSON válido, no formato:
  {"strategies": ["estratégia 1", "estratégia 2"]}
"""


def parse_user_strategies(raw_text: str) -> list[str]:
    """Interpreta o texto livre do usuário e extrai a lista de estratégias
    próprias (RF04), em vez de dividir ingenuamente por vírgula/linha —
    frases naturais com vírgulas internas quebravam nessa abordagem
    anterior, produzindo fragmentos sem sentido (ex.: "por exemplo")
    tratados como estratégia própria."""
    data = _chat_json(USER_STRATEGIES_SYSTEM_PROMPT, raw_text)
    raw_strategies = data.get("strategies", [])
    return [str(item).strip() for item in raw_strategies if str(item).strip()]


STRATEGY_CLASSIFICATION_SYSTEM_PROMPT = """\
Você é um analista que classifica estratégias competitivas em categorias
fixas, para uma heurística de payoff de um jogo de teoria dos jogos.

Categorias possíveis (escolha exatamente uma para cada estratégia):
- "custo": foco em preço baixo, economia, acessibilidade, promoções.
- "diferenciacao": foco em tecnologia, inovação, qualidade superior,
  recursos exclusivos, experiência do usuário, personalização,
  atendimento diferenciado.
- "nicho": foco num segmento específico de clientes (ex.: corporativo,
  um público muito específico, uma vertical de mercado).
- "geral": não se encaixa claramente em nenhuma das anteriores, ou é
  genérica demais para classificar com confiança.

Regras estritas:
- Classifique pelo SENTIDO da estratégia, não apenas por palavras-chave
  literais — frases como "Diversificação de Serviços" ou "Facilitação do
  Agendamento" devem ser classificadas pelo que elas realmente significam
  (ex.: facilitar o agendamento é conveniência/diferenciação de
  experiência, não "geral" só porque não contém a palavra "tecnologia").
- Uma estratégia só deve virar "geral" se genuinamente não sugerir
  nenhuma das outras três categorias.
- Responda em português do Brasil.
- Responda EXCLUSIVAMENTE em JSON válido, no formato:
  {"classifications": [{"strategy": "texto exato da estratégia", "category": "custo|diferenciacao|nicho|geral"}]}
"""


def classify_strategies(strategies: list[str]) -> dict[str, str]:
    """Classifica uma lista de estratégias nas categorias fixas da
    heurística de payoff (custo/diferenciação/nicho/geral), usando o LLM
    para entender o sentido da frase — mais robusto do que casar
    palavras-chave literais contra texto real extraído de sites ou
    descrito pelo usuário (ver `gamebot.payoff.classify_strategy_by_keywords`
    para o fallback determinístico caso esta chamada falhe)."""
    if not strategies:
        return {}
    user_prompt = "Estratégias a classificar:\n" + "\n".join(
        f"- {s}" for s in strategies
    )
    data = _chat_json(STRATEGY_CLASSIFICATION_SYSTEM_PROMPT, user_prompt)
    raw = data.get("classifications", [])
    valid_categories = {"custo", "diferenciacao", "nicho", "geral"}
    result: dict[str, str] = {}
    for item in raw:
        strategy = str(item.get("strategy", "")).strip()
        category = str(item.get("category", "")).strip().lower()
        if strategy and category in valid_categories:
            result[strategy] = category
    return result


PAIR_SCORING_SYSTEM_PROMPT = """\
Você atribui payoffs heurísticos (ganho relativo) para um jogo de teoria
dos jogos entre um usuário/empreendedor e um concorrente, um payoff para
cada combinação (estratégia do usuário x estratégia do concorrente).

Escala ORDINAL FIXA: 1 (baixo), 2 (médio) ou 3 (alto) — nunca outro valor.

Regra: quanto mais as duas estratégias da combinação competem pelo MESMO
público ou pela MESMA necessidade (alta sobreposição — ex.: as duas
prometem "atendimento rápido"), MENOR o payoff para os dois lados (mais
rivalidade direta, ganho menor para ambos). Quanto mais elas atendem
públicos, necessidades ou posicionamentos DIFERENTES ou COMPLEMENTARES
(baixa sobreposição — ex.: uma foca em preço, a outra em tecnologia),
MAIOR o payoff para os dois lados (menos rivalidade direta).

Regras estritas:
- Avalie cada combinação pelo SENTIDO real das duas estratégias
  envolvidas, não por categorias fixas nem por palavras-chave literais.
- O payoff é o MESMO valor para os dois jogadores na mesma combinação —
  este modelo heurístico mede o grau de sobreposição competitiva, não
  ganho individual diferenciado.
- Dê um score para CADA combinação listada, sem pular nenhuma.
- Use os valores 1, 2 e 3 de forma proporcional ao que você observar —
  não force tudo para o mesmo valor nem varie sem justificativa.
- Responda em português do Brasil.
- Responda EXCLUSIVAMENTE em JSON válido, no formato:
  {"scores": [{"user_strategy": "texto exato", "competitor_strategy": "texto exato", "score": 1}]}
"""


def score_heuristic_payoffs(
    user_strategies: list[str], competitor_strategies: list[str]
) -> dict[tuple[str, str], int]:
    """Pontua diretamente (escala 1-3, RD02) cada combinação de estratégia
    do usuário x estratégia do concorrente, pelo grau de sobreposição
    competitiva — mais granular do que classificar cada estratégia
    isoladamente em 4 categorias fixas (`classify_strategies`), que gerava
    linhas/colunas inteiras com o mesmo valor sempre que várias estratégias
    caíam na mesma categoria."""
    if not user_strategies or not competitor_strategies:
        return {}
    pairs_text = "\n".join(
        f"- Usuário: \"{u}\" | Concorrente: \"{c}\""
        for u in user_strategies
        for c in competitor_strategies
    )
    user_prompt = f"Combinações a pontuar:\n{pairs_text}"
    data = _chat_json(PAIR_SCORING_SYSTEM_PROMPT, user_prompt)
    raw = data.get("scores", [])
    result: dict[tuple[str, str], int] = {}
    for item in raw:
        u = str(item.get("user_strategy", "")).strip()
        c = str(item.get("competitor_strategy", "")).strip()
        try:
            score = int(item.get("score"))
        except (TypeError, ValueError):
            continue
        if u and c and score in (1, 2, 3):
            result[(u, c)] = score
    return result


def extract_strategies(company_label: str, text: str) -> list[StrategyCandidate]:
    """Extrai estratégias competitivas prováveis a partir do texto coletado (RF03)."""
    user_prompt = (
        f"Empresa concorrente: {company_label}\n\n"
        f"Texto extraído do site (pode estar truncado):\n\"\"\"\n{text}\n\"\"\""
    )
    data = _chat_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
    raw_strategies = data.get("strategies", [])
    return [
        StrategyCandidate(
            strategy=str(item.get("strategy", "")).strip(),
            evidence=str(item.get("evidence", "")).strip(),
        )
        for item in raw_strategies
        if item.get("strategy")
    ]


IMAGE_EXTRACTION_SYSTEM_PROMPT = """\
Você é um analista de estratégia competitiva. Você recebe uma imagem
(print de tela) da página de uma empresa concorrente, usada quando o link
da página não pôde ser acessado diretamente (bloqueio, exige login, etc.).

Regras estritas:
- Baseie-se SOMENTE no que está visível na imagem. Não invente informação
  que não esteja nela.
- Para cada estratégia identificada, descreva em "evidence" o que na
  imagem embasa essa conclusão (ex.: "preço R$ 39,90 exibido no botão
  principal", "selo de destaque 'atendimento 24h'").
- Identifique entre 2 e 4 estratégias.
- Se a imagem não tiver relação com uma página de concorrente (ex.: foto
  aleatória, tela em branco), devolva uma lista vazia em vez de inventar.
- Responda em português do Brasil.
- Responda EXCLUSIVAMENTE em JSON válido, no formato:
  {"strategies": [{"strategy": "nome curto da estratégia", "evidence": "o que na imagem embasa isso"}]}
"""


def extract_strategies_from_image(
    company_label: str, image_bytes: bytes, mime_type: str
) -> list[StrategyCandidate]:
    """Extrai estratégias competitivas a partir de um print da página do
    concorrente (RF02/RF14 — alternativa quando o link está bloqueado para
    scraping, mas o usuário consegue acessar e fotografar a página)."""
    encoded = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded}"

    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=config.GROQ_VISION_MODEL,
            messages=[
                {"role": "system", "content": IMAGE_EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Empresa concorrente: {company_label}",
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Falha ao consultar o modelo de visão da Groq ({config.GROQ_VISION_MODEL}): {exc}"
        ) from exc

    raw_strategies = data.get("strategies", [])
    return [
        StrategyCandidate(
            strategy=str(item.get("strategy", "")).strip(),
            evidence=str(item.get("evidence", "")).strip(),
        )
        for item in raw_strategies
        if item.get("strategy")
    ]


RECOMMENDATION_SYSTEM_PROMPT = """\
Você é um consultor de estratégia de negócios explicando, para um gestor
sem formação em Teoria dos Jogos, o resultado de uma análise já calculada.

Regras estritas:
- Os resultados (estratégia dominante e equilíbrio de Nash) já foram
  CALCULADOS por um módulo determinístico e são fornecidos a você prontos.
  Você NUNCA deve recalculá-los, contestá-los ou inventar outro resultado
  — sua única tarefa é EXPLICAR o resultado fornecido em linguagem
  acessível.
- Sua resposta DEVE nomear explicitamente o(s) conceito(s) de Teoria dos
  Jogos utilizado(s) (ex.: "estratégia dominante", "equilíbrio de Nash em
  estratégia pura") e explicar em termos simples o que esse conceito
  significa.
- Se não houver estratégia dominante, diga isso claramente (não é um
  erro, é um resultado válido).
- Se não houver equilíbrio de Nash em estratégia pura, diga isso
  claramente e explique que, nesse caso, não há uma combinação estável de
  estratégias simultâneas — isso também é um resultado válido, não uma
  falha do sistema.
- Termine recomendando objetivamente qual estratégia o usuário deveria
  adotar, com base nos resultados.
- Se algum payoff usado for heurístico (estimado), reforce que se trata de
  uma estimativa, não um dado real de mercado.
- Reforce que a recomendação cobre apenas o aspecto de estratégia
  competitiva, não uma avaliação de viabilidade geral do negócio.
- Responda em português do Brasil, em linguagem simples e direta, em no
  máximo 200 palavras.
"""


def _format_matrix_for_prompt(game: Game) -> str:
    lines = []
    for u in game.user_strategies:
        for c in game.competitor_strategies:
            cell = game.get_cell(u, c)
            origem = "heurístico" if cell.is_heuristic else "manual"
            lines.append(
                f"- Você='{u}' x {game.competitor_label}='{c}': "
                f"payoff_você={cell.user_payoff}, payoff_concorrente={cell.competitor_payoff} "
                f"({origem})"
            )
    return "\n".join(lines)


def generate_recommendation(
    game: Game,
    dominant: DominantStrategyResult,
    equilibria: list[tuple[str, str]],
) -> str:
    """Gera a recomendação final em linguagem natural a partir de um
    resultado já calculado pelo solver (RF09)."""
    has_heuristic_cell = any(cell.is_heuristic for cell in game.cells.values())

    dominant_desc = (
        f"Estratégia dominante do usuário: '{dominant.user_strategy}' "
        f"(dominância {dominant.user_dominance})."
        if dominant.user_strategy
        else "Não há estratégia dominante para o usuário nesta matriz."
    )
    equilibria_desc = (
        "Equilíbrio(s) de Nash em estratégia pura: "
        + "; ".join(f"(Você='{u}', {game.competitor_label}='{c}')" for u, c in equilibria)
        if equilibria
        else "Não há equilíbrio de Nash em estratégia pura nesta matriz."
    )

    user_prompt = (
        f"Concorrente analisado: {game.competitor_label}\n"
        f"Suas estratégias: {', '.join(game.user_strategies)}\n"
        f"Estratégias do concorrente: {', '.join(game.competitor_strategies)}\n\n"
        f"Matriz de payoff (payoff_você, payoff_concorrente):\n"
        f"{_format_matrix_for_prompt(game)}\n\n"
        f"Resultado já calculado pelo solver:\n"
        f"{dominant_desc}\n{equilibria_desc}\n\n"
        f"Payoffs heurísticos presentes nesta matriz: "
        f"{'sim' if has_heuristic_cell else 'não'}."
    )

    client = _get_client()
    models_to_try = [config.GROQ_MODEL, config.GROQ_MODEL_FALLBACK]
    last_error: Exception | None = None
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    raise RuntimeError(
        f"Falha ao consultar o LLM (Groq) em todos os modelos configurados: {last_error}"
    ) from last_error
