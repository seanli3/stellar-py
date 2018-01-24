import json


class VertexClass:
    """Vertex class for graph schema

    Attributes:
        name (str): Unique label name
        properties: dict of {key: type}
    """
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


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
        self.properties = properties


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
        self.properties = properties


class EdgeMapping:
    """Edge mapping for data source

    Attributes:
        edge_class: class label
        edge_id: column name for unique ID
        properties: dict of {key: column}
    """
    def __init__(self, edge_class, src_class, src, dst, properties):
        self.edge_class = edge_class
        self.src_class = src_class
        self.src = src
        self.dst = dst
        self.properties = properties


class StellarIngestPayload:
    """Payload object used to start ingestion

    Attributes:
        session_id: session ID
        sources: list of sources and their mappings
        vertex_classes: list of vertex classes
        edge_classes: list of edge classes
    """
    def __init__(self, session_id, sources, vertex_classes, edge_classes):
        self.sessionId = session_id
        self.sources = [s['path'] for s in sources]
        self.graphSchema = {
            "classes": [self.vc2c(vc) for vc in vertex_classes],
            "classLinks": [self.ec2cl(ec) for ec in edge_classes]
        }
        self.mapping = {
            "nodes": [node for s in sources
                      for node in
                      self.vms2nodes(s['path'], s['mapping'].get('vertices', []))],
            "links": [link for s in sources
                      for link in
                      self.ems2links(s['path'], s['mapping'].get('edges', []))]
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


class StellarIngestor:
    """Ingestor object

    Attributes:
        session: Stellar session
        name: name of graph
        schema: graph schema
        sources: list of data sources
    """
    def __init__(self, session, name, schema=None, sources=None):
        self.session = session
        self.name = name
        self.schema = {'vertex_classes':[], 'edge_classes':[]} if schema is None else schema
        self.sources = [] if sources is None else sources

    def add_source(self, path, mapping):
        return StellarIngestor(
            self.session,
            self.name,
            self.schema,
            self.sources + [{"path": path, "mapping": mapping}]
        )

    def get_payload(self):
        return StellarIngestPayload(self.session.session_id,
                                    self.sources,
                                    self.schema['vertex_classes'],
                                    self.schema['edge_classes'])

    def ingest(self):
        return self.session.post("ingestor/start", self.get_payload().to_json())
