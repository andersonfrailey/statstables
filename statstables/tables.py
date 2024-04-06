import pandas as pd
import numpy as np
import warnings
from abc import ABC, abstractmethod
from scipy import stats
from typing import Union
from collections import defaultdict
from pathlib import Path
from .renderers import LatexRenderer, HTMLRenderer
from .utils import pstars, validate_line_location


class Table(ABC):
    """
    Abstract class for defining common characteristics/methods of all tables
    """

    def __init__(self):
        self.reset_params()

    def reset_params(self) -> None:
        """
        Resets all parameters to their default values
        """
        self.caption_location = "bottom"
        self.caption = None
        self.label = None
        self.sig_digits = 3
        self.thousands_sep = ","
        self._index_labels = dict()
        self._column_labels = dict()
        self._multicolumns = []
        self._formatters = dict()
        self.notes = []
        self.custom_lines = defaultdict(list)
        self.custom_tex_lines = defaultdict(list)
        self.custom_html_lines = defaultdict(list)
        self.include_index = False
        self.index_name = ""
        self.show_columns = True

    @property
    def caption_location(self) -> None:
        """
        Location of the caption in the table. Can be either 'top' or 'bottom'.
        """
        return self._caption_location

    @caption_location.setter
    def caption_location(self, location: str) -> None:
        assert location in [
            "top",
            "bottom",
        ], "caption_location must be 'top' or 'bottom'"
        self._caption_location = location

    @property
    def caption(self) -> None:
        """
        Caption for the table. This will be placed above or below the table,
        depending on the caption_location parameter.
        """
        return self._caption

    @caption.setter
    def caption(self, caption: str = None) -> None:
        assert isinstance(caption, (str, type(None))), "Caption must be a string"
        self._caption = caption

    @property
    def label(self) -> None:
        """
        Label for the table. This will be used to reference the table in LaTeX.
        """
        return self._label

    @label.setter
    def label(self, label: str = None) -> None:
        assert isinstance(label, (str, type(None))), "Label must be a string"
        self._label = label

    @property
    def sig_digits(self) -> int:
        """
        Number of significant digits to include in the table
        """
        return self._sig_digits

    @sig_digits.setter
    def sig_digits(self, digits: int) -> None:
        assert isinstance(digits, int), "sig_digits must be an integer"
        self._sig_digits = digits

    @property
    def thousands_sep(self) -> str:
        """
        Character to use as the thousands separator in the table
        """
        return self._thousands_sep

    @thousands_sep.setter
    def thousands_sep(self, sep: str) -> None:
        assert isinstance(sep, str), "thousands_sep must be a string"
        self._thousands_sep = sep

    @property
    def include_index(self) -> bool:
        """
        Whether or not to include the index in the table
        """
        return self._include_index

    @include_index.setter
    def include_index(self, include: bool) -> None:
        assert isinstance(include, bool), "include_index must be True or False"
        self._include_index = include

    @property
    def index_name(self) -> str:
        """
        Name of the index column in the table
        """
        return self._index_name

    @index_name.setter
    def index_name(self, name: str) -> None:
        assert isinstance(name, str), "index_name must be a string"
        self._index_name = name

    @property
    def show_columns(self) -> bool:
        """
        Whether or not to show the column labels in the table
        """
        return self._show_columns

    @show_columns.setter
    def show_columns(self, show: bool) -> None:
        assert isinstance(show, bool), "show_columns must be True or False"
        self._show_columns = show

    def rename_columns(self, columndict: dict) -> None:
        """
        Rename the columns in the table. The keys of the columndict should be the
        current column labels and the values should be the new labels.

        Parameters
        ----------
        columndict : dict
            _description_
        """
        assert isinstance(columndict, dict), "columndict must be a dictionary"
        self._column_labels.update(columndict)

    def rename_index(self, indexdict: dict) -> None:
        """
        Rename the index labels in the table. The keys of the indexdict should
        be the current index labels and the values should be the new labels.

        Parameters
        ----------
        indexdict : dict
            Dictionary where the keys are the current index labels and the values
            are the new labels.
        """
        assert isinstance(indexdict, dict), "indexdict must be a dictionary"
        self._index_labels.update(indexdict)

    # TODO: Add method for creating index labels that span multiple rows
    def add_multicolumns(
        self,
        columns: Union[str, list[str]],
        spans: list[int],
        formats: list[str] = None,
    ) -> None:
        """
        All columns that span multiple columns in the table. These will be placed
        above the individual column labels. The sum of the spans must equal the
        number of columns in the table, not including the index.

        Parameters
        ----------
        columns : Union[str, list[str]]
            If a single string is provided, it will span the entire table. If a list
            is provided, each will span the number of columns in the corresponding
            index of the spans list.
        spans : list[int]
            List of how many columns each multicolumn should span.
        formats : list[str], optional
            Not implemented yet. Will eventually allow for text formatting (bold,
            underline, etc.), by default None
        """
        # TODO: implement formats (underline, bold, etc.)
        # TODO: Allow for placing the multicolumns below the table body
        if not spans:
            spans = [self.ncolumns]
        assert len(columns) == len(spans), "columns and spans must be the same length"
        assert (
            sum(spans) == self.ncolumns
        ), "The sum of spans must equal the number of columns"
        self._multicolumns.append((columns, spans))

    def custom_formatters(self, formatters: dict) -> None:
        """
        Method to set custom formatters either along the columns or index. Each
        key in the formatters dict must be a function that returns a string.

        You cannot set both column and index formatters at this time. Whichever
        is set last will be the one used.

        Parameters
        ----------
        formatters : dict
            Dictionary of fuctions to format the values. The keys should correspond
            to either a column or index label in the table. If you want to format
            along both axis, the key should be a tuple of the form: (index, column)
        axis : str, optional
            Which axis to format along, by default "columns"

        Raises
        ------
        ValueError
            Error is raised if the values in the formatters dict are not functions
        """
        assert all(
            callable(f) for f in formatters.values()
        ), "Values in the formatters dict must be functions"
        self._formatters.update(formatters)

    def add_note(self, note: str, alignment: str = "l", escape: bool = True) -> None:
        """
        Adds a single line note to the bottom on the table, under the bottom line.

        Parameters
        ----------
        note : str
            The text of the note
        alignment : str, optional
            Which side of the table to align the note, by default "l"
        escape : bool, optional
            If true, a \ is added LaTeX characters that must be escaped, by default True
        """
        assert isinstance(note, str), "Note must be a string"
        assert alignment in ["l", "c", "r"], "alignment must be 'l', 'c', or 'r'"
        self.notes.append((note, alignment, escape))

    def remove_note(self, note: str = None, index: int = None) -> None:
        """
        Removes a note that has been added to the table. To specify which note,
        either pass the text of the note as the 'note' parameter or the index of
        the note as the 'index' parameter.

        Parameters
        ----------
        note : str, optional
            Text of note to remove, by default None
        index : int, optional
            Index of the note to be removed, by default None

        Raises
        ------
        ValueError
            Raises and error if neither 'note' or 'index' are provided
        """
        if note is None and index is None:
            raise ValueError("Either 'note' or 'index' must be provided")
        if note is not None:
            self.notes.remove(note)
        elif index is not None:
            self.notes.pop(index)

    def add_line(
        self, line: list[str], location: str = "after-body", label: str = ""
    ) -> None:
        """
        Add a line to the table that will be rendered at the specified location.
        The line will be formatted to fit the table and the number of elements in
        the list should equal the number of columns in the table. The index label
        for the line is an empty string by default, but can be specified with the
        label parameter.

        Parameters
        ----------
        line : list[str]
            A list with each element that will comprise the line. the number of
            elements of this list should equal the number of columns in the table
        location : str, optional
            Where on the table to place the line, by default "bottom"
        label : str, optional:
            The index label for the line, by default ""
        """
        validate_line_location(location)
        assert len(line) == self.ncolumns, "Line must have the same number of columns"
        self.custom_lines[location].append({"line": line, "label": label})

    def remove_line(self, location: str, line: list = None, index: int = None):
        """
        Remove a custom line. To specify which line to remove, either pass the list
        containing the line as the 'line' parameter or the index of the line as the
        'index' parameter.

        Parameters
        ----------
        location : str
            Where in the table the line is located
        line : list, optional
            List containing the line elements, by default None
        index : int, optional
            Index of the line in the custom line list for the specified location, by default None

        Raises
        ------
        ValueError
            Raises an error if neither 'line' or 'index' are provided, or if the
            line cannot be found in the custom lines list.
        """
        validate_line_location(location)
        if line is None and index is None:
            raise ValueError("Either 'line' or 'index' must be provided")

        if line is not None:
            self.custom_lines[location].remove(line)
        elif index is not None:
            self.custom_lines[location].pop(index)

    def add_latex_line(self, line: str, location: str = "bottom") -> None:
        """
        Add line that will only be rendered in the LaTeX output. This method
        assumes the line is formatted as needed, including escape characters and
        line breaks. The provided line will be rendered as is. Note that this is
        different from the generic add_line method, which will format the line
        to fit in either LaTeX or HTML output.

        Parameters
        ----------
        line : str
            The line to add to the table
        location : str, optional
            Where in the table to place the line, by default "bottom"
        """
        validate_line_location(location)
        self.custom_tex_lines[location].append(line)

    def remove_latex_line(self, location: str, line: str = None, index: int = None):
        """
        Remove a custom LaTex line. To specify which line to remove, either pass the list
        containing the line as the 'line' parameter or the index of the line as the
        'index' parameter.

        Parameters
        ----------
        location : str
            Where in the table the line is located.
        line : list, optional
            List containing the line elements.
        index : int, optional
            Index of the line in the custom line list for the specified location.

        Raises
        ------
        ValueError
            Raises an error if neither 'line' or 'index' are provided, or if the
            line cannot be found in the custom lines list.
        """
        validate_line_location(location)
        if line is None and index is None:
            raise ValueError("Either 'line' or 'index' must be provided")

        if line is not None:
            self.custom_tex_lines[location].remove(line)
        elif index is not None:
            self.custom_tex_lines[location].pop(index)

    def add_html_line(self, line: str, location: str = "bottom") -> None:
        """
        Add line that will only be rendered in the HTML output. This method
        assumes the line is formatted as needed, including line breaks. The
        provided line will be rendered as is. Note that this is different from
        the generic add_line method, which will format the line to fit in either
        LaTeX or HTML output.

        Parameters
        ----------
        line : str
            The line to add to the table
        location : str, optional
            Where in the table to place the line. By default "bottom", other options
            are: 'top', 'after-multicolumns', 'after-columns', 'after-body', 'after-footer'.
            Note: not all of these are implemented yet.
        """
        validate_line_location(location)
        self.custom_html_lines[location].append(line)

    def remove_html_line(self, location: str, line: str = None, index: int = None):
        validate_line_location(location)
        if line is None and index is None:
            raise ValueError("Either 'line' or 'index' must be provided")

        if line is not None:
            self.custom_html_lines[location].remove(line)
        elif index is not None:
            self.custom_html_lines[location].pop(index)

    def render_latex(
        self, outfile: Union[str, Path] = None, only_tabular=False
    ) -> Union[str, None]:
        """
        Render the table in LaTeX. Note that you will need to include the booktabs
        package in your LaTeX document. If no outfile is provided, the LaTeX
        string will be returned, otherwise the text will be written to the specified
        file.

        Parameters
        ----------
        outfile : str, Path, optional
            File to write the text to, by default None.
        only_tabular : bool, optional
            If True, the text will only be wrapped in a tabular enviroment. If
            false, the text will also be wrapped in a table enviroment. It is
            False by default.

        Returns
        -------
        Union[str, None]
            If an outfile is not specified, the LaTeX string will be returned.
            Otherwise None will be returned.
        """
        tex_str = LatexRenderer(self).render(only_tabular=only_tabular)
        if not outfile:
            return tex_str
        Path(outfile).write_text(tex_str)

    def render_html(self, outfile: Union[str, Path] = None) -> Union[str, None]:
        """
        Render the table in HTML. Note that you will need to include the booktabs
        package in your LaTeX document. If no outfile is provided, the LaTeX
        string will be returned, otherwise the text will be written to the specified
        file.

        This is also used in the _repr_html_ method to render the tables in
        Jupyter notebooks.

        Parameters
        ----------
        outfile : str, Path, optional
            File to write the text to, by default None.

        Returns
        -------
        Union[str, None]
            If an outfile is not specified, the HTML string will be returned.
            Otherwise None will be returned.
        """
        html_str = HTMLRenderer(self).render()
        if not outfile:
            return html_str
        Path(outfile).write_text(html_str)

    def _repr_html_(self) -> str:
        return self.render_html()

    def _default_formatter(self, value) -> str:
        if isinstance(value, (int, float)):
            return f"{value:{self.thousands_sep}.{self.sig_digits}f}"
        elif isinstance(value, str):
            return value
        return value

    def _format_value(self, _index, col, value):
        if (_index, col) in self._formatters.keys():
            formatter = self._formatters[(_index, col)]
        elif _index in self._formatters.keys():
            formatter = self._formatters.get(_index, self._default_formatter)
        elif col in self._formatters.keys():
            formatter = self._formatters.get(col, self._default_formatter)
        else:
            formatter = self._default_formatter
        return formatter(value)

    @abstractmethod
    def _create_rows(self) -> list[list[str]]:
        pass

    @staticmethod
    def _validate_input_type(value, dtype):
        if not isinstance(value, dtype):
            raise TypeError(f"{value} must be a {dtype}")


class GenericTable(Table):
    """
    A generic table will take in any DataFrame and allow for easy formating and
    column/index naming
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.ncolumns = df.shape[1]
        self.columns = df.columns
        self.nrows = df.shape[0]
        self.reset_params()

    def reset_params(self):
        super().reset_params()
        self.include_index = True

    def _create_rows(self):
        rows = []
        for _index, row in self.df.iterrows():
            _row = [self._index_labels.get(_index, _index)]
            for col, value in zip(row.index, row.values):
                formated_val = self._format_value(_index, col, value)
                _row.append(formated_val)
            if not self.include_index:
                _row.pop(0)
            rows.append(_row)
        return rows


class MeanDifferenceTable(Table):
    def __init__(
        self,
        df: pd.DataFrame,
        var_list: list,
        group_var: str,
        diff_pairs: list[tuple] = None,
        alternative: str = "two-sided",
    ):
        """
        Table that shows the difference in means between the specified groups in
        the data. If there are only two groups, the table will show the difference
        between the two.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the raw data to be compared
        var_list : list
            List of variables to compare means to between the groups
        group_var : str
            The variable in the data to group by
        diff_pairs : list[tuple], optional
            A list containing all of the pairs to take difference between. The
            order they are listed in the tuple will be how they are subtracted.
            If not specified, the difference between the two groups will be taken.
            This must be specified when there are more than two groups.
        alternative : str, optional
            The alternative hypothesis for the t-test. It is a two-sided test
            by default, but can be set to 'greater' or 'less' for a one-sided test.
            For now, the same test is applied to each variable.
        """
        # TODO: allow for grouping on multiple variables
        self.groups = df[group_var].unique()
        self.ngroups = len(self.groups)
        self.var_list = var_list
        if self.ngroups > 2 and not diff_pairs:
            raise ValueError(
                "diff_pairs must be provided if there are more than 2 groups"
            )
        if self.ngroups < 2:
            raise ValueError("There must be at least two groups")
        self.alternative = alternative
        self.type_gdf = df.groupby(group_var)
        self.grp_sizes = self.type_gdf.size()
        self.grp_sizes["Overall Mean"] = df.shape[0]
        self.means = self.type_gdf[var_list].mean().T
        # add toal means column to means
        self.means["Overall Mean"] = df[var_list].mean()
        total_sem = df[var_list].sem()
        total_sem.name = "Overall Mean"
        self.sem = pd.merge(
            self.type_gdf[var_list].sem().T,
            total_sem,
            left_index=True,
            right_index=True,
        )
        self.diff_pairs = diff_pairs
        self.ndiffs = len(self.diff_pairs) if self.diff_pairs else 1
        self.t_stats = {}
        self.pvalues = {}
        self.reset_params()
        self._get_diffs()
        self.ncolumns = self.means.shape[1]
        self.columns = self.means.columns

        self.add_multicolumns(
            ["Means", "", "Differences"], [self.ngroups, 1, self.ndiffs]
        )  # may need to move this later if we make including the total mean optional
        self.add_latex_line(
            (
                "\\cline{2-" + str(self.ngroups + 1) + "}"
                "\\cline{"
                + str(self.ngroups + 3)
                + "-"
                + str(self.ncolumns + 1)
                + "}\\\\\n"
            ),
            location="after-multicolumns",
        )  # this too

    def reset_params(self):
        super().reset_params()
        self.show_n = True
        self.show_standard_errors = True
        self.p_values = [0.1, 0.05, 0.01]
        self.include_index = True
        self.show_stars = True

    @property
    def show_n(self) -> bool:
        return self._show_n

    @show_n.setter
    def show_n(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._show_n = value

    @property
    def show_standard_errors(self) -> bool:
        return self._show_standard_errors

    @show_standard_errors.setter
    def show_standard_errors(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._show_standard_errors = value

    @property
    def show_stars(self) -> bool:
        return self._show_stars

    @show_stars.setter
    def show_stars(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._show_stars = value

    @staticmethod
    def _render(render_func):
        def wrapper(self, **kwargs):
            if self.show_n:
                self.add_line(
                    [
                        f"N={self.grp_sizes[c]:,}" if c in self.grp_sizes.index else ""
                        for c in self.means.columns
                    ],
                    location="after-columns",
                )
            if self.show_stars:
                _p = "p<"
                if render_func.__name__ == "render_latex":
                    _p = "p$<$"
                stars = ", ".join(
                    [
                        f"{'*' * i} {_p} {p}"
                        for i, p in enumerate(
                            sorted(self.p_values, reverse=True), start=1
                        )
                    ]
                )
                note = f"Significance levels: {stars}"
                self.add_note(note, alignment="r", escape=False)
            output = render_func(self, **kwargs)
            # remove all the supurflous lines that may not be needed in future renders
            if self.show_n:
                self.remove_line(location="after-columns", index=-1)
            if self.show_stars:
                self.remove_note(index=-1)
                print("Note: Standard errors assume samples are drawn independently.")
            return output

        return wrapper

    @_render
    def render_latex(self, outfile=None, only_tabular=False) -> str | None:
        return super().render_latex(outfile, only_tabular)

    @_render
    def render_html(self, outfile=None) -> str | None:
        return super().render_html(outfile)

    def _get_diffs(self):
        # TODO: allow for standard errors caluclated under dependent samples
        def sig_test(grp0, grp1, col):
            se_list = []
            for var in self.var_list:
                _stat, pval = stats.ttest_ind(
                    grp0[var], grp1[var], equal_var=False, alternative=self.alternative
                )
                self.t_stats[f"{col}_{var}"] = _stat
                self.pvalues[f"{col}_{var}"] = pval
                s1 = grp0[var].std() ** 2
                s2 = grp1[var].std() ** 2
                n1 = grp0.shape[0]
                n2 = grp1.shape[0]
                se_list.append(np.sqrt(s1 / n1 + s2 / n2))

            return pd.Series(se_list, index=self.var_list)

        if self.diff_pairs is None:
            self.means["Difference"] = (
                self.means[self.groups[0]] - self.means[self.groups[1]]
            )
            grp0 = self.type_gdf.get_group(self.groups[0])
            grp1 = self.type_gdf.get_group(self.groups[1])
            ses = sig_test(grp0, grp1, "Difference")
            ses.name = "Difference"
            self.sem = self.sem.merge(ses, left_index=True, right_index=True)
        else:
            for pair in self.diff_pairs:
                _col = f"{pair[0]} - {pair[1]}"
                self.means[_col] = self.means[pair[0]] - self.means[pair[1]]
                ses = sig_test(
                    self.type_gdf.get_group(pair[0]),
                    self.type_gdf.get_group(pair[1]),
                    _col,
                )
                ses.name = _col
                self.sem = self.sem.merge(ses, left_index=True, right_index=True)

    def _create_rows(self):
        rows = []
        for _index, row in self.means.iterrows():
            sem_row = [""]
            _row = [self._index_labels.get(_index, _index)]
            for col, value in zip(row.index, row.values):
                formated_val = self._format_value(_index, col, value)
                if self.show_standard_errors:
                    try:
                        se = self.sem.loc[_index, col]
                        sem_row.append(f"({se:,.{self.sig_digits}f})")
                    except KeyError:
                        sem_row.append("")
                if self.show_stars:
                    try:
                        pval = self.pvalues[f"{col}_{_index}"]
                        stars = pstars(pval, self.p_values)
                    except KeyError:
                        stars = ""
                    formated_val = f"{formated_val}{stars}"
                _row.append(formated_val)
            rows.append(_row)
            if self.show_standard_errors:
                rows.append(sem_row)
        return rows


class SummaryTable(GenericTable):
    def __init__(self, df: pd.DataFrame, var_list: list[str]):
        summary_df = df[var_list].describe()
        super().__init__(summary_df)

    def reset_params(self):
        super().reset_params()
        self.rename_index(
            {
                "count": "Count",
                "mean": "Mean",
                "std": "Std. Dev.",
                "min": "Min.",
                "max": "Max.",
            }
        )


class ModelTable(Table):
    """
    A table that can be used to show the results of most models passed in, with
    enough user guidance.
    """

    def __init__(
        self,
        models: list,
        param_value_attr: str = "params",
        param_names_attr: str = None,
        std_err_attr: str = None,
        ci_attr: str = None,
        model_names: list[str] = None,
        model_summary_vars: dict = None,  # things like r2, T, etc.
    ):
        self.models = models
        self.ncolumns = len(models)
        self.ci_attr = ci_attr
        self.columns = model_names
        self.std_err_attr = std_err_attr
        # extract data from each model
        self._model_dict = {}
        self._param_names = []
        for i, mod in enumerate(models):
            _params_dict = {}
            _stders_dict = {}
            _cis_dict = {}
            _params = self._get_attr(mod, param_value_attr)
            _names = self._get_attr(mod, param_names_attr)
            _stders = self._get_attr(mod, std_err_attr)
            # _cis = self._get_attr(mod, ci_attr)
            for _name, _param, stder in zip(_names, _params, _stders):
                if _name not in self._param_names:
                    self._param_names.append(_name)
                _params_dict[_name] = _param
                _stders_dict[_name] = stder
                # _cis_dict[_name] = ci
            self._model_dict[i] = {"params": _params_dict, "std_errs": _stders_dict}
        self.reset_params()

    def reset_params(self):
        super().reset_params()
        self.include_index = True
        self.show_model_nums = True
        self._model_nums = [f"({i})" for i in range(1, len(self.models) + 1)]
        # if no column names are provided use the model numbers
        if self.columns is None:
            self.columns = self._model_nums
            self.show_model_nums = False

        self.single_line = False
        self.parameter_order = self._param_names
        self.show_standard_errors = True

    @property
    def show_model_nums(self) -> bool:
        """
        If true, model numbers are included under the column names
        """
        return self._show_model_nums

    @show_model_nums.setter
    def show_model_nums(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._show_model_nums = value

    @property
    def single_row(self) -> bool:
        """
        If true, the significance variable (either standard error or confience interval)
        will be rendered on the same line as the parameter value
        """
        return self._single_row

    @single_row.setter
    def single_row(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._single_row = value

    @property
    def columns(self) -> list:
        return self._columns

    @columns.setter
    def columns(self, column_labels: list[str]) -> None:
        if not column_labels is None:
            if not isinstance(column_labels, list):
                raise TypeError("Column labels must be a list of strings")
            for col in column_labels:
                if not isinstance(col, str):
                    raise ValueError("All column labels must be strings")
        self._columns = column_labels

    @property
    def parameter_order(self) -> list:
        return self._parameter_order

    @parameter_order.setter
    def parameter_order(self, order: list) -> None:
        if not order is None:
            if not isinstance(order, list):
                raise TypeError("Parameter order must be a list of strings")
            for param in order:
                if not isinstance(param, str):
                    raise ValueError("All parameter names must be strings")
            self._parameter_order = order

    @property
    def show_standard_errors(self) -> bool:
        return self._show_standard_errors

    @show_standard_errors.setter
    def show_standard_errors(self, value: bool) -> None:
        self._validate_input_type(value, bool)
        self._show_standard_errors = value

    def _create_rows(self):
        rows = []
        for param in self.parameter_order:
            _row = [self._index_labels.get(param, param)]
            se_row = [""]
            for col, mod in zip(self.columns, self._model_dict.values()):
                param_val = mod["params"].get(param, "")
                se_val = mod["std_errs"].get(param, "")
                _row.append(self._format_value(param, col, param_val))
                if isinstance(se_val, str):
                    se_row.append(se_val)
                else:
                    se_row.append(f"({se_val:,.{self.sig_digits}f})")
            rows.append(_row)
            if self.show_standard_errors:
                rows.append(se_row)

        return rows

    @staticmethod
    def _get_attr(mod, attrstr):
        if "." in attrstr:
            attrs = attrstr.split(".")
            for a in attrs:
                mod = getattr(mod, a)
        else:
            mod = getattr(mod, attrstr)
        return mod

    @staticmethod
    def _render(render_func):
        def wrapper(self, **kwargs):
            if self.show_model_nums:
                self.add_line(self._model_nums, location="after-columns")
            output = render_func(self, **kwargs)
            if self.show_model_nums:
                self.remove_line(location="after-columns", index=-1)
            return output

        return wrapper

    @_render
    def render_latex(self, outfile=None, only_tabular=False) -> str | None:
        return super().render_latex(outfile, only_tabular)

    @_render
    def render_html(self, outfile=None) -> str | None:
        return super().render_html(outfile)


class PanelTable:
    """
    Merge two tables together. Not implemented yet
    """

    def __init__(self, panels: list[Table]):
        pass
