"""
Geração de gráficos comparativos para a análise de GA e SA no Problema da Mochila 0/1.

Gera em results/figures/:
1. ga_config_comparison.png — comparação das variações de GA
2. sa_config_comparison.png — comparação das variações de SA
3. gap_by_group.png — comparação final do Gap Médio (Melhor GA vs Melhor SA)
4. time_by_group.png — comparação final do Tempo Médio de Execução
5. optimal_rate_by_group.png — comparação final da Taxa de Obtenção do Ótimo
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

SUMMARY_BY_CONFIG_CSV = Path("results/summary_by_config.csv")
SUMMARY_BEST_CSV = Path("results/summary.csv")
FIGURES_DIR = Path("results/figures")

plt.style.use('ggplot')
plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})

RAW_RUNS_CSV = Path("results/raw_runs.csv")

def generate_plots():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if not SUMMARY_BY_CONFIG_CSV.exists() or not SUMMARY_BEST_CSV.exists() or not RAW_RUNS_CSV.exists():
        raise FileNotFoundError("Arquivos de resumo/brutos não encontrados em results/")

    df_raw = pd.read_csv(RAW_RUNS_CSV)
    df_raw["is_optimal"] = (df_raw["gap_percent"] == 0.0).astype(int)

    # Nível 1: Média por instância (90 instâncias por configuração)
    inst_summary = df_raw.groupby(["algorithm", "config_name", "instance_id"]).agg(
        inst_mean_gap=("gap_percent", "mean"),
        inst_optimal_rate=("is_optimal", "mean"),
        inst_mean_time_ms=("execution_time_ms", "mean"),
        inst_mean_evals=("evaluations", "mean"),
        inst_mean_iters=("iterations_executed", "mean")
    ).reset_index()

    df_config = pd.read_csv(SUMMARY_BY_CONFIG_CSV)
    df_best = pd.read_csv(SUMMARY_BEST_CSV)

    # -------------------------------------------------------------
    # 1. Gráfico de Análise de Parâmetros do GA (Desvio Padrão sobre as 90 instâncias)
    # -------------------------------------------------------------
    ga_summary = inst_summary[inst_summary["algorithm"] == "GA"].groupby("config_name").agg(
        mean_gap=("inst_mean_gap", "mean"),
        std_gap=("inst_mean_gap", "std"),
        optimal_rate=("inst_optimal_rate", "mean"),
        mean_evals=("inst_mean_evals", "mean")
    ).reset_index().sort_values(by="mean_gap")

    x = np.arange(len(ga_summary))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 5))
    color = 'tab:red'
    ax1.set_xlabel('Configuração do GA')
    ax1.set_ylabel('Gap Médio (%)', color=color)
    ax1.bar(x - width/2, ga_summary['mean_gap'], width, yerr=ga_summary['std_gap'], capsize=4, color=color, label='Gap Médio (%)', alpha=0.85)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Taxa de Ótimo (%)', color=color)
    ax2.bar(x + width/2, ga_summary['optimal_rate'] * 100, width, color=color, label='Taxa de Ótimo (%)', alpha=0.85)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.xticks(x, ga_summary['config_name'], rotation=15)
    plt.title('Sensibilidade de Parâmetros do Algoritmo Genético (GA)')
    plt.savefig(FIGURES_DIR / "ga_config_comparison.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 2. Gráfico de Análise de Parâmetros do SA (Desvio Padrão sobre as 90 instâncias)
    # -------------------------------------------------------------
    sa_summary = inst_summary[inst_summary["algorithm"] == "SA"].groupby("config_name").agg(
        mean_gap=("inst_mean_gap", "mean"),
        std_gap=("inst_mean_gap", "std"),
        optimal_rate=("inst_optimal_rate", "mean"),
        mean_evals=("inst_mean_evals", "mean"),
        mean_iters=("inst_mean_iters", "mean")
    ).reset_index().sort_values(by="mean_gap")

    x = np.arange(len(sa_summary))

    fig, ax1 = plt.subplots(figsize=(10, 5))
    color = 'tab:red'
    ax1.set_xlabel('Configuração do SA')
    ax1.set_ylabel('Gap Médio (%)', color=color)
    ax1.bar(x - width/2, sa_summary['mean_gap'], width, yerr=sa_summary['std_gap'], capsize=4, color=color, label='Gap Médio (%)', alpha=0.85)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Taxa de Ótimo (%)', color=color)
    ax2.bar(x + width/2, sa_summary['optimal_rate'] * 100, width, color=color, label='Taxa de Ótimo (%)', alpha=0.85)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.xticks(x, sa_summary['config_name'], rotation=15)
    plt.title('Sensibilidade de Parâmetros do Simulated Annealing (SA)')
    plt.savefig(FIGURES_DIR / "sa_config_comparison.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 3. Comparação por Tamanho da Instância (n) e por Configuração
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    gap_n_pivot = df_config.pivot_table(index="config_name", columns="n", values="mean_gap", aggfunc="mean")
    gap_n_pivot.plot(kind='bar', figsize=(11, 5), width=0.7)
    plt.title('Gap Médio (%) por Configuração e Tamanho (n)')
    plt.xlabel('Configuração')
    plt.ylabel('Gap Médio (%)')
    plt.xticks(rotation=30)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Tamanho (n)')
    plt.savefig(FIGURES_DIR / "gap_by_config_and_n.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 4. Diagrama de Dispersão: Qualidade (Gap) vs Orçamento Computacional
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10.5, 6.2), constrained_layout=True)
    all_configs = pd.concat([ga_summary.assign(alg='GA'), sa_summary.assign(alg='SA')])

    # Os pontos do GA ficam concentrados em aproximadamente 20.200 avaliações.
    # Deslocamentos individuais mantêm os rótulos legíveis sem alterar os dados.
    annotation_offsets = {
        "GA_BASE": (120, 100),
        "GA_CROSS_060": (120, 80),
        "GA_CROSS_095": (120, 60),
        "GA_MUT_HIGH": (120, 40),
        "GA_MUT_LOW": (120, 20),
        "GA_TOUR_5": (120, 8),
        "GA_POP_50": (8, 8),
        "GA_POP_200": (-8, 10),
        "SA_BASE": (8, 14),
        "SA_COOL_FAST": (8, 8),
        "SA_COOL_SLOW": (8, 8),
        "SA_T0_HIGH": (8, -12),
        "SA_T0_LOW": (8, 8),
    }

    for alg, color, marker in [('GA', '#2b5c8f', 'o'), ('SA', '#d95f02', 's')]:
        sub = all_configs[all_configs['alg'] == alg]
        ax.scatter(sub['mean_evals'], sub['mean_gap'], color=color, marker=marker, s=100, label=alg, zorder=3)
        for _, row in sub.iterrows():
            config_name = row['config_name']
            offset = annotation_offsets.get(config_name, (8, 8))
            horizontal_alignment = 'right' if offset[0] < 0 else 'left'
            vertical_alignment = 'top' if offset[1] < 0 else 'bottom'
            ax.annotate(
                config_name,
                (row['mean_evals'], row['mean_gap']),
                textcoords="offset points",
                xytext=offset,
                ha=horizontal_alignment,
                va=vertical_alignment,
                fontsize=8.5,
                color=color,
                zorder=4,
                bbox={
                    "boxstyle": "round,pad=0.2",
                    "facecolor": "white",
                    "edgecolor": color,
                    "linewidth": 0.5,
                    "alpha": 0.9,
                },
                arrowprops={
                    "arrowstyle": "-",
                    "color": color,
                    "linewidth": 0.7,
                    "alpha": 0.7,
                },
            )

    ax.set_title('Qualidade (Gap Médio) × Orçamento Computacional (Avaliações)')
    ax.set_xlabel('Número Médio de Avaliações de Fitness')
    ax.set_ylabel('Gap Médio (%) [Menor é Melhor]')
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Algoritmo')
    fig.savefig(FIGURES_DIR / "pareto_quality_cost.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # 5. Comparação Final GA vs SA: Gap Médio por Tamanho (n)
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 5))
    gap_pivot = df_best.pivot_table(index="n", columns="algorithm", values="mean_gap", aggfunc="mean")
    gap_pivot.plot(kind='bar', figsize=(8, 5), color=['#2b5c8f', '#d95f02'], width=0.6)
    plt.title('Gap Médio em Relação ao Ótimo (%) por Tamanho (n)')
    plt.xlabel('Tamanho da Instância (n)')
    plt.ylabel('Gap Médio (%)')
    plt.legend(title='Algoritmo (Melhor Config)')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(FIGURES_DIR / "gap_by_group.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 6. Comparação Final GA vs SA: Tempo Médio de Execução (ms)
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 5))
    time_pivot = df_best.pivot_table(index="n", columns="algorithm", values="mean_time_ms", aggfunc="mean")
    time_pivot.plot(kind='bar', figsize=(8, 5), color=['#2b5c8f', '#d95f02'], width=0.6)
    plt.title('Tempo Médio de Execução (ms) por Tamanho (n)')
    plt.xlabel('Tamanho da Instância (n)')
    plt.ylabel('Tempo Médio (ms)')
    plt.legend(title='Algoritmo (Melhor Config)')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(FIGURES_DIR / "time_by_group.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 7. Comparação Final GA vs SA: Taxa de Obtenção do Ótimo (%)
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 5))
    opt_pivot = df_best.pivot_table(index="n", columns="algorithm", values="optimal_rate", aggfunc="mean") * 100
    opt_pivot.plot(kind='bar', figsize=(8, 5), color=['#2b5c8f', '#d95f02'], width=0.6)
    plt.title('Taxa de Obtenção do Ótimo (%) por Tamanho (n)')
    plt.xlabel('Tamanho da Instância (n)')
    plt.ylabel('Taxa de Ótimo (%)')
    plt.legend(title='Algoritmo (Melhor Config)')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(FIGURES_DIR / "optimal_rate_by_group.png", dpi=300)
    plt.close()

    print(f"Gráficos gerados com sucesso na pasta: {FIGURES_DIR}")

if __name__ == "__main__":
    generate_plots()
