from .module import Module, Output


class Relay(Module):
    state = Output()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Relay', id, alias, robot)
        self.off()

    def on(self):
        self.state = 1

    def off(self):
        self.state = 0
