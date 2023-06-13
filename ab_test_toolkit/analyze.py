# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_analyze.ipynb.

# %% auto 0
__all__ = ['p_value_binary', 'p_value_binary_from_counts']

# %% ../nbs/02_analyze.ipynb 5
from scipy.stats import fisher_exact
from .generator import contingency_from_counts
import numpy as np
import pandas as pd

# %% ../nbs/02_analyze.ipynb 6
def p_value_binary(df_contingency, one_sided=True):
    if one_sided == True:
        alternative = "greater"
    else:
        alternative = "two-sided"
    _, p_fischer = fisher_exact(
        np.array(df_contingency[["not_converted", "converted"]]),
        alternative=alternative,
    )
    return p_fischer

# %% ../nbs/02_analyze.ipynb 7
def p_value_binary_from_counts(n0, c0, n1, c1, one_sided=True):
    '''
    Return the p value for conversion rate experiment. Inputs:
    n0: Users control group
    c0: Converted users control group
    n1: Users treatment group
    c1: Converted users treatment group
    '''
    df_contingency = contingency_from_counts(n0, c0, n1, c1)
    return p_value_binary(df_contingency, one_sided=one_sided)
