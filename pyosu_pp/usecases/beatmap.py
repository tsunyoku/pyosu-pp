from typing import Any, Callable, Optional
from pyosu_pp.models.background import Background
from pyosu_pp.models.break_time import BreakTime
from pyosu_pp.models.effect import Effect
from pyosu_pp.models.hit_object import HitObject
from pyosu_pp.models.hit_object_type import HitObjectType
from pyosu_pp.models.hit_sound_type import HitSoundType

from pyosu_pp.models.mode import Mode
from pyosu_pp.models.overlay_position import OverlayPosition
from pyosu_pp.models.sample_set import SampleSet
from pyosu_pp.models.timing_point import TimingPoint
from pyosu_pp.models.vector2 import Vector2
from pyosu_pp.models.video import Video
from pyosu_pp.models.time_signature import TimeSignature

GENERAL_LINES = (
    "AudioFilename",
    "AudioLeadIn",
    "AudioHash",
    "PreviewTime",
    "Countdown",
    "SampleSet",
    "StackLeniency",
    "Mode",
    "LetterboxInBreaks",
    "StoryFireInFront",
    "UseSkinSprites",
    "AlwaysShowPlayfield",
    "OverlayPosition",
    "SkinPreference",
    "EpilepsyWarning",
    "CountdownOffset",
    "SpecialStyle",
    "WidescreenStoryboard",
    "SamplesMatchPlaybackRate",
)

EDITOR_LINES = (
    "Bookmarks",
    "DistanceSpacing",
    "BeatDivisor",
    "GridSize",
    "TimelineZoom",
)

METADATA_LINES = (
    "Title",
    "TitleUnicode",
    "Artist",
    "ArtistUnicode",
    "Creator",
    "Version",
    "Source",
    "Tags",
    "BeatmapID",
    "BeatmapSetID",
)

DIFFICULTY_LINES = (
    "HPDrainRate",
    "CircleSize",
    "OverallDifficulty",
    "ApproachRate",
    "SliderMultiplier",
    "SliderTickRate",
)


def parse_general_line(line: str) -> dict[str, Any]:
    line_split = line.split(": ")
    line_start = line_split[0]
    line_value = line_split[1]

    if line_start not in GENERAL_LINES:
        raise ValueError(f"Invalid line {line_start} found in beatmap")

    value: Any = {
        "AudioFilename": line_value,
        "AudioLeadIn": int(line_value),
        "AudioHash": line_value,
        "PreviewTime": int(line_value),
        "Countdown": line_value == "1",
        "SampleSet": SampleSet(line_value),  # TODO: enum or whatever
        "StackLeniency": float(line_value),
        "Mode": Mode(int(line_value)),
        "LetterboxInBreaks": line_value == "1",
        "StoryFireInFront": line_value == "1",
        "UseSkinSprites": line_value == "1",
        "AlwaysShowPlayfield": line_value == "1",
        "OverlayPosition": OverlayPosition(line_value),
        "SkinPreference": line_value,
        "EpilepsyWarning": line_value == "1",
        "CountdownOffset": int(line_value),
        "SpecialStyle": line_value == "1",
        "WidescreenStoryboard": line_value == "1",
        "SamplesMatchPlaybackRate": line_value == "1",
    }[line_start]

    return {line_start: value}


def parse_editor_line(line: str) -> dict[str, Any]:
    line_split = line.split(": ")
    line_start = line_split[0]
    line_value = line_split[1]

    if line_start not in EDITOR_LINES:
        raise ValueError(f"Invalid line {line_start} found in beatmap")

    value: Any = {
        "Bookmarks": [int(x) for x in line_value.split(",")],
        "DistanceSpacing": float(line_value),
        "BeatDivisor": int(line_value),
        "GridSize": int(line_value),
        "TimelineZoom": float(line_value),
    }[line_start]

    return {line_start: value}


def parse_metadata_line(line: str) -> dict[str, Any]:
    line_split = line.split(":")
    line_start = line_split[0]
    line_value = ":".join(line_split[1:])

    if line_start not in METADATA_LINES:
        raise ValueError(f"Invalid line {line_start} found in beatmap")

    value: Any = {
        "Title": line_value,
        "TitleUnicode": line_value,
        "Artist": line_value,
        "ArtistUnicode": line_value,
        "Creator": line_value,
        "Version": line_value,
        "Source": line_value,
        "Tags": line_value.split(" "),
        "BeatmapID": int(line_value),
        "BeatmapSetID": int(line_value),
    }[line_start]

    return {line_start: value}


def parse_difficulty_line(line: str) -> dict[str, Any]:
    line_split = line.split(":")
    line_start = line_split[0]
    line_value = line_split[1]

    if line_start not in DIFFICULTY_LINES:
        raise ValueError(f"Invalid line {line_start} found in beatmap")

    value: Any = {
        "HPDrainRate": float(line_value),
        "CircleSize": float(line_value),
        "OverallDifficulty": float(line_value),
        "ApproachRate": float(line_value),
        "SliderMultiplier": float(line_value),
        "SliderTickRate": float(line_value),
    }[line_start]

    return {line_start: value}


def parse_events_line(line: str) -> dict[str, Any]:
    if line.startswith("//"):  # comments
        return {}

    event_content = line.split(",")
    if not event_content:
        return {}

    event_data = {
        "filename": event_content[2].strip('"'),
        "x_offset": 0,
        "y_offset": 0,
    }

    if len(event_content) > 3:
        event_data["x_offset"] = int(event_content[3])

    if len(event_content) > 4:
        event_data["y_offset"] = int(event_content[4])

    if event_content == "0":
        return {"Background": Background(**event_data)}
    elif event_content[0] in ("Video", "1"):
        event_data["start_time"] = int(event_content[1])
        return {"Video": Video(**event_data)}
    elif event_content[0] in ("Breaks", "2"):
        event_data["start_time"] = int(event_content[1])
        event_data["end_time"] = int(event_content[2])
        return {"BreakTime": BreakTime(**event_data)}

    raise ValueError(f"Couldn't determine event type for {line}")


def parse_timing_points_line(line: str) -> dict[str, Any]:
    timing_content = line.split(",")
    if not timing_content:
        return {}

    offset = int(timing_content[0])
    beat_length = float(timing_content[1])
    time_signature = TimeSignature.SIMPLE_QUADRUPLE
    sample_set = SampleSet.NONE
    custom_sample_set = 0
    volume = 100
    inherited = True
    effects = Effect.NONE

    if len(timing_content) >= 3:
        time_signature = TimeSignature(int(timing_content[2]))

    if len(timing_content) >= 4:
        sample_set = SampleSet(int(timing_content[3]))

    if len(timing_content) >= 5:
        custom_sample_set = int(timing_content[4])

    if len(timing_content) >= 6:
        volume = int(timing_content[5])

    if len(timing_content) >= 7:
        inherited = int(timing_content[6]) == 1

    if len(timing_content) >= 8:
        effects = Effect(int(timing_content[7]))

    bpm = 0.0
    velocity = 0.0
    if inherited:
        bpm = round(60_000 / beat_length)
    else:
        velocity = abs(100 / beat_length)

    return {
        "TimingPoint": TimingPoint(
            offset=offset,
            beat_length=beat_length,
            time_signature=time_signature,
            sample_set=sample_set,
            custom_sample_set=custom_sample_set,
            volume=volume,
            inherited=inherited,
            effects=effects,
            bpm=bpm,
            velocity=velocity,
        )
    }


def parse_hit_objects_line(line: str) -> dict[str, Any]:  # TODO
    object_content = line.split(",")

    position = Vector2(
        x=float(object_content[0]),
        y=float(object_content[1]),
    )
    start_time = int(object_content[2])
    hit_type = HitObjectType(int(object_content[3]))

    combo_offset = (hit_type & HitObjectType.COMBO_OFFSET) >> 4
    hit_type &= ~HitObjectType.COMBO_OFFSET

    is_new_combo = bool(hit_type & HitObjectType.NEW_COMBO)
    hit_type &= ~HitObjectType.NEW_COMBO

    hit_sound = HitSoundType(int(object_content[4]))

    offset = 1 if hit_type & HitObjectType.HOLD else 0

    extra = object_content[-1].split(":")[offset:]
    extra_data: dict[str, Any] = {
        "sample_set": None,
        "addition_set": None,
        "custom_index": None,
        "volume": None,
        "sample_filename": None,
    }
    if ":" in object_content[-1]:
        extra_data |= {
            "sample_set": SampleSet(int(extra[0])),
            "addition_set": SampleSet(int(extra[1])),
        }

        if len(extra) > 2:
            extra_data["custom_index"] = int(extra[2])

        if len(extra) > 3:
            extra_data["volume"] = int(extra[3])

        if len(extra) > 4:
            extra_data["sample_filename"] = extra[4]

    hit_object: HitObject
    ...


def parse_section_line(section: str, line: str) -> Optional[dict[str, Any]]:
    section_function: Optional[Callable[[str], dict[str, Any]]] = {
        "general": parse_general_line,
        "editor": parse_editor_line,
        "metadata": parse_metadata_line,
        "difficulty": parse_difficulty_line,
        "events": parse_events_line,
        "timingpoints": parse_timing_points_line,
        "hitobjects": parse_hit_objects_line,
    }.get(section)
    if section_function is None:
        return None  # input is sanitised already, we just don't have a handler for this section

    line_data = section_function(line)
    if not line_data:  # also catches {}
        return None

    return line_data
