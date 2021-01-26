from typing import Optional

from watchopticalanalysis.algorithm import Algorithm
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple


class Test(Algorithm["Test.Result", "Test.Result"]):
    """Test algorithm does nothing.
    Intended to test machinary around processing data."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    class Result:
        def __add__(self, rhs: "Test.Result") -> "Test.Result":
            return Test.Result()

    def key(self) -> Optional[str]:
        return "TestAlgorithm"

    def apply(self, data: AnalysisEventTuple) -> "Test.Result":
        return self.Result()

    def finish(self, result: "Test.Result") -> "Test.Result":
        return self.Result()
