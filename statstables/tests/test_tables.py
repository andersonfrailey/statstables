"""
Tests implementation of tables
"""

import pytest
import pandas as pd
import statsmodels.formula.api as smf
from statstables import tables


def test_generic_table(data):
    table = tables.GenericTable(df=data)
    table.index_name = "index"
    table.label = "table:generic"

    table.render_ascii()
    table.render_html()
    table.render_latex()

    table2 = tables.GenericTable(
        data,
        caption_location="top",
        sig_digits=4,
        show_columns=False,
        include_index=False,
        column_labels={"A": "a", "B": "b"},
        index_labels={0: "x", 1: "y"},
        index_name="Index",
    )

    table2.table_params["caption_location"] = "bottom"

    # a couple of basic tables just to make sure the minimum example works
    df = pd.DataFrame({"one": [1, 2, 3], "two": [-1, -2, -3]})
    table = tables.GenericTable(df)
    print(table)

    df = pd.DataFrame({"one": ["1", "2", "3"], "two": ["-1", "-2", "-3"]})
    table = tables.GenericTable(df)
    print(table)


def test_summary_table(data):
    table = tables.SummaryTable(df=data, var_list=["A", "B", "C"])
    table.custom_formatters(
        {
            "count": lambda x: f"{x:,.0f}",
            "max": lambda x: f"{x:,.2f}",
            ("mean", "A"): lambda x: f"{x:,.2f}",
            ("std", "C"): lambda x: f"{x:,.4f}",
        }
    )
    table.rename_index({"count": "Number of Observations"})
    table.rename_columns({"A": "a"})
    table.add_multicolumns(["First", "Second"], [1, 2])
    table.add_line(["Yes", "No", "Yes"], location="after-columns", label="Example")
    table.add_line(["No", "Yes", "No"], location="after-body")
    table.add_line(["Low A", "Low B", "Low C"], location="after-footer", label="Lowest")
    table.add_note("The default note aligns over here.")
    table.add_note("But you can move it to the middle!", alignment="c")
    table.add_note("Or over here!", alignment="r")
    table.caption = "Summary Table"
    table.label = "table:summarytable"
    table.render_html()
    table.render_latex()
    table.render_latex(only_tabular=True)

    table.render_ascii()
    table.render_html()
    table.render_latex()


def test_mean_differences_table(data):
    table = tables.MeanDifferenceTable(
        df=data,
        var_list=["A", "B", "C"],
        group_var="group",
        diff_pairs=[("X", "Y"), ("X", "Z"), ("Y", "Z")],
    )
    table.caption = "Differences in means"
    table.label = "table:differencesinmeans"
    table.table_params["caption_location"] = "top"
    table.custom_formatters({("A", "X"): lambda x: f"{x:.2f}"})

    table.render_ascii()
    table.render_html()
    table.render_latex()

    assert table.table_params["include_index"] == True


def test_model_table(data):
    mod1 = smf.ols("A ~ B + C -1", data=data).fit()
    mod2 = smf.ols("A ~ B + C", data=data).fit()
    mod_table = tables.ModelTable(models=[mod1, mod2])
    mod_table.table_params["show_model_numbers"] = True
    mod_table.parameter_order(["Intercept", "B", "C"])
    # check that various information is and is not present
    mod_text = mod_table.render_ascii()
    assert "N. Groups" not in mod_text
    assert "Pseudo R2" not in mod_text

    binary_mod = smf.probit("binary ~ A + B", data=data).fit()
    binary_table = tables.ModelTable(models=[binary_mod])
    binary_text = binary_table.render_latex()
    assert "Pseudo $R^2$" in binary_text
    binary_table.table_params["show_pseudo_r2"] = False
    binary_text = binary_table.render_html()
    assert "Pseudo R<sup>2</sup>" not in binary_text

    assert binary_table.table_params["include_index"] == True
