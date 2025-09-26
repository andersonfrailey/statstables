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

    def add_model(self, model_results_class: Any, output_class: Any) -> None:
        """
        Add a custom model without giving it a default name

        Parameters
        ----------
        model_results_class : Any
            The model class you want to add

        Returns
        -------
        None
        """
        self[type(model_results_class)] = output_class

    @staticmethod
    def _keyname(key: str):
        return key.replace("<class '", "").replace("'>", "")

    def __setitem__(self, key: str, value: Any):
        msg = "Custom models must inherit from the ModelData class"
        assert value.__base__ == modeltables.ModelData, msg
        self.models[key] = value

    def __getitem__(self, key: str):
        # custom models will be saved with their type as the key, but the natively
        # supported models are passed in as strings (see initialization below)
        # so they will be found in the first exception
        try:
            return self.models[type(key)]
        except KeyError:
            try:
                return self.models[self._keyname(str(key))]
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
