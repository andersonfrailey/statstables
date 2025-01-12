from statstables import (
    tables,
    renderers,
    utils,
    modeltables,
    parameters,
    cellformatting,
)
from statstables.parameters import STParams
from statsmodels.base.wrapper import ResultsWrapper
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.discrete.discrete_model import (
    BinaryResultsWrapper,
    PoissonResultsWrapper,
)
from linearmodels.iv.results import IVResults, OLSResults
from linearmodels.panel.results import (
    PanelEffectsResults,
    PanelResults,
    RandomEffectsResults,
)

__all__ = [
    "STParams",
    "SupportedModels",
    "tables",
    "modeltables",
    "renderers",
    "utils",
    "ResultsWrapper",
    "parameters",
    "cellformatting",
]

SupportedModels = {
    RegressionResultsWrapper: modeltables.StatsModelsData,
    ResultsWrapper: modeltables.StatsModelsData,
    BinaryResultsWrapper: modeltables.StatsModelsData,
    PoissonResultsWrapper: modeltables.StatsModelsData,
    IVResults: modeltables.LinearModelsData,
    OLSResults: modeltables.LinearModelsData,
    PanelEffectsResults: modeltables.LinearModelsData,
    PanelResults: modeltables.LinearModelsData,
    RandomEffectsResults: modeltables.LinearModelsData,
}
