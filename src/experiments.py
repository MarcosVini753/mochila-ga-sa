"""
Execução dos experimentos para Algoritmo Genético e Simulated Annealing.

Mapeia:
PARTE 1 — Algoritmo Genético e Variações de Parâmetros
PARTE 2 — Simulated Annealing e Variações de Parâmetros
PARTE 3 — Comparação final entre o melhor GA e o melhor SA

Lê data/processed/instances_with_optimum.csv
Gera results/raw_runs.csv com os resultados detalhados de cada execução.
"""

import sys
import time
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from knapsack import parse_int_list
from genetic_algorithm import run_genetic_algorithm
from simulated_annealing import run_simulated_annealing

INPUT_CSV = Path("data/processed/instances_with_optimum.csv")
OUTPUT_CSV = Path("results/raw_runs.csv")

RUNS_PER_CONFIG = 10
BASE_SEED = 20260706

# Definindo as configurações/variações para o Algoritmo Genético
# GA_default: pop=100, gen=100, tour=3, cross=0.8, mut=1/n
# GA_var_pop_50: pop=50, gen=100
# GA_var_pop_200: pop=200, gen=100
# GA_var_cross_06: cross=0.6
# GA_var_tour_5: tour=5
GA_CONFIGS = {
    "GA_BASE": {"population_size": 100, "generations": 100, "tournament_size": 3, "crossover_rate": 0.80, "mutation_rate": None},
    "GA_POP_50": {"population_size": 50, "generations": 100, "tournament_size": 3, "crossover_rate": 0.80, "mutation_rate": None},
    "GA_POP_200": {"population_size": 200, "generations": 100, "tournament_size": 3, "crossover_rate": 0.80, "mutation_rate": None},
    "GA_CROSS_060": {"population_size": 100, "generations": 100, "tournament_size": 3, "crossover_rate": 0.60, "mutation_rate": None},
    "GA_CROSS_095": {"population_size": 100, "generations": 100, "tournament_size": 3, "crossover_rate": 0.95, "mutation_rate": None},
    "GA_MUT_LOW": {"population_size": 100, "generations": 100, "tournament_size": 3, "crossover_rate": 0.80, "mutation_rate": "0.5/n"},
    "GA_MUT_HIGH": {"population_size": 100, "generations": 100, "tournament_size": 3, "crossover_rate": 0.80, "mutation_rate": "2/n"},
    "GA_TOUR_5": {"population_size": 100, "generations": 100, "tournament_size": 5, "crossover_rate": 0.80, "mutation_rate": None},
}

SA_CONFIGS = {
    "SA_BASE": {"iterations": 10000, "initial_temperature": 1000.0, "minimum_temperature": 0.001, "cooling_rate": 0.995},
    "SA_COOL_FAST": {"iterations": 10000, "initial_temperature": 1000.0, "minimum_temperature": 0.001, "cooling_rate": 0.98},
    "SA_COOL_SLOW": {"iterations": 10000, "initial_temperature": 1000.0, "minimum_temperature": 0.001, "cooling_rate": 0.999},
    "SA_T0_LOW": {"iterations": 10000, "initial_temperature": 100.0, "minimum_temperature": 0.001, "cooling_rate": 0.995},
    "SA_T0_HIGH": {"iterations": 10000, "initial_temperature": 5000.0, "minimum_temperature": 0.001, "cooling_rate": 0.995},
}

def run_all_experiments():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_CSV}")

    df_instances = pd.read_csv(INPUT_CSV)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    results = []
    total_instances = len(df_instances)
    total_configs = len(GA_CONFIGS) + len(SA_CONFIGS)
    total_runs = total_instances * total_configs * RUNS_PER_CONFIG

    print(f"Iniciando experimentos:")
    print(f"- Instâncias: {total_instances}")
    print(f"- Configurações GA: {len(GA_CONFIGS)}")
    print(f"- Configurações SA: {len(SA_CONFIGS)}")
    print(f"- Execuções por config: {RUNS_PER_CONFIG}")
    print(f"- Total de execuções: {total_runs}\n")

    execution_counter = 0

    for inst_idx, row in df_instances.iterrows():
        instance_id = row["instance_id"]
        n = int(row["n"])
        correlation = row["correlation"]
        capacity = int(row["capacity"])
        optimum_value = int(row["optimum_value"])
        weights = parse_int_list(row["weights"])
        values = parse_int_list(row["values"])

        # Loop por configurações GA
        for config_name, orig_params in GA_CONFIGS.items():
            params = orig_params.copy()
            # Ajustar parâmetro de mutação para valor numérico se necessário
            if params["mutation_rate"] == "0.5/n":
                params["mutation_rate"] = 0.5 / n
            elif params["mutation_rate"] == "2/n":
                params["mutation_rate"] = 2.0 / n

            for run_idx in range(RUNS_PER_CONFIG):
                run_seed = BASE_SEED + inst_idx * 1000 + run_idx
                
                start_time = time.perf_counter()
                res = run_genetic_algorithm(
                    weights=weights,
                    values=values,
                    capacity=capacity,
                    seed=run_seed,
                    **params
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                best_val = res["value"]
                best_weight = res["weight"]
                evals = res["evaluations"]
                iters = res["iterations_executed"]

                gap_percent = ((optimum_value - best_val) / optimum_value * 100.0) if optimum_value > 0 else 0.0

                results.append({
                    "instance_id": instance_id,
                    "n": n,
                    "correlation": correlation,
                    "algorithm": "GA",
                    "config_name": config_name,
                    "run": run_idx,
                    "seed": run_seed,
                    "best_value_found": best_val,
                    "best_weight_found": best_weight,
                    "optimum_value": optimum_value,
                    "gap_percent": gap_percent,
                    "execution_time_ms": elapsed_ms,
                    "evaluations": evals,
                    "iterations_executed": iters
                })
                execution_counter += 1

        # Loop por configurações SA
        for config_name, params in SA_CONFIGS.items():
            for run_idx in range(RUNS_PER_CONFIG):
                run_seed = BASE_SEED + inst_idx * 1000 + run_idx
                
                start_time = time.perf_counter()
                res = run_simulated_annealing(
                    weights=weights,
                    values=values,
                    capacity=capacity,
                    seed=run_seed,
                    **params
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                best_val = res["value"]
                best_weight = res["weight"]
                evals = res["evaluations"]
                iters = res["iterations_executed"]

                gap_percent = ((optimum_value - best_val) / optimum_value * 100.0) if optimum_value > 0 else 0.0

                results.append({
                    "instance_id": instance_id,
                    "n": n,
                    "correlation": correlation,
                    "algorithm": "SA",
                    "config_name": config_name,
                    "run": run_idx,
                    "seed": run_seed,
                    "best_value_found": best_val,
                    "best_weight_found": best_weight,
                    "optimum_value": optimum_value,
                    "gap_percent": gap_percent,
                    "execution_time_ms": elapsed_ms,
                    "evaluations": evals,
                    "iterations_executed": iters
                })
                execution_counter += 1

        if (inst_idx + 1) % 10 == 0 or (inst_idx + 1) == total_instances:
            print(f"Progresso: {inst_idx + 1}/{total_instances} instâncias processadas ({execution_counter}/{total_runs} execuções).")

    df_out = pd.DataFrame(results)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nExperimentos concluídos com sucesso! Resultados salvos em: {OUTPUT_CSV}")

if __name__ == "__main__":
    run_all_experiments()