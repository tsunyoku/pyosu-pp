from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping
from typing import Optional
from pyosu_pp.usecases import beatmap as beatmap_usecases

VALID_SECTIONS = (
    "general",
    "editor",
    "metadata",
    "difficulty",
    "events",
    "colours",
    "timingpoints",
    "hitobjects",
)


@dataclass(frozen=True)
class Beatmap:
    # [General]
    audio_filename: str
    audio_lead_in: int
    audio_hash: str
    preview_time: int
    countdown: bool
    sample_set: Any  # TODO: type
    stack_leniency: float
    mode: Any  # TODO
    letterbox_in_breaks: bool
    story_fire_in_front: bool
    use_skin_sprites: bool
    always_show_playfield: bool
    overlay_position: Any  # TODO: type
    skin_preference: str
    epilepsy_warning: bool
    countdown_offset: int
    special_style: bool
    widescreen_storyboard: bool
    samples_match_playback_rate: bool

    # [Editor]
    bookmarks: list[int]
    distance_spacing: float
    beat_divisor: float
    grid_size: int
    timeline_zoom: float

    # [Metadata]
    title: str
    title_unicode: str
    artist: str
    artist_unicode: str
    creator: str
    version: str
    source: str
    tags: list[str]
    beatmap_id: int
    beatmap_set_id: int

    # [Difficulty]
    hp: float
    cs: float
    od: float
    ar: float
    slider_multiplier: float
    slider_tick_rate: float

    # [Events]
    background: Optional[Any]  # TODO: type
    videos: list[Any]  # TODO: type
    break_times: list[Any] # TODO: type

    # [TimingPoints]
    timing_points: list[Any]  # TODO: type

    # TODO: colours?

    file_version: int
    min_bpm: float
    max_bpm: float

    # NOTE: this is either for single-bpm maps,
    # or in the case of multiple bpms it will take the most common BPM (same behaviour as osu! client)
    bpm: float

    hit_objects: list[Any]
    max_combo: int

    file_hash: str

    circle_count: int
    slider_count: int
    spinner_count: int

    play_time: int
    drain_time: int
    break_time: int

    @property
    def object_count(self) -> int:
        return self.circle_count + self.slider_count + self.spinner_count

    @property
    def beatmap_name(self) -> str:
        return f"{self.artist} - {self.title} [{self.version}] by {self.creator}"

    def __repr__(self) -> str:
        return f"osu! Beatmap: {self.beatmap_name}"

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, dict[str, Any]]) -> Beatmap:
        # TODO: type this mapping?

        return cls(
            audio_filename=mapping["general"]["AudioFilename"],
            audio_lead_in=mapping["general"]["AudioLeadIn"],
            audio_hash=mapping["general"]["AudioHash"],
            preview_time=mapping["general"]["PreviewTime"],
            countdown=mapping["general"]["Countdown"],
            sample_set=mapping["general"]["SampleSet"],
            stack_leniency=mapping["general"]["StackLeniency"],
            mode=mapping["general"]["Mode"],
            letterbox_in_breaks=mapping["general"]["LetterboxInBreaks"],
            story_fire_in_front=mapping["general"]["StoryFireInFront"],
            use_skin_sprites=mapping["general"]["UseSkinSprites"],
            always_show_playfield=mapping["general"]["AlwaysShowPlayfield"],
            overlay_position=mapping["general"]["OverlayPosition"],
            skin_preference=mapping["general"]["SkinPreference"],
            epilepsy_warning=mapping["general"]["EpilepsyWarning"],
            countdown_offset=mapping["general"]["CountdownOffset"],
            special_style=mapping["general"]["SpecialStyle"],
            widescreen_storyboard=mapping["general"]["WidescreenStoryboard"],
            samples_match_playback_rate=mapping["general"]["SamplesMatchPlaybackRate"],
            bookmarks=mapping["editor"]["Bookmarks"],
            distance_spacing=mapping["editor"]["DistanceSpacing"],
            beat_divisor=mapping["editor"]["BeatDivisor"],
            grid_size=mapping["editor"]["GridSize"],
            timeline_zoom=mapping["editor"]["TimelineZoom"],
            title=mapping["metadata"]["Title"],
            title_unicode=mapping["metadata"]["TitleUnicode"],
            artist=mapping["metadata"]["Artist"],
            artist_unicode=mapping["metadata"]["ArtistUnicode"],
            creator=mapping["metadata"]["Creator"],
            version=mapping["metadata"]["Version"],
            source=mapping["metadata"]["Source"],
            tags=mapping["metadata"]["Tags"],
            beatmap_id=mapping["metadata"]["BeatmapID"],
            beatmap_set_id=mapping["metadata"]["BeatmapSetID"],
            hp=mapping["difficulty"]["HPDrainRate"],
            cs=mapping["difficulty"]["CircleSize"],
            od=mapping["difficulty"]["OverallDifficulty"],
            ar=mapping["difficulty"]["ApproachRate"],
            slider_multiplier=mapping["difficulty"]["SliderMultiplier"],
            slider_tick_rate=mapping["difficulty"]["SliderTickRate"],
            ... # TODO: finish
        )

    @classmethod
    def from_str(cls, string: str) -> Beatmap:
        buffer = string.splitlines()
        if not buffer:
            raise ValueError("Beatmap string is empty")

        header_line = buffer.pop(0)
        if header_line[:17] != "osu file format v":
            raise ValueError("Beatmap string is not a valid osu file")

        file_hash = hashlib.md5(string.encode()).hexdigest()
        file_version = int(header_line[17:])

        beatmap_data: dict[str, dict[str, Any]] = defaultdict(dict)
        
        # some pre-defined sections
        beatmap_data["events"]["Videos"] = []
        beatmap_data["events"]["BreakTimes"] = []
        beatmap_data["misc"] = {"file_version": file_version, "file_hash": file_hash}

        current_section: str = ""
        while buffer:
            line = buffer.pop(0)
            if not line:
                continue

            if line[0] == "[" and line[-1] == "]":
                current_section = line[1:-1].lower()

                # next line, start handling actual section data
                continue

            if current_section not in VALID_SECTIONS:
                raise ValueError(f"Invalid section {current_section} found in beatmap")

            line_data = beatmap_usecases.parse_section_line(current_section, line)
            if line_data is not None:
                # special cases
                if "Video" in line_data:
                    beatmap_data[current_section]["Videos"].append(line_data.pop("Video"))
                elif "BreakTime" in line_data:
                    beatmap_data[current_section]["BreakTimes"].append(line_data.pop("BreakTime"))

                beatmap_data[current_section] |= line_data

        return cls.from_mapping(dict(beatmap_data))

    @classmethod
    def from_buffer(cls, buffer: bytes) -> Beatmap:
        raw_buffer = buffer.decode("utf-8-sig")
        return cls.from_str(raw_buffer)

    @classmethod
    def from_file(cls, path: str) -> Beatmap:
        with open(path, "r") as f:
            buffer = f.read()

        return cls.from_str(buffer)
