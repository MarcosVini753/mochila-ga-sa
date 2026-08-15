"""
Simulated Annealing para o Problema da Mochila 0/1.

Implementa um SA canônico com:
- Representação binária
- Vizinhança: flip de 1 bit aleatório
- Resfriamento geométrico (cooling_rate)
- Critério de aceitação de Metropolis para maximização
- Reparo de soluções inviáveis via knapsack.repair_solution

"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import math
from random import Random

from knapsack import (
    evaluate_solution,
    repair_solution,
    random_feasible_solution,
)


def run_simulated_annealing(
    weights: list[int],
    values: list[int],
    capacity: int,
    seed: int,
    iterations: int = 10000,
    initial_temperature: float = 1000.0,
    minimum_temperature: float = 0.001,
    cooling_rate: float = 0.995,
) -> dict:
    """
    Executa o Simulated Annealing para o Problema da Mochila 0/1.

    Parâmetros
    ----------
    weights : list[int]
        Lista de pesos dos itens.
    values : list[int]
        Lista de valores dos itens.
    capacity : int
        Capacidade da mochila.
    seed : int
        Semente para o gerador de números aleatórios (Random).
    iterations : int
        Número máximo de iterações (default 10000).
    initial_temperature : float
        Temperatura inicial (default 1000.0).
    minimum_temperature : float
        Temperatura mínima para parada (default 0.001).
    cooling_rate : float
        Fator de resfriamento geométrico (default 0.995).

    Retorno
    -------
    dict
        Dicionário com as chaves:
        - "solution": list[int] — melhor solução encontrada
        - "value": int — valor total da melhor solução
        - "weight": int — peso total da melhor solução
        - "evaluations": int — número total de avaliações de fitness
    """
    rng = Random(seed)
    n = len(weights)

    # Contador de avaliações
    evaluations = 0

    # --- Solução inicial viável ---
    current_solution = random_feasible_solution(weights, values, capacity, rng)
    evaluations += 1  # random_feasible_solution chama evaluate_solution internamente

    current_value, current_weight = evaluate_solution(
        current_solution, weights, values
    )
    evaluations += 1

    # Melhor solução encontrada até agora
    best_solution = current_solution[:]
    best_value = current_value
    best_weight = current_weight

    # --- Parâmetros do SA ---
    temperature = initial_temperature

    iterations_executed = 0

    # --- Loop principal ---
    for _ in range(iterations):
        if temperature < minimum_temperature:
            break
        iterations_executed += 1

        # Gerar vizinho: flip de 1 bit aleatório
        neighbor = current_solution[:]
        idx = rng.randint(0, n - 1)
        neighbor[idx] = 1 - neighbor[idx]

        # Reparar vizinho (garante viabilidade)
        neighbor = repair_solution(neighbor, weights, values, capacity)
        evaluations += 1  # repair_solution chama evaluate_solution internamente

        # Avaliar vizinho
        neighbor_value, neighbor_weight = evaluate_solution(
            neighbor, weights, values
        )
        evaluations += 1

        # Critério de aceitação (maximização)
        delta = neighbor_value - current_value

        if delta >= 0:
            # Aceita solução melhor ou igual
            current_solution = neighbor
            current_value = neighbor_value
            current_weight = neighbor_weight

            # Atualiza melhor global
            if current_value > best_value:
                best_solution = current_solution[:]
                best_value = current_value
                best_weight = current_weight
        else:
            # Aceita solução pior com probabilidade exp(delta / temperature)
            # delta < 0, então exp(delta/temperature) está em (0, 1)
            acceptance_prob = math.exp(delta / temperature)
            if rng.random() < acceptance_prob:
                current_solution = neighbor
                current_value = neighbor_value
                current_weight = neighbor_weight

        # Resfriamento geométrico
        temperature *= cooling_rate

    return {
        "solution": best_solution,
        "value": best_value,
        "weight": best_weight,
        "evaluations": evaluations,
        "iterations_executed": iterations_executed,
    }
