import itertools
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, DefaultDict, MutableMapping, NamedTuple, Optional

import boost_histogram as bh
import numpy as np
from dask.bag import Bag
from pandas import DataFrame

from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.histoutils import CategoryMean, ExposureWeightedHistogram
from watchoptical.internal.histoutils.categoryselectionstats import (
    CategorySelectionStats,
)
from watchoptical.internal.histoutils.selection import Selection
from watchoptical.internal.ignoreerrors import ignoreerrors
from watchoptical.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.opticsanalysis.eventtype import eventtypefromfile
from watchoptical.internal.opticsanalysis.selectiondefs import SelectionDefs
from watchoptical.internal.opticsanalysis.variable import VariableDefs
from watchoptical.internal.utils.cache import cachedcallable
from watchoptical.internal.utils.collectionutils import sumlist, summap


def _add_accum(left, right):
    c = deepcopy(left)
    c += right
    return c


@dataclass
class OpticsAnalysisResult:
    hist: MutableMapping[str, ExposureWeightedHistogram] = field(default_factory=dict)
    scatter: MutableMapping[str, CategoryMean] = field(default_factory=dict)
    selectionstats: MutableMapping[str, CategorySelectionStats] = field(
        default_factory=dict
    )

    def __add__(self, other):
        return OpticsAnalysisResult(
            hist=summap([self.hist, other.hist]),
            scatter=summap(
                [self.scatter, other.scatter],
                # lambda lhs, rhs: summap([lhs, rhs], _add_accum),
            ),
            selectionstats=summap([self.selectionstats, other.selectionstats]),
        )

    def __str__(self) -> str:
        return (
            f"OpticsAnalysisResult({len(self.hist)} hist, {len(self.scatter)} scatter)"
        )


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


def _eventtypecategory(tree: AnalysisEventTuple) -> str:
    et = eventtypefromfile(tree.analysisfile)
    result = "IBD" if "IBD" in et else "Background"
    return result


def _hascoincidence(data):
    t = data.groupby("mcid").t
    count = t.transform("count")
    dt = t.transform(lambda t: t.max() - t.min())
    return (count >= 2) & (dt.abs() < 50.0)


def _makebonsaihistogram(
    tree: AnalysisEventTuple,
    binning: bh.axis.Axis,
    x: Callable[[DataFrame], Any],
    w: Optional[Callable[[DataFrame], Any]] = None,
    selection: Selection = SelectionDefs.nominal.value,
    subevent: int = 0,
) -> ExposureWeightedHistogram:
    histo = ExposureWeightedHistogram(binning)
    category = Category.fromAnalysisEventTuple(tree)
    data = selection(tree.bonsai).groupby("mcid").nth(subevent)
    xv = np.asarray(x(data))
    wv = None if not w else np.asarray(w(data))
    histo.fill(category, tree.exposure, xv, weight=wv)
    return histo


def _makebasichistograms(
    tree: AnalysisEventTuple, hist: MutableMapping[str, ExposureWeightedHistogram]
):
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, VariableDefs, (None, 0, 1)
    ):
        name = "_".join((variable.name, selection.name, "subevent" + str(subevent)))
        hist[name] = _makebonsaihistogram(
            tree, variable.value.binning, variable.value, selection=selection.value
        )
    return


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


def _weightedmeandict() -> DefaultDict[Category, bh.accumulators.WeightedMean]:
    return defaultdict(bh.accumulators.WeightedMean)


def _makebasicattenuationscatter(tree: AnalysisEventTuple, store: OpticsAnalysisResult):
    category = Category.fromAnalysisEventTuple(tree)
    if category.eventtype == "IBD":
        totalq = tree.anal.pmt_q.groupby("entry").sum().array
        # histogram total Q
        store.hist["ibd_total_charge_by_attenuation"] = ExposureWeightedHistogram(
            bh.axis.Regular(300, 0.0, 150.0)
        ).fill(category, tree.exposure, totalq)
        # calculate mean Q
        meanq = CategoryMean().fill(category, totalq)
        store.scatter["idb_total_charge_by_attenuation_mean"] = meanq
        # calculate mean Q > 10
        meanq_gt10 = CategoryMean().fill(category, totalq[totalq > 10.0])
        store.scatter["idb_total_charge_by_attenuation_mean_gt10"] = meanq_gt10
    return


def _makesensitivityscatter(tree: AnalysisEventTuple, store: OpticsAnalysisResult):
    category = Category.fromAnalysisEventTuple(tree)
    sensitivity = CategoryMean().fill(category, tree.sensitivity.metric)
    store.scatter["sensitvity_metric"] = sensitivity
    return


def _makeselectiontable(tree: AnalysisEventTuple, store: OpticsAnalysisResult):
    category = Category.fromAnalysisEventTuple(tree)
    for selection in list(SelectionDefs):
        store.selectionstats[selection.name] = CategorySelectionStats(
            selection.value
        ).fill(category, tree.bonsai, tree.exposure)


@ignoreerrors
def _analysis(tree: AnalysisEventTuple) -> OpticsAnalysisResult:
    # histo.fill(category, tree.exposure, tree.bonsai.n9.array)
    result = OpticsAnalysisResult()
    _makebasichistograms(tree, result.hist)
    _makebasicattenuationscatter(tree, result)
    _makesensitivityscatter(tree, result)
    _makeselectiontable(tree, result)
    return result


def runopticsanalysis(dataset: WatchmanDataset) -> Bag:
    hist = (
        AnalysisEventTuple.fromWatchmanDataset(dataset)
        .map(_analysis)
        .filter(lambda r: r is not None)
        .reduction(sumlist, sumlist)
    )
    return hist


@cachedcallable(lambda d: f"opticsanalysis/{d.name}")
def shelvedopticsanalysis(dataset: WatchmanDataset) -> OpticsAnalysisResult:
    return runopticsanalysis(dataset).compute()
