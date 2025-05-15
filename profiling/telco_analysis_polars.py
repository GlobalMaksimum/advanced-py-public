import polars as pl
from rich.console import Console

c = Console()

"""
    Low memory : True - 17 sec
    Low memory: False - 16 sec
"""

low_memory = True
c.print(
    pl.read_ndjson("data/telco/capstone.*.jsonl.gz", low_memory=low_memory)
    .group_by("service_type")
    .agg(pl.mean("tenure"), pl.mean("age"))
)

c.print(
    pl.read_ndjson("data/telco/capstone.*.jsonl.gz", low_memory=low_memory)
    .group_by("service_type", "churn")
    .agg(pl.mean("roaming_usage"), pl.mean("avg_call_duration"))
)
