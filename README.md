# Statstables

**This package is in the pre-alpha stage. There are many bugs, not all the features have been implemented yet, and there will likely be significant refactoring which may break backwards compatibility. Please use it anyway.**

A Python package for making nice LaTeX and HTML tables.

This package is inspired by the [stargazer Python package](https://github.com/StatsReporting/stargazer/tree/master) (and by extension the [stargazer R package](https://cran.r-project.org/web/packages/stargazer/vignettes/stargazer.pdf) that inspired that). While `stargazer` is great for formatting output from the models it supports, `statstables` is intended to make it easier to format all the other tables you may need.

Pandas does have a number of functions/methods that allow you to export DataFrames to LaTeX and HTML, but I found them to be unintuitive and limiting. The goal of `statstables` is to allow you to think as much or as little as you'd like about about the tables you're creating. If you want to use all the defaults and get a presentable table, you can. If you want control over all the details, down to how individual cells are formatted, you can do that too. Plus, unlike with the Pandas defaults, all of this is done without changing the underlying DataFrame.

Right now `statstables` only offers very basic tables and the data given to it must be in a Pandas DataFrame. It'll eventually expand to work with more data types and include more complex tables. I'll also write a tutorial on creating custom classes to work with other models.

Examples of how to use `statstables` can be found in the [sample notebook](https://github.com/andersonfrailey/statstables/blob/main/samplenotebook.ipynb). See [`main.tex`](https://github.com/andersonfrailey/statstables/blob/main/main.tex) and [`main.pdf`](https://github.com/andersonfrailey/statstables/blob/main/main.pdf) to see what the tables look like rendered in LaTeX. you will need to include `\usepackage{booktabs}` in the preamble to your TeX file for it to compile.

## Installation

To install the latest release, use

```bash
pip install statstables
```
Or you can clone this repo to use the latest changes.