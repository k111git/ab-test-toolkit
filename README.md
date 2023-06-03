ab-test-toolkit
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Install

``` sh
pip install ab_test_toolkit
```

## imports

``` python
from ab_test_toolkit.generator import (
    generate_binary_data,
    generate_continuous_data,
    data_to_contingency,
)
from ab_test_toolkit.power import (
    simulate_power_binary,
    sample_size_binary,
    simulate_power_continuous,
    sample_size_continuous,
)
from ab_test_toolkit.plotting import (
    plot_power,
    plot_distribution,
    plot_betas,
)
```

## Binary target (e.g. conversion rate experiments)

### Sample size:

We can calculate the sample size required with the function
“sample_size_chi2”. Input needed is:

- Conversion rate control: cr0

- Conversion rate variant for minimal detectable effect: cr1 (for
  example, if we have a conversion rate of 1% and want to detect an
  effect of at least 20% relate, we would set cr0=0.010 and cr1=0.012)

- Significance threshold: alpha. Usually set to 0.05, this defines our
  tolerance for falsely detecting an effect if in reality there is none
  (alpha=0.05 means that in 5% of the cases we will detect an effect
  even though the samples for control and variant are drawn from the
  exact same distribution).

- Statistical power. Usually set to 0.8. This means that if the effect
  is the minimal effect specified above, we have an 80% probability of
  identifying it at statistically significant (and hence 20% of not
  idenfitying it).

- one_sided: If the test is one-sided (one_sided=True) or if it is
  two-sided (one_sided=False). As a rule of thumb, if there are very
  strong reasons to believe that the variant cannot be inferior to the
  control, we can use a one sided test. In case of doubts, using a two
  sided test is better.

let us calculate the sample size for the following example:

``` python
n_sample = sample_size_binary(
    cr0=0.01,
    cr1=0.012,
    alpha=0.05,
    power=0.8,
    one_sided=True,
)
print(f"Required sample size per variant is {int(n_sample)}.")
```

    Required sample size per variant is 33560.

``` python
n_sample_two_sided = sample_size_binary(
    cr0=0.01,
    cr1=0.012,
    alpha=0.05,
    power=0.8,
    one_sided=False,
)
print(
    f"For the two-sided experiment, required sample size per variant is {int(n_sample_two_sided)}."
)
```

    For the two-sided experiment, required sample size per variant is 42606.

### Power simulations

What happens if we use a smaller sample size? And how can we understand
the sample size?

Let us analyze the statistical power with synthethic data. We can do
this with the simulate_power_binary function. We are using some default
argument here, see [this
page](https://k111git.github.io/ab-test-simulator/power.html) for more
information.

``` python
# simulation = simulate_power_binary()
```

Note: The simulation object return the total sample size, so we need to
split it per variant.

``` python
# simulation
```

Finally, we can plot the results (note: the plot function show the
sample size per variant):

``` python
# plot_power(
#     simulation,
#     added_lines=[{"sample_size": sample_size_binary(), "label": "Chi2"}],
# )
```

### The problem of peaking

wip

## Contunious target (e.g. average)

Here we assume normally distributed data (which usually holds due to the
central limit theorem).

### Sample size

We can calculate the sample size required with the function
“continuous_sample_size”. Input needed is:

- mu1: Mean of the control group

- mu2: Mean of the variant group assuming minimal detectable effect
  (e.g. if the mean it 5, and we want to detect an effect as small as
  0.05, mu1=5.00 and mu2=5.05)

- sigma: Standard deviation (we assume the same for variant and control,
  should be estimated from historical data)

- alpha, power, one_sided: as in the binary case

Let us calculate an example:

``` python
n_sample = sample_size_continuous(
    mu1=5.0, mu2=5.05, sigma=1, alpha=0.05, power=0.8, one_sided=True
)
print(f"Required sample size per variant is {int(n_sample)}.")
```

    Required sample size per variant is 4946.

Let us also do some simulations. These show results for the t-test as
well as bayesian testing (only 1-sided).

``` python
# simulation = simulate_power_continuous()
```

``` python
# plot_power(
#     simulation,
#     added_lines=[
#         {"sample_size": continuous_sample_size(), "label": "Formula"}
#     ],
# )
```

## Data Generators

We can also use the data generators for example data to analyze or
visualuze as if they were experiments.

Distribution without effect:

``` python
df_continuous = generate_continuous_data(effect=0)
# plot_distribution(df_continuous)
```

Distribution with effect:

``` python
df_continuous = generate_continuous_data(effect=1)
# plot_distribution(df_continuous)
```

## Visualizations

Plot beta distributions for a contingency table:

``` python
df = generate_binary_data()
df_contingency = data_to_contingency(df)
# fig = plot_betas(df_contingency, xmin=0, xmax=0.04)
```
