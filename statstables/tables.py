import pandas as pd
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
        self.caption_location = "botom"
        self.caption = None
        self.label = None
        self.sig_digits = 3
        self.thousands_sep = ","
        self.index_labels = dict()
        self.column_labels = dict()
        self.multicolumns = []
        self.formatters = None
        self.index_formatter = False
        self.column_formatter = False
        self.notes = []
        self.custom_lines = defaultdict(list)
        self.custom_tex_lines = defaultdict(list)
        self.custom_html_lines = defaultdict(list)
        self.include_index = False
        self.index_name = ""

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
        self.column_labels = columndict

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
        self.index_labels = indexdict

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
        if not spans:
            spans = [self.ncolumns]
        assert len(columns) == len(spans), "columns and spans must be the same length"
        assert (
            sum(spans) == self.ncolumns
        ), "The sum of spans must equal the number of columns"
        # TODO: Allow for the column to also cover the index?
        self.multicolumns.append((columns, spans))

    def custom_formatters(self, formatters: dict, axis: str = "columns") -> None:
        """
        Method to set custom formatters either along the columns or index. Each
        key in the formatters dict must be a function that returns a string.

        You cannot set both column and index formatters at this time. Whichever
        is set last will be the one used.

        Parameters
        ----------
        formatters : dict
            Dictionary of fuctions to format the values. The keys should correspond
            to either a column or index label in the table.
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
        if axis == "columns":
            if self.index_formatter:
                warnings.warn(
                    "You've already set the index formatter. This will be overwritten"
                )
            self.column_formatter = True
        elif axis == "index":
            if self.column_formatter:
                warnings.warn(
                    "You've already set the column formatter. This will be overwritten"
                )
            self.index_formatter = True
        else:
            raise ValueError("axis must be 'columns' or 'index'")
        self.formatters = formatters

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
        self, line: list[str], location: str = "bottom", label: str = ""
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

    @abstractmethod
    def _create_rows(self) -> list[list[str]]:
        pass


class GenerticTable(Table):
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
        for iname, row in self.df.iterrows():
            _row = [self.index_labels.get(iname, iname)]
            for _index, value in zip(row.index, row.values):
                if self.index_formatter:
                    formatter = self.formatters.get(iname, self._default_formatter)
                elif self.column_formatter:
                    formatter = self.formatters.get(_index, self._default_formatter)
                else:
                    formatter = self._default_formatter
                _row.append(formatter(value))
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
        self.sem = self.type_gdf[var_list].sem().T
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
                "\\cline{" + str(self.ngroups + 3) + "-" + str(self.ncolumns + 1) + "}"
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
                self.add_note(note, alignment="r", escape=True)
            output = render_func(self, **kwargs)
            # remove all the supurflous lines that may not be needed in future renders
            if self.show_n:
                self.remove_line(location="after-columns", index=-1)
            if self.show_stars:
                self.remove_note(index=-1)
            return output

        return wrapper

    @_render
    def render_latex(self, buf=None, only_tabular=False) -> str | None:
        return super().render_latex(buf, only_tabular)

    @_render
    def render_html(self, buf=None) -> str | None:

        # self.add_multicolumns(["Means", "Differences"], [self.ngroups, self.ndiffs])
        return super().render_html(buf)

    def _get_diffs(self):
        def sig_test(grp0, grp1, col):
            for var in self.var_list:
                _stat, pval = stats.ttest_ind(
                    grp0[var], grp1[var], equal_var=False, alternative=self.alternative
                )
                self.t_stats[f"{col}_{var}"] = _stat
                self.pvalues[f"{col}_{var}"] = pval

        if self.diff_pairs is None:
            self.means["Difference"] = (
                self.means[self.groups[0]] - self.means[self.groups[1]]
            )
            grp0 = self.type_gdf.get_group(self.groups[0])
            grp1 = self.type_gdf.get_group(self.groups[1])
            sig_test(grp0, grp1, "Difference")
        else:
            for pair in self.diff_pairs:
                _col = f"{pair[0]} - {pair[1]}"
                self.means[_col] = self.means[pair[0]] - self.means[pair[1]]
                sig_test(
                    self.type_gdf.get_group(pair[0]),
                    self.type_gdf.get_group(pair[1]),
                    _col,
                )

    def _create_rows(self):
        rows = []
        for i, row in enumerate(self.means.iterrows()):
            sem_row = [""]
            _row = [self.index_labels.get(row[0], row[0])]
            for _index, value in zip(row[1].index, row[1].values):
                if self.index_formatter:
                    formated_val = self.formatters[row[0]](value)
                elif self.column_formatter:
                    formated_val = self.formatters[_index](value)
                else:
                    formated_val = self._default_formatter(value)
                if self.show_standard_errors:
                    try:
                        se = self.sem.loc[row[0], _index]
                        sem_row.append(f"({se:,.{self.sig_digits}f})")
                    except KeyError:
                        sem_row.append("")
                if self.show_stars:
                    try:
                        pval = self.pvalues[f"{_index}_{row[0]}"]
                        stars = pstars(pval, self.p_values)
                    except KeyError:
                        stars = ""
                    formated_val = f"{formated_val}{stars}"
                _row.append(formated_val)
            rows.append(_row)
            if self.show_standard_errors:
                rows.append(sem_row)
        return rows


class SummaryTable(GenerticTable):
    def __init__(self, df: pd.DataFrame, var_list: list[str]):
        summary_df = df[var_list].describe()
        super().__init__(summary_df)


class PanelTable:
    """
    Merge two tables together
    """

    def __init__(self, panels: list[Table]):
        pass


def mean_diffs_table(
    df,
    group_var,
    var_list,
    index_names=None,
    columns_names=None,
    alternative="two-sided",
    equal_var=False,
    show_tstat=False,
    show_pval=False,
    show_stars=False,
    sigdigits=3,
    plevels=[0.001, 0.01, 0.05],
    includen=False,
    standard_errors=False,
):
    def format_diff(diffs, pvals):
        formatted_diffs = []
        for diff, pval in zip(diffs, pvals):
            if pval < plevels[0]:
                formatted_diffs.append(f"{diff:,.{sigdigits}f}***")
            elif pval < plevels[1]:
                formatted_diffs.append(f"{diff:,.{sigdigits}f}**")
            elif pval < plevels[2]:
                formatted_diffs.append(f"{diff:,.{sigdigits}f}*")
            else:
                formatted_diffs.append(f"{diff:,.{sigdigits}f}")
        return formatted_diffs

    groups = df[group_var].unique()
    type_gdf = df.groupby(group_var)
    means = type_gdf[var_list].mean().T
    # hypothesis test for difference in means between each variable and group
    _stats = []
    pvals = []
    for var in var_list:
        _stat, pval = stats.ttest_ind(
            df[df[group_var] == groups[0]][var],
            df[df[group_var] == groups[1]][var],
            alternative=alternative,
            equal_var=equal_var,
        )
        _stats.append(_stat)
        pvals.append(pval)
    if len(groups) == 2:
        # find difference between the two columns produced and add to means df
        means["Difference"] = means[groups[0]] - means[groups[1]]
        if show_stars:
            means["Difference"] = format_diff(means["Difference"], pvals)
    total_means = df[var_list].mean()
    total_means.name = "Total Mean"
    means = means.merge(total_means, left_index=True, right_index=True)
    if show_tstat:
        means["T-Value"] = _stats
    if show_pval:
        means["P-Value"] = pvals

    # find the standard errors of the means and add between rows
    if standard_errors:
        sems = type_gdf[var_list].sem().T
        sems["Total Mean"] = df[var_list].sem()
        sems.index = ["" for var in sems.index]
        if pd.__version__ < "2.1.0":
            sems = sems.applymap(lambda x: f"({x:,.{sigdigits}f})")
        else:
            sems = sems.map(lambda x: f"({x:,.{sigdigits}f})")
        _dfs = []
        for i, _ in enumerate(var_list):
            _dfs.append(means.iloc[i : i + 1,])
            _dfs.append(sems.iloc[i : i + 1,])
        means = pd.concat(_dfs)
        means.fillna("", inplace=True)
    if includen:
        # get size of each group
        grp_sizes = df.groupby(group_var).size()
        grp_sizes["Total Mean"] = df.shape[0]
        # create a row eith the value from grp_sizes if it's there, otherwise a blank string
        nrow = [
            f"N={grp_sizes[c]:,}" if c in grp_sizes.index else "" for c in means.columns
        ]
        # create a multiindex column from means.columns and nrow
        means.columns = pd.MultiIndex.from_tuples(zip(means.columns, nrow))
    if index_names or columns_names:
        means.rename(index=index_names, columns=columns_names, inplace=True)

    return means
