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


def classify_strategy(strategy_text: str) -> str:
    """Classifica uma estratégia textual numa categoria heurística fixa."""
    normalized = strategy_text.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    return "geral"


def heuristic_payoff_pair(user_strategy: str, competitor_strategy: str) -> tuple[int, int]:
    """Calcula o par de payoffs heurísticos (usuário, concorrente) para uma célula."""
    user_category = classify_strategy(user_strategy)
    competitor_category = classify_strategy(competitor_strategy)

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
    competitor_label: str, user_strategies: list[str], competitor_strategies: list[str]
) -> Game:
    game = Game(
        competitor_label=competitor_label,
        user_strategies=user_strategies,
        competitor_strategies=competitor_strategies,
        mode=MODE_HEURISTIC,
    )
    for u in user_strategies:
        for c in competitor_strategies:
            up, cp = heuristic_payoff_pair(u, c)
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
            tag = "[heurístico]" if cell.is_heuristic else "[manual]"
            row_cells.append(
                f"({cell.user_payoff}, {cell.competitor_payoff})<br><sub>{tag}</sub>"
            )
        rows.append(f"| **{u}** | " + " | ".join(row_cells) + " |")
    return "\n".join(rows)
