"""Ingestion

Classes and methods related to the Ingestor module.

"""

from stellar_py.payload import Payload
from typing import Dict, Optional, List


class NodeMapping:
    """Vertex mapping for data source

    Attributes:
        node_type: type
        node_id: column name for unique ID
        attributes: dict of {key: column}
    """
    def __init__(self, node_type: str, node_id: str, attributes: Dict[str, str]) -> None:
        self.node_type = node_type
        self.node_id = node_id
        self.attributes = attributes or {}


class EdgeMapping:
    """Edge mapping for data source

    Attributes:
        edge_type: type
        src_type: source node type
        src: column name for source node
        dst: column name for destination node
        attributes: dict of {key: column}
    """
    def __init__(self, edge_type: str, src_type: str, src: str, dst: str, attributes: Dict[str, str]) -> None:
        self.edge_type = edge_type
        self.src_type = src_type
        self.src = src
        self.dst = dst
        self.attributes = attributes or {}


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

    def create_mapping(self, node_id: str, attributes: Optional[Dict[str, str]]=None) -> NodeMapping:
        """Create node mapping

        :param node_id:   column name containing node ID
        :param attributes:  dict of property name to column name
        :return:            node mapping
        """
        return NodeMapping(self.name, node_id, self.validate_attributes(attributes))


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

    def create_mapping(self, src: str, dst: str, attributes: Optional[Dict[str, str]]=None) -> EdgeMapping:
        """Create edge mapping

        :param src:         column name containing source ID
        :param dst:         column name containing destination ID
        :param attributes:  dict of property name to column name
        :return:            edge mapping
        """
        return EdgeMapping(self.name, self.src_type, src, dst, self.validate_attributes(attributes))


class GraphSchema:
    """Used to create and define a Graph Schema

    """
    def __init__(self):
        self.node = {}
        self.edge = {}

    def add_node_type(self, name: str, attribute_types: Optional[Dict[str, str]] = None) -> None:
        """Add node class definition to schema

        :param name:        name of node class
        :param attribute_types:  dict of attributes to their types
        """
        if name not in self.node.keys():
            self.node[name] = NodeType(name, attribute_types)

    def add_edge_type(self, name: str, src_type: str, dst_type: str,
                      attribute_types: Optional[Dict[str, str]] = None) -> None:
        """Add edge class definition to schema

        :param name:        name of edge class
        :param src_type:   name of source node class
        :param dst_type:   name of destination node class
        :param attribute_types:  dict of attributes to their types
        """
        if name not in self.edge.keys():
            self.edge[name] = EdgeType(name, src_type, dst_type, attribute_types)


class DataSource:
    """Used to define a data source and its column mappings as graph elements and attributes

    """
    def __init__(self, path: str, node_mappings: Optional[List[NodeMapping]] = None,
                 edge_mappings: Optional[List[EdgeMapping]] = None) -> None:
        self.path = path
        self.node_mappings = node_mappings or []
        self.edge_mappings = edge_mappings or []

    def add_node_mapping(self, node_mapping: NodeMapping) -> None:
        """Add a node mapping

        :param node_mapping: node mapping
        """
        self.node_mappings.append(node_mapping)

    def add_edge_mapping(self, edge_mapping: EdgeMapping) -> None:
        """Add an edge mapping

        :param edge_mapping: edge mapping
        """
        self.edge_mappings.append(edge_mapping)


class StellarIngestPayload(Payload):
    """Payload object used to start ingestion

    Attributes:
        session_id: session ID
        schema: graph schema object
        sources: list of sources and their mappings
    """
    def __init__(self, session_id: str, schema: GraphSchema, sources: List[DataSource], label: str):
        Payload.__init__(self, session_id, label)
        self.sources = [s.path for s in sources]
        self.graphSchema = {
            "classes": [self.nt2c(vc) for vc in schema.node.values()],
            "classLinks": [self.et2cl(ec) for ec in schema.edge.values()]
        }
        self.mapping = {
            "nodes": [node for s in sources
                      for node in
                      self.nms2nodes(s.path, s.node_mappings)],
            "links": [link for s in sources
                      for link in
                      self.ems2links(s.path, s.edge_mappings)]
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
    def nms2nodes(source: str, vms: List[NodeMapping]) -> List[Dict]:
        """Vertex mappings to "nodes" element in payload

        :param source:  data source path
        :param vms:     node mappings
        :return:        "nodes" element in payload
        """
        def nm2node(vm: NodeMapping) -> Dict:
            """Vertex mapping to "node"

            :param vm:  node mapping
            :return:    "node" element in payload
            """
            node = {k: {"column": v, "source": source}
                    for k, v in vm.attributes.items()}
            node["@id"] = {"column": vm.node_id, "source": source}
            node["@type"] = vm.node_type
            return node
        return [nm2node(vm) for vm in vms]

    @staticmethod
    def ems2links(source: str, ems: List[EdgeMapping]) -> List[Dict]:
        """Edge mappings to "links" element in payload

        :param source:  data source path
        :param ems:     edge mappings
        :return:        "links" element in payload
        """
        def em2link(em: EdgeMapping) -> Dict:
            """Edge mapping to "link"

            :param em:  edge mapping
            :return:    "link" element in payload
            """
            link = {k: {"column": v, "source": source}
                    for k, v in em.attributes.items()}
            link["@src"] = {"column": em.src, "source": source}
            link["@dest"] = {"column": em.dst, "source": source}
            link["@type"] = {"name": em.edge_type, "source": em.src_type}
            return link
        return [em2link(em) for em in ems]


def create_graph_schema() -> GraphSchema:
    """Exposed method to create graph schema

    :return: graph schema object
    """
    return GraphSchema()


def new_data_source(path: str) -> DataSource:
    """Exposed method to create new data source

    :param path:    data source path
    :return:        new data source object
    """
    return DataSource(path)
