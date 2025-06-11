from typing import Any
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


class SupportedModelsClass(dict):
    def __init__(self, models: dict):
        super().__init__()
        self.models = models

    @staticmethod
    def _keyname(key: str):
        # return f"<class '{item}'>"
        return key.replace("<class '", "").replace("'>", "")

    def __setitem__(self, key: str, value: Any):
        msg = "Custom models must inherit from the ModelData class"
        assert value.__base__ == modeltables.ModelData, msg
        self.models[key] = value

    def __getitem__(self, key: str):
        try:
            return self.models[key]
        except KeyError:
            try:
                return self.models[self._keyname(key)]
            except KeyError:
                msg = (
                    f"{key} is unsupported. To use custom models, "
                    "add them to the `st.SupportedModels` dictionary."
                )
                raise KeyError(msg)


SupportedModels = SupportedModelsClass(
    {
        "statsmodels.regression.linear_model.RegressionResultsWrapper": modeltables.StatsModelsData,
        "statsmodels.base.wrapper.ResultsWrapper": modeltables.StatsModelsData,
        "statsmodels.discrete.discrete_model.BinaryResultsWrapper": modeltables.StatsModelsData,
        "statsmodels.discrete.discrete_model.PoissonResultsWrapper": modeltables.StatsModelsData,
        "linearmodels.iv.results.IVResults": modeltables.LinearModelsData,
        "linearmodels.iv.results.OLSResults": modeltables.LinearModelsData,
        "linearmodels.panel.results.PanelEffectsResults": modeltables.LinearModelsData,
        "linearmodels.panel.results.PanelResults": modeltables.LinearModelsData,
        "linearmodels.panel.results.RandomEffectsResults": modeltables.LinearModelsData,
        "pyfixest.estimation.feols_.Feols": modeltables.PyFixestModel,
        "pyfixest.estimation.fepois_.Fepois": modeltables.PyFixestModel,
    }
)
