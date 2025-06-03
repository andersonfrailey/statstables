from statstables import (
    tables,
    renderers,
    utils,
    modeltables,
    parameters,
    cellformatting,
)
from statstables.parameters import STParams

__all__ = [
    "STParams",
    "SupportedModels",
    "tables",
    "modeltables",
    "renderers",
    "utils",
    "parameters",
    "cellformatting",
]

SupportedModels = {
    "RegressionResultsWrapper": modeltables.StatsModelsData,
    "ResultsWrapper": modeltables.StatsModelsData,
    "BinaryResultsWrapper": modeltables.StatsModelsData,
    "PoissonResultsWrapper": modeltables.StatsModelsData,
    "IVResults": modeltables.LinearModelsData,
    "OLSResults": modeltables.LinearModelsData,
    "PanelEffectsResults": modeltables.LinearModelsData,
    "PanelResults": modeltables.LinearModelsData,
    "RandomEffectsResults": modeltables.LinearModelsData,
}
