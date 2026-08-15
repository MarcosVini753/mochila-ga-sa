import sys
import time
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from dynamic_programming import exact_knapsack_value
from knapsack import parse_int_list


INPUT_PATH = Path("data/processed/instances.csv")
OUTPUT_PATH = Path("data/processed/instances_with_optimum.csv")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Arquivo data/processed/instances.csv não encontrado. "
            "Execute primeiro: python3 src/dataset_loader.py"
        )

    df = pd.read_csv(INPUT_PATH)

    rows = []
    start_all = time.perf_counter()

    for index, row in df.iterrows():
        weights = parse_int_list(row["weights"])
        values = parse_int_list(row["values"])
        capacity = int(row["capacity"])

        start = time.perf_counter()

        optimum_value = exact_knapsack_value(
            weights=weights,
            values=values,
            capacity=capacity,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        new_row = row.to_dict()
        new_row["optimum_value"] = optimum_value
        new_row["optimum_time_ms"] = elapsed_ms

        rows.append(new_row)

        print(
            f"[{index + 1:03d}/{len(df)}] "
            f"{row['instance_id']} | "
            f"n={row['n']} | "
            f"{row['correlation']} | "
            f"ótimo={optimum_value} | "
            f"{elapsed_ms:.2f} ms"
        )

    output_df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_PATH, index=False)

    total_elapsed = time.perf_counter() - start_all

    print()
    print(f"Arquivo salvo em: {OUTPUT_PATH}")
    print(f"Total de instâncias processadas: {len(output_df)}")
    print(f"Tempo total: {total_elapsed:.2f} s")
    print()
    print("Resumo do valor ótimo por tamanho e correlação:")
    print(
        output_df
        .groupby(["n", "correlation"])["optimum_value"]
        .agg(["count", "mean", "min", "max"])
    )


if __name__ == "__main__":
    main()
