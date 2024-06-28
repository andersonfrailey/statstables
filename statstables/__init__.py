from statstables import tables, renderers, utils, modeltables
from statsmodels.base.wrapper import ResultsWrapper
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.discrete.discrete_model import BinaryResultsWrapper
from linearmodels.iv.results import IVResults, OLSResults
from linearmodels.panel.results import (
    PanelEffectsResults,
    PanelResults,
    RandomEffectsResults,
)

__all__ = ["STParams", "SupportedModels"]


class Params(dict):
    def __init__(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)

    def _set(self, key, val):
        dict.__setitem__(self, key, val)

    def _get(self, key):
        return dict.__getitem__(self, key)


STParams = Params()
STParams["ascii_padding"] = 2
STParams["ascii_header_char"] = "="
STParams["ascii_footer_char"] = "="
STParams["ascii_border_char"] = ""
STParams["ascii_mid_rule_char"] = "-"
STParams["double_top_rule"] = True
STParams["double_bottom_rule"] = False
STParams["max_html_notes_length"] = 80
STParams["max_ascii_notes_length"] = 80
STParams["index_alignment"] = "l"
STParams["column_alignment"] = "c"

SupportedModels = {
    RegressionResultsWrapper: modeltables.StatsModelsData,
    ResultsWrapper: modeltables.StatsModelsData,
    BinaryResultsWrapper: modeltables.StatsModelsData,
    IVResults: modeltables.LinearModelsData,
    OLSResults: modeltables.LinearModelsData,
    PanelEffectsResults: modeltables.LinearModelsData,
    PanelResults: modeltables.LinearModelsData,
    RandomEffectsResults: modeltables.LinearModelsData,
}
