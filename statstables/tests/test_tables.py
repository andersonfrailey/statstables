import pytest
import statsmodels.formula.api as smf
from statstables import tables


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

    with pytest.raises(AssertionError):
        table.caption_location = "middle"

    bool_properties = ["include_index", "show_columns"]
    for prop in bool_properties:
        setattr(table, prop, True)
        setattr(table, prop, False)
        with pytest.raises(AssertionError):
            setattr(table, prop, "True")


def test_mean_differences_table(data):
    table = tables.MeanDifferenceTable(
        df=data,
        var_list=["A", "B", "C"],
        group_var="group",
        diff_pairs=[("X", "Y"), ("X", "Z"), ("Y", "Z")],
    )
    table.caption = "Differences in means"
    table.label = "table:differencesinmeans"
    table.caption_location = "top"
    table.custom_formatters({("A", "X"): lambda x: f"{x:.2f}"})

    bool_properties = ["show_n", "show_standard_errors", "show_stars"]
    for prop in bool_properties:
        setattr(table, prop, True)
        setattr(table, prop, False)
        with pytest.raises(TypeError):
            setattr(table, prop, "True")


def test_model_table(data):
    mod1 = smf.ols("A ~ B + C -1", data=data).fit()
    mod2 = smf.ols("A ~ B + C", data=data).fit()
    mod_table = tables.ModelTable(models=[mod1, mod2])
    mod_table.show_model_nums = True
    mod_table.parameter_order(["Intercept", "B", "C"])
    # check that various information is and is not present
    mod_text = mod_table.render_ascii()
    assert "N. Groups" not in mod_text
    assert "Pseudo R2" not in mod_text

    binary_mod = smf.probit("binary ~ A + B", data=data).fit()
    binary_table = tables.ModelTable(models=[binary_mod])
    binary_text = binary_table.render_latex()
    assert "Pseudo $R^2$" in binary_text
    binary_table.show_pseudo_r2 = False
    binary_text = binary_table.render_html()
    assert "Pseudo R<sup>2</sup>" not in binary_text

    bool_properties = [
        "show_r2",
        "show_adjusted_r2",
        "show_dof",
        "show_cis",
        "show_ses",
        "show_fstat",
        "single_row",
        "show_observations",
        "show_model_numbers",
        "show_model_type",
        "show_pseudo_r2",
        "show_ngroups",
    ]
    for prop in bool_properties:
        setattr(mod_table, prop, True)
        setattr(mod_table, prop, False)
        with pytest.raises(AssertionError):
            setattr(mod_table, prop, "True")
