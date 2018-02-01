class StellarGraph:
    """Reference to a Stellar Graph
    """
    def __init__(self, path):
        self.path = path

    def save(self, path, file_format="json"):
        raise NotImplementedError()
