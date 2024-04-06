from abc import ABC, abstractmethod


class Renderer:
    def __init__(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def generate_header(self): ...

    @abstractmethod
    def generate_body(self): ...

    @abstractmethod
    def generate_footer(self): ...

    @abstractmethod
    def _create_line(self): ...


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

            if self.table.caption is not None:
                header += "  \\caption{" + self.table.caption + "}\n"

            if self.table.label is not None:
                header += "  \\label{" + self.table.label + "}\n"

        content_columns = "c" * self.table.ncolumns
        if self.table.include_index:
            content_columns = "l" + content_columns
        header += "\\begin{tabular}{" + content_columns + "}\n"
        header += "  \\toprule\n"
        # if len(self.table._multicolumns) > 0:
        # if self.table.include_index:
        # header += ("  " + self.table.index_name + " & ") * self.table.include_index
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
            # header += "\\\\\n"
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
            # header += "\\\\\n"
        if self.table.custom_lines["after-columns"]:
            for line in self.table.custom_lines["after-columns"]:
                # header += ("  " + line["label"] + " & ") * self.table.include_index
                # header += " & ".join(line["line"])
                # header += "\\\\\n"
                header += self._create_line(line)
            # header += "\\\\\n"
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
            footer += "\\end{table}\n"

        return footer

    def _escape(self, text):
        for char, escaped in self._ESCAPE_CHARS:
            text = text.replace(char, escaped)
        return text

    def _create_line(self, line):
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
        # if len(self.table._multicolumns) > 0:
        # header += "    <tr>\n"
        # header += (
        #     f"      <th>{self.table.index_name}</th>\n" * self.table.include_index
        # )
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
                # header += "    <tr>\n"
                # header += f"      <th>{line['label']}</th>\n" * self.table.include_index
                # for l in line["line"]:
                #     header += f"      <th>{l}</th>\n"
                # header += "    </tr>\n"
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
