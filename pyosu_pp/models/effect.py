from enum import IntFlag


class Effect(IntFlag):
    NONE = 0
    KIAI = 1 << 0
    OMIT_FIRST_BAR_LINE = 1 << 3
