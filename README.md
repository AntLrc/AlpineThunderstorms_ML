# AlpineThunderstorms_ML
This repository corresponds to my current work for my project at UNIL: **Post-Processing of Precipitation & Wind Gusts from Alpine Thunderstorms**.

## Initial scientific motivation

Motivated by recent developments in machine learning (ML)-based downscaling, this project combines extreme-value theory (EVT) and super-resolution algorithms to develop algorithms that can generate spatially-resolved extremes that have not been seen during training. 

Methodologically, the optimal way of combining EVT distributions, such as Generalized Extreme-Value (GEV) distribution for block maxima and Generalized Pareto Distribution (GPD) for threshold exceedances, with ML/statistical modeling tools for atmospheric applications remains an open question. Current approaches (see Boulaghiem et al., 2022, or Diaz et al., 2022) use EVT to describe marginal distributions and ML to represent the spatial dependence structure (copula). An unresolved issue is how much EVT can constrain ML algorithms without losing the necessary descriptive ability for atmospheric applications. This varies from loose constraints, including no strict parameterization, even of the marginals, to strict constraints involving EVT-based parameterization of spatial dependence structures, e.g., through max-stable or generalized Pareto processes. Another open question concerns the most suitable architectures for statistical constraints. Successful applications have used various algorithms, such as conditional generative adversarial networks (Stengel et al., 2020) and diffusion probabilistic models (Addison et al., 2022; Mardani et al., 2023).

More specifically, this project aims at using publically available data from wind stations along with precipitation data to predict alpine thunderstorm from short-term to medium-term forecasts. THe idea would be to post-process well-known AI weather forecast models (e.g. PanguWeather) to identify thunderstorm formation / evolution.

