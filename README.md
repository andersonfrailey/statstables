# Statstables

**This package is in the pre-alpha stage. There are many bugs, not all the features have been implemented yet, and there will likely be significant refactoring which may break backwards compatibility. Please use it anyway.**

A Python package for making nice LaTeX and HTML tables.

This package is inspired by the [stargazer Python package](https://github.com/StatsReporting/stargazer/tree/master) (and by extension the [stargazer R package](https://cran.r-project.org/web/packages/stargazer/vignettes/stargazer.pdf) that inspired that). While stargazer is great for formatting regression output, `statstables` is intended to make it easier to format all other tables.

Pandas does have a number of functions/methods that allow you to export tables to LaTeX and HTML, but I found them to be unintuitive and limiting. The goal of `statstables` is to allow you to think as much or as little as you'd like about about the tables you're creating. If you want to use all the defaults and get a presentable table, you can. If you want control over all the details, down to how individual cells are formatted, you can do that too. Plus, unlike with the Pandas defaults, all of this is done without changing the underlying DataFrame.

Right now `statstables` only offers very basic tables. It'll eventually expand and I'll also write a tutorial on creating custom classes to work with other models.

Examples of how to use `statstables` can be found in the sample notebook. See `main.tex` and `main.pdf` to see what the tables look like rendered in LaTeX. you will need to include `\usepackage{booktabs}` in your TeX file for it to compile.
