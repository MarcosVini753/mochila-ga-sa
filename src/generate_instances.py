from pathlib import Path
import subprocess

import numpy as np
from pisinger_knapsack import (
    CorrelationType,
    generate_instance,
    save_instance,
)


OUTPUT_DIR = Path("data/generated/instances")
MANIFEST_PATH = Path("data/generated/manifest.json")

SIZES = [20, 50, 100]
CORRELATIONS = [
    CorrelationType.UNCORRELATED,
    CorrelationType.WEAKLY_CORRELATED,
    CorrelationType.STRONGLY_CORRELATED,
]

INSTANCES_PER_GROUP = 10
BASE_SEED = 20260706


def correlation_label(correlation_type: CorrelationType) -> str:
    value = correlation_type.value

    if value == "uncorrelated":
        return "uncorrelated"
    if value == "weakly":
        return "weakly"
    if value == "strongly":
        return "strongly"

    return str(value)


def build_manifest_with_cli() -> None:
    subprocess.run(
        [
            "pisinger-knapsack",
            "manifest",
            "build",
            "--dir",
            str(OUTPUT_DIR),
            "--out",
            str(MANIFEST_PATH),
        ],
        check=True,
    )


def verify_manifest_with_cli() -> None:
    subprocess.run(
        [
            "pisinger-knapsack",
            "manifest",
            "verify",
            "--dir",
            str(OUTPUT_DIR),
            "--manifest",
            str(MANIFEST_PATH),
        ],
        check=True,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Remove instâncias antigas para evitar mistura de experimentos.
    for old_file in OUTPUT_DIR.glob("*.json"):
        old_file.unlink()

    if MANIFEST_PATH.exists():
        MANIFEST_PATH.unlink()

    total = 0

    for n in SIZES:
        for correlation in CORRELATIONS:
            label = correlation_label(correlation)

            for instance_index in range(INSTANCES_PER_GROUP):
                seed = BASE_SEED + (n * 1000) + (len(label) * 100) + instance_index
                rng = np.random.default_rng(seed)

                instance = generate_instance(
                    rng=rng,
                    n=n,
                    correlation_type=correlation,
                    R=1000,
                )

                instance_id = f"n{n}_{label}_{instance_index:02d}"
                output_path = OUTPUT_DIR / f"{instance_id}.json"

                save_instance(
                    instance,
                    output_path,
                    metadata={
                        "instance_id": instance_id,
                        "seed": seed,
                        "n": n,
                        "correlation": label,
                        "R": 1000,
                    },
                )

                print(f"Gerada: {output_path}")
                total += 1

    build_manifest_with_cli()
    verify_manifest_with_cli()

    print()
    print(f"Total de instâncias geradas: {total}")
    print(f"Manifesto salvo em: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
