from constants import SUPPORTED_HASHES


class DoHash:
    def __init__(self, types):
        self.T = []
        for x in types:
            if x in SUPPORTED_HASHES:
                self.T.append(SUPPORTED_HASHES[x]())

    def update(self, data):
        [x.update(data) for x in self.T]

    def get(self):
        return [x.hexdigest() for x in self.T]
