from typing import NamedTuple

from watchopticalanalysis.internal.eventtype import eventtypefromfile
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple


class Category(NamedTuple):
    eventtype: str
    attenuation: float
    scattering: float

    @classmethod
    def fromAnalysisEventTuple(cls, tree: AnalysisEventTuple) -> "Category":
        return Category(
            _eventtypecategory(tree),
            _attenuationfromtree(tree),
            _scatteringfromtree(tree),
        )

    def __str__(self):
        return f"({self.eventtype}, att={self.attenuation}, scat={self.scattering})"


def _eventtypecategory(tree: AnalysisEventTuple) -> str:
    et = eventtypefromfile(tree.analysisfile)
    result = "IBD" if "ibd" in et else "Background"
    return result


def _attenuationfromtree(tree: AnalysisEventTuple) -> float:
    if tree.generatemcconfig.injectratdb is not None:
        for v in tree.generatemcconfig.injectratdb.values():
            if v.config.attenuation is not None:
                return v.config.attenuation
    return 1.0


def _scatteringfromtree(tree: AnalysisEventTuple) -> float:
    if tree.generatemcconfig.injectratdb is not None:
        for v in tree.generatemcconfig.injectratdb.values():
            if v.config.scattering is not None:
                return v.config.scattering
    return 1.0
