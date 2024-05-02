from core.ui.modules.test import test

class ui:
    def __init__(self):
        self.modules = []
        self.fetch_modules()
    
    def fetch_modules(self):
        self.modules.append(test())
