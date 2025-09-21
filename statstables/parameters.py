"""
Creates defult values for the tables
"""

from collections import ChainMap
from difflib import get_close_matches


class PackageParams(dict):
    def __init__(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)

    def _set(self, key, val):
        dict.__setitem__(self, key, val)

    def _get(self, key):
        return dict.__getitem__(self, key)


# generalized parameters that users may want to set for all of their tables
STParams = PackageParams()
STParams["ascii_padding"] = 2
STParams["ascii_header_char"] = "="
STParams["ascii_footer_char"] = "-"
STParams["ascii_border_char"] = ""
STParams["ascii_mid_rule_char"] = "-"
STParams["double_top_rule"] = True
STParams["ascii_double_top_rule"] = False
STParams["double_bottom_rule"] = False
STParams["ascii_double_bottom_rule"] = False
STParams["max_html_notes_length"] = 80
STParams["max_ascii_notes_length"] = 80
STParams["index_alignment"] = "l"
STParams["column_alignment"] = "c"

DEFAULT_TABLE_PARAMS = {
    "caption_location": "top",
    "sig_digits": 3,
    "thousands_sep": ",",
    "include_index": True,
    "show_columns": True,
    "column_escape": False,
    "index_escape": False,
    "use_tabularx": False,
} | STParams

BOOL_TABLE_PARAMS = {
    "double_top_rule",
    "ascii_double_top_rule",
    "double_bottom_rule",
    "ascii_double_bottom_rule",
    "include_index",
    "show_columns",
    "column_escape",
    "index_escape",
    "use_tabularx",
}

STR_TABLE_PARAMS = {
    "ascii_header_char",
    "ascii_footer_char",
    "ascii_border_char",
    "ascii_mid_rule_char",
    "index_alignment",
    "column_alignment",
    "caption_location",
    "thousands_sep",
}
INT_TABLE_PARAMS = {
    "ascii_padding",
    "max_html_notes_length",
    "max_ascii_notes_length",
    "sig_digits",
}


class TableParams(ChainMap):
    VALID_ALIGNMENTS = ["l", "r", "c", "left", "right", "center", "^", "<", ">"]

    def __init__(
        self, user_params: dict, default_params: dict = DEFAULT_TABLE_PARAMS
    ) -> None:
        super().__init__({}, user_params, default_params)

    def __getitem__(self, name):
        return super().__getitem__(name)

    def __setitem__(self, name, value):
        self._validate_param(name, value)
        self.maps[0][name] = value

    def __getattr__(self, name):
        return self[name]

    def __contains__(self, value):
        return value in self.maps[0] | value in self.maps[1] | value in self.maps[2]

    def reset_params(self, restore_to_defaults=False):
        """
        Clearthe user provided parameters
        """
        if restore_to_defaults:
            self.maps[0].clear()
            self.maps[1].clear()
        else:
            self.maps[0].clear()

    # Parameter validation
    def _validate_param(self, name: str, value: bool | str | int) -> None:
        if name not in DEFAULT_TABLE_PARAMS.keys():
            close_matches = get_close_matches(name, DEFAULT_TABLE_PARAMS.keys())
            raise AttributeError(
                f"{name} is not a supported attribute. Close matches: {close_matches}"
            )
        # type validation
        if name in BOOL_TABLE_PARAMS:
            assert isinstance(value, bool), f"{name} must be True or False"
        elif name in STR_TABLE_PARAMS:
            assert isinstance(value, str), f"{name} must be a string"
        elif name in INT_TABLE_PARAMS:
            assert isinstance(value, int), f"{name} must be an integer"
        # value validation for specific types of parameters
        if name == "caption_location":
            assert value in [
                "top",
                "bottom",
            ], "caption_location must be 'top' or 'bottom'"
        if name.endswith("_alignment"):
            assert (
                value in self.VALID_ALIGNMENTS
            ), f"{name} must be in {self.VALID_ALIGNMENTS}"


DEFAULT_MEAN_DIFFS_TABLE_PARAMS = DEFAULT_TABLE_PARAMS | {
    "show_n": True,
    "show_standard_errors": True,
    "p_values": [0.1, 0.05, 0.01],
    "include_index": True,
    "show_stars": True,
    "show_significance_levels": True,
}

BOOL_MEAN_DIFFS_TABLE_PARAMS = {
    "show_n",
    "show_standard_errors",
    "show_stars",
    "show_significance_levels",
}


class MeanDiffsTableParams(TableParams):
    def __init__(self, user_params: dict) -> None:
        super().__init__(user_params, DEFAULT_MEAN_DIFFS_TABLE_PARAMS)

    def _validate_param(self, name, value):
        if name not in DEFAULT_MEAN_DIFFS_TABLE_PARAMS.keys():
            close_matches = get_close_matches(name, DEFAULT_TABLE_PARAMS.keys())
            raise AttributeError(
                f"{name} is not a supported attribute. Close matches: {close_matches}"
            )
        if name in BOOL_MEAN_DIFFS_TABLE_PARAMS:
            assert isinstance(value, bool), f"{name} must be True or False"
        elif name == "p_values":
            assert isinstance(value, list), "p_values must be a list"
            assert all(isinstance(p, float) for p in value), "p_values must be floats"
        elif name == "include_index":
            raise AttributeError(
                "include_index is not a valid parameter for MeanDifferencesTable"
            )
        else:
            super()._validate_param(name, value)


DEFAULT_MODEL_TABLE_PARAMS = DEFAULT_TABLE_PARAMS | {
    "show_r2": True,
    "show_adjusted_r2": False,
    "show_pseudo_r2": True,
    "show_dof": False,
    "show_ses": True,
    "show_cis": False,
    "show_fstat": True,
    "single_row": False,
    "show_observations": True,
    "show_ngroups": True,
    "show_model_numbers": True,
    "p_values": [0.1, 0.05, 0.01],
    "show_stars": True,
    "show_model_type": True,
    "dependent_variable": "",
    "include_index": True,
    "show_significance_levels": True,
    "dependent_var_cover_index": False,
    "dependent_var_alignment": "c",
    "underline_dependent_variable_name": True,
}

BOOL_MODEL_TABLE_PARAMS = {
    "show_r2",
    "show_adjusted_r2",
    "show_pseudo_r2",
    "show_dof",
    "show_ses",
    "show_cis",
    "show_fstat",
    "single_row",
    "show_observations",
    "show_ngroups",
    "show_model_numbers",
    "show_stars",
    "show_model_type",
    "show_significance_levels",
    "dependent_var_cover_index",
    "underline_dependent_variable_name",
}


class ModelTableParams(TableParams):
    def __init__(self, user_params: dict) -> None:
        super().__init__(user_params, DEFAULT_MODEL_TABLE_PARAMS)

    def _validate_param(self, name, value):
        if name not in DEFAULT_MODEL_TABLE_PARAMS.keys():
            close_matches = get_close_matches(name, DEFAULT_TABLE_PARAMS.keys())
            raise AttributeError(
                f"{name} is not a supported attribute. Close matches: {close_matches}"
            )
        if name in BOOL_MODEL_TABLE_PARAMS:
            assert isinstance(value, bool), f"{name} must be True or False"
        elif name == "p_values":
            assert isinstance(value, list), "p_values must be a list"
            assert all(isinstance(p, float) for p in value), "p_values must be floats"
        elif name == "dependent_variable":
            assert isinstance(value, str), "dependent_variable must be a string"
        elif name == "include_index":
            raise AttributeError(
                "include_index is not a valid parameter for ModelTable"
            )
        else:
            super()._validate_param(name, value)
