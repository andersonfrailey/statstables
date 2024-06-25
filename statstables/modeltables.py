# Tables that can be used to export model information
import statstables as st
from .tables import Table
from abc import ABC, abstractmethod
from typing import Any, TypeAlias
from dataclasses import dataclass
from statsmodels.base.wrapper import ResultsWrapper
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.discrete.discrete_model import BinaryResultsWrapper
from linearmodels.iv.results import IVResults, OLSResults
from linearmodels.panel.results import (
    PanelEffectsResults,
    PanelResults,
    RandomEffectsResults,
)

ModelTypes: TypeAlias = (
    ResultsWrapper
    | RegressionResultsWrapper
    | IVResults
    | OLSResults
    | PanelEffectsResults
    | PanelResults
    | RandomEffectsResults
    | BinaryResultsWrapper
    | Any
)

# TODO: Eventually automatically add a line saying what type of model it is
INT_VARS = ["observations"]


@dataclass
class ModelData(ABC):
    model: ModelTypes

    def __post_init__(self):
        self.data = {}
        self.pull_params()

    @abstractmethod
    def pull_params(self):
        """
        Pull the parameter estimates from the model
        """
        pass

    def get_formatted_value(self, stat, sig_digits=3):
        """
        Get a formatted value for the table
        """
        if stat in INT_VARS:
            return f"{int(getattr(self, stat))}"
        return f"{getattr(self, stat):.{sig_digits}f}"

    def __getitem__(self, name: str) -> Any:
        return self.data[name]

    def __getattr__(self, name) -> Any:
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(f"ModelData object has no attribute {name}")


# information every model must have
# REQUIRED_INFO = [
#     "params",
#     "param_labels",
#     "sterrs",
#     "r2",
#     "pvalues",
#     "cis_low",
#     "cis_high",
#     "observations",
# ]

STATSMODELS_MAP = {
    "params": "params",
    "sterrs": "bse",
    "r2": "rsquared",
    "pvalues": "pvalues",
    "adjusted_r2": "rsquared_adj",
    "fstat": "fvalue",
    "fstat_pvalue": "f_pvalue",
    "observations": "nobs",
    "dof_model": "df_model",
    "dof_resid": "df_resid",
    "pseudo_r2": "prsquared",
}


@dataclass
class StatsModelsData(ModelData):

    def __post_init__(self):
        super().__post_init__()
        self.summary_parameters = [
            "nobs",
            "r2",
            "fstat",
            "fstat_p",
            "dof_model",
        ]

    def pull_params(self) -> None:
        """
        Pull the parameter estimates from the model
        """
        # make a dictionary with the parameter values so they can be looked up
        # by covariate order. If cov. order not provided, use the order of the first
        # model, then add on as needed for subsequent models
        for info, attr in STATSMODELS_MAP.items():
            try:
                self.data[info] = getattr(self.model, attr)
            except AttributeError:
                pass
        self.data["param_labels"] = set(self.model.params.index.values)
        self.data["cis_low"] = self.model.conf_int()[0]
        self.data["cis_high"] = self.model.conf_int()[1]
        self.data["dependent_variable"] = self.model.model.endog_names


LINEAR_MODELS_MAP = {
    "params": "params",
    "p_values": "pvalues",
    "sterrs": "std_errors",
    "r2": "rsquared",
    "degree_freedom": "df_model",
    "degree_freedom_resid": "df_resid",
    "observations": "nobs",
}


@dataclass
class LinearModelsData(ModelData):

    def __post_init__(self):
        super().__post_init__()
        self.summary_parameters = [
            "nobs",
            "r2",
            "fstat",
            "fstat_p",
            "dof_model",
        ]

    def pull_params(self) -> None:
        """
        Pull the parameter estimates from the model
        """
        # make a dictionary with the parameter values so they can be looked up
        # by covariate order. If cov. order not provided, use the order of the first
        # model, then add on as needed for subsequent models
        for info, attr in LINEAR_MODELS_MAP.items():
            try:
                self.data[info] = getattr(self.model, attr)
            except AttributeError:
                pass
        self.data["param_labels"] = set(self.model.params.index.values)
        self.data["cis_low"] = self.model.conf_int()["lower"]
        self.data["cis_high"] = self.model.conf_int()["upper"]
        self.data["dependent_variable"] = self.model.summary.tables[0].data[0][1]
