import pandas as pd
import numpy as np
import json, pytz, os
from collections import Counter
from .tennis_utils import *

TIMEZONE = {
    "rg17": pytz.timezone('Europe/Paris'),
    "uo17": pytz.timezone('America/New_York')
}

QUALIFIER_START = {
    "rg17": 1495576800, # 2017-05-24 0:00 Paris (2017-05-22 and 2017-05-23 is missing from data)
    "uo17": 1503374400 # 2017-08-22 0:00 New York
}

TOURNAMENT_START = {
    "rg17": 1495922400, # 2017-05-28 0:00 Paris
    "uo17": 1503892800 # 2017-08-28 0:00 New York
}

DATES_WITH_QUALIFIERS = {
    "rg17": ["2017-05-%.2i" % i for i in range(24,32)] + ["2017-06-%.2i" % i for i in range(1,12)],
    "uo17": ["2017-08-%.2i" % i for i in range(22,32)] + ["2017-09-%.2i" % i for i in range(1,11)]
}

DATES_WITHOUT_QUALIFIERS = {
    "rg17": ["2017-05-%.2i" % i for i in range(28,32)] + ["2017-06-%.2i" % i for i in range(1,12)],
    "uo17": ["2017-08-%.2i" % i for i in range(28,32)] + ["2017-09-%.2i" % i for i in range(1,11)]
}

DATES_WITH_NO_GAMES = {
    "rg17": ["2017-05-27"],
    "uo17": ["2017-08-26","2017-08-27"]
}

def group_edges(df, key_col="date"):
    edges_grouped = {}
    grouped = df.groupby(key_col)
    for key, group in grouped:
        edges_grouped[key] = group
    return edges_grouped

def reindex_labels(label_dict, id2account, account2index):
    tuples = []
    for key, label in label_dict.items():
        new_id = account2index[id2account[key]]
        tuples.append((new_id, label))
    new_dict = dict(tuples)
    ordered_dict = dict(sorted(new_dict.items()))
    return ordered_dict

class TennisDataHandler():
    
    def __init__(self, data_dir, data_id, include_qualifiers=True, verbose=False):
        self.verbose = verbose
        self.data_id = data_id
        self.data_dir = data_dir + "/" + data_id
        if not os.path.exists(self.data_dir):
            bashCommand = """mkdir -p %s; cd %s; wget https://dms.sztaki.hu/~fberes/tennis/%s.zip; unzip %s.zip""" % (data_dir, data_dir, data_id, data_id)
            print(bashCommand)
            print("Downloading data from 'https://dms.sztaki.hu/~fberes/tennis' STARTED...")
            os.system(bashCommand)
            print("Data was DOWNLOADED!")
        self.include_qualifiers = include_qualifiers
        self._load_files(self.data_id, self.data_dir)
        self._filter_data()
        self._extract_mappings()
        self._prepare_edges()
        self.daily_p_dict, self.daily_p_df = extract_daily_players(self.schedule, self.player_accounts)
        
    def _load_files(self, data_id, data_dir):
        mention_file_path = "%s/%s_mentions_with_names.csv" % (data_dir, data_id)
        tennis_match_file_path = "%s/%s_schedule.csv" % (data_dir, data_id)
        player_assigments_path = "%s/%s_player_accounts.json" % (data_dir, data_id)
        mentions = pd.read_csv(mention_file_path, sep="|")
        mentions = mentions[["epoch","src","trg","src_screen_str", "trg_screen_str"]]
        self.mentions = mentions
        if self.verbose:
            print("\n### Load Twitter mentions ###")
            print(self.mentions.head(3))
        sep = "|" if data_id == "rg17" else ";"
        self.schedule = pd.read_csv(tennis_match_file_path, sep=sep)
        if self.verbose:
            print("\n### Load event schedule ###")
            print(self.schedule.head(3))
        with open(player_assigments_path) as f:
            self.player_accounts = json.load(f)
            if self.verbose:
                print("\n### Load player accounts ###")
                print("Rafael Nadal accounts:", self.player_accounts["Rafael Nadal"])
        if self.verbose:
            print("Done")
        
    def _filter_data(self):
        if self.include_qualifiers:
            self.start_time = QUALIFIER_START[self.data_id]
            self.dates = DATES_WITH_QUALIFIERS[self.data_id]
        else:
            self.start_time = TOURNAMENT_START[self.data_id]
            self.dates = DATES_WITHOUT_QUALIFIERS[self.data_id]
        self.end_time = self.start_time + 86400 * len(self.dates)
        self.dates_with_no_games = DATES_WITH_NO_GAMES[self.data_id]
        if self.verbose:
            print("\n### Filter data ###")
            print("Start time:", self.start_time)
            print("End time:", self.end_time)
            print("Number of days:", len(self.dates))
            print("Dates:", self.dates)
            print("Dates with no games:", self.dates_with_no_games)
        mentions = self.mentions
        mentions = mentions[(mentions["epoch"] >= self.start_time) & (mentions["epoch"] <= self.end_time)]
        mentions = mentions.assign(date=mentions["epoch"].apply(lambda x: epoch2date(x, TIMEZONE[self.data_id])))
        self.number_of_edges = len(mentions)
        self.number_of_nodes = len(set(mentions["src"]).union(set(mentions["trg"])))
        self.mentions = mentions
        if self.verbose:
            print("Number of mentions (edges):", self.number_of_edges)
            print("Number of accounts (nodes):", self.number_of_nodes)
            #print("Min epoch:", mentions["epoch"].min(), "Max epoch:", mentions["epoch"].max())
        
    def _extract_mappings(self):
        # account to id
        mentions = self.mentions
        targets = list(zip(mentions["trg_screen_str"], mentions["trg"]))
        sources = list(zip(mentions["src_screen_str"], mentions["src"]))
        self.account_to_id = dict(sources+targets)
        #print(len(self.account_to_id))
        #self.id_to_account = dict(zip(self.account_to_id.values(), self.account_to_id.keys()))
        rev_targets = list(zip(mentions["trg"],mentions["trg_screen_str"]))
        rev_sources = list(zip(mentions["src"],mentions["src_screen_str"]))
        self.id_to_account = dict(rev_sources+rev_targets)
        nodes = list(self.account_to_id.values())
        # tennis account to player
        tennis_account_to_player = {}
        alternative_players = {}
        alternative_players["uo17"] = {
            "Carla Suarez Navarro":"Carla Suárez Navarro",
            "Coco Vandeweghe":"CoCo Vandeweghe",
            "Juan Martin Del Potro":"Juan Martin del Potro",
            "Diede De Groot":"Diede de Groot",
            "Mariana Duque-Marino":"Mariana Duque-Mariño",
            "Alex De Minaur":"Alex de Minaur",
            "Tracy Austin-Holt":"Tracy Austin"
        }
        # reverse alternative name mapping for rg17
        alternative_players["rg17"] = dict(zip(alternative_players["uo17"].values(),alternative_players["uo17"].keys()))
        for p, account_names in self.player_accounts.items():
            cleaned_p = alternative_players[self.data_id].get(p, p)
            for a_name in account_names:
                tennis_account_to_player[a_name] = cleaned_p
        self.tennis_account_to_player = tennis_account_to_player
        
    def _prepare_edges(self):
        group_cols = ["src","trg","date"]
        weighted_edges = self.mentions.groupby(by=group_cols)["epoch"].count().reset_index()
        weighted_edges.rename({"epoch":"weight"}, axis=1, inplace=True)
        self.weighted_edges = weighted_edges
        self.edges_grouped = group_edges(self.mentions[group_cols], key_col="date")
        self.weighted_edges_grouped = group_edges(self.weighted_edges, key_col="date")
    
    def summary(self):
        """Show the data summary"""
        return {
            "data_id":self.data_id,
            "include_qualifiers": self.include_qualifiers,
            "dates": self.dates,
            "dates_with_no_game": self.dates_with_no_games,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "number_of_edges": self.number_of_edges,
            "number_of_nodes": self.number_of_nodes
        }
    
    def visualize(self, kind="graph", figsize=(12,8)):
        """Visualize the data. Choose from 'graph' and 'players' options for the 'kind' argument."""
        fig = None
        if kind == "graph":
            fig = visu_graph(self, figsize)
        elif kind == "players":
            fig = visu_players(self, figsize)
        else:
            raise RuntimeError("Choose 'kind' parameter from 'players' or 'graph'!")
        return fig
    
    def get_daily_players(self, date_id):
        """Get daily tennis players"""
        if not date_id in self.dates:
            raise RuntimeError("Invalid date_id! Not present in collected dates:", self.dates)
        elif date_id in self.dates_with_no_games:
            raise RuntimeError("There was no game on this day!")
        else:
            return self.daily_p_dict[date_id]

    def show_daily_players(self):
        """Show daily information about tennis players"""
        return self.daily_p_df[self.daily_p_df["date"].isin(self.dates)]
    
    def get_daily_relevance_labels(self, binary=True):
        if binary:
            label_value_dict = {"current":1.0, "previous":0.0, "next":0.0}
        else:
            label_value_dict = {"current":2.0, "previous":1.0, "next":1.0}
        daily_found_player_dict = dict(zip(self.daily_p_df["date"], self.daily_p_df["found_players"]))
        for d in self.dates_with_no_games:
            daily_found_player_dict[d] = []
        mapper_dicts = (self.tennis_account_to_player, self.account_to_id, daily_found_player_dict)
        daily_label_dicts = get_daily_label_dicts(label_value_dict, self.dates, self.mentions, mapper_dicts, self.verbose)
        return daily_label_dicts
    
    def export_relevance_labels(self, output_dir, binary=True, only_pos_label=False):
        """Export label files for each date. Use 'only_pos_label=True' if you want to export only the relevant nodes per day."""
        daily_label_dicts = self.get_daily_relevance_labels(binary)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print("%s folder was created." % output_dir)
        with open("%s/summary.json" % output_dir, 'w') as f:
            json.dump(self.summary(), f, indent="   ", sort_keys=False)
        #pd.DataFrame(list(self.account_to_id.items())).sort_values(0).to_csv("%s/account_to_id.csv" % output_dir, index=False)
        #pd.DataFrame(list(self.tennis_account_to_player.items())).sort_values(0).to_csv("%s/tennis_account_to_player.csv" % output_dir, index=False)
        print("Exporting files STARTED")
        for i, date in enumerate(self.dates):
            sorted_user_labels = []
            for u in sorted(daily_label_dicts[date].keys()):
                label_value = daily_label_dicts[date][u]
                if only_pos_label:
                    # export only positive user labels
                    if label_value > 0.0:
                        sorted_user_labels.append((u, label_value))
                else:
                    sorted_user_labels.append((u, label_value))
            print(date, len(sorted_user_labels))
            scores2file(sorted_user_labels,"%s/labels_%i.csv" % (output_dir, i))
        print("Exporting files DONE")
        
    def export_edges(self, output_dir, sep="|"):
        """Export edges (mentions) into file. Only time and node identifiers will be expoerted!"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print("%s folder was created." % output_dir)
        with open("%s/summary.json" % output_dir, 'w') as f:
            json.dump(self.summary(), f, indent="   ", sort_keys=False)
        self.mentions[["epoch","src","trg"]].to_csv("%s/edges.csv" % output_dir, index=False, header=False, sep=sep)
        
    def _reindex_edges(self, df, account_to_index=None):
        if account_to_index != None:
            src = df["src"].apply(lambda x: account_to_index.get(self.id_to_account.get(x)))
            trg = df["trg"].apply(lambda x: account_to_index.get(self.id_to_account.get(x)))
        else:
            src = df["src"]
            trg = df["trg"]
        return src, trg
    
    def _get_snapshot_edges(self, snapshot_id, edge_type="temporal", account_to_index=None):
        snap_edges = []
        if edge_type == "temporal":
            df = self.mentions[self.mentions["date"]==snapshot_id][["src","trg","epoch"]].sort_values("epoch")
            src, trg = self._reindex_edges(df, account_to_index)
            weights = list(df["epoch"])
        else:
            df = self.weighted_edges_grouped[snapshot_id]
            src, trg = self._reindex_edges(df, account_to_index)
            if edge_type == "weighted":
                weights = list(df["weight"])
            else:
                weights = list(np.ones(len(df)))
        snap_edges = list(zip(src, trg))
        return snap_edges, weights
    
    def get_account_recoder(self):
        mention_activity = list(self.mentions["src_screen_str"]) + list(self.mentions["trg_screen_str"])
        cnt = Counter(mention_activity)
        accounts, counts = zip(*cnt.most_common())
        node_mapping = dict(zip(accounts,range(len(accounts))))
        return node_mapping

    def get_data(self, edge_type="temporal", binary_label=True, max_snapshot_idx=None):
        account_to_index = self.get_account_recoder()
        labels = self.get_daily_relevance_labels(binary=binary_label)
        data = {}
        idx = 0
        dates = self.dates
        if max_snapshot_idx != None:
            dates = dates[:max_snapshot_idx]
        for idx, date in enumerate(dates):
            y = reindex_labels(labels[date], self.id_to_account, account_to_index)
            node_keys = list(y.keys())
            X = dict(zip(node_keys, node_keys))
            edges, weights = self._get_snapshot_edges(date, edge_type, account_to_index)
            data[str(idx)] = {
                "index":idx,
                "date":date,
                "edges": edges,
                "weights": weights,
                "y": list([y[node] for node in range(len(account_to_index))]),
                "X": list([X[node] for node in range(len(account_to_index))]),
            }
            if self.include_qualifiers:
                data[str(idx)]["game_day"] = not date in self.dates_with_no_games            
            idx += 1
        data["time_periods"] = len(data)
        data["node_ids"] = account_to_index
        return data
    
    def to_json(self, path, edge_type="temporal", binary_label=True, max_snapshot_idx=None):
        data = self.get_data(edge_type, binary_label, max_snapshot_idx)
        with open(path, 'w') as f:
            json.dump(data, f)
        