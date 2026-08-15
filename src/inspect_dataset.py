from pathlib import Path
import ast
import re
import pandas as pd


RAW_DIR = Path("data/raw")


def parse_list_cell(value):
    """
    Converte células como '[1, 2, 3]' ou '1 2 3' para lista de inteiros.
    Funciona de forma tolerante para diferentes formatos textuais.
    """
    if pd.isna(value):
        return []

    text = str(value).strip()

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [int(float(x)) for x in parsed]
    except Exception:
        pass

    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    return [int(float(x)) for x in numbers]


def find_column(columns, candidates):
    normalized = {col.lower().strip().replace(" ", "_"): col for col in columns}

    for candidate in candidates:
        key = candidate.lower().strip().replace(" ", "_")
        if key in normalized:
            return normalized[key]

    return None


def inspect_csv(path):
    df = pd.read_csv(path)

    print("=" * 80)
    print(f"Arquivo: {path.name}")
    print(f"Dimensão: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(f"Colunas: {list(df.columns)}")
    print("\nPrimeiras 3 linhas:")
    print(df.head(3).to_string(index=False))

    weights_col = find_column(df.columns, ["weights", "weight", "pesos"])
    values_col = find_column(df.columns, ["prices", "price", "values", "value", "valores"])
    capacity_col = find_column(df.columns, ["capacity", "capacidade"])
    best_value_col = find_column(df.columns, ["best price", "best_price", "best value", "best_value"])
    best_picks_col = find_column(df.columns, ["best picks", "best_picks", "picks"])

    print("\nColunas identificadas:")
    print(f"weights_col    = {weights_col}")
    print(f"values_col     = {values_col}")
    print(f"capacity_col   = {capacity_col}")
    print(f"best_value_col = {best_value_col}")
    print(f"best_picks_col = {best_picks_col}")

    if weights_col and values_col:
        sample = df.head(100).copy()
        sample["n_weights"] = sample[weights_col].apply(lambda x: len(parse_list_cell(x)))
        sample["n_values"] = sample[values_col].apply(lambda x: len(parse_list_cell(x)))

        print("\nQuantidade de itens detectada nas primeiras 100 linhas:")
        print("weights:", sample["n_weights"].value_counts().sort_index().to_dict())
        print("values :", sample["n_values"].value_counts().sort_index().to_dict())

    if capacity_col:
        print("\nResumo da capacidade:")
        print(df[capacity_col].describe())

    if best_value_col:
        print("\nResumo do melhor valor conhecido:")
        print(df[best_value_col].describe())


def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "Nenhum CSV encontrado em data/raw. "
            "Verifique se o download do Kaggle foi feito corretamente."
        )

    for path in csv_files:
        inspect_csv(path)


if __name__ == "__main__":
    main()
