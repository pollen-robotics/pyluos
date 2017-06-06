from .module import Module, Output


class Led(Module):
    color = Output()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'LED', id, alias, robot)
        self.color = (0, 0, 0)
