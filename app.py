"""Ponto de entrada do chatbot (Chainlit). Executar com: chainlit run app.py"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import chainlit as cl

from gamebot import payoff, scraping, solver
from gamebot.llm import (
    classify_strategies,
    extract_strategies,
    extract_strategies_from_image,
    generate_recommendation,
    parse_user_strategies,
    score_heuristic_payoffs,
    search_competitor_by_name,
)

WELCOME_MESSAGE = """\
Este assistente ajuda a decidir **qual estratégia competitiva adotar** \
frente a um concorrente específico, usando conceitos de Teoria dos Jogos \
(estratégia dominante e equilíbrio de Nash).

> **Escopo:** a análise cobre apenas o aspecto estratégico/competitivo. \
Ela **não** avalia viabilidade financeira, operacional ou de mercado do \
negócio como um todo.

Para começar, me diga o **concorrente que você quer analisar** — pode ser \
só o nome (ex.: "Doctoralia"), o link do site dele, um print da página \
(ícone de clipe) ou um trecho do texto dela. Se você só souber o nome, eu \
tento pesquisar e encontrar as informações sozinho.

---
*Projetado por Raiff Nóbrega e Maria Cecília Paiva.*
"""

HEURISTIC_DISCLAIMER = (
    "\n\n> ⚠️ Os payoffs heurísticos são **estimativas ordinais** (escala 1 a "
    "3) calculadas a partir da categoria textual de cada estratégia — "
    "**não são dados reais de mercado**. Critério: estratégias na mesma "
    "categoria competem diretamente pelo mesmo público (payoff 1); em "
    "categorias diferentes, a sobreposição é menor (payoff 3); quando uma "
    "estratégia não se encaixa claramente numa categoria, o resultado é "
    "tratado como incerto (payoff 2)."
)

STAGE_AWAITING_LINK = "awaiting_link"
STAGE_AWAITING_MANUAL_TEXT = "awaiting_manual_text"
STAGE_AWAITING_USER_STRATEGIES = "awaiting_user_strategies"
STAGE_AWAITING_MANUAL_CELL = "awaiting_manual_cell"
STAGE_DONE = "done"

MANUAL_CELL_PATTERN = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*,\s*(-?\d+(?:[.,]\d+)?)\s*$")


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("stage", STAGE_AWAITING_LINK)
    cl.user_session.set("competitors", [])
    await cl.Message(content=WELCOME_MESSAGE).send()


async def _present_strategies(company_label: str, strategies, source: str) -> None:
    """Exibe as estratégias já extraídas (de texto ou de imagem) e segue
    o fluxo para pedir as estratégias do próprio usuário."""
    if not strategies:
        await cl.Message(
            content=(
                "Não identifiquei estratégias claras nessa fonte. Pode enviar "
                "outro link, colar um trecho de texto do site do concorrente, "
                "ou mandar um print de outra parte da página."
            )
        ).send()
        cl.user_session.set("stage", STAGE_AWAITING_LINK)
        return

    lines = [f"### Estratégias identificadas — {company_label} ({source})\n"]
    for item in strategies:
        lines.append(f"- **{item.strategy}**\n  > _{item.evidence}_")
    await cl.Message(content="\n".join(lines)).send()

    cl.user_session.set("competitor_label", company_label)
    cl.user_session.set(
        "competitor_strategies", [s.strategy for s in strategies]
    )
    cl.user_session.set("stage", STAGE_AWAITING_USER_STRATEGIES)

    await cl.Message(
        content=(
            "Agora me diga: quais são **as suas próprias estratégias "
            "possíveis** diante desse concorrente? Pode escrever à "
            "vontade, em texto corrido — preciso de **pelo menos 2** "
            "estratégias (ex.: \"vou apostar em preço baixo e também em "
            "um atendimento mais rápido que o da concorrência\")."
        )
    ).send()


async def _extract_and_show(company_label: str, text: str, source: str) -> None:
    async with cl.Step(name="Extração de estratégias (Groq / Llama 3)") as step:
        step.input = text[:500]
        try:
            strategies = extract_strategies(company_label, text)
        except Exception as exc:  # noqa: BLE001
            step.output = f"Falha na extração: {exc}"
            await cl.Message(
                content=(
                    "Não consegui interpretar o texto com o modelo de linguagem "
                    f"agora ({exc}). Podemos tentar novamente enviando o link "
                    "de outro concorrente."
                )
            ).send()
            cl.user_session.set("stage", STAGE_AWAITING_LINK)
            return
        step.output = f"{len(strategies)} estratégia(s) identificada(s)."

    await _present_strategies(company_label, strategies, source)


async def _extract_and_show_from_image(
    company_label: str, image_bytes: bytes, mime_type: str, source: str
) -> None:
    async with cl.Step(name="Leitura da imagem (Groq / visão)") as step:
        step.input = f"Imagem ({mime_type}, {len(image_bytes)} bytes)"
        try:
            strategies = extract_strategies_from_image(company_label, image_bytes, mime_type)
        except Exception as exc:  # noqa: BLE001
            step.output = f"Falha na leitura da imagem: {exc}"
            await cl.Message(
                content=(
                    "Não consegui interpretar essa imagem agora "
                    f"({exc}). Pode tentar enviar de novo, ou colar um "
                    "trecho de texto do site do concorrente em vez disso."
                )
            ).send()
            return
        step.output = f"{len(strategies)} estratégia(s) identificada(s)."

    await _present_strategies(company_label, strategies, source)


async def _ask_payoff_mode() -> None:
    res = await cl.AskActionMessage(
        content=(
            "Como você quer definir os payoffs da matriz? Payoffs são o "
            "'ganho' relativo de cada combinação de estratégias — não um "
            "número real de lucro, a menos que você tenha esse dado."
        ),
        actions=[
            cl.Action(
                name="heuristico",
                payload={"mode": payoff.MODE_HEURISTIC},
                label="Heurística automática (estimativa 1–3)",
            ),
            cl.Action(
                name="manual",
                payload={"mode": payoff.MODE_MANUAL},
                label="Inserir valores reais manualmente",
            ),
        ],
    ).send()

    mode = (res or {}).get("payload", {}).get("mode", payoff.MODE_HEURISTIC)
    competitor_label = cl.user_session.get("competitor_label")
    competitor_strategies = cl.user_session.get("competitor_strategies")
    user_strategies = cl.user_session.get("user_strategies")

    if mode == payoff.MODE_HEURISTIC:
        pair_scores = None
        category_map = None

        async with cl.Step(name="Pontuação heurística por combinação (Groq / Llama 3)") as step:
            try:
                pair_scores = score_heuristic_payoffs(user_strategies, competitor_strategies)
                if len(pair_scores) < len(user_strategies) * len(competitor_strategies):
                    raise RuntimeError("resposta incompleta do modelo (faltaram combinações)")
            except Exception as exc:  # noqa: BLE001
                step.output = f"Falha, tentando classificação por categoria: {exc}"
                pair_scores = None
            else:
                step.output = "; ".join(
                    f"{u} x {c} = {s}" for (u, c), s in pair_scores.items()
                )

        if pair_scores is None:
            async with cl.Step(name="Classificação por categoria (fallback, Groq / Llama 3)") as step:
                all_strategies = user_strategies + competitor_strategies
                step.input = ", ".join(all_strategies)
                try:
                    category_map = classify_strategies(all_strategies)
                except Exception as exc:  # noqa: BLE001
                    step.output = f"Falha, usando palavras-chave: {exc}"
                    category_map = None
                else:
                    step.output = ", ".join(
                        f"{s} → {category_map.get(s, 'geral')}" for s in all_strategies
                    )

        game = payoff.build_heuristic_game(
            competitor_label,
            user_strategies,
            competitor_strategies,
            category_map=category_map,
            pair_scores=pair_scores,
        )
        await _show_matrix(game)
    else:
        game = payoff.build_empty_manual_game(
            competitor_label, user_strategies, competitor_strategies
        )
        cl.user_session.set("current_game", game)
        cl.user_session.set("stage", STAGE_AWAITING_MANUAL_CELL)
        await _ask_next_manual_cell()


async def _ask_next_manual_cell() -> None:
    game: payoff.Game = cl.user_session.get("current_game")
    pending = game.pending_cells()
    if not pending:
        cl.user_session.set("stage", STAGE_DONE)
        await _show_matrix(game)
        return
    u, c = pending[0]
    await cl.Message(
        content=(
            f"Combinação **\"{u}\"** (sua estratégia) x **\"{c}\"** "
            f"({game.competitor_label}):\n"
            "Informe o payoff no formato `seu_valor,valor_do_concorrente` "
            "(ex.: `3,2`)."
        )
    ).send()


async def _show_matrix(game: payoff.Game) -> None:
    matrix_md = payoff.render_matrix_markdown(game)
    disclaimer = HEURISTIC_DISCLAIMER if game.mode == payoff.MODE_HEURISTIC else ""
    await cl.Message(
        content=(
            f"### Matriz de payoff — Você x {game.competitor_label}\n\n"
            f"{matrix_md}{disclaimer}"
        )
    ).send()
    cl.user_session.set("current_game", game)

    async with cl.Step(name="Solver de teoria dos jogos (determinístico)") as step:
        dominant = solver.find_dominant_strategies(game)
        equilibria = solver.find_pure_nash_equilibria(game)
        step.output = (
            f"Dominante — você: {dominant.user_strategy or 'nenhuma'} "
            f"({dominant.user_dominance or '-'}); "
            f"concorrente: {dominant.competitor_strategy or 'nenhuma'} "
            f"({dominant.competitor_dominance or '-'}). "
            f"Equilíbrios de Nash puros: {equilibria or 'nenhum'}."
        )

    async with cl.Step(name="Geração da recomendação (Groq / Llama 3)") as step:
        try:
            recommendation = generate_recommendation(game, dominant, equilibria)
            step.output = recommendation
        except Exception as exc:  # noqa: BLE001
            step.output = f"Falha: {exc}"
            await cl.Message(
                content=(
                    "A matriz e os resultados do solver foram calculados "
                    "corretamente, mas não consegui gerar a recomendação em "
                    f"linguagem natural agora ({exc}). Os resultados brutos "
                    "do solver estão logo acima, na etapa do solver."
                )
            ).send()
            cl.user_session.set("stage", STAGE_DONE)
            return

    await cl.Message(
        content=f"### Recomendação\n\n{recommendation}\n\n---\nEnvie um novo link de concorrente para analisar outro cenário."
    ).send()
    cl.user_session.set("stage", STAGE_DONE)


def _parse_strategy_list_fallback(raw: str) -> list[str]:
    """Separação ingênua (uma por linha), usada apenas se a chamada ao LLM
    falhar — ver `parse_user_strategies` para o caminho normal."""
    lines = [line.strip() for line in raw.split("\n")]
    return [line for line in lines if line]


def _first_image_element(message: cl.Message) -> cl.Image | None:
    """Retorna o primeiro anexo de imagem da mensagem, se houver — usado
    como alternativa ao link/texto quando o site do concorrente está
    bloqueado, mas o usuário consegue enviar um print da página (RF02/RF14)."""
    for element in message.elements or []:
        if (element.mime or "").startswith("image/"):
            return element
    return None


def _read_image_bytes(element: cl.Image) -> bytes:
    if element.content:
        content = element.content
        return content if isinstance(content, bytes) else content.encode("utf-8")
    if element.path:
        with open(element.path, "rb") as f:
            return f.read()
    raise RuntimeError("Imagem recebida sem conteúdo nem caminho de arquivo.")


_URL_LIKE_PATTERN = re.compile(
    r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(/\S*)?$"
)


def _normalize_url(text: str) -> str | None:
    """Aceita links sem `http(s)://` ou `www.` (ex.: `doctoralia.com.br`),
    normalizando para uma URL completa. Retorna None se o texto não
    parecer um link (nesse caso, tratamos como nome de empresa — ver
    `_search_and_show`)."""
    candidate = text.strip()
    if not candidate or " " in candidate:
        return None
    if candidate.startswith("http://") or candidate.startswith("https://"):
        return candidate
    if _URL_LIKE_PATTERN.match(candidate):
        return f"https://{candidate}"
    return None


async def _fetch_and_extract_by_url(url: str) -> None:
    async with cl.Step(name="Coleta do conteúdo do site") as step:
        step.input = url
        try:
            page = scraping.fetch_page_text(url)
        except scraping.ScrapingError as exc:
            step.output = f"Falha: {exc}"
            cl.user_session.set("stage", STAGE_AWAITING_MANUAL_TEXT)
            cl.user_session.set("pending_company_label", url)
            await cl.Message(
                content=(
                    f"Não consegui coletar o conteúdo desse link automaticamente "
                    f"({exc}).\n\nVocê pode colar manualmente, numa próxima "
                    "mensagem, um trecho de texto do site desse concorrente "
                    "(ex.: a página \"sobre\" ou a home), ou enviar um print "
                    "da página."
                )
            ).send()
            return
        step.output = f"{len(page.text)} caracteres coletados."

    await _extract_and_show(url, page.text, source="scraping automático")


async def _search_and_show(company_name: str) -> None:
    """Quando o usuário só informa o NOME do concorrente (sem link), tenta
    buscar na internet via Groq Compound (busca + visita de site reais).
    Se a busca falhar por qualquer motivo — inclusive o limite de tokens
    do tier gratuito da Groq para esse modelo, que é instável —, cai de
    volta para pedir link, texto ou print, sem travar a conversa."""
    async with cl.Step(name="Busca do concorrente na internet (Groq Compound)") as step:
        step.input = company_name
        try:
            url, summary = search_competitor_by_name(company_name)
        except Exception as exc:  # noqa: BLE001
            step.output = f"Falha na busca: {exc}"
            url, summary = None, ""
        else:
            step.output = f"URL encontrada: {url or 'nenhuma'}\n\n{summary[:500]}"

    has_useful_summary = len(summary.strip()) > 80
    if not has_useful_summary:
        cl.user_session.set("stage", STAGE_AWAITING_MANUAL_TEXT)
        cl.user_session.set("pending_company_label", company_name)
        await cl.Message(
            content=(
                f"Não consegui pesquisar \"{company_name}\" na internet agora "
                "(a busca automática está instável no momento). Pode me "
                "enviar o **link do site** dele, colar um **trecho de "
                "texto**, ou mandar um **print da página**?"
            )
        ).send()
        return

    source = f"busca na internet ({url})" if url else "busca na internet"
    await _extract_and_show(company_name, summary, source=source)


@cl.on_message
async def on_message(message: cl.Message) -> None:
    stage = cl.user_session.get("stage")
    content = message.content.strip()

    if stage == STAGE_AWAITING_MANUAL_TEXT:
        company_label = cl.user_session.get("pending_company_label", "Concorrente")
        image_element = _first_image_element(message)
        if image_element is not None:
            await _extract_and_show_from_image(
                company_label,
                _read_image_bytes(image_element),
                image_element.mime or "image/png",
                source="print enviado pelo usuário",
            )
            return
        if not content:
            await cl.Message(
                content=(
                    "Não recebi texto nem imagem. Cole um trecho do site do "
                    "concorrente, ou envie um print da página (ícone de "
                    "clipe, abaixo do campo de mensagem)."
                )
            ).send()
            return
        await _extract_and_show(company_label, content, source="texto colado manualmente")
        return

    if stage == STAGE_AWAITING_USER_STRATEGIES:
        async with cl.Step(name="Interpretação das suas estratégias (Groq / Llama 3)") as step:
            step.input = content
            try:
                strategies = parse_user_strategies(content)
            except Exception as exc:  # noqa: BLE001
                step.output = f"Falha, usando separação simples: {exc}"
                strategies = _parse_strategy_list_fallback(content)
            else:
                step.output = f"{len(strategies)} estratégia(s) identificada(s)."

        if len(strategies) < 2:
            await cl.Message(
                content=(
                    "Preciso de pelo menos 2 estratégias suas para montar o "
                    "jogo. Pode descrever com um pouco mais de detalhe?"
                )
            ).send()
            return
        cl.user_session.set("user_strategies", strategies)
        await _ask_payoff_mode()
        return

    if stage == STAGE_AWAITING_MANUAL_CELL:
        game: payoff.Game = cl.user_session.get("current_game")
        match = MANUAL_CELL_PATTERN.match(content)
        if not match:
            await cl.Message(
                content=(
                    "Formato inválido. Envie dois números separados por "
                    "vírgula, ex.: `3,2`."
                )
            ).send()
            return
        u, c = game.pending_cells()[0]
        user_payoff = float(match.group(1).replace(",", "."))
        competitor_payoff = float(match.group(2).replace(",", "."))
        game.set_cell(u, c, user_payoff, competitor_payoff, is_heuristic=False)
        await _ask_next_manual_cell()
        return

    if stage == STAGE_DONE:
        if _first_image_element(message) is not None or content:
            cl.user_session.set("stage", STAGE_AWAITING_LINK)
            await on_message(message)
            return
        await cl.Message(
            content=(
                "Análise deste concorrente concluída. Envie o próximo "
                "concorrente (nome, link, texto ou print) para começar "
                "outra análise."
            )
        ).send()
        return

    # STAGE_AWAITING_LINK (default)
    image_element = _first_image_element(message)
    if image_element is not None:
        company_label = content if content else "Concorrente (via imagem)"
        await _extract_and_show_from_image(
            company_label,
            _read_image_bytes(image_element),
            image_element.mime or "image/png",
            source="print enviado pelo usuário",
        )
        return

    if not content:
        await cl.Message(
            content=(
                "Não recebi nada. Me diga o nome do concorrente, o link do "
                "site dele, cole um trecho de texto, ou envie um print da "
                "página (ícone de clipe)."
            )
        ).send()
        return

    normalized_url = _normalize_url(content)
    if normalized_url is not None:
        await _fetch_and_extract_by_url(normalized_url)
        return

    # Não é link nem imagem: trata como nome do concorrente e tenta buscar
    # na internet (com fallback automático se a busca falhar).
    await _search_and_show(content)
