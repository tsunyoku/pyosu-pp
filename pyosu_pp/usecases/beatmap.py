from typing import Any, Callable, Optional

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
        "SampleSet": line_value,  # TODO: enum or whatever
        "StackLeniency": float(line_value),
        "Mode": int(line_value),  # TODO: enum or whatever
        "LetterboxInBreaks": line_value == "1",
        "StoryFireInFront": line_value == "1",
        "UseSkinSprites": line_value == "1",
        "AlwaysShowPlayfield": line_value == "1",
        "OverlayPosition": line_value,  # TODO: enum or whatever
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


def parse_events_line(line: str) -> dict[str, Any]:  # TODO
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
        return {"Background": event_data}
    elif event_content[0] in ("Video", "1"):
        event_data["start_time"] = int(event_content[1])
        return {"Video": event_data}  # TODO: video type?
    elif event_content[0] in ("Breaks", "2"):
        event_data["start_time"] = int(event_content[1])
        event_data["end_time"] = int(event_content[2])
        return {"BreakTime": event_data}  # TODO: break type?

    raise ValueError(f"Couldn't determine event type for {line}")


def parse_timing_points_line(line: str) -> dict[str, Any]:  # TODO
    ...


def parse_hit_objects_line(line: str) -> dict[str, Any]:  # TODO
    ...


def parse_section_line(section: str, line: str) -> Optional[dict[str, Any]]:  # TODO
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

    return section_function(line)
