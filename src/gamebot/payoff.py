"""Modelagem do jogo e montagem da matriz de payoff (RF04-RF06, RF10-RF11).

A matriz é sempre 2 jogadores (usuário x 1 concorrente por vez), com N
estratégias do usuário e M estratégias do concorrente (RD01: mínimo 2 por
jogador). Cada célula guarda o payoff do usuário, o payoff do concorrente e
se aquele valor é heurístico (estimado) ou informado manualmente (RF11).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Escala ordinal heurística fixa e documentada (RD02): 1 = baixo, 3 = alto.
HEURISTIC_LOW = 1
HEURISTIC_MEDIUM = 2
HEURISTIC_HIGH = 3

MODE_HEURISTIC = "heuristico"
MODE_MANUAL = "manual"

# Critério da heurística (mantido explícito para citar na interface — RNF02):
# estratégias classificadas na MESMA categoria competem diretamente pelo
# mesmo público (maior rivalidade => payoff baixo para os dois lados).
# Estratégias em categorias DIFERENTES se sobrepõem menos (menor rivalidade
# => payoff alto para os dois lados). Quando uma das estratégias não se
# encaixa claramente em nenhuma categoria, o resultado é tratado como
# incerto (payoff médio).
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "custo": [
        "preço", "preco", "custo", "barato", "econôm", "econom",
        "acessív", "acessiv", "popular", "desconto", "baixo custo",
    ],
    "diferenciacao": [
        "tecnolog", "inovaç", "inovac", "premium", "exclusiv", "qualidade",
        "diferencia", "avanç", "avanc", "proprietári", "proprietari",
    ],
    "nicho": [
        "nicho", "especializ", "segmento", "corporativ", "foco em",
        "vertical", "personaliz",
    ],
}


VALID_CATEGORIES = {"custo", "diferenciacao", "nicho", "geral"}


def classify_strategy_by_keywords(strategy_text: str) -> str:
    """Classifica uma estratégia por palavras-chave fixas.

    Serve como *fallback* determinístico caso a classificação via LLM
    (mais robusta para frases reais, ver `gamebot.llm.classify_strategies`)
    não esteja disponível. Sozinho, esse método é frágil: frases reais
    como "Diversificação de Serviços" ou "Facilitação do Agendamento" não
    contêm nenhuma das palavras-chave e caem em "geral" — por isso não é
    mais o caminho padrão, só o de segurança.
    """
    normalized = strategy_text.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    return "geral"


def heuristic_payoff_pair(
    user_strategy: str,
    competitor_strategy: str,
    category_map: dict[str, str] | None = None,
) -> tuple[int, int]:
    """Calcula o par de payoffs heurísticos (usuário, concorrente) para uma
    célula. Se `category_map` for fornecido (normalmente vindo de
    `gamebot.llm.classify_strategies`), usa-o; caso contrário, cai para a
    classificação por palavras-chave."""
    if category_map is not None:
        user_category = category_map.get(user_strategy, "geral")
        competitor_category = category_map.get(competitor_strategy, "geral")
    else:
        user_category = classify_strategy_by_keywords(user_strategy)
        competitor_category = classify_strategy_by_keywords(competitor_strategy)

    if user_category == "geral" or competitor_category == "geral":
        value = HEURISTIC_MEDIUM
    elif user_category == competitor_category:
        value = HEURISTIC_LOW
    else:
        value = HEURISTIC_HIGH
    return value, value


@dataclass
class PayoffCell:
    user_payoff: float
    competitor_payoff: float
    is_heuristic: bool


@dataclass
class Game:
    competitor_label: str
    user_strategies: list[str]
    competitor_strategies: list[str]
    mode: str
    cells: dict[tuple[str, str], PayoffCell] = field(default_factory=dict)

    def set_cell(
        self,
        user_strategy: str,
        competitor_strategy: str,
        user_payoff: float,
        competitor_payoff: float,
        is_heuristic: bool,
    ) -> None:
        self.cells[(user_strategy, competitor_strategy)] = PayoffCell(
            user_payoff=user_payoff,
            competitor_payoff=competitor_payoff,
            is_heuristic=is_heuristic,
        )

    def get_cell(self, user_strategy: str, competitor_strategy: str) -> PayoffCell:
        return self.cells[(user_strategy, competitor_strategy)]

    def is_complete(self) -> bool:
        return len(self.cells) == len(self.user_strategies) * len(self.competitor_strategies)

    def pending_cells(self) -> list[tuple[str, str]]:
        all_pairs = [
            (u, c) for u in self.user_strategies for c in self.competitor_strategies
        ]
        return [pair for pair in all_pairs if pair not in self.cells]


def build_heuristic_game(
    competitor_label: str,
    user_strategies: list[str],
    competitor_strategies: list[str],
    category_map: dict[str, str] | None = None,
    pair_scores: dict[tuple[str, str], int] | None = None,
) -> Game:
    """Monta a matriz heurística. Prioridade de fonte do payoff, da mais
    para a menos granular:
    1. `pair_scores` — nota 1-3 dada pelo LLM direto para aquela
       combinação específica (`gamebot.llm.score_heuristic_payoffs`).
    2. `category_map` — categoria (custo/diferenciação/nicho/geral) dada
       pelo LLM por estratégia (`gamebot.llm.classify_strategies`).
    3. Nenhum dos dois: classificação por palavras-chave (fallback local,
       sem chamada de API).
    """
    game = Game(
        competitor_label=competitor_label,
        user_strategies=user_strategies,
        competitor_strategies=competitor_strategies,
        mode=MODE_HEURISTIC,
    )
    for u in user_strategies:
        for c in competitor_strategies:
            score = pair_scores.get((u, c)) if pair_scores else None
            if score is not None:
                up, cp = score, score
            else:
                up, cp = heuristic_payoff_pair(u, c, category_map=category_map)
            game.set_cell(u, c, up, cp, is_heuristic=True)
    return game


def build_empty_manual_game(
    competitor_label: str, user_strategies: list[str], competitor_strategies: list[str]
) -> Game:
    return Game(
        competitor_label=competitor_label,
        user_strategies=user_strategies,
        competitor_strategies=competitor_strategies,
        mode=MODE_MANUAL,
    )


def render_matrix_markdown(game: Game) -> str:
    """Renderiza a matriz de payoff como tabela Markdown (RF10), marcando
    heurístico vs. manual (RF11)."""
    header = "| Você \\ " + game.competitor_label + " | " + " | ".join(
        game.competitor_strategies
    ) + " |"
    separator = "|---" * (len(game.competitor_strategies) + 1) + "|"
    rows = [header, separator]
    for u in game.user_strategies:
        row_cells = []
        for c in game.competitor_strategies:
            cell = game.cells.get((u, c))
            if cell is None:
                row_cells.append("_pendente_")
                continue
            tag = "heurístico" if cell.is_heuristic else "manual"
            # Markdown puro (sem HTML: o Chainlit roda com
            # unsafe_allow_html=false por segurança, já que parte do texto
            # nas células vem de sites externos raspados).
            row_cells.append(
                f"({cell.user_payoff}, {cell.competitor_payoff}) _{tag}_"
            )
        rows.append(f"| **{u}** | " + " | ".join(row_cells) + " |")
    return "\n".join(rows)
