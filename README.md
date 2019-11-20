twittertennis
==============

Utility python package for RG17 and UO17 Twitter tennis tournament data sets.

# Introduction

This repository is a utility Python package for RG17 (Roland-Garros 2017) and UO17 (USOpen 2017) Twitter tennis tournament data sets.

I used these data sets for several research on dynamic networks observing the underlying Twitter mention graph. A huge advantage of our data is that **the nodes (Twitter accounts) of the network is temporally labeled** thus we could compare online graph algortihms in **supervised evaluation** tasks.

# How to deploy?

*If you use this Python package please cite one of our previous work from the references section.*

## Requirements

This package was developed in Python 3.5 conda environment.

## Install

```bash
pip install .
```

# Quick start

## Example

In this short example the RG17 (Roland-Garros 2017) data set is processed by the *TennisDataHandler* object. **The data is automatically downloaded to '../data/' folder during the first execution!** After (downloading and) processing the data the daily node relevance labels are exported into YOUR_OUTPUT_DIR folder. 

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

## Details

See more detailed examples and some description about the data in this [notebook](./examples/Examples.ipynb)

# References

We used RG17 and UO17 Twitter tennis data sets in some of our previous work. You can find the BibTex reference format of our papers below:

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
number="1",
pages="32",
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
number="1",
pages="64",
}
```
