
class InfoStruct:
    def __init__(self, infodict):
        self.infos = infodict

    def update(self, infodict):
        self.infos.update(infodict)

    def getinfo(self):
        return self.infos