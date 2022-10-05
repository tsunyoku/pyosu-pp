from dataclasses import dataclass


@dataclass
class Video:
    start_time: int
    filename: str
    x_offset: int
    y_offset: int
