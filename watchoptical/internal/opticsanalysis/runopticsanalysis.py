import itertools
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, MutableMapping, NamedTuple, Optional

import boost_histogram as bh
import numpy as np
from dask.bag import Bag
from pandas import DataFrame

from watchoptical.internal.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.eventtype import eventtypefromfile
from watchoptical.internal.histoutils import ExposureWeightedHistogram
from watchoptical.internal.opticsanalysis.selection import SelectionDefs
from watchoptical.internal.opticsanalysis.variable import VariableDefs
from watchoptical.internal.utils import shelveddecorator, sumlist, summap
from watchoptical.internal.wmdataset import WatchmanDataset


def _add_accum(left, right):
    c = deepcopy(left)
    c += right
    return c


@dataclass
class OpticsAnalysisResult:
    hist: MutableMapping[str, ExposureWeightedHistogram] = field(default_factory=dict)
    scatter: MutableMapping[str, dict] = field(default_factory=dict)

    def __add__(self, other):
        return OpticsAnalysisResult(
            hist=summap([self.hist, other.hist]),
            scatter=summap(
                [self.scatter, other.scatter],
                lambda lhs, rhs: summap([lhs, rhs], _add_accum),
            ),
        )

    def __str__(self) -> str:
        return (
            f"OpticsAnalysisResult({len(self.hist)} hist, {len(self.scatter)} scatter)"
        )


class Category(NamedTuple):
    eventtype: str
    attenuation: float

    @classmethod
    def fromAnalysisEventTuple(cls, tree: AnalysisEventTuple) -> "Category":
        return Category(_eventtypecategory(tree), _attenuationfromtree(tree))


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
    selection: Callable[[DataFrame], DataFrame] = SelectionDefs.nominal,
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
    # this should return the expect rate for this process in number of events per second
    macro = str(tree.macro)
    match = re.search(
        r"(?s).*OPTICS.*?doped_water.*?ABSLENGTH_value2.*?\[(.*?),.*", macro
    )
    if match:
        return float(match.group(1))
    raise ValueError("failed to parse macro", macro)


def _makebasicattenuationscatter(tree: AnalysisEventTuple, store: OpticsAnalysisResult):
    category = Category.fromAnalysisEventTuple(tree)
    if category == "IBD":
        attenuation = _attenuationfromtree(tree)
        category = f"{attenuation:0.5e}"
        totalq = tree.anal.pmt_q.groupby("entry").sum().array
        # histogram total Q
        store.hist["ibd_total_charge_by_attenuation"] = ExposureWeightedHistogram(
            bh.axis.Regular(300, 0.0, 150.0)
        ).fill(category, tree.exposure, totalq)
        # calculate mean Q
        meanq = defaultdict(bh.accumulators.WeightedMean)
        meanq[category].fill(totalq)
        store.scatter["idb_total_charge_by_attenuation_mean"] = meanq
        # calculate mean Q > 10
        meanq_gt10 = defaultdict(bh.accumulators.WeightedMean)
        meanq_gt10[category].fill(totalq[totalq > 10.0])
        store.scatter["idb_total_charge_by_attenuation_mean_gt10"] = meanq_gt10
    return


def _makesensitivityscatter(tree: AnalysisEventTuple, store: OpticsAnalysisResult):
    attenuation = _attenuationfromtree(tree)
    category = f"{attenuation:0.5e}"
    sensitivity = defaultdict(bh.accumulators.WeightedMean)
    sensitivity[category].fill(tree.sensitivity.metric)
    store.scatter["sensitvity_metric"] = sensitivity
    return


def _analysis(tree: AnalysisEventTuple) -> OpticsAnalysisResult:
    # histo.fill(category, tree.exposure, tree.bonsai.n9.array)
    result = OpticsAnalysisResult()
    _makebasichistograms(tree, result.hist)
    _makebasicattenuationscatter(tree, result)
    _makesensitivityscatter(tree, result)
    return result


def runopticsanalysis(dataset: WatchmanDataset) -> Bag:
    hist = (
        AnalysisEventTuple.fromWatchmanDataset(dataset)
        .map(_analysis)
        .reduction(sumlist, sumlist)
    )
    return hist


@shelveddecorator(lambda d: f"opticsanalysis/{d.name}")
def shelvedopticsanalysis(dataset: WatchmanDataset) -> OpticsAnalysisResult:
    return runopticsanalysis(dataset).compute()
