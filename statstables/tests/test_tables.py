"""
Tests implementation of tables
"""

import pytest
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.api import add_constant
from statstables import tables
from faker import Faker
from pathlib import Path
from linearmodels.datasets import wage_panel
from linearmodels.panel import PooledOLS, RandomEffects, PanelOLS

CUR_PATH = Path(__file__).resolve().parent


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


def test_long_table():
    fake = Faker()
    Faker.seed(512)
    np.random.seed(410)
    names = [fake.name() for _ in range(100)]
    x1 = np.random.randint(500, 10000, 100)
    x2 = np.random.uniform(size=100)
    longdata = pd.DataFrame({"Names": names, "X1": x1, "X2": x2})
    longtable = tables.GenericTable(longdata, longtable=True, include_index=False)
    temp_path = Path("longtable_actual.tex")
    expected_tex = Path(CUR_PATH, "..", "..", "longtable.tex")

    compare_expected_output(
        expected_file=expected_tex,
        actual_table=longtable,
        render_type="tex",
        temp_file=temp_path,
    )


def test_panel_table():
    fake = Faker()
    Faker.seed(202)
    panela_df = pd.DataFrame(
        {
            "ID": [1234, 6789, 1023, 5810, 9182],
            "School": ["Texas", "UVA", "UMBC", "UGA", "Rice"],
        },
        index=[fake.name_male() for _ in range(5)],
    )
    panela = tables.GenericTable(
        panela_df,
        formatters={"ID": lambda x: f"{x}"},
    )
    panelb_df = pd.DataFrame(
        {
            "ID": [9183, 5734, 1290, 4743, 8912],
            "School": ["Wake Forrest", "Emory", "Texas", "UVA", "Columbia"],
        },
        index=[fake.name_female() for _ in range(5)],
    )
    panelb = tables.GenericTable(panelb_df, formatters={"ID": lambda x: f"{x}"})
    panel = tables.PanelTable([panela, panelb], ["Men", "Women"])

    compare_expected_output(
        expected_file=Path(CUR_PATH, "..", "..", "panel.tex"),
        actual_table=panel,
        render_type="tex",
        temp_file=Path("panel_table_actual.tex"),
    )


def test_linear_models():
    data = wage_panel.load()
    year = pd.Categorical(data.year)
    data = data.set_index(["nr", "year"])
    data["year"] = year

    data = wage_panel.load()
    year = pd.Categorical(data.year)
    data = data.set_index(["nr", "year"])
    data["year"] = year
    exog_vars = [
        "black",
        "hisp",
        "exper",
        "expersq",
        "married",
        "educ",
        "union",
        "year",
    ]
    exog = add_constant(data[exog_vars])
    pooled_mod = PooledOLS(data.lwage, exog).fit()
    random_mod = RandomEffects(data.lwage, exog).fit()
    exog_vars = [
        "expersq",
        "union",
        "married",
    ]
    panel_exog = add_constant(data[exog_vars])
    panel_mod = PanelOLS(
        data.lwage, panel_exog, entity_effects=True, time_effects=True
    ).fit()
    covariate_labels = {
        # statstables will convert LaTeX to unicode when rendering HTML and ASCII tables
        "const": r"$\alpha$",
        "exper": "Experience",
        "expersq": "Experience$^2$",
        "union": "Union",
        "married": "Married",
        "black": "Black",
    }
    covariate_order = ["const", "exper", "expersq", "union", "married", "black"]
    panel_table_long_name = tables.ModelTable(
        [pooled_mod, random_mod, panel_mod],
        covariate_labels=covariate_labels,
        covariate_order=covariate_order,
        dependent_variable_name="A Long Title That Would Look Odd",
        dependent_var_cover_index=True,
        dependent_var_alignment="r",
        show_stars=False,
        use_tabularx=True,
    )
    compare_expected_output(
        expected_file=Path(CUR_PATH, "..", "..", "wage_table_long_name.tex"),
        actual_table=panel_table_long_name,
        render_type="tex",
        temp_file=Path("wage_table_long_name_actual.tex"),
    )


def compare_expected_output(
    expected_file: Path, actual_table: tables.Table, render_type: str, temp_file: Path
):
    match render_type:
        case "tex":
            actual_table.render_latex(temp_file)
    actual_text = temp_file.read_text()
    expected_text = expected_file.read_text()
    try:
        assert actual_text == expected_text
        temp_file.unlink()
    except AssertionError as e:
        msg = f"Output has changed. New output in {str(temp_file)}"
        raise e(msg)
