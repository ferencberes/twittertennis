import twittertennis.handler as tt
import os

delim = os.path.sep
fp = os.path.realpath(__file__)
fdir = delim.join(fp.split(delim)[:-1])
data_dir = os.path.join(fdir, "..", "data")

def test_load_rg17_with_qualifiers():
    handler = tt.TennisDataHandler(data_dir, "rg17", include_qualifiers=True)
    summary = handler.summary()
    assert summary["data_id"] == "rg17"
    assert len(summary) == 8
    assert len(summary["dates"]) == 19
    assert len(summary["dates_with_no_game"]) == 1
    assert '2017-05-27' in summary["dates_with_no_game"]
    assert summary["start_time"] == 1495576800
    assert summary["end_time"] == 1497218400
    assert summary["number_of_nodes"] == 78095
    assert summary["number_of_edges"] == 336234
    
def test_load_rg17_without_qualifiers():
    handler = tt.TennisDataHandler(data_dir, "rg17", include_qualifiers=False)
    summary = handler.summary()
    assert len(summary["dates"]) == 15
    assert summary["start_time"] == 1495922400
    assert summary["number_of_nodes"] == 74984
    assert summary["number_of_edges"] == 311562
    
def test_load_uo17_with_qualifiers():
    handler = tt.TennisDataHandler(data_dir, "uo17", include_qualifiers=True)
    summary = handler.summary()
    assert summary["data_id"] == "uo17"
    assert len(summary["dates"]) == 20
    assert len(summary["dates_with_no_game"]) == 2
    assert '2017-08-26' in summary["dates_with_no_game"] and '2017-08-27' in summary["dates_with_no_game"]
    assert summary["start_time"] == 1503374400
    assert summary["end_time"] == 1505102400
    assert summary["number_of_nodes"] == 106106
    assert summary["number_of_edges"] == 475085
    
def test_load_uo17_without_qualifiers():
    handler = tt.TennisDataHandler(data_dir, "uo17", include_qualifiers=False)
    summary = handler.summary()
    assert len(summary["dates"]) == 14
    assert summary["start_time"] == 1503892800
    assert summary["number_of_nodes"] == 99191
    assert summary["number_of_edges"] == 417637