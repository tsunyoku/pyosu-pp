from enum import Enum


class OverlayPosition(str, Enum):
    NO_CHANGE = "NoChange"
    BELOW = "Below"
    ABOVE = "Above"
