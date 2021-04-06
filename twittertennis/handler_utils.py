import networkx as nx
from collections import Counter

### EDGES ###

def group_edges(df, key_col="date"):
    edges_grouped = {}
    grouped = df.groupby(key_col)
    for key, group in grouped:
        edges_grouped[key] = group
    return edges_grouped

def get_weighted_edges(df, group_cols):
    weighted_edges = df.groupby(by=group_cols)["epoch"].count().reset_index()
    weighted_edges.rename({"epoch":"weight"}, axis=1, inplace=True)
    return weighted_edges

def prepare_edges(mentions, snapshot_col="date"):
    group_cols = ["src","trg",snapshot_col]
    weighted_edges = get_weighted_edges(mentions, group_cols)
    weighted_edges_grouped = group_edges(weighted_edges, snapshot_col)
    edges_grouped = group_edges(mentions[group_cols], snapshot_col)
    return weighted_edges, weighted_edges_grouped, edges_grouped

### NODE REINDEXING ###

def get_account_recoder(mentions, k=None, src_col="src_screen_str", trg_col="trg_screen_str"):
    mention_activity = list(mentions[src_col]) + list(mentions[trg_col])
    cnt = Counter(mention_activity)
    if k == None:
        accounts, counts = zip(*cnt.most_common())
    else:
        accounts, counts = zip(*cnt.most_common(k))
    node_mapping = dict(zip(accounts,range(len(accounts))))
    return node_mapping

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