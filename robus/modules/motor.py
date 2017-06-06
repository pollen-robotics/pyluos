from .module import Module, Output


class Motor(Module):
    position = Output()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Motor', id, alias, robot)
        self.position = 90
