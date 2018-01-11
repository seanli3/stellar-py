import json

class VertexClass:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties

class EdgeClass:
    def __init__(self, name, src_class, dst_class, properties):
        self.name = name
        self.src_class = src_class
        self.dst_class = dst_class
        self.properties = properties

class VertexMapping:
    def __init__(self, vertex_class, vertex_id, properties):
        self.vertex_class = vertex_class
        self.vertex_id = vertex_id
        self.properties = properties

class EdgeMapping:
    def __init__(self, edge_class, src_class, src, dst, properties):
        self.edge_class = edge_class
        self.src_class = src_class
        self.src = src
        self.dst = dst
        self.properties = properties

class StellarIngestPayload:
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
    def vc2c(self, vertex_class):
        return {
            "name": vertex_class.name,
            "props": vertex_class.properties
        }
    def ec2cl(self, edge_class):
        return {
            "name": edge_class.name,
            "source": edge_class.src_class,
            "target": edge_class.dst_class,
            "props": edge_class.properties
        }
    def vms2nodes(self, source, vms):
        return [self.vm2node(source, vm) for vm in vms]
    def ems2links(self, source, ems):
        return [self.em2link(source, em) for em in ems]
    def vm2node(self, source, vm):
        node = {k: {"column": v, "source": source}
                for k, v in vm.properties.items()}
        node["@id"] = {"column": vm.vertex_id, "source": source}
        node["@type"] = vm.vertex_class
        return node
    def em2link(self, source, em):
        link = {k: {"column": v, "source": source}
                for k, v in em.properties.items()}
        link["@src"] = {"column": em.src, "source": source}
        link["@dest"] = {"column": em.dst, "source": source}
        link["@type"] = {"name": em.edge_class, "source": em.src_class}
        return link
    def to_json(self):
        return json.dumps(self.__dict__, indent=4)

class StellarIngestor:
    def __init__(self, session, name, schema, sources=[]):
        self.session = session
        self.name = name
        self.schema = schema
        self.sources = sources
    def add_source(self, path, mapping):
        return StellarIngestor(
            self.session,
            self.name,
            self.schema,
            self.sources + [{"path": path, "mapping": mapping}]
        )
    def ingest(self):
        data = StellarIngestPayload(self.session.session_id,
                                    self.sources,
                                    self.schema['vertex_classes'],
                                    self.schema['edge_classes']).to_json()
        return self.session.post("ingestor/start", data)
