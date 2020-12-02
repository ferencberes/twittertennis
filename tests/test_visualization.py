import os, sys
import pandas as pd

delim = os.path.sep
fp = os.path.realpath(__file__)
fdir = delim.join(fp.split(delim)[:-1])
data_dir = os.path.join(fdir, "..", "data")

from twittertennis.handler import TennisDataHandler

def test_players():
    handler = TennisDataHandler(data_dir, "rg17", include_qualifiers=True)
    fig = handler.visualize(kind="players")
    assert fig != None
    
def test_graph():
    handler = TennisDataHandler(data_dir, "rg17", include_qualifiers=True)
    fig = handler.visualize(kind="graph")
    assert fig != None