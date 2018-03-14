"""Ingestion

Classes and methods related to the Ingestor module.

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

from stellar.payload import Payload
from typing import Dict, Optional, List, Union


class NodeMapping:
    """Vertex mapping for data source

    Attributes:
        node_type: type
        path: path to source file
        node_id: column name for unique ID
        attributes: dict of {key: column}
    """
    def __init__(self, node_type: str, path: str, column: str, map_attributes: Dict[str, str]) -> None:
        self.node_type = node_type
        self.path = path
        self.node_id = column
        self.attributes = map_attributes or {}


class EdgeMapping:
    """Edge mapping for data source

    Attributes:
        edge_type: type
        src_type: source node type
        path: path to source file
        src: column name for source node
        dst: column name for destination node
        attributes: dict of {key: column}
    """
    def __init__(self, edge_type: str, src_type: str, path: str, src: str, dst: str,
                 map_attributes: Dict[str, str]) -> None:
        self.edge_type = edge_type
        self.src_type = src_type
        self.path = path
        self.src = src
        self.dst = dst
        self.attributes = map_attributes or {}


class ElementType:
    """Generic graph element class

    """
    def __init__(self, name: str, attribute_types: Dict[str, str]) -> None:
        self.name = name
        self.attribute_types = attribute_types or {}

    def validate_attributes(self, attributes: Dict[str, str]):
        """Require attributes to be validated

        :param attributes:  element attributes
        :return:            element attributes
        """
        if not attributes:
            return attributes
        schema_props_keys = set(self.attribute_types.keys())
        mapping_props_keys = set(attributes.keys())
        if len(mapping_props_keys - schema_props_keys.intersection(mapping_props_keys)) > 0:
            raise KeyError("invalid attributes")
        return attributes


class NodeType(ElementType):
    """Vertex class for graph schema

    Attributes:
        name (str): Unique label name
        attribute_types (Dict[str, str]): dict of {key: type}
    """
    def __init__(self, name: str, attribute_types: Dict[str, str]) -> None:
        ElementType.__init__(self, name, attribute_types)

    def create_map(self, path: str, column: str, map_attributes: Optional[Dict[str, str]]=None) -> NodeMapping:
        """Create node mapping

        :param path:            path to source file
        :param column:          column name containing node ID
        :param map_attributes:  dict of property name to column name
        :return:                node mapping
        """
        return NodeMapping(self.name, path, column, self.validate_attributes(map_attributes))


class EdgeType(ElementType):
    """Edge class for graph schema

    Attributes:
        name (str): Unique label name
        src_type (str): source node type name
        dst_type (str): destination node type name
        attribute_types (Dict[str, str]): dict of {key: type}
    """
    def __init__(self, name: str, src_type: str, dst_type: str, attribute_types: Dict[str, str]) -> None:
        ElementType.__init__(self, name, attribute_types)
        self.src_type = src_type
        self.dst_type = dst_type

    def create_map(self, path: str, src: str, dst: str, map_attributes: Optional[Dict[str, str]]=None) -> EdgeMapping:
        """Create edge mapping

        :param path:            path to source file
        :param src:             column name containing source ID
        :param dst:             column name containing destination ID
        :param map_attributes:  dict of property name to column name
        :return:                edge mapping
        """
        return EdgeMapping(self.name, self.src_type, path, src, dst, self.validate_attributes(map_attributes))


class GraphSchema:
    """Used to create and define a Graph Schema

    """
    def __init__(self):
        self.node = {}  # type: Dict[str, NodeType]
        self.edge = {}  # type: Dict[str, EdgeType]

    def add_node_type(self, name: str, attribute_types: Optional[Dict[str, str]] = None):
        """Add node class definition to schema

        :param name:        name of node class
        :param attribute_types:  dict of attributes to their types
        """
        if name in self.node.keys():
            print("WARNING: Overwriting existing node type '{}'".format(name))
        self.node[name] = NodeType(name, attribute_types)
        return self

    def add_edge_type(self, name: str, src_type: str, dst_type: str,
                      attribute_types: Optional[Dict[str, str]] = None):
        """Add edge class definition to schema

        :param name:        name of edge class
        :param src_type:   name of source node class
        :param dst_type:   name of destination node class
        :param attribute_types:  dict of attributes to their types
        """
        if name in self.edge.keys():
            print("WARNING: Overwriting existing edge type '{}'".format(name))
        self.edge[name] = EdgeType(name, src_type, dst_type, attribute_types)
        return self


class StellarIngestPayload(Payload):
    """Payload object used to start ingestion

    Attributes:
        session_id: session ID
        schema: graph schema object
        sources: list of sources and their mappings
    """
    def __init__(self, session_id: str, schema: GraphSchema, mappings: List[Union[NodeMapping, EdgeMapping]],
                 label: str):
        Payload.__init__(self, session_id, label)
        self.sources = list(set([m.path for m in mappings]))
        self.graphSchema = {
            "classes": [self.nt2c(vc) for vc in schema.node.values()],
            "classLinks": [self.et2cl(ec) for ec in schema.edge.values()]
        }
        self.mapping = {
            "nodes": [self.nm2node(m) for m in mappings if isinstance(m, NodeMapping)],
            "links": [self.em2link(m) for m in mappings if isinstance(m, EdgeMapping)]
        }

    @staticmethod
    def nt2c(node_type: NodeType) -> Dict[str, str]:
        """Vertex class to payload "class" element

        :param node_type:    node class
        :return:                "class" element in payload
        """
        return {
            "name": node_type.name,
            "props": node_type.attribute_types
        }

    @staticmethod
    def et2cl(edge_type: EdgeType) -> Dict[str, str]:
        """Edge class to payload "class link" element

        :param edge_type:  edge class
        :return:            "class link" element in payload
        """
        return {
            "name": edge_type.name,
            "source": edge_type.src_type,
            "target": edge_type.dst_type,
            "props": edge_type.attribute_types
        }

    @staticmethod
    def nm2node(vm: NodeMapping) -> Dict:
        """Vertex mapping to "node"

        :param vm:  node mapping
        :return:    "node" element in payload
        """
        node = {k: {"column": v, "source": vm.path}
                for k, v in vm.attributes.items()}
        node["@id"] = {"column": vm.node_id, "source": vm.path}
        node["@type"] = vm.node_type
        return node

    @staticmethod
    def em2link(em: EdgeMapping) -> Dict:
        """Edge mapping to "link"

        :param em:  edge mapping
        :return:    "link" element in payload
        """
        link = {k: {"column": v, "source": em.path}
                for k, v in em.attributes.items()}
        link["@src"] = {"column": em.src, "source": em.path}
        link["@dest"] = {"column": em.dst, "source": em.path}
        link["@type"] = {"name": em.edge_type, "source": em.src_type}
        return link


def create_schema() -> GraphSchema:
    """Exposed method to create graph schema

    :return: graph schema object
    """
    return GraphSchema()
