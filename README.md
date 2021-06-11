twittertennis
==============

![build](https://github.com/ferencberes/twittertennis/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/ferencberes/twittertennis/branch/master/graph/badge.svg?token=O3SJ5GEHFV)](https://codecov.io/gh/ferencberes/twittertennis)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ferencberes/twittertennis/v_0.1.0?filepath=examples%2FFirstLook.ipynb)

Utility python package for RG17 and UO17 Twitter tennis tournament data sets.

# Introduction

This repository is a Python package that ease the interaction with our tennis tournament Twitter data sets RG17 (Roland-Garros 2017) and UO17 (USOpen 2017). In our research, we used the underlying Twitter mention graphs to analyse the performance of mulitple dynamic centrality measures and temporal node embedding methods. A huge advantage of our data is that **the nodes (Twitter accounts) of the network are temporally labeled** thus we could compare online graph algortihms in **supervised evaluation** tasks. The labels encode whether a given node in the Twitter mention network is related to a tennis player who participates in a tournament on the given day.

# How to deploy?

## Install

```bash
python setup.py install
```

## Tests

```
python setup.py test
```

# Examples

## Quick start

In this short example the RG17 (Roland-Garros 2017) data set is processed by the *TennisDataHandler* object. **The data is automatically downloaded to the '../data/' folder during the first execution!** After (downloading and) processing the data, daily node relevance labels are exported and prepared for further analysis. 

```python
import twittertennis.handler as tt

handler = tt.TennisDataHandler("../data/", "rg17", include_qualifiers=True)
print(handler.summary())
handler.export_relevance_labels(YOUR_OUTPUT_DIR, binary=True)
```
OR change the last line of the code if you only want to export relevant nodes for each day:
```python
handler.export_relevance_labels(YOUR_OUTPUT_DIR, binary=True, only_pos_label=True)
```

See more examples and information about the data in this [notebook](./examples/FirstLook.ipynb).

# References

```
@article{Beres2018,
author="B{\'e}res, Ferenc
and P{\'a}lovics, R{\'o}bert
and Ol{\'a}h, Anna
and Bencz{\'u}r, Andr{\'a}s A.",
title="Temporal walk based centrality metric for graph streams",
journal="Applied Network Science",
year="2018",
volume="3",
number="32",
pages="26",
issn="2364-8228",
}
```
```
@Article{Béres2019,
author="B{\'e}res, Ferenc
and Kelen, Domokos M.
and P{\'a}lovics, R{\'o}bert
and Bencz{\'u}r, Andr{\'a}s A.",
title="Node embeddings in dynamic graphs",
journal="Applied Network Science",
year="2019",
volume="4",
number="64",
pages="25",
}
```
