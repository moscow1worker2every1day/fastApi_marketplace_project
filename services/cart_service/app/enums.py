from enum import Enum


class DeltaEnum(int, Enum):
    increase = 1
    decrease = -1
