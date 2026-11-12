#!/usr/bin/env python3
"""Converts a FNF (old charting system) / Psych / Forever Engine JSON chart into the Chart([...], bpm) format.
If you wanna convert a FNF (new charting system) JSON chart, convert it to Psych Engine chart using PSYCH ENGINE TO BASE GAME PORTER.py (it does both ways) (do a Google research. I'm too lazy to include the link to the GitHub)

Use :
    python psych_to_numworks.py chart-hard.json -o export.py --name frostbite

The format have 18 entries:
  0..3   notes opponent (left, down, up, right)
  4..7   notes player   (left, down, up, right)
  8..9   unused values (0)
  10..13 sustains opponent
  14..17 sustains player
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

def get_song_data(data: dict[str, Any]) -> dict[str, Any]:
    song = data.get("song", data)
    if not isinstance(song, dict):
        raise ValueError("The 'song' property must be an object")
    if not isinstance(song.get("notes"), list):
        raise ValueError("Impossible to find song.note in the JSON file")
    return song


def build_tempo_segments(song: dict[str, Any]) -> list[tuple[float, float, float]]:
    bpm = float(song.get("bpm", 120))
    if bpm <= 0:
        raise ValueError(f"Invalid initial BPM: {bpm}")

    cursor_ms = 0.0
    segments: list[tuple[float, float, float]] = []

    for section_index, section in enumerate(song["notes"]):
        if section.get("changeBPM", False):
            section_bpm = section.get("bpm")
            if section_bpm is None or float(section_bpm) <= 0:
                raise ValueError(
                    f"Section {section_index}: changeBPM is toggled, "
                    "but its BPM is absent or invalid."
                )
            bpm = float(section_bpm)

        length_in_steps = float(section.get("lengthInSteps", 16))
        if length_in_steps < 0:
            raise ValueError(f"Section {section_index}: lengthInSteps is negative.")

        step_ms = (60000.0 / bpm) / 4.0
        end_ms = cursor_ms + length_in_steps * step_ms
        segments.append((cursor_ms, end_ms, bpm))
        cursor_ms = end_ms

    return segments


def bpm_at(time_ms: float, segments: list[tuple[float, float, float]], fallback: float) -> float:
    """Returns the active BPM at a given time"""
    for start_ms, end_ms, bpm in segments:
        if start_ms <= time_ms < end_ms:
            return bpm
    if segments and time_ms >= segments[-1][1]:
        return segments[-1][2]
    return fallback


def make_sustain_ticks(
    start_ms: float,
    duration_ms: float,
    segments: list[tuple[float, float, float]],
    fallback_bpm: float,
) -> list[int]:
    if duration_ms <= 1e-6:
        return []

    end_ms = start_ms + duration_ms
    tick_ms = start_ms
    ticks: list[int] = []

    # La limite protège aussi contre une éventuelle donnée BPM/section invalide.
    iterations = 0
    while True:
        bpm = bpm_at(tick_ms, segments, fallback_bpm)
        interval_ms = (60000.0 / bpm) / 4.0
        if interval_ms <= 0:
            raise ValueError(f"Invalid sustain interval at {tick_ms} ms.")

        tick_ms += interval_ms
        if tick_ms > end_ms + 1e-7:
            break

        ticks.append(round(tick_ms))
        iterations += 1
        if iterations > 1_000_000:
            raise ValueError("Sustain weirdly long: security stop")

    return ticks


def convert_chart(song: dict[str, Any]) -> tuple[list[Any], float, dict[str, int]]:
    """Converts all the notes in the 18 channels"""
    initial_bpm = float(song.get("bpm", 120))
    if initial_bpm <= 0:
        raise ValueError(f"Invalid initial BPM: {initial_bpm}")

    tempo_segments = build_tempo_segments(song)
    channels: list[Any] = [[] for _ in range(18)]
    channels[8] = 0
    channels[9] = 0

    stats = {"notes": 0, "sustains": 0, "events_ignored": 0}

    for section_index, section in enumerate(song["notes"]):
        must_hit = bool(section.get("mustHitSection", False))
        section_notes = section.get("sectionNotes", [])

        for note_index, note in enumerate(section_notes):
            if not isinstance(note, list) or len(note) < 2:
                raise ValueError(
                    f"Invalid note in the section {section_index}, index {note_index}."
                )

            time_ms = float(note[0])
            note_data = int(note[1])

            # noteData=-1 correspond aux événements du chart (caméra, effets, etc.).
            if note_data < 0:
                stats["events_ignored"] += 1
                continue
            if note_data > 7:
                raise ValueError(
                    f"noteData={note_data} not supported "
                    f"(section {section_index}, note {note_index})."
                )

            is_player = must_hit ^ (note_data >= 4)
            lane = note_data % 4
            head_channel = lane + (4 if is_player else 0)
            sustain_channel = head_channel + 10

            channels[head_channel].append(round(time_ms))
            stats["notes"] += 1

            sustain_ms = float(note[2]) if len(note) >= 3 else 0.0
            if sustain_ms > 1e-6:
                channels[sustain_channel].extend(
                    make_sustain_ticks(time_ms, sustain_ms, tempo_segments, initial_bpm)
                )
                stats["sustains"] += 1

    # orders ms
    for index, channel in enumerate(channels):
        if index not in (8, 9):
            channel.sort()

    return channels, initial_bpm, stats


def format_channel(value: Any, indent: str = "    ", width: int = 96) -> str:
    """Formats a ms list of seperated lines if it's too big"""
    if not isinstance(value, list):
        return f"{indent}{value}"

    if not value:
        return f"{indent}[]"

    lines = [f"{indent}["]
    current = indent + "    "
    line = current
    for i, number in enumerate(value):
        token = str(number) + (", " if i < len(value) - 1 else "")
        if len(line) + len(token) > width and line.strip():
            lines.append(line.rstrip())
            line = current
        line += token
    if line.strip():
        lines.append(line.rstrip())
    lines.append(f"{indent}]")
    return "\n".join(lines)


def safe_identifier(value: str) -> str:
    value = re.sub(r"\W+", "_", value.strip(), flags=re.UNICODE).strip("_")
    if not value:
        value = "converted_chart"
    if value[0].isdigit():
        value = "chart_" + value
    return value


def render_output(channels: list[Any], bpm: float, name: str, chart_class: str = "Chart") -> str:
    rendered_channels = [format_channel(value, i) for i, value in enumerate(channels)]
    bpm_text = str(int(bpm)) if bpm.is_integer() else repr(bpm)
    body = "\n".join(rendered_channels)
    return f"{name} = {chart_class}([\n{body}\n], {bpm_text})\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Converts a FNF (old charting system) / Psych / Forever Engine JSON chart into a Numworks Engine chart"
    )
    parser.add_argument("input", type=Path, help="Source JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Output file (default: <name>.py)")
    parser.add_argument("--name", help="Name of the variable of the chart, e. g. monochrome (i like this music :D)")
    args = parser.parse_args()

    try:
        with args.input.open("r", encoding="utf-8") as file:
            data = json.load(file)
        song = get_song_data(data)
        channels, bpm, stats = convert_chart(song)

        default_name = song.get("song") or args.input.stem
        name = safe_identifier(args.name or str(default_name).lower())
        chart_class = "Chart"
        output_text = render_output(channels, bpm, name, chart_class)

        output_path = args.output or args.input.with_name(args.input.stem + ".py")
        output_path.write_text(output_text, encoding="utf-8")

        print(f"Chart converti : {output_path}")
        print(f"BPM initial : {bpm:g}")
        print(f"Notes : {stats['notes']}")
        print(f"Sustains : {stats['sustains']}")
        print(f"Événements ignorés : {stats['events_ignored']}")
        return 0

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
