"""
Algoritmo Genético para o Problema da Mochila 0/1.

Implementa um GA canônico com:
- Representação binária
- Seleção por torneio
- Crossover uniforme
- Mutação bit flip
- Elitismo
- Reparo de soluções inviáveis via knapsack.repair_solution

"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from random import Random

from knapsack import (
    evaluate_solution,
    repair_solution,
    random_feasible_solution,
)


def run_genetic_algorithm(
    weights: list[int],
    values: list[int],
    capacity: int,
    seed: int,
    population_size: int = 100,
    generations: int = 100,
    tournament_size: int = 3,
    crossover_rate: float = 0.8,
    mutation_rate: float | None = None,
) -> dict:
    """
    Executa o Algoritmo Genético para o Problema da Mochila 0/1.

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
    population_size : int
        Tamanho da população (default 100).
    generations : int
        Número de gerações (default 100).
    tournament_size : int
        Tamanho do torneio para seleção (default 3).
    crossover_rate : float
        Probabilidade de crossover (default 0.8).
    mutation_rate : float | None
        Probabilidade de mutação por bit. Se None, usa 1/n (default None).

    Retorno
    -------
    dict
        Dicionário com as chaves:
        - "solution": list[int] — melhor solução encontrada
        - "value": int — valor total da melhor solução
        - "weight": int — peso total da melhor solução
        - "evaluations": int — número total de avaliações de fitness
    """
    if mutation_rate is None:
        mutation_rate = 1.0 / len(weights)

    rng = Random(seed)

    # Contador de avaliações (cada chamada a evaluate_solution incrementa)
    evaluations = 0

    # --- Geração da população inicial ---
    population: list[list[int]] = []
    fitness: list[int] = []
    for _ in range(population_size):
        indiv = random_feasible_solution(weights, values, capacity, rng)
        # random_feasible_solution chamou repair_solution e evaluate_solution internamente (1 aval)
        val, _ = evaluate_solution(indiv, weights, values)
        evaluations += 2
        population.append(indiv)
        fitness.append(val)

    # --- Elitismo: preservar o melhor indivíduo ---
    best_idx = max(range(len(fitness)), key=lambda i: fitness[i])
    best_solution = population[best_idx][:]
    best_value = fitness[best_idx]
    _, best_weight = evaluate_solution(best_solution, weights, values)

    # --- Loop principal: gerações ---
    for _ in range(generations):
        new_population: list[list[int]] = []

        # Elitismo: carregar o melhor indivíduo para a próxima geração
        elite = best_solution[:]
        new_population.append(elite)

        # Gerar o restante da nova população
        while len(new_population) < population_size:
            # Seleção por torneio
            parent1 = _tournament_selection(population, fitness, tournament_size, rng)
            parent2 = _tournament_selection(population, fitness, tournament_size, rng)

            # Crossover uniforme
            child1, child2 = _uniform_crossover(parent1, parent2, crossover_rate, rng)

            # Mutação bit flip
            child1 = _bit_flip_mutation(child1, mutation_rate, rng)
            child2 = _bit_flip_mutation(child2, mutation_rate, rng)

            # Reparo (garante viabilidade)
            child1 = repair_solution(child1, weights, values, capacity)
            evaluations += 1  # repair_solution chama evaluate_solution internamente
            child2 = repair_solution(child2, weights, values, capacity)
            evaluations += 1

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        # Atualizar população e fitness
        population = new_population
        fitness = []
        for indiv in population:
            val, _ = evaluate_solution(indiv, weights, values)
            fitness.append(val)
            evaluations += 1

        # Atualizar melhor solução (elitismo)
        best_gen_idx = max(range(len(fitness)), key=lambda i: fitness[i])
        if fitness[best_gen_idx] > best_value:
            best_solution = population[best_gen_idx][:]
            best_value = fitness[best_gen_idx]

    # Peso do melhor indivíduo
    _, best_weight = evaluate_solution(best_solution, weights, values)

    return {
        "solution": best_solution,
        "value": best_value,
        "weight": best_weight,
        "evaluations": evaluations,
        "iterations_executed": generations,
    }


# ============================================================
# Operadores genéticos auxiliares
# ============================================================


def _tournament_selection(
    population: list[list[int]],
    fitness: list[int],
    tournament_size: int,
    rng: Random,
) -> list[int]:
    """
    Seleciona um indivíduo por torneio determinístico.
    Retorna o melhor entre `tournament_size` candidatos sorteados.
    """
    candidates = rng.sample(range(len(population)), tournament_size)
    best_candidate = max(candidates, key=lambda i: fitness[i])
    return population[best_candidate][:]


def _uniform_crossover(
    parent1: list[int],
    parent2: list[int],
    crossover_rate: float,
    rng: Random,
) -> tuple[list[int], list[int]]:
    """
    Aplica crossover uniforme com probabilidade `crossover_rate`.
    Cada bit dos filhos é sorteado aleatoriamente entre os pais.
    Se o crossover não ocorrer, retorna cópias dos pais.
    """
    n = len(parent1)
    child1 = parent1[:]
    child2 = parent2[:]

    if rng.random() < crossover_rate:
        for i in range(n):
            if rng.random() < 0.5:
                child1[i], child2[i] = child2[i], child1[i]

    return child1, child2


def _bit_flip_mutation(
    individual: list[int],
    mutation_rate: float,
    rng: Random,
) -> list[int]:
    """
    Aplica mutação bit flip com probabilidade `mutation_rate` por bit.
    """
    mutated = individual[:]
    for i in range(len(mutated)):
        if rng.random() < mutation_rate:
            mutated[i] = 1 - mutated[i]
    return mutated