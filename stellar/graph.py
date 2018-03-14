"""Stellar Graph

Classes and methods related to referencing and operating on a stellar graph.

"""

__copyright__ = """

    This file is part of stellar-py, Stellar Python Client.

    Copyright 2018 CSIRO Data61

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

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

    def to_networkx(self, inc_type_as: Optional[str] = None) -> nx.MultiDiGraph:
        """Load graph with networkx

        :param inc_type_as:     Specify name of "type" attribute to include it as an attribute
        :return:                networkx MultiDiGraph
        """
        graph_dict = self._load_graph(meta_keys={inc_type_as: 'label'}) if inc_type_as else self._load_graph()
        g = nx.MultiDiGraph()
        g.add_nodes_from(graph_dict['vertices'])
        g.add_edges_from(graph_dict['edges'])
        return g

    def to_graphml(self, filepath: str, inc_type_as: Optional[str] = None) -> bool:
        """Write graph out to GraphML format

        :param filepath:    Output path
        :param inc_type_as: Specify name of "type" attribute to include it as an attribute
        :return:            True if successful
        """
        try:
            nx.write_graphml(nx.DiGraph(self.to_networkx(inc_type_as)), filepath)
            return True
        except:
            return False
