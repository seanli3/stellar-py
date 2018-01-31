import json


def validate_props(schema_props, mapping_props):
    if not mapping_props:
        return mapping_props
    schema_props_keys = set(schema_props.keys())
    mapping_props_keys = set(mapping_props.keys())
    if len(mapping_props_keys - schema_props_keys.intersection(mapping_props_keys)) > 0:
        raise KeyError("invalid properties")
    return mapping_props


class VertexClass:
    """Vertex class for graph schema

    Attributes:
        name (str): Unique label name
        properties: dict of {key: type}
    """
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties or {}

    def create_mapping(self, vertex_id, properties=None):
        return VertexMapping(self.name, vertex_id, validate_props(self.properties, properties))


class EdgeClass:
    """Edge class for graph schema

    Attributes:
        name (str): Unique label name
        src_class (str): source vertex class label name
        dst_class (str): destination vertex class label name
        properties: dict of {key: type}
    """
    def __init__(self, name, src_class, dst_class, properties):
        self.name = name
        self.src_class = src_class
        self.dst_class = dst_class
        self.properties = properties or {}

    def create_mapping(self, src, dst, properties=None):
        return EdgeMapping(self.name, self.src_class, src, dst, validate_props(self.properties, properties))


class VertexMapping:
    """Vertex mapping for data source

    Attributes:
        vertex_class: class label
        vertex_id: column name for unique ID
        properties: dict of {key: column}
    """
    def __init__(self, vertex_class, vertex_id, properties):
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
    def __init__(self, edge_class, src_class, src, dst, properties):
        self.edge_class = edge_class
        self.src_class = src_class
        self.src = src
        self.dst = dst
        self.properties = properties or {}


class GraphSchema:
    def __init__(self):
        self.vertex = {}
        self.edge = {}

    def add_vertex_class(self, name, properties=None):
        if name not in self.vertex.keys():
            self.vertex[name] = VertexClass(name, properties)

    def add_edge_class(self, name, src_class, dst_class, properties=None):
        if name not in self.edge.keys():
            self.edge[name] = EdgeClass(name, src_class, dst_class, properties)


class DataSource:
    def __init__(self, path, vertex_mappings=None, edge_mappings=None):
        self.path = path
        self.vertex_mappings = vertex_mappings or []
        self.edge_mappings = edge_mappings or []

    def add_vertex_mapping(self, vertex_mapping):
        self.vertex_mappings.append(vertex_mapping)

    def add_edge_mapping(self, edge_mapping):
        self.edge_mappings.append(edge_mapping)


class StellarIngestPayload:
    """Payload object used to start ingestion

    Attributes:
        session_id: session ID
        schema: graph schema object
        sources: list of sources and their mappings
    """
    def __init__(self, session_id, schema, sources):
        self.sessionId = session_id
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
    def vc2c(vertex_class):
        return {
            "name": vertex_class.name,
            "props": vertex_class.properties
        }

    @staticmethod
    def ec2cl(edge_class):
        return {
            "name": edge_class.name,
            "source": edge_class.src_class,
            "target": edge_class.dst_class,
            "props": edge_class.properties
        }

    @staticmethod
    def vms2nodes(source, vms):
        def vm2node(vm):
            node = {k: {"column": v, "source": source}
                    for k, v in vm.properties.items()}
            node["@id"] = {"column": vm.vertex_id, "source": source}
            node["@type"] = vm.vertex_class
            return node
        return [vm2node(vm) for vm in vms]

    @staticmethod
    def ems2links(source, ems):
        def em2link(em):
            link = {k: {"column": v, "source": source}
                    for k, v in em.properties.items()}
            link["@src"] = {"column": em.src, "source": source}
            link["@dest"] = {"column": em.dst, "source": source}
            link["@type"] = {"name": em.edge_class, "source": em.src_class}
            return link
        return [em2link(em) for em in ems]

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)


def create_graph_schema():
    return GraphSchema()


def new_data_source(path):
    return DataSource(path)
