class CColor:
    def __init__(self, color: tuple):
        self.color: tuple = color # ARGB

    def getAlpha(self) -> int:
        return self.color[0]
    
    def getRed(self) -> int:
        return self.color[1]
    
    def getGreen(self) -> int:
        return self.color[2]
    
    def getBlue(self) -> int:
        return self.color[3]

    def getRGB(self):
        return self.color[1:3]
    
    def getColor(self):
        return self.color