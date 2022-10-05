from dataclasses import dataclass
from pyosu_pp.models.time_signature import TimeSignature
from pyosu_pp.models.sample_set import SampleSet
from pyosu_pp.models.effect import Effect


@dataclass
class TimingPoint:
    offset: int
    beat_length: float
    time_signature: TimeSignature
    sample_set: SampleSet
    custom_sample_set: int
    volume: int
    inherited: bool
    effects: Effect
    bpm: float
    velocity: float
