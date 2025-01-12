import math
import statstables as st
import textwrap
from abc import ABC, abstractmethod
from .utils import VALID_LINE_LOCATIONS


class Renderer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def generate_header(self) -> str:
        ...

    @abstractmethod
    def generate_body(self) -> str:
        ...

    @abstractmethod
    def generate_footer(self) -> str:
        ...

    @abstractmethod
    def _create_line(self, line) -> str:
        ...

    @abstractmethod
    def _format_value(self, formatting_dict: dict, **kwargs) -> str:
        ...


class LatexRenderer(Renderer):
    # LaTeX escape characters, borrowed from pandas.io.formats.latex and Stargazer
    _ESCAPE_CHARS = [
        ("\\", r"\textbackslash "),
        ("_", r"\_"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde "),
        ("^", r"\textasciicircum "),
        ("&", r"\&"),
        (">", "$>$"),
        ("<", "$<$"),
    ]
    ALIGNMENTS = {
        "l": "l",
        "c": "c",
        "r": "r",
        "left": "l",
        "center": "c",
        "right": "r",
    }

    def __init__(self, table):
        self.table = table
        self.ialign = self.ALIGNMENTS[self.table.table_params["index_alignment"]]
        self.calign = self.ALIGNMENTS[self.table.table_params["column_alignment"]]

    def render(self, only_tabular=False):
        out = self.generate_header(only_tabular)
        out += self.generate_body()
        out += self.generate_footer(only_tabular)

        return out

    def generate_header(self, only_tabular=False):
        header = ""
        if not only_tabular:
            header += "\\begin{table}[!ht]\n  \\centering\n"

            if self.table.table_params["caption_location"] == "top":
                if self.table.caption is not None:
                    header += "  \\caption{" + self.table.caption + "}\n"

                if self.table.label is not None:
                    header += "  \\label{" + self.table.label + "}\n"

        content_columns = self.calign * self.table.ncolumns
        if self.table.table_params["include_index"]:
            content_columns = self.ialign + content_columns
        header += "\\begin{tabular}{" + content_columns + "}\n"
        header += "  \\toprule\n"
        if st.STParams["double_top_rule"]:
            header += "  \\toprule\n"
        for col, spans, underline in self.table._multicolumns:
            # TODO: convert the line below to allow for labeling each multicolumn
            # header += ("  " + self.table.index_name + " & ") * self.table.table_params['include_index']
            header += "  & " * self.table.table_params["include_index"]
            underline_line = ""
            underline_start = self.table.table_params["include_index"] + 1
            mcs = []
            for c, s in zip(col, spans):
                mcs.append(f"\\multicolumn{{{s}}}{{c}}{{{c}}}")
                if underline:
                    if c == "":
                        underline_start += s
                        continue
                    underline_line += (
                        "\\cmidrule(lr){"
                        + f"{underline_start}-"
                        + f"{underline_start + s -1}"
                        + "}"
                    )
                    underline_start += s
            header += " & ".join(mcs) + " \\\\\n"
            if underline:
                header += "  " + underline_line + " \\\\\n"
        if self.table.custom_tex_lines["after-multicolumns"]:
            for line in self.table.custom_tex_lines["after-multicolumns"]:
                header += "  " + line + "\n"
        if self.table.table_params["show_columns"]:
            header += ("  " + self.table.index_name + " & ") * self.table.table_params[
                "include_index"
            ]
            header += " & ".join(
                [
                    self._escape(self.table._column_labels.get(col, col))
                    for col in self.table.columns
                ]
            )
            header += "\\\\\n"
        if self.table.custom_tex_lines["after-columns"]:
            for line in self.table.custom_tex_lines["after-columns"]:
                header += "  " + line + "\n"
        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line)
        header += "  \\midrule\n"

        return header

    def generate_body(self):
        rows = self.table._create_rows()
        row_str = ""
        for row in rows:
            row_str += (
                "  " + " & ".join([self._format_value(r) for r in row]) + " \\\\\n"
            )
        for line in self.table.custom_tex_lines["after-body"]:
            row_str += line
        for line in self.table.custom_lines["after-body"]:
            row_str += self._create_line(line)
        if isinstance(self.table, st.tables.ModelTable):
            row_str += "  \\midrule\n"
            for line in self.table.custom_lines["before-model-stats"]:
                row_str += self._create_line(line)
            stats_rows = self.table._create_stats_rows(renderer="latex")
            for row in stats_rows:
                row_str += (
                    "  " + " & ".join([self._format_value(r) for r in row]) + " \\\\\n"
                )
            for line in self.table.custom_lines["after-model-stats"]:
                row_str += self._create_line(line)
        return row_str

    def generate_footer(self, only_tabular=False):
        footer = "  \\bottomrule\n"
        if self.table.custom_lines["after-footer"]:
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line)
            footer += "  \\bottomrule\n"
            if st.STParams["double_bottom_rule"]:
                footer += "  \\bottomrule\n"
        if self.table.notes:
            for note, alignment, escape in self.table.notes:
                align_cols = (
                    self.table.ncolumns + self.table.table_params["include_index"]
                )
                footer += f"  \\multicolumn{{{align_cols}}}{{{alignment}}}"
                _note = self._escape(note) if escape else note
                footer += "{{" + "\\small \\textit{" + _note + "}}}\\\\\n"

        footer += "\\end{tabular}\n"
        if not only_tabular:
            if self.table.table_params["caption_location"] == "bottom":
                if self.table.caption is not None:
                    footer += "  \\caption{" + self.table.caption + "}\n"

                if self.table.label is not None:
                    footer += "  \\label{" + self.table.label + "}\n"
            footer += "\\end{table}\n"

        return footer

    def _escape(self, text: str) -> str:
        for char, escaped in self._ESCAPE_CHARS:
            text = text.replace(char, escaped)
        return text

    def _create_line(self, line: dict) -> str:
        out = ""
        if line["deliminate"]:
            out += "  \\midrule\n"
        out += ("  " + line["label"] + " & ") * self.table.table_params["include_index"]
        out += " & ".join(line["line"])
        out += "\\\\\n"

        return out

    def _format_value(self, formatting_dict: dict) -> str:
        """
        Formats a value in the table
        """
        start = ""
        end = ""
        if formatting_dict["bold"]:
            start += r"\textbf{"
            end += "}"
        if formatting_dict["italic"]:
            start += r"\textit{"
            end += "}"
        if formatting_dict["color"] is not None:
            start += r"\textcolor{" + formatting_dict["color"] + "}{"
            end += "}"
        _value = formatting_dict["value"]
        if formatting_dict["escape"]:
            _value = self._escape(_value)
        return start + _value + end


class HTMLRenderer(Renderer):
    ALIGNMENTS = {
        "l": "left",
        "c": "center",
        "r": "right",
        "left": "left",
        "center": "center",
        "right": "right",
    }

    def __init__(self, table, _class):
        self.table = table
        self.ncolumns = self.table.ncolumns + int(
            self.table.table_params["include_index"]
        )
        self.ialign = self.ALIGNMENTS[self.table.table_params["index_alignment"]]
        self.calign = self.ALIGNMENTS[self.table.table_params["column_alignment"]]
        self._class = _class

    def render(self):
        out = self.generate_header()
        out += self.generate_body()
        out += self.generate_footer()
        return out

    def generate_header(self):
        header = "<table>\n"
        if self._class:
            header = f'<table class="{self._class}">\n'
        header += "  <thead>\n"
        if self.table.caption and self.table.table_params["caption_location"] == "top":
            header += f'    <tr><th  colspan="{self.ncolumns}" style="text-align:center">{self.table.caption}</th></tr>\n'
        for col, spans, underline in self.table._multicolumns:
            header += "    <tr>\n"
            header += (
                f'      <th style="text-align:{self.ialign};"></th>\n'
            ) * self.table.table_params["include_index"]
            th = '<th colspan="{s}" style="text-align:{a};">{c}</th>'
            if underline:
                th = '<th colspan="{s}" style="text-align:{a};"><u>{c}</u></th>'
            header += "      " + " ".join(
                [
                    # f'<th colspan="{s}" style="text-align:center;">{c}</th>'
                    th.format(c=c, s=s, a=self.calign)
                    for c, s in zip(col, spans)
                ]
            )
            header += "\n"
            header += "    </tr>\n"
        for line in self.table.custom_html_lines["after-multicolumns"]:
            # TODO: Implement
            pass
        if self.table.table_params["show_columns"]:
            header += "    <tr>\n"
            header += (
                f"      <th>{self.table.index_name}</th>\n"
            ) * self.table.table_params["include_index"]
            for col in self.table.columns:
                header += f'      <th style="text-align:{self.calign};">{self.table._column_labels.get(col, col)}</th>\n'
            header += "    </tr>\n"
        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line)
        header += "  </thead>\n"
        header += "  <tbody>\n"
        return header

    def generate_body(self):
        rows = self.table._create_rows()
        row_str = ""
        for row in rows:
            row_str += "    <tr>\n"
            for i, r in enumerate(row):
                alignment = self.calign
                if i == 0 and self.table.table_params["include_index"]:
                    alignment = self.ialign
                val = self._format_value(r, alignment)
                row_str += f"{val}\n"
            row_str += "    </tr>\n"
        for line in self.table.custom_html_lines["after-body"]:
            row_str += line
        for line in self.table.custom_lines["after-body"]:
            row_str += self._create_line(line)
        if isinstance(self.table, st.tables.ModelTable):
            # insert a horizontal rule before the stats rows
            row_str += "    <tr>\n"
            row_str += (
                "      <td colspan='100%' style='border-top: 1px solid black;'></td>\n"
            )
            row_str += "    </tr>\n"
            for line in self.table.custom_lines["before-model-stats"]:
                row_str += self._create_line(line)
            stats_rows = self.table._create_stats_rows(renderer="html")
            for row in stats_rows:
                row_str += "    <tr>\n"
                for i, r in enumerate(row):
                    alignment = self.calign
                    if i == 0 and self.table.table_params["include_index"]:
                        alignment = self.ialign
                    val = self._format_value(r, alignment)
                    row_str += f"{val}\n"
                row_str += "    </tr>\n"
            for line in self.table.custom_lines["after-model-stats"]:
                row_str += self._create_line(line)
        return row_str

    def generate_footer(self):
        footer = ""
        if self.table.custom_lines["after-footer"]:
            footer += "    <tr>\n"
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line)
            footer += "    </tr>\n"
        if self.table.notes:
            ncols = self.table.ncolumns + self.table.table_params["include_index"]
            for note, alignment, _ in self.table.notes:
                _notes = textwrap.wrap(note, width=st.STParams["max_html_notes_length"])
                for _note in _notes:
                    footer += (
                        f'    <tr><td colspan="{ncols}" '
                        f'style="text-align:{self.ALIGNMENTS[alignment]};'
                        f'"><i>{_note}</i></td></tr>\n'
                    )
        if (
            self.table.caption
            and self.table.table_params["caption_location"] == "bottom"
        ):
            footer += f'    <tr><th colspan="{self.ncolumns}" style="text-align:center">{self.table.caption}</th></tr>\n'
        footer += "  </tbody>\n"
        footer += "</table>"
        return footer

    def _create_line(self, line):
        out = ""
        if line["deliminate"]:
            out += "    <tr>\n"
            out += (
                "      <td colspan='100%' style='border-top: 1px solid black;'></td>\n"
            )
            out += "    </tr>\n"
        out = "    <tr>\n"
        out += (
            f'      <th style="text-align:{self.ialign};"' + f">{line['label']}</th>\n"
        ) * self.table.table_params["include_index"]
        for l in line["line"]:
            out += f'      <td style="text-align:{self.calign};">{l}</td>\n'
        out += "    </tr>\n"

        return out

    def _format_value(self, formatting_dict: dict, alignment: str) -> str:
        cell = f"      <td"
        if formatting_dict["class"]:
            _class = formatting_dict["class"]
            cell += f' class="{_class}"'
        if formatting_dict["id"]:
            _id = formatting_dict["id"]
            cell += f' id="{_id}"'
        # cell style section
        style = f' style="text-align:{alignment};'
        if formatting_dict["color"]:
            style += f" color: #{formatting_dict['color']};"
        # close out the attributes section of the code
        cell += style + '">'
        # create the actual value part of the code
        start = ""
        end = ""
        if formatting_dict["bold"]:
            start += "<strong>"
            end += "</strong>"
        if formatting_dict["italic"]:
            start += "<em>"
            end += "</em>"
        val = formatting_dict["value"]
        # create full cell
        cell += f"{start}{val}{end}</td>\n"
        return cell


class ASCIIRenderer(Renderer):
    ALIGNMENTS = {
        "l": "<",
        "c": "^",
        "r": ">",
        "left": "<",
        "center": "^",
        "right": ">",
    }

    def __init__(self, table):
        self.table = table
        # number of spaces to place on either side of cell values
        self.padding = st.STParams["ascii_padding"]
        self.ncolumns = self.table.ncolumns + int(
            self.table.table_params["include_index"]
        )
        self.ialign = self.ALIGNMENTS[self.table.table_params["index_alignment"]]
        self.calign = self.ALIGNMENTS[self.table.table_params["column_alignment"]]
        self.reset_size_parameters()

    def reset_size_parameters(self):
        self.max_row_len = 0
        self.max_body_cell_size = 0
        self.max_index_name_cell_size = 0
        self._len = 0

    def render(self) -> str:
        self._get_table_widths()
        out = self.generate_header()
        out += self.generate_body()
        out += self.generate_footer()
        return out

    def generate_header(self) -> str:
        header = ""
        if self.table.caption and self.table.table_params["caption_location"] == "top":
            header += f"\n{self.table.caption:^{self._len + (2 * self._border_len)}}\n"
        header += (
            st.STParams["ascii_header_char"] * (self._len + (2 * self._border_len))
            + "\n"
        )
        if st.STParams["ascii_double_top_rule"]:
            header += (
                st.STParams["ascii_header_char"] * (self._len + (2 * self._border_len))
                + "\n"
            )
        for col, span, underline in self.table._multicolumns:
            header += st.STParams["ascii_border_char"] + (
                " "
                * self.max_index_name_cell_size
                * self.table.table_params["include_index"]
            )
            underlines = (
                st.STParams["ascii_border_char"]
                + " "
                * self.max_index_name_cell_size
                * self.table.table_params["include_index"]
            )

            for c, s in zip(col, span):
                _size = self.max_body_cell_size * s
                header += f"{c:^{_size}}"
                uchar = "-" if c != "" else " "
                underlines += f"{uchar * (_size - 2):^{_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"
            if underline:
                header += underlines + f"{st.STParams['ascii_border_char']}\n"
        if self.table.table_params["show_columns"]:
            header += st.STParams["ascii_border_char"]
            header += (
                f"{self.table.index_name:^{self.max_index_name_cell_size}}"
            ) * self.table.table_params["include_index"]
            for col in self.table.columns:
                header += f"{self.table._column_labels.get(col, col):^{self.max_body_cell_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"

        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line)
        header += (
            st.STParams["ascii_border_char"]
            + st.STParams["ascii_mid_rule_char"] * (self._len)
            + f"{st.STParams['ascii_border_char']}\n"
        )
        return header

    # get the length of the header lines by counting number of characters in each column
    def generate_body(self) -> str:
        rows = self.table._create_rows()
        body = ""
        for row in rows:
            body += st.STParams["ascii_border_char"]
            for i, r in enumerate(row):
                _size = self.max_body_cell_size
                _align = self.calign
                if i == 0 and self.table.table_params["include_index"]:
                    _size = self.max_index_name_cell_size - self.padding
                    _align = self.ialign
                    body += (
                        " " * self.padding + f"{self._format_value(r):{_align}{_size}}"
                    )
                else:
                    body += f"{self._format_value(r):{_align}{_size}}"
            body += f"{st.STParams['ascii_border_char']}\n"

        for line in self.table.custom_lines["after-body"]:
            body += self._create_line(line)

        if isinstance(self.table, st.tables.ModelTable):
            body += (
                st.STParams["ascii_mid_rule_char"]
                * (self._len + (2 * self._border_len))
                + "\n"
            )
            for line in self.table.custom_lines["before-model-stats"]:
                body += self._create_line(line)
            stats_rows = self.table._create_stats_rows(renderer="ascii")
            for row in stats_rows:
                body += f"{st.STParams['ascii_border_char']}"
                for i, r in enumerate(row):
                    _size = self.max_body_cell_size
                    if i == 0 and self.table.table_params["include_index"]:
                        _size = self.max_index_name_cell_size - self.padding
                        body += (
                            " " * self.padding
                            + f"{self._format_value(r):{self.ialign}{_size}}"
                        )
                    else:
                        body += f"{self._format_value(r):{self.calign}{_size}}"
                body += f"{st.STParams['ascii_border_char']}\n"
            for line in self.table.custom_lines["after-model-stats"]:
                body += self._create_line(line)
        return body

    def generate_footer(self) -> str:
        footer = st.STParams["ascii_footer_char"] * (self._len + (2 * self._border_len))
        if st.STParams["ascii_double_bottom_rule"]:
            footer += st.STParams["ascii_footer_char"] * (
                self._len + (2 * self._border_len)
            )
        if self.table.custom_lines["after-footer"]:
            footer += "\n"
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line)
            footer += st.STParams["ascii_footer_char"] * (
                self._len + (2 * self._border_len)
            )
            if st.STParams["ascii_double_bottom_rule"]:
                footer += st.STParams["ascii_footer_char"] * (
                    self._len + (2 * self._border_len)
                )
        if self.table.notes:
            # footer += "\n"
            for note, alignment, _ in self.table.notes:
                notes = textwrap.wrap(
                    note, width=min(self._len, st.STParams["max_ascii_notes_length"])
                )
                _alignment = self.ALIGNMENTS[alignment]
                for _note in notes:
                    footer += f"\n{_note:{_alignment}{self._len}}"
        if (
            self.table.caption
            and self.table.table_params["caption_location"] == "bottom"
        ):
            footer += f"\n{self.table.caption:^{self._len + (2 * self._border_len)}}\n"
        return footer

    def _create_line(self, line) -> str:
        _line = ""
        if line["deliminate"]:
            _line += (
                st.STParams["ascii_mid_rule_char"]
                * (self._len + (2 * self._border_len))
                + "\n"
            )
        _line += st.STParams["ascii_border_char"]
        if self.table.table_params["include_index"]:
            _line += (
                " " * self.padding
                + f"{line['label']:{self.ialign}{self.max_index_name_cell_size - self.padding}}"
            )
        for l in line["line"]:
            _line += f"{l:{self.calign}{self.max_body_cell_size}}"
        _line += st.STParams["ascii_border_char"] + "\n"
        return _line

    def _get_table_widths(self) -> None:
        self.reset_size_parameters()
        # find longest row and biggest cell
        rows = self.table._create_rows()
        for row in rows:
            row_len = 0
            for i, cell in enumerate(row):
                cell_size = len(str(cell["value"])) + (self.padding * 2)
                row_len += cell_size
                # find specific length if it's an index
                if i == 0 and self.table.table_params["include_index"]:
                    self.max_index_name_cell_size = max(
                        self.max_index_name_cell_size, cell_size
                    )
                # length for all the other cells
                else:
                    self.max_body_cell_size = max(self.max_body_cell_size, cell_size)
            self.max_row_len = max(self.max_row_len, row_len)
        if isinstance(self.table, st.tables.ModelTable):
            stats_rows = self.table._create_stats_rows(renderer="ascii")
            for row in stats_rows:
                row_len = 0
                for i, cell in enumerate(row):
                    cell_size = len(str(cell["value"])) + (self.padding * 2)
                    self.max_body_cell_size = max(self.max_body_cell_size, cell_size)
                    row_len += cell_size
                    if i == 0 and self.table.table_params["include_index"]:
                        self.max_index_name_cell_size = max(
                            self.max_index_name_cell_size, cell_size
                        )
                self.max_row_len = max(self.max_row_len, row_len)

        if self.table.table_params["include_index"]:
            index_name_size = len(str(self.table.index_name)) + (self.padding * 2)
            self.max_index_name_cell_size = max(
                self.max_index_name_cell_size, index_name_size
            )
            # check line size of all line labels
            for loc in VALID_LINE_LOCATIONS:
                for line in self.table.custom_lines[loc]:
                    self.max_index_name_cell_size = max(
                        self.max_index_name_cell_size,
                        len(line["label"]) + (self.padding * 2),
                    )

        # find longest column and length needed for all columns
        if self.table.table_params["show_columns"]:
            col_len = 0
            # loop through all the columns
            for col in self.table.columns:
                # check label size
                label = self.table._column_labels.get(col, col)
                col_size = len(str(label)) + (self.padding * 2)
                self.max_body_cell_size = max(self.max_body_cell_size, col_size)
                col_len += col_size
            # check size of index labels
            if self.table.table_params["include_index"]:
                col_len += self.max_index_name_cell_size
            self.max_row_len = max(self.max_row_len, col_len)
        # get size of multicolumns
        if self.table._multicolumns:
            for col, span, _ in self.table._multicolumns:
                for c, s in zip(col, span):
                    # total space the multicolumn will span over based on the size
                    # of the body cells
                    span_size = self.max_body_cell_size * s
                    # size of the multicolumn label after padding
                    col_size = len(c) + (self.padding * 2)
                    multi_col_size = math.ceil(max(span_size, col_size) / s)
                    self.max_body_cell_size = max(
                        self.max_body_cell_size, multi_col_size
                    )

        self._len = self.max_body_cell_size * self.table.ncolumns
        self._len += self.max_index_name_cell_size
        self._border_len = len(st.STParams["ascii_border_char"])

    def _format_value(self, formatting_dict: dict) -> str:
        return formatting_dict["value"]

    ##### Properties #####
    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, value):
        assert isinstance(value, int), "Padding must be an integer"
        if value < 0:
            raise ValueError("Padding must be a non-negative integer")
        if value > 20:
            raise ValueError("Woah there buddy. That's a lot of space.")
        self._padding = value
