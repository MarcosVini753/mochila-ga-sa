"""
Sumarização dos resultados brutos gerados em results/raw_runs.csv.

Gera:
1. results/summary_by_config.csv — agregando por n, correlation, algorithm, config_name
2. results/summary.csv — resumo agregado por n, correlation, algorithm (usando a melhor configuração de cada um)
3. Determinação da melhor configuração para GA e melhor para SA com base no menor gap médio e taxa de ótimo.
"""

from pathlib import Path
import pandas as pd

RAW_RUNS_CSV = Path("results/raw_runs.csv")
SUMMARY_BY_CONFIG_CSV = Path("results/summary_by_config.csv")
SUMMARY_BEST_CSV = Path("results/summary.csv")

def summarize():
    if not RAW_RUNS_CSV.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {RAW_RUNS_CSV}")

    df = pd.read_csv(RAW_RUNS_CSV)

    # Criar coluna auxiliar is_optimal (1 se gap_percent == 0, senão 0)
    df["is_optimal"] = (df["gap_percent"] == 0.0).astype(int)

    # Agregação em dois níveis:
    # Nível 1: Média por instância (10 execuções -> 1 média de instância)
    inst_summary = df.groupby(["n", "correlation", "algorithm", "config_name", "instance_id"]).agg(
        inst_mean_gap=("gap_percent", "mean"),
        inst_optimal_rate=("is_optimal", "mean"),
        inst_mean_time_ms=("execution_time_ms", "mean"),
        inst_mean_evaluations=("evaluations", "mean"),
        inst_mean_iterations=("iterations_executed", "mean"),
        inst_mean_value=("best_value_found", "mean"),
    ).reset_index()

    # Nível 2: Estatísticas entre instâncias (10 médias de instância -> média e desvio do grupo)
    grouped = inst_summary.groupby(["n", "correlation", "algorithm", "config_name"]).agg(
        mean_value=("inst_mean_value", "mean"),
        std_value=("inst_mean_value", "std"),
        mean_gap=("inst_mean_gap", "mean"),
        std_gap=("inst_mean_gap", "std"),
        mean_time_ms=("inst_mean_time_ms", "mean"),
        std_time_ms=("inst_mean_time_ms", "std"),
        mean_evaluations=("inst_mean_evaluations", "mean"),
        std_evaluations=("inst_mean_evaluations", "std"),
        mean_iterations=("inst_mean_iterations", "mean"),
        std_iterations=("inst_mean_iterations", "std"),
        optimal_rate=("inst_optimal_rate", "mean")
    ).reset_index()

    grouped.to_csv(SUMMARY_BY_CONFIG_CSV, index=False)
    print(f"Resumo por configuração salvo em: {SUMMARY_BY_CONFIG_CSV}")

    # 2. Avaliar globalmente sobre as 90 médias de instâncias (agregação rigorosa em 2 níveis)
    global_config_summary = inst_summary.groupby(["algorithm", "config_name"]).agg(
        overall_mean_gap=("inst_mean_gap", "mean"),
        overall_std_gap=("inst_mean_gap", "std"),
        overall_optimal_rate=("inst_optimal_rate", "mean"),
        overall_mean_time_ms=("inst_mean_time_ms", "mean"),
        overall_std_time_ms=("inst_mean_time_ms", "std"),
        overall_mean_evaluations=("inst_mean_evaluations", "mean"),
        overall_mean_iterations=("inst_mean_iterations", "mean"),
    ).reset_index()

    print("\n--- Desempenho Global das Configurações de GA ---")
    ga_summary = global_config_summary[global_config_summary["algorithm"] == "GA"].sort_values(by=["overall_mean_gap", "overall_optimal_rate"], ascending=[True, False])
    print(ga_summary.to_string(index=False))

    best_ga_config = ga_summary.iloc[0]["config_name"]
    print(f"\nMelhor configuração GA escolhida: {best_ga_config}")

    print("\n--- Desempenho Global das Configurações de SA ---")
    sa_summary = global_config_summary[global_config_summary["algorithm"] == "SA"].sort_values(by=["overall_mean_gap", "overall_optimal_rate"], ascending=[True, False])
    print(sa_summary.to_string(index=False))

    best_sa_config = sa_summary.iloc[0]["config_name"]
    print(f"\nMelhor configuração SA escolhida: {best_sa_config}")

    # 3. Filtrar apenas as melhores configurações para o summary.csv principal
    df_best_ga = grouped[(grouped["algorithm"] == "GA") & (grouped["config_name"] == best_ga_config)]
    df_best_sa = grouped[(grouped["algorithm"] == "SA") & (grouped["config_name"] == best_sa_config)]

    df_summary = pd.concat([df_best_ga, df_best_sa]).sort_values(by=["n", "correlation", "algorithm"])
    df_summary.to_csv(SUMMARY_BEST_CSV, index=False)
    print(f"\nResumo da comparação dos MELHORES (GA vs SA) salvo em: {SUMMARY_BEST_CSV}")

if __name__ == "__main__":
    summarize()