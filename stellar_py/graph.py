class StellarGraph:
    """Reference to a Stellar Graph
    """
    def __init__(self, session):
        self.session = session
    def save(self, path, file_format="json"):
        raise NotImplementedError()
