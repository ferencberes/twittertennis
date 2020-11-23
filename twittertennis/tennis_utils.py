import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

### Utils ###

def scores2file(score_map, output_file, sep=" "):
    """Export scores to .csv files"""
    score_df = pd.DataFrame(score_map, columns=["node_id","score"])
    score_df.to_csv(output_file,sep=sep, header=False, index=False)

def epoch2date(epoch, tz_info=None):
    """Convert epoch to date based on timezone information. If 'tz_info==None' then local timezone information is used."""
    if tz_info == None:
        dt = datetime.datetime.fromtimestamp(epoch)
    else:
        dt = datetime.datetime.fromtimestamp(epoch, tz=tz_info)
    return "%i-%.2i-%.2i" % (dt.year, dt.month, dt.day)

### Tennis player information ###

def update_match_counts(df, true_matches):
    found_players=set(true_matches.keys())
    df["found_players"] = df["players"].apply(lambda p_list: [p for p in p_list if p in true_matches])
    df['missing_players'] = df['players'].apply(lambda x: list(set(x)-found_players))
    df["num_players"] = df.apply(lambda x: len(x["players"]), axis=1)
    df["num_found_players"] = df.apply(lambda x: len(x["found_players"]), axis=1)
    df["num_missing_players"] = df.apply(lambda x: len(x["missing_players"]), axis=1)
    df["frac_missing_players"] = df["num_missing_players"] / df["num_players"]

def extract_daily_players(schedule_df, player_accounts, category_filter_func=None):
    """Return daily tennis players in dictionary and dataframe based on the schedule and the found player-account assigments."""
    true_matches = player_accounts
    # creating dataframe
    if category_filter_func == None:
        schedule_df_tmp = schedule_df
    else:
            schedule_df_tmp = schedule_df[schedule_df["matchHeader"].apply(category_filter_func)]
    daily_players = {}
    for index, row in schedule_df_tmp.iterrows():
        date, winner, loser = row["date"], row["playerName active"], row["playerName opponent"]
        header, court, match = row["matchHeader"], row["courtName"], row["orderNumber"]
        match_id = "%s_%s_%i" % (header, court, match)
        if not date in daily_players:
            daily_players[date] = {}
        daily_players[date][winner] = match_id
        daily_players[date][loser] = match_id
    # daily players grouped
    daily_players_grouped = [(key, set(daily_players[key].keys())) for key in daily_players]
    daily_players_df = pd.DataFrame(daily_players_grouped, columns=["date", "players"])
    update_match_counts(daily_players_df, true_matches)
    daily_players_df = daily_players_df.sort_values("date").reset_index(drop=True)
    return daily_players, daily_players_df

### Labeling nodes ###

def set_label_value(label_value_dict, user, date_idx, collected_dates, screen_name_to_player, daily_found_player_dict):
    label = 0.0
    if user in screen_name_to_player:
        if screen_name_to_player[user] in daily_found_player_dict[collected_dates[date_idx]]:
            label = label_value_dict["current"]
        elif date_idx > 0 and screen_name_to_player[user] in daily_found_player_dict[collected_dates[date_idx-1]]:
            label = label_value_dict["previous"]
        elif date_idx < len(collected_dates)-1:
            next_date = collected_dates[date_idx+1]
            if next_date in daily_found_player_dict and screen_name_to_player[user] in daily_found_player_dict[next_date]:
                label = label_value_dict["next"]
    return label

def get_daily_label_dicts(label_value_dict, collected_dates, mentions_df, mapper_dicts):
    """Label users in mention data based on schedule."""
    screen_name_to_player, user_dict, daily_found_player_dict = mapper_dicts
    print(len(screen_name_to_player), len(user_dict), len(daily_found_player_dict), len(mentions_df))
    daily_label_dicts = {}
    print("Labeling users STARTED")
    for date_idx, date in enumerate(collected_dates):
        label_dict = {}
        for user in user_dict:
            user_id = user_dict[user]
            label_dict[user_id] = set_label_value(label_value_dict, user, date_idx, collected_dates, screen_name_to_player, daily_found_player_dict)
        daily_label_dicts[date] = label_dict
    print("Labeling users FINISHED")
    return daily_label_dicts

### Visualization ###

def visu_players(handler, figsize=(15,10)):
    df = handler.daily_p_df
    df = df[df["date"].isin(handler.dates)]
    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=figsize)
    sns.set_color_codes("muted")
    sns.barplot(x="num_players", y="date", data=df,
            label="Total number of players", color="b")
    sns.set_color_codes("muted")
    sns.barplot(x="num_found_players", y="date", data=df,
            label="Number of players with\n assigned Twitter account", color="#21456e")
    ax.legend( loc="lower right", frameon=True)
    ax.set(xlabel="Number of tennis players",ylabel="")
    plt.xlim((0,220))
    sns.despine(left=True, bottom=True)
    plt.legend(loc='upper right')
    plt.show()
    
def visu_graph(handler, figsize=(12,8)):
    num_of_mentions = handler.mentions["date"].value_counts()
    num_of_nodes = {}
    for d in handler.dates:
        num_of_nodes[d] = get_num_nodes(handler.mentions, d)
    visu_mention_count(handler.dates, num_of_mentions, num_of_nodes, figsize)

def visu_mention_count(tournament_dates, num_of_mentions, num_of_nodes, figsize=(12,8)):
    x = range(len(tournament_dates))
    x_ticks = [d[5:] for d in tournament_dates]
    y_ticks = [10000*i for i in range(1,5)]
    edges = [num_of_mentions[d] for d in tournament_dates]
    nodes = [num_of_nodes[d] for d in tournament_dates]
    plt.figure(figsize=figsize)
    plt.gcf().subplots_adjust(bottom=0.2)
    plt.plot(x,edges, "-", linewidth=5.0,label="Number of edges (mentions)", c="#21456e")
    plt.plot(x,nodes, "--",linewidth=5.0,label="Number of nodes (accounts)", c="#e84d3d")
    plt.xticks(x, x_ticks, rotation=90)
    plt.yticks(y_ticks,y_ticks)
    plt.legend()
    
def get_num_nodes(df,date):
    partial_df = df[df["date"] == date]
    return len(set(partial_df["src"]).union(set(partial_df["trg"])))
