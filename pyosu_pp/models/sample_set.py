from enum import Enum


class SampleSet(str, Enum):
    NONE = "None"
    NORMAL = "Normal"
    SOFT = "Soft"
    DRUM = "Drum"
