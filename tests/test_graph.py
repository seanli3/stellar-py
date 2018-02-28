from stellar.graph import *
import pytest


EPGM_PATH = 'tests/res/lotr.epgm'


def test_repr():
    graph = StellarGraph(EPGM_PATH, "")
    graph_uuid = StellarGraph('/tmp/stellar/abcdef01-1234-1234-9876-abcdefff5690/graph', "")
    assert repr(graph) == "StellarGraph('{}')".format(EPGM_PATH)
    assert repr(graph_uuid) == "StellarGraph(abcdef01-1234-1234-9876-abcdefff5690)"


def test_load_epgm():
    def count_by_label(elems, label):
        """Count elements by label

        :param elems:   graph elements
        :param label:   element label
        :return:        count
        """
        return sum(el['meta']['label'] == label for el in elems)

    graph = StellarGraph(EPGM_PATH, "")
    epgm = graph._load_epgm()
    assert 'vertices' in epgm
    assert 'edges' in epgm
    assert 'graphs' in epgm
    assert count_by_label(epgm['vertices'], 'Location') == 2
    assert count_by_label(epgm['vertices'], 'Person') == 3
    assert count_by_label(epgm['vertices'], 'Restaurant') == 2
    assert count_by_label(epgm['edges'], 'born-in') == 2
    assert count_by_label(epgm['edges'], 'friends-with') == 2
    assert count_by_label(epgm['edges'], 'reviewed') == 3
    assert count_by_label(epgm['edges'], 'located-in') == 3
    assert count_by_label(epgm['edges'], 'duplicate-of') == 1
    assert count_by_label(epgm['graphs'], 'empty') == 1
    assert count_by_label(epgm['graphs'], 'base-line') == 1
    assert count_by_label(epgm['graphs'], 'pre-er') == 1
    assert count_by_label(epgm['graphs'], 'new-info') == 1
    assert count_by_label(epgm['graphs'], 'post-er') == 1


def test_load_graph():
    graph = StellarGraph(EPGM_PATH, "")._load_graph()
    assert len(graph['vertices']) == 7
    assert len(graph['edges']) == 11


def test_load_empty_graph():
    graph = StellarGraph(EPGM_PATH, "")._load_graph(index=0)
    assert len(graph['vertices']) == 0
    assert len(graph['edges']) == 0


def test_load_graph_with_meta():
    graph = StellarGraph(EPGM_PATH, "")._load_graph(meta_keys={'stellar_label': 'label', 'stellar_non': 'non'})
    assert len(graph['vertices']) == 7
    assert len(graph['edges']) == 11
    assert sum(attr['stellar_label'] == 'Location' for _, attr in graph['vertices']) == 2
    assert sum(attr['stellar_non'] == '' for _, attr in graph['vertices']) == 7
    assert sum(attr['stellar_label'] == 'born-in' for _, _, attr in graph['edges']) == 2
    assert sum(attr['stellar_non'] == '' for _, _, attr in graph['edges']) == 11


def test_to_networkx():
    graph = StellarGraph(EPGM_PATH, "").to_networkx()
    assert graph.number_of_nodes() == 7
    assert graph.number_of_edges() == 11
    assert sum(attr.setdefault('race', '') == 'Hobbit' for _, attr in graph.nodes(data=True)) == 3
    assert sum(attr.setdefault('stars', 0) > 3 for _, _, attr in graph.edges(data=True)) == 2


def test_to_networkx_with_label():
    graph = StellarGraph(EPGM_PATH, "").to_networkx(inc_label_as='my_label')
    assert graph.number_of_nodes() == 7
    assert graph.number_of_edges() == 11
    assert sum(attr['my_label'] == 'Location' for _, attr in graph.nodes(data=True)) == 2
    assert sum(attr['my_label'] == 'born-in' for _, _, attr in graph.edges(data=True)) == 2
