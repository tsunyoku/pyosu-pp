from dataclasses import dataclass
from typing import Optional
from pyosu_pp.models.vector2 import Vector2
from pyosu_pp.models.hit_sound_type import HitSoundType
from pyosu_pp.models.sample_set import SampleSet


@dataclass
class HitObject:
    position: Vector2
    start_time: int
    end_time: int
    hit_sound: HitSoundType
    is_new_combo: bool
    combo_offset: int

    sample_set: Optional[SampleSet]
    addition_set: Optional[SampleSet]
    custom_index: Optional[int]
    volume: Optional[int]
    sample_filename: Optional[str]


class Circle(HitObject):
    pass


class Spinner(HitObject):
    pass
