"""
Creates defult values for the tables
"""

from collections import ChainMap


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
    "include_index": False,
    "show_columns": True,
} | STParams


class TableParams(ChainMap):
    VALID_ALIGNMENTS = ["l", "r", "c", "left", "right", "center"]

    def __init__(
        self, user_params: dict, default_params: dict = DEFAULT_TABLE_PARAMS
    ) -> None:
        super().__init__({}, user_params, default_params)
        # self.params = ChainMap({}, user_params, self.DEFAULT_TABLE_PARAMS)

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
            # self.params = ChainMap({}, {}, self.DEFAULT_TABLE_PARAMS)
        else:
            # self.params.clear()
            self.maps[0].clear()

    # Parameter validation
    def _validate_param(self, name, value):
        match name:
            case "caption_location":
                assert value in [
                    "top",
                    "bottom",
                ], "caption_location must be 'top' or 'bottom'"
            case "sig_digits":
                assert isinstance(value, int), "sig_digits must be an integer"
            case "thousands_sep":
                assert isinstance(value, str), "thousands_sep must be a string"
            case "include_index":
                assert isinstance(value, bool), "include_index must be True or False"
            case "show_columns":
                assert isinstance(value, bool), "show_columns must be True or False"
            case "column_alignment":
                assert (
                    value in self.VALID_ALIGNMENTS
                ), f"column_alignment must be in {self.VALID_ALIGNMENTS}"
            case _:
                raise AttributeError(f"Invalid parameter: {name}")

    # @property
    # def index_alignment(self) -> str:
    #     """
    #     Alignment of the index column in the table
    #     """
    #     return self.params["index_alignment"]

    # @index_alignment.setter
    # def index_alignment(self, alignment: str) -> None:
    #     assert (
    #         alignment in self.VALID_ALIGNMENTS
    #     ), f"index_alignment must be in {self.VALID_ALIGNMENTS}"
    #     self.params["index_alignment"] = alignment


DEFAULT_MEAN_DIFFS_TABLE_PARAMS = DEFAULT_TABLE_PARAMS | {
    "show_n": True,
    "show_standard_errors": True,
    "p_values": [0.1, 0.05, 0.01],
    "include_index": True,
    "show_stars": True,
    "show_significance_levels": True,
}


class MeanDiffsTableParams(TableParams):
    def __init__(self, user_params: dict) -> None:
        # self.params = ChainMap({}, user_params, self.DEFAULT_TABLE_PARAMS)
        super().__init__(user_params, DEFAULT_MEAN_DIFFS_TABLE_PARAMS)

    def _validate_param(self, name, value):
        match name:
            case "show_n":
                assert isinstance(value, bool), "show_n must be True or False"
            case "show_standard_errors":
                assert isinstance(
                    value, bool
                ), "show_standard_errors must be True or False"
            case "p_values":
                assert isinstance(value, list), "p_values must be a list"
            case "include_index":
                assert isinstance(value, bool), "include_index must be True or False"
            case "show_stars":
                assert isinstance(value, bool), "show_stars must be True or False"
            case "show_significance_levels":
                assert isinstance(
                    value, bool
                ), "show_significance_levels must be True or False"
            case _:
                super()._validate_param(name, value)

    # def reset_params(self, restore_to_defaults=False):
    #     """
    #     Clear all of the user provided parameters
    #     """
    #     if restore_to_defaults:
    #         self.params = ChainMap({}, {}, self.DEFAULT_TABLE_PARAMS)
    #     else:
    #         self.params.clear()


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
}


class ModelTableParams(TableParams):
    def __init__(self, user_params: dict) -> None:
        # self.params = ChainMap({}, user_params, self.DEFAULT_TABLE_PARAMS)
        super().__init__(user_params, DEFAULT_MODEL_TABLE_PARAMS)

    def _validate_param(self, name, value):
        match name:
            case "show_r2":
                assert isinstance(value, bool), "show_r2 must be True or False"
            case "show_adjusted_r2":
                assert isinstance(value, bool), "show_adjusted_r2 must be True or False"
            case "show_pseudo_r2":
                assert isinstance(value, bool), "show_pseudo_r2 must be True or False"
            case "show_dof":
                assert isinstance(value, bool), "show_dof must be True or False"
            case "show_ses":
                assert isinstance(value, bool), "show_ses must be True or False"
            case "show_cis":
                assert isinstance(value, bool), "show_cis must be True or False"
            case "show_fstat":
                assert isinstance(value, bool), "show_fstat must be True or False"
            case "single_row":
                assert isinstance(value, bool), "single_row must be True or False"
            case "show_observations":
                assert isinstance(
                    value, bool
                ), "show_observations must be True or False"
            case "show_ngroups":
                assert isinstance(value, bool), "show_ngroups must be True or False"
            case "show_model_numbers":
                assert isinstance(
                    value, bool
                ), "show_model_numbers must be True or False"
            case "show_model_type":
                assert isinstance(value, bool), "show_model_type must be True or False"
            case "dependent_variable":
                assert isinstance(value, str), "dependent_variable must be a string"
            case "p_values":
                assert isinstance(value, list), "p_values must be a list"

    # def reset_params(self, restore_to_defaults=False):
    #     """
    #     Clear all of the user provided parameters
    #     """
    #     if restore_to_defaults:
    #         self.params = ChainMap({}, {}, self.DEFAULT_TABLE_PARAMS)
    #     else:
    #         self.params.clear()
