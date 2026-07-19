"""Solver de teoria dos jogos: estratégia dominante e equilíbrio de Nash em
estratégia pura (RF07, RF08).

Módulo 100% determinístico, implementado pela dupla — não depende de LLM
nem de bibliotecas externas em produção. `nashpy` é usado apenas nos testes
(ver `tests/test_solver.py`) para validar os resultados contra uma
implementação de referência.
"""

from __future__ import annotations

from dataclasses import dataclass

from .payoff import Game

DOMINANCE_STRICT = "estrita"
DOMINANCE_WEAK = "fraca"


@dataclass
class DominantStrategyResult:
    user_strategy: str | None
    user_dominance: str | None
    competitor_strategy: str | None
    competitor_dominance: str | None


def _find_dominant_strategy(
    own_strategies: list[str],
    opponent_strategies: list[str],
    payoff_of: "callable",
) -> tuple[str | None, str | None]:
    """payoff_of(own, opponent) -> payoff do jogador dono das `own_strategies`."""
    for candidate in own_strategies:
        dominates_all = True
        strict_over_all = True
        for other in own_strategies:
            if other == candidate:
                continue
            for opponent_strategy in opponent_strategies:
                candidate_payoff = payoff_of(candidate, opponent_strategy)
                other_payoff = payoff_of(other, opponent_strategy)
                if candidate_payoff < other_payoff:
                    dominates_all = False
                    break
                if candidate_payoff <= other_payoff:
                    strict_over_all = False
            if not dominates_all:
                break
        if dominates_all:
            return candidate, (DOMINANCE_STRICT if strict_over_all else DOMINANCE_WEAK)
    return None, None


def find_dominant_strategies(game: Game) -> DominantStrategyResult:
    user_payoff_of = lambda u, c: game.get_cell(u, c).user_payoff  # noqa: E731
    competitor_payoff_of = lambda c, u: game.get_cell(u, c).competitor_payoff  # noqa: E731

    user_strategy, user_dominance = _find_dominant_strategy(
        game.user_strategies, game.competitor_strategies, user_payoff_of
    )
    competitor_strategy, competitor_dominance = _find_dominant_strategy(
        game.competitor_strategies, game.user_strategies, competitor_payoff_of
    )
    return DominantStrategyResult(
        user_strategy=user_strategy,
        user_dominance=user_dominance,
        competitor_strategy=competitor_strategy,
        competitor_dominance=competitor_dominance,
    )


def find_pure_nash_equilibria(game: Game) -> list[tuple[str, str]]:
    """Retorna a lista de pares (estratégia_usuário, estratégia_concorrente)
    que são equilíbrio de Nash em estratégia pura (nenhum jogador melhora
    desviando unilateralmente)."""
    best_user_response_given_competitor: dict[str, set[str]] = {}
    for c in game.competitor_strategies:
        payoffs = [(u, game.get_cell(u, c).user_payoff) for u in game.user_strategies]
        best_value = max(p for _, p in payoffs)
        best_user_response_given_competitor[c] = {
            u for u, p in payoffs if p == best_value
        }

    best_competitor_response_given_user: dict[str, set[str]] = {}
    for u in game.user_strategies:
        payoffs = [
            (c, game.get_cell(u, c).competitor_payoff) for c in game.competitor_strategies
        ]
        best_value = max(p for _, p in payoffs)
        best_competitor_response_given_user[u] = {
            c for c, p in payoffs if p == best_value
        }

    equilibria = []
    for u in game.user_strategies:
        for c in game.competitor_strategies:
            if (
                u in best_user_response_given_competitor[c]
                and c in best_competitor_response_given_user[u]
            ):
                equilibria.append((u, c))
    return equilibria
