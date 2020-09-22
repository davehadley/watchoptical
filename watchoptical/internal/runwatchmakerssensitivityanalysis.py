from dataclasses import dataclass


@dataclass(frozen=True)
class WatchMakersSensitivityAnalysisConfig:
    inputdirectory: str
    outputdirectory: str


def runwatchmakerssensitivityanalysis(config: WatchMakersSensitivityAnalysisConfig):
    pass
