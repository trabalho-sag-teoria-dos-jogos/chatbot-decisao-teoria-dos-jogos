"""Valida o solver próprio contra exemplos clássicos da literatura de
Teoria dos Jogos e, quando aplicável, contra a biblioteca `nashpy` (usada
apenas como referência de teste — ver docs/01-planejamento-implementacao.md)."""

import numpy as np
import nashpy as nash

from gamebot.payoff import Game, MODE_MANUAL
from gamebot.solver import find_dominant_strategies, find_pure_nash_equilibria


def _manual_game(
    user_strategies: list[str],
    competitor_strategies: list[str],
    user_payoffs: list[list[float]],
    competitor_payoffs: list[list[float]],
) -> Game:
    game = Game(
        competitor_label="Concorrente",
        user_strategies=user_strategies,
        competitor_strategies=competitor_strategies,
        mode=MODE_MANUAL,
    )
    for i, u in enumerate(user_strategies):
        for j, c in enumerate(competitor_strategies):
            game.set_cell(
                u, c, user_payoffs[i][j], competitor_payoffs[i][j], is_heuristic=False
            )
    return game


def test_prisoners_dilemma_dominant_strategy_and_nash():
    # Cooperar / Delatar — payoffs clássicos do dilema do prisioneiro.
    game = _manual_game(
        user_strategies=["Cooperar", "Delatar"],
        competitor_strategies=["Cooperar", "Delatar"],
        user_payoffs=[[3, 0], [5, 1]],
        competitor_payoffs=[[3, 5], [0, 1]],
    )

    result = find_dominant_strategies(game)
    assert result.user_strategy == "Delatar"
    assert result.user_dominance == "estrita"
    assert result.competitor_strategy == "Delatar"
    assert result.competitor_dominance == "estrita"

    equilibria = find_pure_nash_equilibria(game)
    assert equilibria == [("Delatar", "Delatar")]

    # Validação cruzada com nashpy.
    A = np.array([[3, 0], [5, 1]])  # payoffs do usuário (linha)
    B = np.array([[3, 5], [0, 1]])  # payoffs do concorrente (coluna)
    nash_game = nash.Game(A, B)
    pure_equilibria = list(nash_game.support_enumeration())
    # (Delatar, Delatar) = índice (1, 1) -> vetor puro [0,1] x [0,1]
    assert any(
        np.array_equal(eq[0], [0, 1]) and np.array_equal(eq[1], [0, 1])
        for eq in pure_equilibria
    )


def test_battle_of_sexes_multiple_equilibria_no_dominant_strategy():
    game = _manual_game(
        user_strategies=["Ópera", "Futebol"],
        competitor_strategies=["Ópera", "Futebol"],
        user_payoffs=[[2, 0], [0, 1]],
        competitor_payoffs=[[1, 0], [0, 2]],
    )

    result = find_dominant_strategies(game)
    assert result.user_strategy is None
    assert result.competitor_strategy is None

    equilibria = find_pure_nash_equilibria(game)
    assert set(equilibria) == {("Ópera", "Ópera"), ("Futebol", "Futebol")}


def test_matching_pennies_no_pure_equilibrium():
    game = _manual_game(
        user_strategies=["Cara", "Coroa"],
        competitor_strategies=["Cara", "Coroa"],
        user_payoffs=[[1, -1], [-1, 1]],
        competitor_payoffs=[[-1, 1], [1, -1]],
    )

    result = find_dominant_strategies(game)
    assert result.user_strategy is None
    assert result.competitor_strategy is None

    equilibria = find_pure_nash_equilibria(game)
    assert equilibria == []


def test_weakly_dominant_strategy_is_detected():
    # Estratégia A do usuário empata ou vence B contra qualquer resposta,
    # mas não vence estritamente em todos os casos -> dominância fraca.
    game = _manual_game(
        user_strategies=["A", "B"],
        competitor_strategies=["X", "Y"],
        user_payoffs=[[2, 3], [2, 1]],
        competitor_payoffs=[[1, 1], [1, 1]],
    )

    result = find_dominant_strategies(game)
    assert result.user_strategy == "A"
    assert result.user_dominance == "fraca"
