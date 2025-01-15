"""
Test parameter implementations
"""

import pytest
import statstables as st
import statsmodels.formula.api as smf


def test_generic_table_params(data):
    """
    Test each of the parameter settings and validation
    """
    generic_table = st.tables.GenericTable(data)
    general_parameter_tests(generic_table, "generic")


def general_parameter_tests(table, table_type):
    """
    Tests the parameters included in all tables.
    """
    # specific parameter tests
    # ensure valid values are allowed
    for val in ["l", "r", "c", "left", "right", "center"]:
        table.table_params["column_alignment"] = val
        table.table_params["index_alignment"] = val

    table.table_params["sig_digits"] = 4
    table.table_params["thousands_sep"] = "."

    table.table_params["ascii_padding"] = 3
    # ensure invalid values throw errors
    with pytest.raises(AssertionError):
        table.table_params["caption_location"] = "middle"
        table.table_params["column_alignment"] = 1
        table.table_params["column_alignment"] = "a"

    bool_properties = [
        "include_index",
        "show_columns",
        "double_top_rule",
        "ascii_double_top_rule",
        "double_bottom_rule",
        "ascii_double_bottom_rule",
    ]
    include_index_invalid = ["meandiffs", "model"]
    for prop in bool_properties:
        # include index isn't allowed for model tables
        if table_type in include_index_invalid and prop == "include_index":
            continue
        table.table_params[prop] = True
        table.table_params[prop] = False
        with pytest.raises(AssertionError):
            table.table_params[prop] = "True"
            table.table_params[prop] = 1
            table.table_params[prop] = 0.5

    ascii_str_properties = [
        "ascii_header_char",
        "ascii_footer_char",
        "ascii_border_char",
        "ascii_mid_rule_char",
    ]
    for prop in ascii_str_properties:
        table.table_params[prop] = "."
        with pytest.raises(AssertionError):
            table.table_params[prop] = True
            table.table_params[prop] = 1
            table.table_params[prop] = 0.5


def test_mean_differences_table_params(data):
    """
    Test each of the parameters for a mean differences table
    """
    table = st.tables.MeanDifferenceTable(
        df=data,
        var_list=["A", "B", "C"],
        group_var="group",
        diff_pairs=[("X", "Y"), ("X", "Z"), ("Y", "Z")],
    )
    general_parameter_tests(table, "meandiffs")
    # test parameter types
    bool_params = [
        "show_n",
        "show_standard_errors",
        "show_stars",
        "show_significance_levels",
    ]
    for param in bool_params:
        table.table_params[param] = True
        table.table_params[param] = False
        with pytest.raises(AssertionError):
            table.table_params[param] = "True"
            table.table_params[param] = 1
            table.table_params[param] = 0.5

    table.table_params["p_values"] = [0.15, 0.05, 0.01]
    with pytest.raises(AssertionError):
        table.table_params["p_values"] = 0.05
        table.table_params["p_values"] = [0.15, 0.05, "0.01"]
        table.table_params["p_values"] = ["ten", "five", "one"]
        table.table_params["p_values"] = [10, 5, 1]

    with pytest.raises(AttributeError):
        table.table_params["include_index"] = True
        table.table_params["include_index"] = False


def test_model_table_params(data):
    mod1 = smf.ols("A ~ B + C -1", data=data).fit()
    mod2 = smf.ols("A ~ B + C", data=data).fit()
    mod_table = st.tables.ModelTable(models=[mod1, mod2])
    general_parameter_tests(mod_table, "model")

    with pytest.raises(AttributeError):
        mod_table.table_params["include_index"] = True
        mod_table.table_params["include_index"] = False

    bool_params = [
        "show_r2",
        "show_adjusted_r2",
        "show_pseudo_r2",
        "show_dof",
        "show_ses",
        "show_cis",
        "show_fstat",
        "single_row",
        "show_observations",
        "show_ngroups",
        "show_model_numbers",
        "show_stars",
        "show_model_type",
        "show_significance_levels",
    ]
    for param in bool_params:
        mod_table.table_params[param] = True
        mod_table.table_params[param] = False
        with pytest.raises(AssertionError):
            mod_table.table_params[param] = "True"
            mod_table.table_params[param] = 1
            mod_table.table_params[param] = 0.5
