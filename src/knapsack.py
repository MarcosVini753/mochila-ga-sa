from random import Random


def parse_int_list(text: str) -> list[int]:
    """
    Converte uma célula textual como '1,2,3' em lista de inteiros.
    """
    if not isinstance(text, str):
        raise TypeError(f"Esperado str, recebido {type(text)}")

    if text.strip() == "":
        return []

    return [int(value) for value in text.split(",")]


def evaluate_solution(
    solution: list[int],
    weights: list[int],
    values: list[int],
) -> tuple[int, int]:
    """
    Retorna (valor_total, peso_total) de uma solução binária.
    """
    total_value = 0
    total_weight = 0

    for selected, weight, value in zip(solution, weights, values):
        if selected == 1:
            total_value += value
            total_weight += weight

    return total_value, total_weight


def is_feasible(
    solution: list[int],
    weights: list[int],
    capacity: int,
) -> bool:
    """
    Verifica se a solução respeita a capacidade da mochila.
    """
    _, total_weight = evaluate_solution(
        solution=solution,
        weights=weights,
        values=[0] * len(weights),
    )

    return total_weight <= capacity


def repair_solution(
    solution: list[int],
    weights: list[int],
    values: list[int],
    capacity: int,
) -> list[int]:
    """
    Repara uma solução inválida removendo itens com pior razão valor/peso.

    Essa estratégia mantém a comparação simples: tanto GA quanto SA sempre
    trabalham com soluções viáveis após a etapa de reparo.
    """
    repaired = solution[:]
    total_value, total_weight = evaluate_solution(repaired, weights, values)

    if total_weight <= capacity:
        return repaired

    selected_items = [i for i, bit in enumerate(repaired) if bit == 1]

    selected_items.sort(
        key=lambda i: values[i] / weights[i]
    )

    for item_index in selected_items:
        if total_weight <= capacity:
            break

        if repaired[item_index] == 1:
            repaired[item_index] = 0
            total_weight -= weights[item_index]

    return repaired


def random_solution(
    n_items: int,
    rng: Random,
) -> list[int]:
    """
    Gera uma solução binária aleatória.
    """
    return [rng.randint(0, 1) for _ in range(n_items)]


def random_feasible_solution(
    weights: list[int],
    values: list[int],
    capacity: int,
    rng: Random,
) -> list[int]:
    """
    Gera uma solução aleatória e aplica reparo caso ela ultrapasse a capacidade.
    """
    solution = random_solution(len(weights), rng)

    return repair_solution(
        solution=solution,
        weights=weights,
        values=values,
        capacity=capacity,
    )

