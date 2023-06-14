# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_data_generation.ipynb.

# %% auto 0
__all__ = ['generate_binary_data', 'generate_continuous_data', 'data_to_contingency', 'generate_contingency',
           'contingency_from_counts']

# %% ../nbs/00_data_generation.ipynb 4
import numpy as np
from scipy.stats import binom
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

from scipy.stats import binom

# %% ../nbs/00_data_generation.ipynb 6
def generate_binary_data(N=1000, cr0=0.010, cr1=0.011, split=0.5):
    """
    Generates synthethic data for a binary experiement with two groups (0: Control, 1: Variant).
    Inputs:
    N: Sample size (total number of users)
    Split: % of users assigned randomly to the variant (group 1)
    cr0: Conversion rate control
    cr1: Conversion rate variant
    """
    N_variant = binom.rvs(N, split, size=1)[0]
    N_control = N - N_variant
    control = np.random.choice([0, 1], N_control, p=[1 - cr0, cr0])
    variant = np.random.choice([0, 1], N_variant, p=[1 - cr1, cr1])
    return pd.concat(
        [
            pd.DataFrame({"group": 0, "target": control}),
            pd.DataFrame({"group": 1, "target": variant}),
        ]
    ).sample(frac=1.0)

# %% ../nbs/00_data_generation.ipynb 8
def generate_continuous_data(
    N=1000, base=5, effect=0, noise=1, std=1, split=0.5
):
    """
    Generates synthethic data for a continuous experiement with two groups (0: Control, 1: Variant).
    Inputs:
    N: Sample size (total number of users)
    """
    i = range(1, N + 1)
    d = np.random.binomial(1, split, N)
    #     y0 = base + effect * d + noise * np.random.normal(0, std, N)
    y0 = np.random.normal(base + effect * d, std, N)
    df = pd.DataFrame({"individual": i, "group": d, "target": y0})
    return df

# %% ../nbs/00_data_generation.ipynb 10
def data_to_contingency(df):
    """
    Converts output from generate_binary_data to a contingency table
    """
    df_result = df.groupby("group").agg(
        users=("target", "size"), converted=("target", "sum")
    )
    df_result["not_converted"] = df_result["users"] - df_result["converted"]
    df_result["cvr"] = df_result["converted"] / df_result["users"]
    return df_result

# %% ../nbs/00_data_generation.ipynb 11
def generate_contingency(N=1000, split=0.50, cr0=0.010, cr1=0.011,exact=False):
    """
    Generate contingency table using binominal distribution
    For exact=False, we draw the numbers from the binominal distribution.
    For exact=True, we calculate the numbers from multiplying number users * conversion rate
    """
    assert N > 5, "N need to be more than 5"
    assert split >= 0.01, "Split needs to be >= 1%"
    assert split <= 0.99, "Split needs to be <= 99%"
    if exact==False:
        while True:
            n1 = binom.rvs(N, split, loc=0, size=1)[0]
            if n1 < N and n1 > 0:
                break
        n0 = N - n1
        c0 = binom.rvs(n0, cr0, loc=0, size=1)[0]
        c1 = binom.rvs(n1, cr1, loc=0, size=1)[0]
    elif exact==True:
        n0=int(np.round(N*split))
        n1=N-n0
        c0=int(np.round(n0*cr0))
        c1=int(np.round(n1*cr1))
    else:
        raise Exception("Invalid input for exact parameter in generate_contingency function.")
    df_result = pd.DataFrame(
        {"group": [0, 1], "users": [n0, n1], "converted": [c0, c1]}
    )
    df_result["not_converted"] = df_result["users"] - df_result["converted"]
    df_result["cvr"] = df_result["converted"] / df_result["users"]
    return df_result.set_index('group')

# %% ../nbs/00_data_generation.ipynb 12
def contingency_from_counts(n0, c0, n1, c1):
    """
    Generate contingency table from following input:
    n0: users in control group
    c0: number of converted users in control group
    n1: users in treatment group
    c1: number of converted user sin treatment group
    """
    assert (
        n0 >= c0
    ), "Number of converted users in control group cannot be larger than total users"
    assert (
        n1 >= c1
    ), "Number of converted users in treatment group cannot be larger than total users"
    df_result = pd.DataFrame(
        {"group": [0, 1], "users": [n0, n1], "converted": [c0, c1]}
    )
    df_result["not_converted"] = df_result["users"] - df_result["converted"]
    df_result["cvr"] = df_result["converted"] / df_result["users"]
    return df_result.set_index("group")
