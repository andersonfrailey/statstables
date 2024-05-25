from abc import ABC, abstractmethod
import statstables as st


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
    ]

    def __init__(self, table):
        self.table = table

    def render(self, only_tabular=False):
        out = self.generate_header(only_tabular)
        out += self.generate_body()
        out += self.generate_footer(only_tabular)

        return out

    def generate_header(self, only_tabular=False, column_alignment=None):
        header = ""
        if not only_tabular:
            header += "\\begin{table}[!htbp]\n  \\centering\n"

            if self.table.caption_location == "top":
                if self.table.caption is not None:
                    header += "  \\caption{" + self.table.caption + "}\n"

                if self.table.label is not None:
                    header += "  \\label{" + self.table.label + "}\n"

        content_columns = "c" * self.table.ncolumns
        if self.table.include_index:
            content_columns = "l" + content_columns
        header += "\\begin{tabular}{" + content_columns + "}\n"
        header += "  \\toprule\n"
        for col, spans in self.table._multicolumns:
            header += ("  " + self.table.index_name + " & ") * self.table.include_index
            header += " & ".join(
                [
                    f"\\multicolumn{{{s}}}{{c}}{{{self._escape(c)}}}"
                    for c, s in zip(col, spans)
                ]
            )
            header += " \\\\\n"
        if self.table.custom_tex_lines["after-multicolumns"]:
            for line in self.table.custom_tex_lines["after-multicolumns"]:
                header += "  " + line + "\n"
        if self.table.show_columns:
            header += ("  " + self.table.index_name + " & ") * self.table.include_index
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
            row_str += "  " + " & ".join([self._escape(r) for r in row]) + " \\\\\n"
        for line in self.table.custom_lines["after-body"]:
            row_str += self._create_line(line)
        for line in self.table.custom_tex_lines["after-body"]:
            row_str += line
        return row_str

    def generate_footer(self, only_tabular=False):
        footer = "  \\bottomrule\n"
        if self.table.custom_lines["after-footer"]:
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line)
            footer += "  \\bottomrule\n"
        if self.table.notes:
            for note, alignment, escape in self.table.notes:
                align_cols = self.table.ncolumns + self.table.include_index
                footer += f"  \\multicolumn{{{align_cols}}}{{{alignment}}}"
                _note = self._escape(note) if escape else note
                footer += "{{" + "\\small \\textit{" + _note + "}}}\\\\\n"

        footer += "\\end{tabular}\n"
        if not only_tabular:
            if self.table.caption_location == "bottom":
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
        out = ("  " + line["label"] + " & ") * self.table.include_index
        out += " & ".join(line["line"])
        out += "\\\\\n"

        return out


class HTMLRenderer(Renderer):
    ALIGNMENTS = {"l": "left", "c": "center", "r": "right"}

    def __init__(self, table):
        self.table = table
        self.ncolumns = self.table.ncolumns + int(self.table.include_index)

    def render(self):
        out = self.generate_header()
        out += self.generate_body()
        out += self.generate_footer()
        return out

    def generate_header(self):
        header = "<table>\n"
        header += "  <thead>\n"
        for col, spans in self.table._multicolumns:
            header += "    <tr>\n"
            header += (
                f"      <th>{self.table.index_name}</th>\n"
            ) * self.table.include_index
            header += "      " + " ".join(
                [
                    f'<th colspan="{s}" style="text-align:center;">{c}</th>'
                    for c, s in zip(col, spans)
                ]
            )
            header += "\n"
            header += "    </tr>\n"
        for line in self.table.custom_html_lines["after-multicolumns"]:
            # TODO: Implement
            pass
        if self.table.show_columns:
            header += "    <tr>\n"
            header += (
                f"      <th>{self.table.index_name}</th>\n"
            ) * self.table.include_index
            for col in self.table.columns:
                header += f'      <th style="text-align:center;">{self.table._column_labels.get(col, col)}</th>\n'
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
            for r in row:
                row_str += f"      <td>{r}</td>\n"
            row_str += "    </tr>\n"
        for line in self.table.custom_lines["after-body"]:
            row_str += self._create_line(line)
        for line in self.table.custom_html_lines["after-body"]:
            row_str += line
            pass
        return row_str

    def generate_footer(self):
        footer = ""
        if self.table.custom_lines["after-footer"]:
            footer += "    <tr>\n"
            for line in self.table.custom_lines["after-footer"]:
                footer += self._create_line(line)
            footer += "    </tr>\n"
        if self.table.notes:
            ncols = self.table.ncolumns + self.table.include_index
            for note, alignment, _ in self.table.notes:
                # TODO: This doesn't actually align where expected in a notebook. Fix.
                footer += (
                    f'    <tr><td colspan="{ncols}" '
                    f'style="text-align:{self.ALIGNMENTS[alignment]};'
                    f'"><i>{note}</i></td></tr>\n'
                )
        footer += "  </tbody>\n"
        return footer

    def _create_line(self, line):
        out = "    <tr>\n"
        out += (f"      <th>{line['label']}</th>\n") * self.table.include_index
        for l in line["line"]:
            out += f"      <th>{l}</th>\n"
        out += "    </tr>\n"

        return out


class ASCIIRenderer(Renderer):
    ALIGNMENTS = {"l": "<", "c": "^", "r": ">"}

    def __init__(self, table):
        self.table = table
        # number of spaces to place on either side of cell values
        self.padding = st.STParams["ascii_padding"]
        self.ncolumns = self.table.ncolumns + int(self.table.include_index)
        self.reset_size_parameters()

    def reset_size_parameters(self):
        self.max_row_len = 0
        self.max_body_cell_size = 0
        self.max_index_name_cell_size = 0
        self._len = 0

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

    def render(self) -> str:
        self._get_table_widths()
        out = self.generate_header()
        out += self.generate_body()
        out += self.generate_footer()
        return out

    def generate_header(self) -> str:
        header = (
            st.STParams["ascii_header_char"] * (self._len + (2 * self._border_len))
            + "\n"
        )
        # underlines = st.STParams["ascii_border_char"]
        for col, span in self.table._multicolumns:
            header += st.STParams["ascii_border_char"] + (
                " " * self.max_index_name_cell_size * self.table.include_index
            )
            # underlines += " " * self.max_index_name_cell_size * self.table.include_index

            for c, s in zip(col, span):
                _size = self.max_body_cell_size * s
                # if self.table.include_index:
                #     _size += self.max_body_cell_size *
                header += f"{c:^{_size}}"
                # underlines += f"{'-' * len(c):^{_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"
            # header += underlines + f"{st.STParams['ascii_border_char']}\n"
        if self.table.show_columns:
            header += st.STParams["ascii_border_char"]
            header += (
                f"{self.table.index_name:^{self.max_index_name_cell_size}}"
            ) * self.table.include_index
            for col in self.table.columns:
                header += f"{self.table._column_labels.get(col, col):^{self.max_body_cell_size}}"
            header += f"{st.STParams['ascii_border_char']}\n"
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
                if i == 0 and self.table.include_index:
                    _size = self.max_index_name_cell_size
                body += f"{r:^{_size}}"
            body += f"{st.STParams['ascii_border_char']}\n"
        return body

    def generate_footer(self) -> str:
        footer = st.STParams["ascii_footer_char"] * (self._len + (2 * self._border_len))
        if self.table.notes:
            for note, alignment, _ in self.table.notes:
                footer += "\n"
                _alignment = self.ALIGNMENTS[alignment]
                footer += f"{note:{_alignment}{self._len}}"
        return footer

    def _create_line(self, line) -> str:
        return ""

    def _get_table_widths(self) -> None:
        self.reset_size_parameters()
        # find longest row and biggest cell
        rows = self.table._create_rows()
        for row in rows:
            row_len = 0
            for i, cell in enumerate(row):
                cell_size = len(str(cell)) + (self.padding * 2)
                self.max_body_cell_size = max(self.max_body_cell_size, cell_size)
                row_len += cell_size
                if i == 0 and self.table.include_index:
                    self.max_index_name_cell_size = max(
                        self.max_index_name_cell_size, cell_size
                    )
            self.max_row_len = max(self.max_row_len, row_len)

        if self.table.include_index:
            index_name_size = len(str(self.table.index_name)) + (self.padding * 2)
            self.max_index_name_cell_size = max(
                self.max_index_name_cell_size, index_name_size
            )

        # find longest column and length needed for all columns
        if self.table.show_columns:
            col_len = 0
            for col in self.table.columns:
                col_size = len(str(col)) + (self.padding * 2)
                self.max_body_cell_size = max(self.max_body_cell_size, col_size)
                col_len += col_size
            if self.table.include_index:
                col_len += self.max_index_name_cell_size
            self.max_row_len = max(self.max_row_len, col_len)
        self._len = self.max_body_cell_size * self.table.ncolumns
        self._len += self.max_index_name_cell_size
        self._border_len = len(st.STParams["ascii_border_char"])
