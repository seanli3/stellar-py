"""Stellar Graph

Classes and methods related to referencing and operating on a stellar graph.

"""

import networkx as nx
import os
import json
import re
from typing import Dict, List, Tuple, Optional

GraphElement = Dict[str, any]
EPGM = Dict[str, List[GraphElement]]
GraphDict = Dict[str, Tuple]


class StellarGraph:
    """Reference to a Stellar Graph
    """
    def __init__(self, path: str, label: str):
        self.path = path
        self.label = label

    def __repr__(self):
        m = re.search("([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", self.path)
        if not m:
            return "StellarGraph('{}')".format(self.path)
        else:
            return "StellarGraph({})".format(m.group(0))

    def _load_epgm(self) -> EPGM:
        """Load graphs from EPGM path
        """
        if not os.path.isdir(self.path):
            raise Exception("Path {} does not exist!".format(self.path))

        g = {'graphs': list(), 'vertices': list(), 'edges': list()}

        for k in g.keys():
            fname = os.path.join(self.path, str(k) + '.json')
            with open(fname, 'r', encoding='utf-8') as fp:
                g[k] = [json.loads(l) for l in fp.readlines()]

        return g

    def _load_graph(self, index: int = -1, meta_keys: Optional[Dict[str, str]] = None) -> GraphDict:
        """Load graph at index from EPGM path

        :param index:   graph index from EPGM
        :return:        graph dict
        """
        def data_x_meta(element: GraphElement) -> Dict[str, any]:
            """Merge data and meta using meta keys

            :param element:     graph element dict
            :return:            merged data dict
            """
            if not meta_keys:
                return element['data']
            else:
                return {**element['data'], **{k: element['meta'].setdefault(v, '') for k, v in meta_keys.items()}}

        epgm = self._load_epgm()
        graph_id = epgm['graphs'][index]['id']
        graph_dict = dict()
        graph_dict['vertices'] = [(v['id'], data_x_meta(v)) for v in epgm['vertices']
                                  if graph_id in v['meta']['graphs']]
        graph_dict['edges'] = [(e['source'], e['target'], data_x_meta(e)) for e in epgm['edges']
                               if graph_id in e['meta']['graphs']]
        return graph_dict

    def to_networkx(self, inc_label_as: Optional[str] = None) -> nx.MultiDiGraph:
        """Load graph with networkx

        :param inc_label_as:    include label as an attribute
        :return:                networkx MultiDiGraph
        """
        graph_dict = self._load_graph(meta_keys={inc_label_as: 'label'}) if inc_label_as else self._load_graph()
        g = nx.MultiDiGraph()
        g.add_nodes_from(graph_dict['vertices'])
        g.add_edges_from(graph_dict['edges'])
        return g
