from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


def plotscatter(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plotscatter(data, dest)


def _plotscatter(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    for k, d in data.scatter.items():
        # _simplescatterplot(k, d)
        pass


def _simplescatterplot():
    pass
