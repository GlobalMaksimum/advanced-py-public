from pathlib import Path

from rich.console import Console
import gzip
import json


from collections import defaultdict

## 377.470.254
# age: 3M
# tenure: 3.5M
# service_type: 10 M
# call_duration: 5M
# roaming_usage: 5M


# d = {
#     "churn":[...],
#     "avg_call_duration":np.array
# }


def mean(
    rowsource: list[dict],
    group: tuple[str],
    measure: tuple[str],
    skip_none: bool = True,
) -> dict[str, dict[str, tuple[float, int]]]:
    """
    d = {"Prepaid": {
        "avg_call":
        "roaming"
    }
    """
    d = {}

    count = 0

    for row in rowsource:
        key = tuple([row[g] for g in group])

        if all((row[m] is not None for m in measure)):
            dd = d.get(key, defaultdict(int))

            for m in measure:
                dd[m] += row[m]

            d[key] = dd

            count += 1

    for key in d:
        for m in measure:
            d[key][m] = (
                d[key][m] / count,
                count,
            )

    return d


class TelcoStats:
    def __init__(self, paths):
        self.paths = [paths]
        self.print = Console().log

        self._cache()

    def _cache(self):
        self.cache = []

        for path in self.paths:
            with gzip.open(path) as fp:
                for line in fp:
                    d = json.loads(line)

                    # match d["service_type"]:
                    #     case "Prepaid":
                    #         d["service_type"] = 0
                    #     case "Postpaid":
                    #         d["service_type"] = 1
                    #     case "Broadband":
                    #         d["service_type"] = 2

                    self.cache.append(
                        {
                            k: v
                            for k, v in d.items()
                            if k
                            in [
                                "churn",
                                "age",
                                "tenure",
                                "service_type",
                                "avg_call_duration",
                                "roaming_usage",
                            ]
                        }
                    )

        self.print(self.cache[:3])

    def run(self):
        self.age_and_tenure()
        self.avg_usage()
        self.service_quality()
        self.app_usage()

    def age_and_tenure(self):
        self.print("Calculating age & tenure")

        """
        select service_type, avg(age), avg(tenure) 
        from files... group by 1
        """

        stats = mean(
            self.cache,
            group=("service_type",),
            measure=("tenure", "age"),
            skip_none=True,
        )

        return stats

        # self.print(stats)

    def avg_usage(self):
        self.print("Calculating Usage Statistics")

        """
        select service_type, avg(avg_call_duration), avg(roaming_usage) 
        from files... group by 1
        """

        stats = mean(
            self.cache,
            group=(
                "service_type",
                "churn",
            ),
            measure=("avg_call_duration", "roaming_usage"),
            skip_none=True,
        )

        return stats

        # self.print(stats)

    def service_quality(self): ...

    def app_usage(self): ...


def merge_stats(*args) -> dict[str, dict[str, float]]:
    console = Console()
    # console.print(args)
    total = {key: {} for key in args[0]}
    count = {key: {} for key in args[0]}
    stats = {key: {} for key in args[0]}

    for key in total:
        for m in args[0][key]:
            total[key][m] = 0
            count[key][m] = 0

    for partial_stat in args:
        for key in partial_stat:
            for m in partial_stat[key]:
                try:
                    total[key][m] += partial_stat[key][m][0] * partial_stat[key][m][1]
                    count[key][m] += partial_stat[key][m][1]
                except KeyError as e:
                    print(partial_stat[key][m])
                    raise Exception(e)

    for key in total:
        for m in total[key]:
            stats[key][m] = total[key][m] / count[key][m]

    return stats


def useless(path):
    return TelcoStats(path).age_and_tenure()


if __name__ == "__main__":
    # stats = TelcoStats(Path("data/telco/").glob("*.jsonl.gz"))
    # stats1 = TelcoStats(Path("data/telco/").glob("capstone.1.jsonl.gz"))
    # stats2 = TelcoStats(Path("data/telco/").glob("capstone.2.jsonl.gz"))

    # partial1, partial2 = (
    #    TelcoStats(Path("data/telco/").glob("capstone.1.jsonl.gz")).age_and_tenure(),
    #    TelcoStats(Path("data/telco/").glob("capstone.2.jsonl.gz")).age_and_tenure(),
    # )

    from multiprocessing import Pool
    from concurrent.futures import ThreadPoolExecutor

    console = Console()

    console.print([p for p in Path("data/telco/").glob("*.jsonl.gz")])

    # with Pool(processes=2) as pool:
    #     partials = pool.map(
    #         useless, [p for p in Path("data/telco/").glob("*.jsonl.gz")]
    #     )

    with ThreadPoolExecutor(max_workers=2) as pool:
        partials = pool.map(
            useless, [p for p in Path("data/telco/").glob("*.jsonl.gz")]
        )

    stats = merge_stats(*partials)

    console.print(stats)

    # stats1.run()
    # stats2.run()

    # a + b + c + d = (a+b) +(c+d)

    """
    
    + Merge partial sums for final result
    - Thread Parallism
    - Process Parallism


    """


# (mean1, count1) + (mean2, count2) -> (mean1 * count1 + mean2*count2)/(count1 + count2)
