import json
from pathlib import Path

import pandas as pd


INSTANCES_DIR = Path("data/generated/instances")
OUTPUT_PATH = Path("data/processed/instances.csv")


def load_instance(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    metadata = data.get("metadata", {})

    instance_id = metadata.get("instance_id", path.stem)
    seed = metadata.get("seed")
    n = int(data["n"])
    capacity = int(data["capacity"])
    correlation = str(data["correlation_type"])

    values = [int(x) for x in data["values"]]
    weights = [int(x) for x in data["weights"]]

    if len(values) != n:
        raise ValueError(f"{path}: quantidade de valores difere de n.")

    if len(weights) != n:
        raise ValueError(f"{path}: quantidade de pesos difere de n.")

    row = {
        "instance_id": instance_id,
        "source_file": path.name,
        "n": n,
        "correlation": correlation,
        "capacity": capacity,
        "seed": seed,
        "values": ",".join(map(str, values)),
        "weights": ",".join(map(str, weights)),
    }

    return row


def main() -> None:
    if not INSTANCES_DIR.exists():
        raise FileNotFoundError(
            "Diretório data/generated/instances não encontrado. "
            "Execute primeiro src/generate_instances.py."
        )

    files = sorted(INSTANCES_DIR.glob("*.json"))

    if not files:
        raise FileNotFoundError("Nenhuma instância JSON encontrada.")

    rows = [load_instance(path) for path in files]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Arquivo salvo em: {OUTPUT_PATH}")
    print(f"Total de instâncias: {len(df)}")
    print()
    print("Resumo por tamanho e correlação:")
    print(df.groupby(["n", "correlation"]).size())


if __name__ == "__main__":
    main()
