# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_wrappers.ipynb.

# %% auto 0
__all__ = ['info', 'simulate_evolution_binary', 'realizations_of_evolution_binary', 'plot_realization',
           'plot_snapshots_distribution', 'analytics_null_vs_effect', 'plot_analytics', 'plot_analytics_compact',
           'plot_comparison_ate_pvalue', 'hello']

# %% ../nbs/04_wrappers.ipynb 6
import numpy as np
import pandas as pd
from ab_test_toolkit.generator import (
    data_to_contingency,
    generate_binary_data,
    generate_contingency,
)
from .analyze import p_value_binary
import plotly.io as pio

pio.templates.default = "simple_white"

import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.express as px

# %% ../nbs/04_wrappers.ipynb 7
def simulate_evolution_binary(
    N=10000,
    cr0=0.10,
    cr1=0.11,
    snapshot_sizes=np.arange(1000, 10001, 1000),
    one_sided=True,
):
    """
    Simulates the evolution of a binary experiment.
    """
    df = generate_binary_data(N=N, cr0=cr0, cr1=cr1)
    plot_sizes = snapshot_sizes
    result_dfs = []
    for current_size in plot_sizes:
        df1 = df[:current_size]
        df_c = data_to_contingency(df1)
        users0, users1 = df_c.users
        converted0, converted1 = df_c.converted
        rate0, rate1 = df_c.cvr
        ate = rate1 - rate0
        pv = p_value_binary(df_c, one_sided=one_sided)
        out_df = pd.DataFrame(
            {
                "size": [current_size],
                "users0": users0,
                "users1": users1,
                "converted0": converted0,
                "converted1": converted1,
                "cr0": rate0,
                "cr1": rate1,
                "pv": [pv],
                "ate": [ate],
            }
        )
        result_dfs.append(out_df)
    result_df = pd.concat(result_dfs)
    return result_df

# %% ../nbs/04_wrappers.ipynb 9
def realizations_of_evolution_binary(
    N_realizations=50,
    cr0=0.10,
    cr1=0.11,
    snapshot_sizes=np.arange(1000, 10001, 1000),
    one_sided=True,
):
    N = np.max(snapshot_sizes)
    realizations_df = []
    for i in range(0, N_realizations):
        result_df = simulate_evolution_binary(
            N=N,
            cr0=cr0,
            cr1=cr1,
            snapshot_sizes=snapshot_sizes,
            one_sided=one_sided,
        )
        realizations_df.append(result_df)
        if (i % 10) == 0:
            print(f"{i} done")
    print("all done")

    snapshots_df = [
        pd.DataFrame(
            [
                {
                    "realization": i,
                    "ate": realizations_df[i].iloc[j].ate,
                    "pvalue": realizations_df[i].iloc[j].pv,
                }
                for i in range(0, N_realizations)
            ]
        ).sort_values(by="ate")
        for j in range(0, len(snapshot_sizes))
    ]
    return {
        "dataframes": realizations_df,
        "snapshots": snapshots_df,
        "snapshot_sizes": snapshot_sizes,
    }

# %% ../nbs/04_wrappers.ipynb 10
def plot_realization(
    plot_df, multiply_ate=1.0, alpha=0.05, ate_line=0.01, info=False
):
    colors = ["#1f77b4", "#ff7f0e"]
    colors_bottom=['#2ca02c','#d62728']
    if info == False:
        n_cols = 1
        specs = [[{"secondary_y": False}]]
        height = 400
    else:
        n_cols = 2
        specs = [[{"secondary_y": False}], [{"secondary_y": True}]]
        height = 700
    fig = make_subplots(
        rows=n_cols,
        cols=1,
        specs=specs,
    )

    if len(plot_df) >= 20:
        mode = "lines"
    else:
        mode = "lines+markers"

    for group in [0, 1]:
        fig.add_trace(
            go.Scatter(
                x=plot_df["size"],
                y=plot_df[f"converted{group}"],
                mode=mode,
                name=f"Group: {group}",
                line_color=colors[group],
                legendgroup="1",
            ),
            row=1,
            col=1,
        )

    if info == True:
        fig.add_trace(
            go.Scatter(
                x=plot_df["size"],
                y=plot_df[f"pv"],
                mode=mode,
                name=f"pvalue",
                line_color=colors_bottom[0],
                legendgroup="2",
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=plot_df["size"],
                y=[alpha] * len(plot_df["size"]),
                mode="lines",
                name=f"p={alpha}",
                line_color=colors_bottom[0],
                line_dash="dot",
                legendgroup="2",
            ),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=plot_df["size"],
                y=multiply_ate * plot_df[f"ate"],
                mode=mode,
                name=f"ate",
                line_color=colors_bottom[1],
                legendgroup="2",
            ),
            row=2,
            col=1,
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=plot_df["size"],
                y=[ate_line] * len(plot_df["size"]),
                mode="lines",
                name=f"ate={ate_line}",
                line_color=colors_bottom[1],
                line_dash="dot",
                legendgroup="2",
            ),
            row=2,
            col=1,
            secondary_y=True,
        )
        fig.update_yaxes(
            title_text="ate",
            secondary_y=True,
            row=2,
            col=1,
        )

        fig.update_yaxes(
            title_text="pvalue", secondary_y=False, row=2, col=1, range=[0, 1]
        )

    fig.update_yaxes(
        title_text="Conversions",
        secondary_y=False,
        row=1,
        col=1,
    )

    fig.update_layout(
        height=height,
        width=1000,
        title_text="",
        legend_tracegroupgap=250,
    )
    return fig

# %% ../nbs/04_wrappers.ipynb 11
def plot_snapshots_distribution(
    snapshots, vline_x=None, snapshot_indices=None
):
    if snapshot_indices == None:
        snapshot_indices = [0, int(len(snapshots) / 2.0), len(snapshots) - 1]
    fig = ff.create_distplot(
        [snapshots[j]["ate"] for j in snapshot_indices],
        snapshot_indices,
        show_hist=False,
        show_rug=True,
    )
    if vline_x != None:
        fig.add_vline(
            x=vline_x, line_width=1, line_dash="dash", line_color="gray"
        )

    fig.update_layout(
        template="simple_white",
        xaxis_title="ATE",
        yaxis_title="PDF",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.95),
        height=600,
    )
    #     fig.update_xaxes(range=[-0.04, 0.04])
    return fig

# %% ../nbs/04_wrappers.ipynb 13
def analytics_null_vs_effect(r0, r1, alpha=0.1, ate_limit=0.005):
    """
    Shows the power and false positives of using a p value vs directly the ATE
    r0,r1: Realization objects from realizations_of_evolution_binary
    r0: No effect
    r1: With effect
    """
    ate = dict()
    pv = dict()
    for effect, snapshot in zip(
        ["null", "effect"], [r0["snapshots"], r1["snapshots"]]
    ):
        ate[effect] = dict()
        ate[effect]["positives"] = [
            (df["ate"] > ate_limit).mean() for df in snapshot
        ]
        ate[effect]["negatives"] = [
            (df["ate"] <= ate_limit).mean() for df in snapshot
        ]
        pv[effect] = dict()
        pv[effect]["positives"] = [
            (df["pvalue"] < alpha).mean() for df in snapshot
        ]
        pv[effect]["negatives"] = [
            (df["pvalue"] >= alpha).mean() for df in snapshot
        ]

    fp = pv["null"]["positives"][-1]
    fn = pv["effect"]["negatives"][-1]
    tp = pv["effect"]["positives"][-1]
    tn = pv["null"]["negatives"][-1]

    confusion_p = pd.DataFrame({0: [tn, fp], 1: [fn, tp]}) / 2.0

    fp = ate["null"]["positives"][-1]
    fn = ate["effect"]["negatives"][-1]
    tp = ate["effect"]["positives"][-1]
    tn = ate["null"]["negatives"][-1]

    confusion_ate = pd.DataFrame({0: [tn, fp], 1: [fn, tp]}) / 2.0

    return {
        "ate": ate,
        "pv": pv,
        "confusion_p": confusion_p,
        "confusion_ate": confusion_ate,
        "alpha": alpha,
        "snapshot_sizes": r0["snapshot_sizes"],
    }

# %% ../nbs/04_wrappers.ipynb 14
def plot_analytics(analytics):
    """
    plots elements of confusion matrix over time
    """
    alpha = analytics["alpha"]

    my_sizes = analytics["snapshot_sizes"]

    if len(my_sizes) >= 100:
        label_every = 10
    elif len(my_sizes) >= 30:
        label_every = 4
    elif len(my_sizes) >= 20:
        label_every = 2
    else:
        label_every = 1

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("No true effect", "With true effect"),
        vertical_spacing=0.1,
    )
    colors = ["#1f77b4", "#ff7f0e"]
    for idx, appraoch in enumerate(["ate", "pv"]):
        tn = analytics[appraoch]["null"]["negatives"]
        fp = analytics[appraoch]["null"]["positives"]
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(tn))),
                y=tn,
                mode="lines",
                name=f"{appraoch} TN",
                line_color=colors[idx],
                legendgroup="1",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(fp))),
                y=fp,
                mode="lines",
                name=f"{appraoch} FP",
                line_color=colors[idx],
                legendgroup="1",
                line=dict(dash="dash"),
            ),
            row=1,
            col=1,
        )

    for idx, appraoch in enumerate(["ate", "pv"]):
        tn = analytics[appraoch]["effect"]["negatives"]
        fp = analytics[appraoch]["effect"]["positives"]
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(tn))),
                y=tn,
                mode="lines",
                name=f"{appraoch} FN",
                line_color=colors[idx],
                legendgroup="2",
                line=dict(dash="dash"),
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(fp))),
                y=fp,
                mode="lines",
                name=f"{appraoch} TP",
                line_color=colors[idx],
                legendgroup="2",
            ),
            row=2,
            col=1,
        )

    fig.update_yaxes(
        title_text="",
        row=2,
        col=1,
    )
    fig.update_yaxes(
        title_text="",
        row=1,
        col=1,
    )
    fig.update_xaxes(
        title_text="Time",
        row=2,
        col=1,
    )

    fig.update_layout(
        height=800,
        width=1000,
        title_text=f"Power and False Positives, alpha={alpha}",
        legend_tracegroupgap=350,
    )

    fig = fig.update_xaxes(
        title_text="Size per variant",
        tickvals=np.array(range(0, len(my_sizes)))[::label_every],
        ticktext=my_sizes[::label_every]
        / 2.0,  # divide by 2 due to sample size per variant.
        row=2,
        col=1,
    )
    return fig

# %% ../nbs/04_wrappers.ipynb 15
def plot_analytics_compact(analytics, approach):
    """
    plots elements of confusion matrix over time.
    input: analytics element from analytics_null_vs_effect
    approach: "both", "ate", or "pv".
    """
    alpha = analytics["alpha"]

    my_sizes = analytics["snapshot_sizes"]

    if len(my_sizes) >= 100:
        label_every = 10
    elif len(my_sizes) >= 30:
        label_every = 4
    elif len(my_sizes) >= 20:
        label_every = 2
    else:
        label_every = 1

    fig = make_subplots()
    colors = ["#1f77b4", "#ff7f0e"]

    if approach != "both":
        tp = analytics[approach]["effect"]["positives"]
        fp = analytics[approach]["null"]["positives"]
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(fp))),
                y=fp,
                mode="lines",
                name=f"False positives (alpha)",
                line_color=colors[0],
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=np.array(range(0, len(tp))),
                y=tp,
                mode="lines",
                name=f"True positives (power)",
                line_color=colors[1],
            ),
        )

    else:
        dasher = ["solid", "dash"]
        for idx, this_approach in enumerate(["ate", "pv"]):
            tp = analytics[this_approach]["effect"]["positives"]
            fp = analytics[this_approach]["null"]["positives"]
            fig.add_trace(
                go.Scatter(
                    x=np.array(range(0, len(fp))),
                    y=fp,
                    mode="lines",
                    name=f"False positives {this_approach}",
                    line=dict(dash=dasher[idx]),
                    line_color=colors[0],
                ),
            )
            fig.add_trace(
                go.Scatter(
                    x=np.array(range(0, len(tp))),
                    y=tp,
                    mode="lines",
                    name=f"True positives {this_approach}",
                    line=dict(dash=dasher[idx]),
                    line_color=colors[1],
                ),
            )

    fig.update_yaxes(title_text="", range=[0, 1])
    fig.update_xaxes(
        title_text="Time",
    )

    fig.update_layout(
        height=600,
        width=1000,
        title_text=f"Power and False Positives: {approach}",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    fig = fig.update_xaxes(
        title_text="Size per variant",
        tickvals=np.array(range(0, len(my_sizes)))[::label_every],
        ticktext=my_sizes[::label_every]
        / 2.0,  # divide by 2 due to sample size per variant.
    )
    return fig

# %% ../nbs/04_wrappers.ipynb 16
def plot_comparison_ate_pvalue(
    cr0=0.10, crmax=0.12, sizes=[1000, 2000, 5000, 10000], one_sided=True
):
    """
    Compares the average treatment effect (difference in conversion rates) with the P value for different sample sizes.
    Inputs:
    sizes: List of total sample sizes considered
    cr0: baseline conversion rate
    crmax: max conversion rate (we will plot ATEs until crmax - cr0)
    Output: Plot
    """
    dfs = []
    for size in sizes:
        pvs = []
        ates = []
        for cr1 in np.linspace(cr0, crmax, 100):
            df = generate_contingency(N=size, cr0=cr0, cr1=cr1, exact=True)
            this_ate = df.loc[1].cvr - df.loc[0].cvr
            this_pv = p_value_binary(df, one_sided=one_sided)
            pvs.append(this_pv)
            ates.append(this_ate)
        out = pd.DataFrame({"ate": ates, "pvs": pvs})
        out["size"] = size
        dfs.append(out)
    out_all = pd.concat(dfs)
    fig = px.line(out_all, x="ate", y="pvs", color="size")
    fig.update_layout(
        height=600,
        width=800,
        legend=dict(yanchor="top", y=1, xanchor="right", x=0.99),
    )
    # fig.update_xaxes(showspikes=True, spikemode="across", spikethickness=1)
    # fig.update_yaxes(showspikes=True, spikemode="across", spikethickness=1)
    # fig.update_layout(hoverdistance=100)
    return fig

# %% ../nbs/04_wrappers.ipynb 20
info = dict()
info[
    "ate"
] = """Average treatment effect (ate) describes the difference between the variant and the control.
For the example for a conversion rate experiment, this is the difference between the two conversion rates of the variant and control group."""
info[
    "power"
] = """Statistical power. Usually set to 0.8. This means that if the effect is the minimal effect specified above, we have an 80% probability of correctly identifying it at statistically significant (and hence 20% of not idenfitying it)."""
info[
    "cr1"
] = """Conversion rate variant for minimal detectable effect: cr1 (for example, if we have a conversion rate of 1% and want to detect an effect of at least 20% relate, we would set cr0=0.010 and cr1=0.012)"""
info["cr0"] = """Conversion rate control: cr0"""
info[
    "relative_uplift"
] = f"""Percentage of minimal detectable improvement over the base conversion rate cr0. E.g. if cr0 is 5.0%, a 10% improvement means we would observe a conversion rate of 5.5%."""
info[
    "sided"
] = """As a rule of thumb, if there are very strong reasons to believe that the variant cannot be inferior to the control, we can use a one sided test. In case of doubts, using a two sided test is better.
"""
info[
    "alpha"
] = """Significance threshold: alpha. Usually set to 0.05, this defines our tolerance for falsely detecting an effect if in reality there is none (alpha=0.05 means that in 5% of the cases we will detect an effect even though the samples for control and variant are drawn from the exact same distribution).

"""
info[
    "sigma"
] = """Standard deviation (we assume the same for variant and control, should be estimated from historical data).

"""
info[
    "mu0"
] = """Mean of the control group.

"""
info[
    "mu1"
] = """Mean of the variant group assuming minimal detectable effect (e.g. if the mean it 5, and we want to detect an effect as small as 0.05, mu1=5.00 and mu2=5.05)"""

# %% ../nbs/04_wrappers.ipynb 21
def hello():
    print(
        f"""
    Welcome :) \n
    You can find additional documentation here: https://k111git.github.io/ab-test-toolkit/
    """
    )
    pass
