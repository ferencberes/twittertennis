import pandas as pd
import networkx as nx
from collections import Counter

### EDGES ###

def groupby_count(df, group_cols, count_col):
    parts = [df[col] for col in group_cols]
    tuples = list(zip(*parts))
    cnt = Counter(tuples)
    keys, counts = zip(*list(cnt.items()))
    res = pd.DataFrame(keys, columns=group_cols)
    res[count_col] = counts
    return res

def group_edges(df, key_col="date"):
    edges_grouped = {}
    keys = sorted(list(df[key_col].unique()))
    for key in keys:
        edges_grouped[key] = df[df[key_col]==key].copy()
    return edges_grouped

def get_weighted_edges(df, group_cols):
    weighted_edges = groupby_count(df, group_cols, "weight")
    return weighted_edges

def prepare_edges(mentions, snapshot_col="date"):
    group_cols = ["src","trg",snapshot_col]
    weighted_edges = get_weighted_edges(mentions, group_cols)
    weighted_edges_grouped = group_edges(weighted_edges, snapshot_col)
    edges_grouped = group_edges(mentions[group_cols], snapshot_col)
    return weighted_edges, weighted_edges_grouped, edges_grouped

### NODE REINDEXING ###

def reindex_labels(label_dict, id2account, account2index):
    tuples = []
    for key, label in label_dict.items():
        account = id2account[key]
        if account in account2index:
            new_id = account2index[account]
            tuples.append((new_id, label))
    new_dict = dict(tuples)
    ordered_dict = dict(sorted(new_dict.items()))
    return ordered_dict

def reindex_edges(df, id_to_account, account_to_index=None, src_col="src_screen_str", trg_col="trg_screen_str"):
    if account_to_index != None:
        accounts = list(account_to_index.keys())
        tmp = df.copy()
        # old solution would also be good with isnull()
        tmp[src_col] = tmp["src"].apply(lambda x: id_to_account.get(x))
        tmp[trg_col] = tmp["trg"].apply(lambda x: id_to_account.get(x))
        tmp = tmp[tmp[src_col].isin(accounts) & tmp[trg_col].isin(accounts)]
        src = tmp[src_col].apply(lambda x: account_to_index.get(x))
        trg = tmp[trg_col].apply(lambda x: account_to_index.get(x))
    else:
        src = df["src"]
        trg = df["trg"]
    return src, trg

### LABELS ###

def regression_labels(df, snapshot_col):
    label_records = groupby_count(df, [snapshot_col,"trg"], "count")
    snapshots = sorted(list(label_records[snapshot_col].unique()))
    labels = {}
    for snapshot_id in snapshots:
        rec_tmp = label_records[label_records[snapshot_col]==snapshot_id]
        dict_tmp = dict(zip(rec_tmp["trg"],rec_tmp["count"]))
        labels[snapshot_id] = dict_tmp
    return labels

### FEATURES ###

def calculate_node_features(G, total_nodes=None, degree=True, transitivity=True):
    """Calculate degree and node transitivty as node features. The graph nodes must have integer identifiers from 0 to N-1 where N is the number of nodes in G."""
    if total_nodes == None:
        total_nodes = G.number_of_nodes()
    scores = []
    if degree:
        degs = dict(nx.degree(G))
        scores.append([degs.get(i,0) for i in range(total_nodes)])
    if transitivity:
        trans = dict(nx.clustering(G))
        scores.append([trans.get(i,0) for i in range(total_nodes)])
    return list(zip(*scores))