# Tables that can be used to export model information
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass

# model stats that should always be formatted as integers
INT_VARS = ["observations", "ngroups"]


@dataclass
class ModelData(ABC):
    model: Any

    def __post_init__(self):
        self.data = {}
        self.pull_params()

    @abstractmethod
    def pull_params(self):
        """
        Pull the parameter estimates from the model
        """
        pass

    def get_formatted_value(self, stat: str, sig_digits=3):
        """
        Get a formatted value for the table
        """
        value = getattr(self, stat)
        if stat in INT_VARS:
            return f"{int(value):,}"
        if isinstance(value, str):
            return f"{value}"
        return f"{value:,.{sig_digits}f}"

    def __getitem__(self, name: str) -> Any:
        return self.data[name]

    def __getattr__(self, name) -> Any:
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(f"ModelData object has no attribute {name}")


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
        self.data["model_type"] = self.model.model.__class__.__name__


LINEAR_MODELS_MAP = {
    "params": "params",
    "pvalues": "pvalues",
    "sterrs": "std_errors",
    "r2": "rsquared",
    "adjusted_r2": "rsquared_adj",
    "degree_freedom": "df_model",
    "degree_freedom_resid": "df_resid",
    "observations": "nobs",
    "model_type": "_method",
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
        self.data["fstat"] = self.model.f_statistic.stat
        self.data["fstat_pvalue"] = self.model.f_statistic.pval
        if self.model.__class__.__name__ in [
            "PanelEffectsResults",
            "RandomEffectsResults",
            "PanelResults",
        ]:
            self.data["ngroups"] = self.model.entity_info.total


PYFIXEST_MAP = {"params": "coef"}


@dataclass
class PyFixestModel(ModelData):
    def __post_init__(self):
        super().__post_init__()

    def pull_params(self):
        params = self.model.coef()
        self.data["params"] = params
        self.data["param_labels"] = set(params.index.values)
        confint = self.model.confint()
        self.data["cis_low"] = confint["2.5%"]
        self.data["cis_high"] = confint["97.5%"]
        self.data["dependent_variable"] = self.model._depvar
        self.data["pvalues"] = self.model.pvalue()
