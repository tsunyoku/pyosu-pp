from enum import IntFlag


class HitSoundType(IntFlag):
    NORMAL = 0
    WHISTLE = 1 << 1
    FINISH = 1 << 2
    CLAP = 1 << 3
