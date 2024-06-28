import pandas as pd
import numpy as np
import statstables as st
from abc import ABC, abstractmethod
from scipy import stats
from typing import Union, Callable
from collections import defaultdict
from pathlib import Path
from .renderers import LatexRenderer, HTMLRenderer, ASCIIRenderer
from .utils import pstars, validate_line_location


class Table(ABC):
    """
    Abstract class for defining common characteristics/methods of all tables
    """

    VALID_ALIGNMENTS = ["l", "r", "c", "left", "right", "center"]

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
        # self._multiindex = []
        self._formatters = dict()
        self.notes = []
        self.custom_lines = defaultdict(list)
        self.custom_tex_lines = defaultdict(list)
        self.custom_html_lines = defaultdict(list)
        self.include_index = False
        self.index_name = ""
        self.show_columns = True
        self.index_alignment = st.STParams["index_alignment"]
        self.column_alignment = st.STParams["column_alignment"]

    @property
    def ncolumns(self) -> int:
        return self._ncolumns

    @ncolumns.setter
    def ncolumns(self, ncolumns: int) -> None:
        self._ncolumns = ncolumns

    @property
    def caption_location(self) -> str:
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
    def caption(self) -> str | None:
        """
        Caption for the table. This will be placed above or below the table,
        depending on the caption_location parameter.
        """
        return self._caption

    @caption.setter
    def caption(self, caption: str | None = None) -> None:
        assert isinstance(caption, (str, type(None))), "Caption must be a string"
        self._caption = caption

    @property
    def label(self) -> str | None:
        """
        Label for the table. This will be used to reference the table in LaTeX.
        """
        return self._label

    @label.setter
    def label(self, label: str | None = None) -> None:
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

    @property
    def index_alignment(self) -> str:
        """
        Alignment of the index column in the table
        """
        return self._index_alignment

    @index_alignment.setter
    def index_alignment(self, alignment: str) -> None:
        assert (
            alignment in self.VALID_ALIGNMENTS
        ), f"index_alignment must be in {self.VALID_ALIGNMENTS}"
        self._index_alignment = alignment

    @property
    def column_alignment(self) -> str:
        """
        Alignment of the column labels in the table
        """
        return self._column_alignment

    @column_alignment.setter
    def column_alignment(self, alignment: str) -> None:
        assert (
            alignment in self.VALID_ALIGNMENTS
        ), f"column_alignment must be in {self.VALID_ALIGNMENTS}"
        self._column_alignment = alignment

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
        columns: str | list[str],
        spans: list[int] | None = None,
        formats: list[str] | None = None,
        position: int | None = None,
        underline: bool = True,
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
        _position = len(self._multicolumns) if position is None else position
        self._multicolumns.insert(_position, (columns, spans, underline))

    def remove_multicolumn(self, column=None, index=None) -> None:
        if column is None and index is None:
            raise ValueError("Either 'column' or 'index' must be provided")
        if column is not None:
            self._multicolumns.remove(column)
        elif index is not None:
            self._multicolumns.pop(index)

    # def add_multiindex(self, index: list[str], spans: list[tuple]) -> None:
    #     """
    #     Add a multiindex to the table. This will be placed above the index column
    #     in the table. The sum of the spans must equal the number of rows in the table.

    #     Parameters
    #     ----------
    #     index : list[str]
    #         List of labels for the multiindex
    #     spans : list[tuple]
    #         List of tuples that indicate where the index should start and how many
    #         rows it should span. The first element of the tuple should be the row
    #         it starts and the second should be the number of rows it spans.
    #     """
    #     assert len(index) == len(spans), "index and spans must be the same length"
    #     self._multiindex.append((index, spans))
    #     for i, s in zip(index, spans):
    #         self._multiindex[s[0]] = {"index": i, "end": s[1]}

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

    def add_note(
        self,
        note: str,
        alignment: str = "r",
        escape: bool = True,
        position: int | None = None,
    ) -> None:
        """
        Adds a single line note to the bottom on the table, under the bottom line.

        Parameters
        ----------
        note : str
            The text of the note
        alignment : str, optional
            Which side of the table to align the note, by default "l"
        escape : bool, optional
            If true, a "\" is added LaTeX characters that must be escaped, by default True
        position : int, optional
            The position in the notes list to insert the note. Inserts note at the
            end of the list by default.
        """
        assert isinstance(note, str), "Note must be a string"
        assert alignment in ["l", "c", "r"], "alignment must be 'l', 'c', or 'r'"
        _position = len(self.notes) if position is None else position
        self.notes.insert(_position, (note, alignment, escape))

    def add_notes(self, notes: list[tuple]) -> None:
        """
        Adds multiple notes to the table. Each element of notes should be a tuple
        where the first element is the text of the note, the second is the alignment
        parameter and the third is the escape parameter.
        """
        for note in notes:
            self.add_note(note=note[0], alignment=note[1], escape=note[2])

    def remove_note(self, note: str | None = None, index: int | None = None) -> None:
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
        self,
        line: list[str],
        location: str = "after-body",
        label: str = "",
        position: int | None = None,
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
        _position = len(self.custom_lines[location]) if position is None else position
        self.custom_lines[location].insert(_position, {"line": line, "label": label})

    def remove_line(
        self, location: str, line: list | None = None, index: int | None = None
    ) -> None:
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

    def remove_latex_line(
        self, location: str, line: str | None = None, index: int | None = None
    ) -> None:
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

    def remove_html_line(
        self, location: str, line: str | None = None, index: int | None = None
    ):
        validate_line_location(location)
        if line is None and index is None:
            raise ValueError("Either 'line' or 'index' must be provided")

        if line is not None:
            self.custom_html_lines[location].remove(line)
        elif index is not None:
            self.custom_html_lines[location].pop(index)

    def render_latex(
        self, outfile: Union[str, Path, None] = None, only_tabular=False
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
        return None

    def render_html(self, outfile: Union[str, Path, None] = None) -> Union[str, None]:
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
        return None

    def render_ascii(self) -> str:
        return ASCIIRenderer(self).render()

    def __str__(self) -> str:
        return self.render_ascii()

    def __repr__(self) -> str:
        return self.render_ascii()

    def _repr_html_(self):
        return self.render_html()

    def _default_formatter(self, value: Union[int, float, str]) -> str:
        if isinstance(value, (int, float)):
            return f"{value:{self.thousands_sep}.{self.sig_digits}f}"
        elif isinstance(value, str):
            return value
        return value

    def _format_value(self, _index: str, col: str, value: Union[int, float, str]):
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
        """
        This method should return a list of lists, where each inner list is a
        row in the body of the table. Each element of those inner lists should
        be one cell in the table.
        """
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

    def __init__(self, df: pd.DataFrame | pd.Series):
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
            # if _index in self._multiindex.keys():
            #     _row.insert(0, self._multiindex[_index]["index"])
            rows.append(_row)
        return rows


class MeanDifferenceTable(Table):
    def __init__(
        self,
        df: pd.DataFrame,
        var_list: list,
        group_var: str,
        diff_pairs: list[tuple] | None = None,
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
                "`diff_pairs` argument must be provided if there are more than 2 groups"
            )
        if self.ngroups < 2:
            raise ValueError("There must be at least two groups")
        self.alternative = alternative
        self.type_gdf = df.groupby(group_var)
        # adjust these to only count non-null values
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
        diff_word = "Differences" if len(var_list) > 1 else "Difference"
        self.add_multicolumns(
            ["Means", "", diff_word], [self.ngroups, 1, self.ndiffs]
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
    def render_latex(self, outfile=None, only_tabular=False) -> Union[str, None]:
        return super().render_latex(outfile, only_tabular)

    @_render
    def render_html(self, outfile=None) -> Union[str, None]:
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
                formatted_val = self._format_value(_index, col, value)
                if self.show_standard_errors:
                    try:
                        se = self.sem.loc[_index, col]
                        formatted_se = self._format_value(_index, col, se)
                        sem_row.append(f"({formatted_se})")
                    except KeyError:
                        sem_row.append("")
                if self.show_stars:
                    try:
                        pval = self.pvalues[f"{col}_{_index}"]
                        stars = pstars(pval, self.p_values)
                    except KeyError:
                        stars = ""
                    formatted_val = f"{formatted_val}{stars}"
                _row.append(formatted_val)
            rows.append(_row)
            if self.show_standard_errors:
                rows.append(sem_row)
        return rows


class SummaryTable(GenericTable):
    def __init__(self, df: pd.DataFrame, var_list: list[str]):
        summary_df = df[var_list].describe()
        super().__init__(summary_df)

    def reset_params(self) -> None:
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
    # stats that get included in the table footer
    # configuration  is (name of the attribute, label, whether it has a p-value)
    model_stats = [
        ("observations", "Observations", False),
        ("ngroups", "N. of groups", False),
        ("r2", {"latex": "R^2", "html": "R<sup>2</sup>", "ascii": "R2"}, False),
        (
            "adjusted_r2",
            {
                "latex": "Adjusted R^2",
                "html": "Adjusted R<sup>2</sup>",
                "ascii": "Adjusted R2",
            },
            False,
        ),
        (
            "pseudo_r2",
            {
                "latex": "Pseudo R^2",
                "html": "Pseudo R<sup>2</sup>",
                "ascii": "Pseudo R2",
            },
            False,
        ),
        ("fstat", "F Statistic", True),
        ("dof", "DoF", False),
        ("model_type", "Model", False),
    ]

    def __init__(self, models: list):
        """
        Initialize an instance of the ModelsTable class.

        Parameters
        ----------
        models : list
            List of the models to include in the table. Each item in the list should
            be a fitted model of one of the supported types (see `st.SupportedModels`).
            If a type is not natively supported, it can be added to the `st.SupportedModels`
            dictionary to still work with this table.

        Raises
        ------
        KeyError
            Raised if a model is not supported. To use custom models, add them to the
            `st.SupportedModels` dictionary.
        """
        self.models = []
        self.params = set()
        self.ncolumns = len(models)
        dep_vars = []
        for mod in models:
            try:
                mod_obj = st.SupportedModels[type(mod)](mod)
                self.models.append(mod_obj)
            except KeyError as e:
                msg = (
                    f"{type(mod)} is unsupported. To use custom models, "
                    "add them to the `st.SupportedModels` dictionary."
                )
                raise KeyError(msg) from e
            self.params.update(mod_obj.param_labels)
            dep_vars.append(mod_obj.dependent_variable)

        self.all_param_labels = sorted(self.params)
        self.reset_params()
        # check whether all dep_vars are the same. If they are, display the variable
        # name by default.
        if all(var == dep_vars[0] for var in dep_vars):
            self.dependent_variable_name = dep_vars[0]

    def reset_params(self):
        super().reset_params()
        self.show_r2 = True
        self.show_adjusted_r2 = False
        self.show_pseudo_r2 = True
        self.show_dof = False
        self.show_ses = True
        self.show_cis = False
        self.show_fstat = True
        self.single_row = False
        self.show_observations = True
        self.show_ngroups = True
        self.show_model_numbers = True
        self._model_nums = [f"({i})" for i in range(1, len(self.models) + 1)]
        self.columns = self._model_nums
        self.param_labels = self.all_param_labels

        self.p_values = [0.1, 0.05, 0.01]
        self.show_stars = True
        self.show_model_type = True
        self.dependent_variable = ""
        self.include_index = True

    def rename_covariates(self, names: dict) -> None:
        """
        Dictionary renaming the covariate labels in the table. The format should be:
        {parameter_name: desired_label}. If a covariate is not in the dictionary,
        the parameter name will be used.

        Parameters
        ----------
        names : dict
            Dictionary containing the new names for the covariates
        """
        self._index_labels = names

    def parameter_order(self, order: list) -> None:
        """
        Set the order of the parameters in the table. An error will be raised if
        the parameter is not in any of the models.

        Parameters
        ----------
        order : list
            List of the parameters in the order you want them to appear in the table.
        """
        for p in order:
            assert p in self.all_param_labels
        self.param_labels = order

    def _create_rows(self):
        rows = []
        for param in self.param_labels:
            row = [self._index_labels.get(param, param)]
            se_row = [""]
            ci_row = [""]
            for i, mod in enumerate(self.models):
                if param not in mod.param_labels:
                    row.append("")
                    se_row.append("")
                    ci_row.append("")
                    continue
                param_val = mod.params[param]
                pvalue = mod.pvalues[param]
                se = f"({mod.sterrs[param]:.{self.sig_digits}f})"
                se_row.append(se)
                ci_low = f"{mod.cis_low[param]:.{self.sig_digits}f}"
                ci_high = f"{mod.cis_high[param]:.{self.sig_digits}f}"
                ci = f"({ci_low}, {ci_high})"
                ci_row.append(ci)
                stars = pstars(pvalue, self.p_values)
                row_val = (
                    f"{self._format_value(param, i, param_val)}"
                    + stars * self.show_stars
                    + f" {se}" * self.single_row * self.show_ses
                    + f" {ci}" * self.single_row * self.show_cis
                )

                row.append(row_val)
            rows.append(row)
            if self.show_ses and not self.single_row:
                rows.append(se_row)
            if self.show_cis and not self.single_row:
                rows.append(ci_row)
        return rows

    def _create_stats_rows(self, renderer: str) -> list:
        """
        Internal method to create rows for model statistics.

        Parameters
        ----------
        renderer : str
            The type of renderer being used. Should be 'latex', 'html', or 'ascii'

        Returns
        -------
        list
            List containing each row of statistics
        """
        rows = []
        for stat, name, pvalue in self.model_stats:
            _name = name
            if isinstance(name, dict):
                _name = name[renderer]
            if not getattr(self, f"show_{stat}"):
                continue
            row = [_name]
            for mod in self.models:
                try:
                    val = mod.get_formatted_value(stat, self.sig_digits)
                    if pvalue and self.show_stars:
                        stars = pstars(getattr(mod, f"{stat}_pvalue"), self.p_values)
                        val = f"{val}{stars}"
                    row.append(val)
                except AttributeError:
                    row.append("")
            # only add the stat if at least one model has it
            if not all(r == "" for r in row):
                rows.append(row)
        return rows

    @staticmethod
    def _render(render_func: Callable):
        """
        Wrapper for the render function to add a p-value note formatted to fit
        the type of renderer being used.

        Parameters
        ----------
        render_func : Callable
            The rendering function being wrapped
        """

        def wrapper(self, **kwargs):
            if self.show_stars:
                _p = "p<"
                if render_func.__name__ == "render_latex":
                    _p = "p$<$"
                stars = ", ".join(
                    [
                        f"{'*' * i}{_p}{p}"
                        for i, p in enumerate(
                            sorted(self.p_values, reverse=True), start=1
                        )
                    ]
                )
                stars_note = f"{stars}"
                self.add_note(stars_note, alignment="r", escape=False, position=0)
                _stars_note = (stars_note, "r", False)
            output = render_func(self, **kwargs)
            if self.show_stars:
                self.remove_note(note=_stars_note)

            return output

        return wrapper

    @_render
    def render_latex(self, outfile=None, only_tabular=False) -> Union[str, None]:
        return super().render_latex(outfile, only_tabular)

    @_render
    def render_html(self, outfile=None) -> Union[str, None]:
        return super().render_html(outfile)

    @_render
    def render_ascii(self) -> Union[str, None]:
        return super().render_ascii()

    ##### Properties #####
    @property
    def dependent_variable_name(self) -> str:
        return self._dependent_variable_name

    @dependent_variable_name.setter
    def dependent_variable_name(self, name: str) -> None:
        # remove current dependent variable from multicolumns to update later
        if len(self._multicolumns) > 0:
            try:
                col = (
                    ["", f"Dependent Variable: {self.dependent_variable_name}"],
                    [1, self.ncolumns - 1],
                )
                self.remove_multicolumn(col)
            except ValueError:
                pass
        self._dependent_variable_name = name
        if name != "":
            self.add_multicolumns(
                ["", f"Dependent Variable: {name}"], [1, self.ncolumns - 1], position=0
            )

    @property
    def show_r2(self) -> bool:
        return self._show_r2

    @show_r2.setter
    def show_r2(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_r2 = show

    @property
    def show_adjusted_r2(self) -> bool:
        return self._show_adjusted_r2

    @show_adjusted_r2.setter
    def show_adjusted_r2(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_adjusted_r2 = show

    @property
    def show_dof(self) -> bool:
        return self._show_dof

    @show_dof.setter
    def show_dof(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_dof = show

    @property
    def show_cis(self) -> bool:
        return self._show_cis

    @show_cis.setter
    def show_cis(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_cis = show

    @property
    def show_ses(self) -> bool:
        return self._show_ses

    @show_ses.setter
    def show_ses(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_ses = show

    @property
    def show_fstat(self) -> bool:
        return self._show_fstat

    @show_fstat.setter
    def show_fstat(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_fstat = show

    @property
    def single_row(self) -> bool:
        return self._single_row

    @single_row.setter
    def single_row(self, single: bool) -> None:
        assert isinstance(single, bool)
        self._single_row = single

    @property
    def show_observations(self) -> bool:
        return self._show_observations

    @show_observations.setter
    def show_observations(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_observations = show

    @property
    def show_model_numbers(self) -> bool:
        return self._show_model_numbers

    @show_model_numbers.setter
    def show_model_numbers(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_model_numbers = show

    @property
    def show_model_type(self) -> bool:
        return self._show_model_type

    @show_model_type.setter
    def show_model_type(self, show: bool) -> None:
        assert isinstance(show, bool)
        self._show_model_type = show


class PanelTable:
    """
    Merge two tables together. Not implemented yet
    """

    def __init__(self, panels: list[Table]):
        pass
