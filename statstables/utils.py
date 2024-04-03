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
]


def validate_line_location(line_location: str) -> None:
    if line_location not in VALID_LINE_LOCATIONS:
        raise ValueError(
            f"Invalid line location: {line_location}. "
            f"Valid line locations are: {VALID_LINE_LOCATIONS}"
        )
