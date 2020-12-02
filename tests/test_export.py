import os, sys
import pandas as pd

delim = os.path.sep
fp = os.path.realpath(__file__)
fdir = delim.join(fp.split(delim)[:-1])
data_dir = os.path.join(fdir, "..", "data")

from twittertennis.handler import TennisDataHandler

def test_label_export():
    dir1 = os.path.join(fdir, "rg17_with_qTrue")
    dir2 = dir1 + "_relevant"
    handler = TennisDataHandler(data_dir, "rg17", include_qualifiers=True)
    handler.export_relevance_labels(dir1, binary=True, only_pos_label=False)
    handler.export_relevance_labels(dir2, binary=True, only_pos_label=True)
    assert len(os.listdir(dir1)) == 20
    assert len(os.listdir(dir2)) == 20
    fp1 = os.path.join(dir1, "labels_18.csv")
    fp2 = os.path.join(dir2, "labels_18.csv")
    df1 = pd.read_csv(fp1, header=None)
    df2 = pd.read_csv(fp2, header=None)
    assert len(df1) == 78094
    assert len(df2) == 18