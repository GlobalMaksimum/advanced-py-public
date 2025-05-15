import pandas as pd
from rich.console import Console
from pathlib import Path


"""
    Usage: 709 MB max memory
    Usage: 510 MB max memory (with dtype set)
    Elapsed time: 43 sec

"""


if __name__ == "__main__":
    c = Console()

    # c.print(df.head())

    dfs = []

    for path in Path("data/telco").glob("capstone.*.jsonl.gz"):
        df = pd.concat(
            (
                chunk[
                    [
                        "churn",
                        "age",
                        "tenure",
                        "service_type",
                        "avg_call_duration",
                        "roaming_usage",
                    ]
                ]
                for chunk in pd.read_json(
                    path,
                    compression="gzip",
                    lines=True,
                    chunksize=100_000,
                    dtype={
                        "age": "int32",
                        "tenure": "int32",
                        "service_type": "category",
                        "avg_call_duration": "float32",
                        "roaming_usage": "float32",
                    },
                )
            ),
            axis=0,
        )
        # df.info(verbose=False, memory_usage="deep")
        # c.print(df.memory_usage(index=False))
        # sys.exit(1)
        dfs.append(df)

    df = pd.concat(dfs, axis=0)
    dfs = []

    c.print(df.groupby("service_type").agg({"tenure": ["mean"], "age": ["mean"]}))

    c.print(
        df.groupby(["service_type", "churn"]).agg(
            {"avg_call_duration": ["mean"], "roaming_usage": ["mean"]}
        )
    )
