import datetime
from pathlib import Path
from typing import Optional

from watchopticalanalysis.algorithm import Algorithm
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple


class Timestamp(Algorithm["Timestamp.Result", "Timestamp.Result"]):
    """Write the finishing time to the output directory."""

    def __init__(self, output: Path) -> None:
        super().__init__()
        self.output = output

    class Result:
        def __add__(self, rhs: "Timestamp.Result") -> "Timestamp.Result":
            return Timestamp.Result()

    def key(self) -> Optional[str]:
        return "Timestamp"

    def apply(self, data: AnalysisEventTuple) -> "Timestamp.Result":
        return self.Result()

    def finish(self, result: "Timestamp.Result") -> "Timestamp.Result":
        self.output.mkdir(exist_ok=True, parents=True)
        filename = self.output / "timestamp.txt"
        with open(filename, "w") as f:
            f.write(str(datetime.datetime.now().isoformat()))
        return self.Result()
