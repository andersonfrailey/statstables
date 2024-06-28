# Statstables

**This package is in the pre-alpha stage. There are many bugs, not all the features have been implemented yet, and there will likely be significant refactoring which may break backwards compatibility. Please use it anyway.**

A Python package for making nice LaTeX, HTML, and ASCII text tables.

This package is inspired by the [stargazer Python package](https://github.com/StatsReporting/stargazer/tree/master) (and by extension the [stargazer R package](https://cran.r-project.org/web/packages/stargazer/vignettes/stargazer.pdf) that inspired that). `statstables` can be used to render output from a number of natively supported models (those in the `statsmodels` and `linearmodels` packages), while giving users the ability to easily implement custom renderers for models not currently supported. It can also be used to create just about any other table you may need in a research project.

The goal of `statstables` is to allow you to think as much or as little as you'd like about about the tables you're creating. If you want to use all the defaults and get a presentable table, you can. If you want control over all the details, down to how individual cells are formatted, you can do that too. All of this is done without changing the underlying object containing the data, whether that's a Pandas DataFrame or fitted model.

Examples of how to use `statstables` can be found in the [sample notebook](https://github.com/andersonfrailey/statstables/blob/main/samplenotebook.ipynb). See [`main.tex`](https://github.com/andersonfrailey/statstables/blob/main/main.tex) and [`main.pdf`](https://github.com/andersonfrailey/statstables/blob/main/main.pdf) to see what the tables look like rendered in LaTeX. you will need to include `\usepackage{booktabs}` in the preamble to your TeX file for it to compile.

## Installation

To install the latest release, use

```bash
pip install statstables
```
Or you can clone this repo to use the latest changes.
