import math
import statstables as st
import textwrap
from abc import ABC, abstractmethod
from .utils import VALID_LINE_LOCATIONS, replace_latex


class Renderer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

    @abstractmethod
    def generate_header(self) -> str: ...

    @abstractmethod
    def generate_body(self) -> str: ...

    @abstractmethod
    def generate_footer(self) -> str: ...

    @abstractmethod
    def _create_line(self, line) -> str: ...

    @abstractmethod
    def _format_value(self, formatting_dict: dict, **kwargs) -> str: ...


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
    TABULARX_ALIGNMENTS = {
        "l": r">{\raggedright\arraybackslash}",
        "c": r">{\centering\arraybackslash}",
        "r": r">{\raggedleft\arraybackslash}",
        "left": r">{\raggedright\arraybackslash}",
        "center": r">{\centering\arraybackslash}",
        "right": r">{\raggedleft\arraybackslash}",
    }

    def __init__(self, table):
        self.table = table
        self.ialign = self.ALIGNMENTS[self.table.table_params["index_alignment"]]
        self.calign = self.ALIGNMENTS[self.table.table_params["column_alignment"]]
        self.start_tabular = "\\begin{tabular}{"
        self.end_tabular = "\\end{tabular}\n"
        if self.table.table_params["use_tabularx"]:
            self.ialign = (
                self.TABULARX_ALIGNMENTS[self.table.table_params["index_alignment"]]
                + "X"
            )
            self.calign = (
                self.TABULARX_ALIGNMENTS[self.table.table_params["column_alignment"]]
                + "X"
            )
            self.start_tabular = "\\begin{tabularx}{\\textwidth}{"
            self.end_tabular = "\\end{tabularx}\n"

    def render(self, only_tabular=False):
        out = self.generate_header(only_tabular)
        out += self.generate_body()
        out += self.generate_footer(only_tabular)
        out = out.replace("−", "-")

        return out

    def generate_header(self, only_tabular=False):
        header = ""
        if not only_tabular:
            header += "\\begin{table}[!ht]\n  \\centering\n"

            if self.table.table_params["caption_location"] == "top":
                # if it's a long table, caption must go in longtable environment
                if self.table.caption is not None and not self.table.longtable:
                    header += "  \\caption{" + self.table.caption + "}\n"

                if self.table.label is not None and not self.table.longtable:
                    header += "  \\label{" + self.table.label + "}\n"

        # alignment for the individual columns
        col_alignments = self.calign * self.table.ncolumns
        index_alignment = self.ialign
        if self.table.table_params["include_index"]:
            col_alignments = index_alignment + col_alignments
        begin = self.start_tabular
        if self.table.longtable:
            begin = "\\begin{longtable}{"
        header += begin + col_alignments + "}\n"
        # add caption for longtables
        if (
            self.table.table_params["caption_location"] == "top"
            and self.table.longtable
        ):
            if self.table.caption is not None:
                header += "  \\caption{" + self.table.caption + "}"

            if self.table.label is not None:
                header += "  \\label{" + self.table.label + "}"
            if self.table.caption is not None or self.table.label is not None:
                header += r"\\" + "\n"
        if self.table.panel_label is not None:
            n = len(self.table.columns) + self.table.table_params["include_index"]
            header += (
                f"  \\multicolumn{{{n}}}"
                + f"{{{self.table.panel_label_alignment}}}"
                + f"{{{self.table.panel_label}}}"
                + r"\\"
                + "\n"
            )
        header += "  \\toprule\n"
        if self.table.table_params["double_top_rule"]:
            header += "  \\toprule\n"
        column_content = (
            ""  # created for storing column info that's repeated in a longtable
        )
        for row in self.table._multicolumns:
            # TODO: convert the line below to allow for labeling each multicolumn
            # header += ("  " + self.table.index_name + " & ") * self.table.table_params['include_index']
            header += (
                "  & "
                * self.table.table_params["include_index"]
                * (1 - row["cover_index"])
            )
            column_content += "  & " * self.table.table_params["include_index"]
            underline_line = ""
            underline_start = self.table.table_params["include_index"] + 1
            if row["cover_index"]:
                underline_start -= 1
            mcs = []
            for c, s in zip(row["columns"], row["spans"]):
                mcs.append(f"\\multicolumn{{{s}}}{{{row['alignment']}}}{{{c}}}")
                if row["underline"]:
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
            column_content += " & ".join(mcs) + " \\\\\n"
            if row["underline"]:
                header += "  " + underline_line + "\n"
                column_content += "  " + underline_line + "\n"
        if self.table.custom_tex_lines["after-multicolumns"]:
            for line in self.table.custom_tex_lines["after-multicolumns"]:
                header += "  " + line + "\n"
                column_content += "  " + line + "\n"
        if self.table.table_params["show_columns"]:
            header += ("  " + self.table.index_name + " & ") * self.table.table_params[
                "include_index"
            ]
            column_content += (
                "  " + self.table.index_name + " & "
            ) * self.table.table_params["include_index"]
            header += "  " + " & ".join(
                [
                    self._escape(self.table._column_labels.get(col, col))
                    for col in self.table.columns
                ]
            )
            column_content += " & ".join(
                [
                    self._escape(self.table._column_labels.get(col, col))
                    for col in self.table.columns
                ]
            )
            header += "\\\\\n"
            column_content += "\\\\\n"
        if self.table.custom_tex_lines["after-columns"]:
            for line in self.table.custom_tex_lines["after-columns"]:
                header += "  " + line + "\n"
                column_content += "  " + line + "\n"
        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line)
                column_content += self._create_line(line)
        if self.table.table_params["show_columns"]:
            header += "  \\midrule\n"

        if self.table.longtable:
            header += "  \\endfirsthead\n\n"

            # define columns for other heads
            header += "  \\toprule\n"
            if self.table.table_params["double_top_rule"]:
                header += "  \\toprule\n"
            header += "  " + column_content + "\n"
            header += "  \\midrule\n  \\endhead\n\n  \\midrule\n"
            n = len(self.table.columns) + (1 * self.table.table_params["include_index"])
            header += (
                "  \\multicolumn{" + f"{n}" + r"}{r}{Continued on next page} \\" + "\n"
            )
            header += "  \\midrule\n  \\endfoot\n\n  \\bottomrule\n  \\endlastfoot \n\n"

        return header

    def generate_body(self):
        rows = self.table._create_rows()
        row_str = ""
        for row in rows:
            row_str += "  "
            for i, r in enumerate(row):
                _r = r
                if i == 0 and self.table.table_params["include_index"]:
                    # opptionally escape index
                    _r["escape"] = self.table.table_params["index_escape"]
                row_str += " & " * (i != 0) + self._format_value(_r)
            row_str += " \\\\\n"
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
            # longtables already have a bottom rule
            if not self.table.longtable:
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

        if self.table.longtable:
            if self.table.table_params["caption_location"] == "bottom":
                if self.table.caption is not None:
                    footer += "  \\caption{" + self.table.caption + "}\n"

                if self.table.label is not None:
                    footer += "  \\label{" + self.table.label + "}\n"
            footer += "\\end{longtable}\n"
        else:
            footer += self.end_tabular
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

    def _format_value(self, formatting_dict: dict, **kwargs) -> str:
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

    def render(self, convert_latex=True):
        out = self.generate_header(convert_latex=convert_latex)
        out += self.generate_body(convert_latex=convert_latex)
        out += self.generate_footer(convert_latex=convert_latex)
        # sometimes python uses the wrong encoding for a minus sign/hyphen. Accounts for that
        out = out.replace("−", "-")
        return out

    def generate_header(self, convert_latex=True):
        header = "<table>\n"
        if self._class:
            header = f'<table class="{self._class}">\n'
        header += "  <thead>\n"
        if self.table.caption and self.table.table_params["caption_location"] == "top":
            caption = self.table.caption
            if convert_latex:
                caption = replace_latex(caption)
            header += f'    <tr><th  colspan="{self.ncolumns}" style="text-align:center">{caption}</th></tr>\n'
        for row in self.table._multicolumns:
            header += "    <tr>\n"
            header += (
                (f'      <th style="text-align:{self.ialign};"></th>\n')
                * self.table.table_params["include_index"]
                * (1 - row["cover_index"])
            )
            th = '<th colspan="{s}" style="text-align:{a};">{c}</th>'
            if row["underline"]:
                th = '<th colspan="{s}" style="text-align:{a};"><u>{c}</u></th>'
            header += "      "
            for c, s in zip(row["columns"], row["spans"]):
                _col = c
                if convert_latex:
                    _col = replace_latex(c)
                header += " " + th.format(c=_col, s=s, a=row["alignment"])
            header += "\n"
            header += "    </tr>\n"
        for line in self.table.custom_html_lines["after-multicolumns"]:
            # TODO: Implement
            pass
        if self.table.table_params["show_columns"]:
            header += "    <tr>\n"
            _index_name = self.table.index_name
            if convert_latex:
                _index_name = replace_latex(_index_name)
            header += (f"      <th>{_index_name}</th>\n") * self.table.table_params[
                "include_index"
            ]
            for col in self.table.columns:
                header += f'      <th style="text-align:{self.calign};">{self.table._column_labels.get(col, col)}</th>\n'
            header += "    </tr>\n"
        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line)
        header += "  </thead>\n"
        header += "  <tbody>\n"
        return header

    def generate_body(self, convert_latex=True):
        rows = self.table._create_rows()
        row_str = ""
        for row in rows:
            row_str += "    <tr>\n"
            for i, r in enumerate(row):
                alignment = self.calign
                if i == 0 and self.table.table_params["include_index"]:
                    alignment = self.ialign
                val = self._format_value(r, alignment)
                if convert_latex:
                    val = replace_latex(val)
                row_str += f"{val}\n"
            row_str += "    </tr>\n"
        for line in self.table.custom_html_lines["after-body"]:
            row_str += line
        for line in self.table.custom_lines["after-body"]:
            row_str += self._create_line(line, convert_latex=convert_latex)
        if isinstance(self.table, st.tables.ModelTable):
            # insert a horizontal rule before the stats rows
            row_str += "    <tr>\n"
            row_str += (
                "      <td colspan='100%' style='border-top: 1px solid black;'></td>\n"
            )
            row_str += "    </tr>\n"
            for line in self.table.custom_lines["before-model-stats"]:
                row_str += self._create_line(line, convert_latex=convert_latex)
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
                row_str += self._create_line(line, convert_latex=convert_latex)
        return row_str

    def generate_footer(self, convert_latex=True):
        footer = ""
        if self.table.custom_lines["after-footer"]:
            footer += "    <tr>\n"
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line, convert_latex=convert_latex)
            footer += "    </tr>\n"
        if self.table.notes:
            ncols = self.table.ncolumns + self.table.table_params["include_index"]
            for note, alignment, _ in self.table.notes:
                _notes = textwrap.wrap(note, width=st.STParams["max_html_notes_length"])
                for _note in _notes:
                    _note_str = _note
                    if convert_latex:
                        _note_str = replace_latex(_note_str)
                    footer += (
                        f'    <tr><td colspan="{ncols}" '
                        f'style="text-align:{self.ALIGNMENTS[alignment]};'
                        f'"><i>{_note_str}</i></td></tr>\n'
                    )
        if (
            self.table.caption
            and self.table.table_params["caption_location"] == "bottom"
        ):
            caption = self.table.caption
            if convert_latex:
                caption = replace_latex(caption)
            footer += f'    <tr><th colspan="{self.ncolumns}" style="text-align:center">{caption}</th></tr>\n'
        footer += "  </tbody>\n"
        footer += "</table>"
        return footer

    def _create_line(self, line, convert_latex=True):
        out = ""
        if line["deliminate"]:
            out += "    <tr>\n"
            out += (
                "      <td colspan='100%' style='border-top: 1px solid black;'></td>\n"
            )
            out += "    </tr>\n"
        out = "    <tr>\n"
        label = line["label"]
        if convert_latex:
            label = replace_latex(label)
        out += (
            f'      <th style="text-align:{self.ialign};"' + f">{label}</th>\n"
        ) * self.table.table_params["include_index"]
        for l in line["line"]:
            out += f'      <td style="text-align:{self.calign};">{l}</td>\n'
        out += "    </tr>\n"

        return out

    def _format_value(self, formatting_dict: dict, alignment: str, **kwargs) -> str:
        cell = f"      <td"
        if formatting_dict["class"]:
            _class = formatting_dict["class"]
            cell += f' class="{_class}"'
        if formatting_dict["id"]:
            _id = formatting_dict["id"]
            cell += f' id="{_id}"'
        # cell style section
        style = f' style="text-align: {alignment};'
        if formatting_dict["color"]:
            style += f" color: {formatting_dict['color']};"
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
        "<": "<",
        "^": "^",
        ">": ">",
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

    def render(self, convert_latex=True) -> str:
        self._get_table_widths(convert_latex=convert_latex)
        out = self.generate_header(convert_latex=convert_latex)
        out += self.generate_body(convert_latex=convert_latex)
        out += self.generate_footer(convert_latex=convert_latex)
        out = out.replace("−", "-")
        return out

    def generate_header(self, convert_latex=True) -> str:
        header = ""
        if self.table.caption and self.table.table_params["caption_location"] == "top":
            caption = self.table.caption
            if convert_latex:
                caption = replace_latex(caption)
            header += f"\n{caption:^{self._len + (2 * self._border_len)}}\n"
        header += (
            st.STParams["ascii_header_char"] * (self._len + (2 * self._border_len))
            + "\n"
        )
        if st.STParams["ascii_double_top_rule"]:
            header += (
                st.STParams["ascii_header_char"] * (self._len + (2 * self._border_len))
                + "\n"
            )
        for row in self.table._multicolumns:
            header += st.STParams["ascii_border_char"] + (
                " "
                * self.max_index_name_cell_size
                * self.table.table_params["include_index"]
                * (1 - row["cover_index"])
            )
            underlines = st.STParams[
                "ascii_border_char"
            ] + " " * self.max_index_name_cell_size * self.table.table_params[
                "include_index"
            ] * (
                1 - row["cover_index"]
            )

            for c, s in zip(row["columns"], row["spans"]):
                _size = self.max_body_cell_size * s
                _col = c
                if convert_latex:
                    _col = replace_latex(c)
                # TODO: fix alignment
                _align = self.ALIGNMENTS[row["alignment"]]
                # add a pad to name for non-center alignments since underline will
                # also have a pad. This makes the two line up
                if _align == "<":
                    _col = " " + _col
                if _align == ">":
                    _col += " "
                header += f"{_col:{_align}{_size}}"
                uchar = "-" if c != "" else " "
                underlines += f"{uchar * (_size - 2):^{_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"
            if row["underline"]:
                header += underlines + f"{st.STParams['ascii_border_char']}\n"
        if self.table.table_params["show_columns"]:
            header += st.STParams["ascii_border_char"]
            _index_name = self.table.index_name
            if convert_latex:
                _index_name = replace_latex(_index_name)
            _size = self.max_index_name_cell_size
            _align = self.ialign
            header += (f"{_index_name:{_align}{_size}}") * self.table.table_params[
                "include_index"
            ]
            for col in self.table.columns:
                _col = self.table._column_labels.get(col, col)
                if convert_latex:
                    _col = replace_latex(_col)
                header += f"{_col:^{self.max_body_cell_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"

        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                header += self._create_line(line, convert_latex=convert_latex)
        if self.table.table_params["show_columns"]:
            header += (
                st.STParams["ascii_border_char"]
                + st.STParams["ascii_mid_rule_char"] * (self._len)
                + f"{st.STParams['ascii_border_char']}\n"
            )
        return header

    # get the length of the header lines by counting number of characters in each column
    def generate_body(self, convert_latex=True) -> str:
        rows = self.table._create_rows()
        body = ""
        for row in rows:
            body += st.STParams["ascii_border_char"]
            for i, r in enumerate(row):
                _size = self.max_body_cell_size
                _align = self.calign
                _val = self._format_value(r)
                if convert_latex:
                    _val = replace_latex(_val)
                if i == 0 and self.table.table_params["include_index"]:
                    _size = self.max_index_name_cell_size - self.padding
                    _align = self.ialign
                    body += " " * self.padding + f"{_val:{_align}{_size}}"
                else:
                    body += f"{_val:{_align}{_size}}"
            body += f"{st.STParams['ascii_border_char']}\n"

        for line in self.table.custom_lines["after-body"]:
            body += self._create_line(line, convert_latex=convert_latex)

        if isinstance(self.table, st.tables.ModelTable):
            body += (
                st.STParams["ascii_mid_rule_char"]
                * (self._len + (2 * self._border_len))
                + "\n"
            )
            for line in self.table.custom_lines["before-model-stats"]:
                body += self._create_line(line, convert_latex=convert_latex)
            stats_rows = self.table._create_stats_rows(renderer="ascii")
            for row in stats_rows:
                body += f"{st.STParams['ascii_border_char']}"
                for i, r in enumerate(row):
                    _size = self.max_body_cell_size
                    _val = self._format_value(r)
                    if convert_latex:
                        _val = replace_latex(_val)
                    if i == 0 and self.table.table_params["include_index"]:
                        _size = self.max_index_name_cell_size - self.padding
                        body += " " * self.padding + f"{_val:{self.ialign}{_size}}"
                    else:
                        body += f"{_val:{self.calign}{_size}}"
                body += f"{st.STParams['ascii_border_char']}\n"
            for line in self.table.custom_lines["after-model-stats"]:
                body += self._create_line(line, convert_latex=convert_latex)
        return body

    def generate_footer(self, convert_latex=True) -> str:
        footer = st.STParams["ascii_footer_char"] * (self._len + (2 * self._border_len))
        if st.STParams["ascii_double_bottom_rule"]:
            footer += st.STParams["ascii_footer_char"] * (
                self._len + (2 * self._border_len)
            )
        if self.table.custom_lines["after-footer"]:
            footer += "\n"
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line, convert_latex=convert_latex)
            footer += st.STParams["ascii_footer_char"] * (
                self._len + (2 * self._border_len)
            )
            if st.STParams["ascii_double_bottom_rule"]:
                footer += st.STParams["ascii_footer_char"] * (
                    self._len + (2 * self._border_len)
                )
        if self.table.notes:
            for note, alignment, _ in self.table.notes:
                notes = textwrap.wrap(
                    note, width=min(self._len, st.STParams["max_ascii_notes_length"])
                )
                _alignment = self.ALIGNMENTS[alignment]
                for _note in notes:
                    _note_val = _note
                    if convert_latex:
                        _note_val = replace_latex(_note_val)
                    footer += f"\n{_note_val:{_alignment}{self._len}}"
        if (
            self.table.caption
            and self.table.table_params["caption_location"] == "bottom"
        ):
            caption = self.table.caption
            if convert_latex:
                caption = replace_latex(caption)
            footer += f"\n{caption:^{self._len + (2 * self._border_len)}}\n"
        return footer

    def _create_line(self, line, convert_latex=True) -> str:
        _line = ""
        if line["deliminate"]:
            _line += (
                st.STParams["ascii_mid_rule_char"]
                * (self._len + (2 * self._border_len))
                + "\n"
            )
        _line += st.STParams["ascii_border_char"]
        label = line["label"]
        if convert_latex:
            label = replace_latex(label)
        if self.table.table_params["include_index"]:
            _line += (
                " " * self.padding
                + f"{label:{self.ialign}{self.max_index_name_cell_size - self.padding}}"
            )
        for l in line["line"]:
            _l = l
            if convert_latex:
                _l = replace_latex(l)
            _line += f"{_l:{self.calign}{self.max_body_cell_size}}"
        _line += st.STParams["ascii_border_char"] + "\n"
        return _line

    def _get_table_widths(self, convert_latex=True) -> None:
        self.reset_size_parameters()
        # find longest row and biggest cell
        rows = self.table._create_rows()
        for row in rows:
            row_len = 0
            for i, cell in enumerate(row):
                _val = cell["value"]
                if convert_latex:
                    _val = replace_latex(_val)
                cell_size = len(_val) + (self.padding * 2)
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
                    _val = cell["value"]
                    if convert_latex:
                        _val = replace_latex(_val)
                    cell_size = len(_val) + (self.padding * 2)
                    self.max_body_cell_size = max(self.max_body_cell_size, cell_size)
                    row_len += cell_size
                    if i == 0 and self.table.table_params["include_index"]:
                        self.max_index_name_cell_size = max(
                            self.max_index_name_cell_size, cell_size
                        )
                self.max_row_len = max(self.max_row_len, row_len)

        if self.table.table_params["include_index"]:
            _index_name = self.table.index_name
            if convert_latex:
                _index_name = replace_latex(_index_name)
            index_name_size = len(_index_name) + (self.padding * 2)
            self.max_index_name_cell_size = max(
                self.max_index_name_cell_size, index_name_size
            )
            # check line size of all line labels
            for loc in VALID_LINE_LOCATIONS:
                for line in self.table.custom_lines[loc]:
                    label = line["label"]
                    if convert_latex:
                        label = replace_latex(label)
                    self.max_index_name_cell_size = max(
                        self.max_index_name_cell_size,
                        len(label) + (self.padding * 2),
                    )

        # find longest column and length needed for all columns
        if self.table.table_params["show_columns"]:
            col_len = 0
            # loop through all the columns
            for col in self.table.columns:
                # check label size
                label = self.table._column_labels.get(col, col)
                if convert_latex:
                    label = replace_latex(label)
                col_size = len(str(label)) + (self.padding * 2)
                self.max_body_cell_size = max(self.max_body_cell_size, col_size)
                col_len += col_size
            # check size of index labels
            if self.table.table_params["include_index"]:
                col_len += self.max_index_name_cell_size
            self.max_row_len = max(self.max_row_len, col_len)
        # get size of multicolumns
        if self.table._multicolumns:
            for row in self.table._multicolumns:
                for c, s in zip(row["columns"], row["spans"]):
                    # total space the multicolumn will span over based on the size
                    # of the body cells
                    span_size = self.max_body_cell_size * s
                    # size of the multicolumn label after padding
                    _col = c
                    if convert_latex:
                        _col = replace_latex(_col)
                    col_size = len(_col) + (self.padding * 2)
                    multi_col_size = math.ceil(max(span_size, col_size) / s)
                    self.max_body_cell_size = max(
                        self.max_body_cell_size, multi_col_size
                    )

        self._len = self.max_body_cell_size * self.table.ncolumns
        self._len += self.max_index_name_cell_size
        self._border_len = len(st.STParams["ascii_border_char"])

    def _format_value(self, formatting_dict: dict, **kwargs) -> str:
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
