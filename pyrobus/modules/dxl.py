from .module import Module, Input, Output


class DynamixelMotor(Module):
    present_position = Input()
    goal_position = Output()

    present_speed = Input()
    moving_speed = Output()

    torque_limit = Output()
    compliant = Output()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)
