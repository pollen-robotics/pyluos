from .dxl import DynamixelMotor
from .distance import Distance
from .button import Button
from .potard import Potard
from .servo import Servo
from .relay import Relay
from .led import Led


__all__ = [
    'name2mod',
    'DynamixelMotor',
    'Distance',
    'Button',
    'Potard',
    'Servo',
    'Relay',
    'Led',
]

name2mod = {
    'dynamixel': DynamixelMotor,
    'distance': Distance,
    'button': Button,
    'potard': Potard,
    'servo': Servo,
    'relay': Relay,
    'led': Led,
}
