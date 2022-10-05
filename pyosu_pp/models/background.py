from dataclasses import dataclass


@dataclass
class Background:
    filename: str
    x_offset: int
    y_offset: int
