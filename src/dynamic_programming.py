import numpy as np


def exact_knapsack_value(
    weights: list[int],
    values: list[int],
    capacity: int,
) -> int:
    """
    Resolve a Mochila 0/1 por programação dinâmica.

    Retorna apenas o valor ótimo. Isso é suficiente para calcular o gap
    dos algoritmos metaheurísticos.

    Complexidade aproximada:
    O(n * capacidade)
    """
    dp = np.zeros(capacity + 1, dtype=np.int64)

    for weight, value in zip(weights, values):
        if weight > capacity:
            continue

        candidate = dp[:-weight] + value
        np.maximum(dp[weight:], candidate, out=dp[weight:])

    return int(dp[capacity])

