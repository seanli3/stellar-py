"""Ingestion

Classes and methods related to the Ingestor module.

"""

from stellar_py.payload import Payload
from typing import Dict, Optional, List


class VertexMapping:
    """Vertex mapping for data source

    Attributes:
        vertex_class: class label
        vertex_id: column name for unique ID
        properties: dict of {key: column}
    """
    def __init__(self, vertex_class: str, vertex_id: str, properties: Dict[str, str]) -> None:
        self.vertex_class = vertex_class
        self.vertex_id = vertex_id
        self.properties = properties or {}


class EdgeMapping:
    """Edge mapping for data source

    Attributes:
        edge_class: class label
        src_class: source vertex class label
        src: column name for source vertex
        dst: column name for destination vertex
        properties: dict of {key: column}
    """
    def __init__(self, edge_class: str, src_class: str, src: str, dst: str, properties: Dict[str, str]) -> None:
        self.edge_class = edge_class
        self.src_class = src_class
        self.src = src
        self.dst = dst
        self.properties = properties or {}


class ElementClass:
    """Generic graph element class

    """
    def __init__(self, name: str, properties: Dict[str, str]) -> None:
        self.name = name
        self.properties = properties or {}

    def validate_props(self, properties: Dict[str, str]):
        """Require properties to be validated

        :param properties:  element properties
        :return:            element properties
        """
        if not properties:
            return properties
        schema_props_keys = set(self.properties.keys())
        mapping_props_keys = set(properties.keys())
        if len(mapping_props_keys - schema_props_keys.intersection(mapping_props_keys)) > 0:
            raise KeyError("invalid properties")
        return properties


class VertexClass(ElementClass):
    """Vertex class for graph schema

    Attributes:
        name (str): Unique label name
        properties (Dict[str, str]): dict of {key: type}
    """
    def __init__(self, name: str, properties: Dict[str, str]) -> None:
        ElementClass.__init__(self, name, properties)

    def create_mapping(self, vertex_id: str, properties: Optional[Dict[str, str]]=None) -> VertexMapping:
        """Create vertex mapping

        :param vertex_id:   column name containing vertex ID
        :param properties:  dict of property name to column name
        :return:            vertex mapping
        """
        return VertexMapping(self.name, vertex_id, self.validate_props(properties))


class EdgeClass(ElementClass):
    """Edge class for graph schema

    Attributes:
        name (str): Unique label name
        src_class (str): source vertex class label name
        dst_class (str): destination vertex class label name
        properties (Dict[str, str]): dict of {key: type}
    """
    def __init__(self, name: str, src_class: str, dst_class: str, properties: Dict[str, str]) -> None:
        ElementClass.__init__(self, name, properties)
        self.src_class = src_class
        self.dst_class = dst_class

    def create_mapping(self, src: str, dst: str, properties: Optional[Dict[str, str]]=None) -> EdgeMapping:
        """Create edge mapping

        :param src:         column name containing source ID
        :param dst:         column name containing destination ID
        :param properties:  dict of property name to column name
        :return:            edge mapping
        """
        return EdgeMapping(self.name, self.src_class, src, dst, self.validate_props(properties))


class GraphSchema:
    """Used to create and define a Graph Schema

    """
    def __init__(self):
        self.vertex = {}
        self.edge = {}

    def add_vertex_class(self, name: str, properties: Optional[Dict[str, str]] = None) -> None:
        """Add vertex class definition to schema

        :param name:        name of vertex class
        :param properties:  dict of properties to their types
        """
        if name not in self.vertex.keys():
            self.vertex[name] = VertexClass(name, properties)

    def add_edge_class(self, name: str, src_class: str, dst_class: str,
                       properties: Optional[Dict[str, str]] = None) -> None:
        """Add edge class definition to schema

        :param name:        name of edge class
        :param src_class:   name of source vertex class
        :param dst_class:   name of destination vertex class
        :param properties:  dict of properties to their types
        """
        if name not in self.edge.keys():
            self.edge[name] = EdgeClass(name, src_class, dst_class, properties)


class DataSource:
    """Used to define a data source and its column mappings as graph elements and properties

    """
    def __init__(self, path: str, vertex_mappings: Optional[List[VertexMapping]] = None,
                 edge_mappings: Optional[List[EdgeMapping]] = None) -> None:
        self.path = path
        self.vertex_mappings = vertex_mappings or []
        self.edge_mappings = edge_mappings or []

    def add_vertex_mapping(self, vertex_mapping: VertexMapping) -> None:
        """Add a vertex mapping

        :param vertex_mapping: vertex mapping
        """
        self.vertex_mappings.append(vertex_mapping)

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
            "classes": [self.vc2c(vc) for vc in schema.vertex.values()],
            "classLinks": [self.ec2cl(ec) for ec in schema.edge.values()]
        }
        self.mapping = {
            "nodes": [node for s in sources
                      for node in
                      self.vms2nodes(s.path, s.vertex_mappings)],
            "links": [link for s in sources
                      for link in
                      self.ems2links(s.path, s.edge_mappings)]
        }

    @staticmethod
    def vc2c(vertex_class: VertexClass) -> Dict[str, str]:
        """Vertex class to payload "class" element

        :param vertex_class:    vertex class
        :return:                "class" element in payload
        """
        return {
            "name": vertex_class.name,
            "props": vertex_class.properties
        }

    @staticmethod
    def ec2cl(edge_class: EdgeClass) -> Dict[str, str]:
        """Edge class to payload "class link" element

        :param edge_class:  edge class
        :return:            "class link" element in payload
        """
        return {
            "name": edge_class.name,
            "source": edge_class.src_class,
            "target": edge_class.dst_class,
            "props": edge_class.properties
        }

    @staticmethod
    def vms2nodes(source: str, vms: List[VertexMapping]) -> List[Dict]:
        """Vertex mappings to "nodes" element in payload

        :param source:  data source path
        :param vms:     vertex mappings
        :return:        "nodes" element in payload
        """
        def vm2node(vm: VertexMapping) -> Dict:
            """Vertex mapping to "node"

            :param vm:  vertex mapping
            :return:    "node" element in payload
            """
            node = {k: {"column": v, "source": source}
                    for k, v in vm.properties.items()}
            node["@id"] = {"column": vm.vertex_id, "source": source}
            node["@type"] = vm.vertex_class
            return node
        return [vm2node(vm) for vm in vms]

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
                    for k, v in em.properties.items()}
            link["@src"] = {"column": em.src, "source": source}
            link["@dest"] = {"column": em.dst, "source": source}
            link["@type"] = {"name": em.edge_class, "source": em.src_class}
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
