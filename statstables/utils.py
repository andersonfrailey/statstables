import numpy as np
import unicodeit


def format_values(vals, pvals, plevels, sigdigits):
    formatted_vals = []
    for val, pval in zip(vals, pvals):
        if pval < plevels[0]:
            formatted_vals.append(f"{val:,.{sigdigits}f}***")
        elif pval < plevels[1]:
            formatted_vals.append(f"{val:,.{sigdigits}f}**")
        elif pval < plevels[2]:
            formatted_vals.append(f"{val:,.{sigdigits}f}*")
        else:
            formatted_vals.append(f"{val:,.{sigdigits}f}")
    return formatted_vals


def pstars(value, plevels):
    if np.isnan(value):
        return ""
    levels = sorted(plevels, reverse=True)
    stars = ""
    for pval in levels:
        if value > pval:
            break
        stars += "*"
    return stars


VALID_LINE_LOCATIONS = [
    "after-multicolumns",
    "after-columns",
    "after-body",
    "after-footer",
    "after-model-stats",
    "before-model-stats",
]


def validate_line_location(line_location: str | None) -> None:
    if line_location not in VALID_LINE_LOCATIONS:
        raise ValueError(
            f"Invalid line location: {line_location}. "
            f"Valid line locations are: {VALID_LINE_LOCATIONS}"
        )


def replace_latex(line: str) -> str:
    assert isinstance(line, str)
    # remove dollar signs used to indicate latex section
    if "\\$" not in line:
        line = line.replace("$", "")
    else:
        line = line.replace("\\$", "__dollar_sign__")
        line = line.replace("$", "")
        line = line.replace("__dollar_sign__", "$")
    return unicodeit.replace(line)


def latex_preamble() -> str:
    preamble = r"% You must add \usepackage{booktabs} to your LaTex document for table to compile."
    preamble += "\n"
    preamble += r"% If you use color in your formatting, you must also add \usepackage{xcolor} to the preamble."
    preamble += "\n\n"
    preamble += r"% If you are making a longtable, you must add \usepackage{longtable} to the preamble."
    preamble += "\n\n"
    return preamble
