#!/usr/bin/env python3
"""Convertit un chart JSON Psych / Forever Engine vers le format Chart([...], bpm).
Si vous voulez convertir un chart JSON FNF (base game), convertissez-le avec PSYCH ENGINE TO BASE GAME PORTER.py (il fait dans les deux sens) (cherchez sur Google j'ai le flemme)

Usage :
    python psych_to_numworks.py chart-hard.json -o export.py --name frostbite

Le format de sortie contient 18 entrées :
  0..3   notes opponent (left, down, up, right)
  4..7   notes player   (left, down, up, right)
  8..9   valeurs inutilisées (0)
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


LANE_COMMENTS = [
    "opponent left",
    "opponent down",
    "opponent up",
    "opponent right",
    "player left",
    "player down",
    "player up",
    "player right",
    "unused",
    "unused",
    "opponent sustain left",
    "opponent sustain down",
    "opponent sustain up",
    "opponent sustain right",
    "player sustain left",
    "player sustain down",
    "player sustain up",
    "player sustain right",
]


def get_song_data(data: dict[str, Any]) -> dict[str, Any]:
    """Accepte aussi bien un JSON FNF avec racine 'song' qu'un objet song direct."""
    song = data.get("song", data)
    if not isinstance(song, dict):
        raise ValueError("La propriété 'song' du JSON doit être un objet.")
    if not isinstance(song.get("notes"), list):
        raise ValueError("Impossible de trouver la liste 'song.notes' dans le JSON.")
    return song


def build_tempo_segments(song: dict[str, Any]) -> list[tuple[float, float, float]]:
    """Construit les intervalles (début_ms, fin_ms, BPM) à partir des sections."""
    bpm = float(song.get("bpm", 120))
    if bpm <= 0:
        raise ValueError(f"BPM initial invalide : {bpm}")

    cursor_ms = 0.0
    segments: list[tuple[float, float, float]] = []

    for section_index, section in enumerate(song["notes"]):
        if section.get("changeBPM", False):
            section_bpm = section.get("bpm")
            if section_bpm is None or float(section_bpm) <= 0:
                raise ValueError(
                    f"Section {section_index}: changeBPM est activé, "
                    "mais son BPM est absent ou invalide."
                )
            bpm = float(section_bpm)

        length_in_steps = float(section.get("lengthInSteps", 16))
        if length_in_steps < 0:
            raise ValueError(f"Section {section_index}: lengthInSteps négatif.")

        step_ms = (60000.0 / bpm) / 4.0
        end_ms = cursor_ms + length_in_steps * step_ms
        segments.append((cursor_ms, end_ms, bpm))
        cursor_ms = end_ms

    return segments


def bpm_at(time_ms: float, segments: list[tuple[float, float, float]], fallback: float) -> float:
    """Renvoie le BPM actif à un instant donné."""
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
    """Génère un tick tous les 1/16 de temps, sans inclure la tête du sustain."""
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
            raise ValueError(f"Intervalle de sustain invalide à {tick_ms} ms.")

        tick_ms += interval_ms
        if tick_ms > end_ms + 1e-7:
            break

        ticks.append(round(tick_ms))
        iterations += 1
        if iterations > 1_000_000:
            raise ValueError("Sustain anormalement long : arrêt de sécurité.")

    return ticks


def convert_chart(song: dict[str, Any]) -> tuple[list[Any], float, dict[str, int]]:
    """Convertit toutes les notes du chart vers les 18 canaux demandés."""
    initial_bpm = float(song.get("bpm", 120))
    if initial_bpm <= 0:
        raise ValueError(f"BPM initial invalide : {initial_bpm}")

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
                    f"Note invalide dans la section {section_index}, index {note_index}."
                )

            time_ms = float(note[0])
            note_data = int(note[1])

            # noteData=-1 correspond aux événements du chart (caméra, effets, etc.).
            if note_data < 0:
                stats["events_ignored"] += 1
                continue
            if note_data > 7:
                raise ValueError(
                    f"noteData={note_data} non pris en charge "
                    f"(section {section_index}, note {note_index})."
                )

            # Dans FNF, noteData 4..7 inverse le camp indiqué par mustHitSection.
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

    # Le tri rend le résultat chronologique, même si les notes JSON sont désordonnées.
    for index, channel in enumerate(channels):
        if index not in (8, 9):
            channel.sort()

    return channels, initial_bpm, stats


def format_channel(value: Any, index: int, indent: str = "    ", width: int = 96) -> str:
    """Formate une liste de temps sur plusieurs lignes si elle est longue."""
    comment = f"# {index} = {LANE_COMMENTS[index]}"
    if not isinstance(value, list):
        return f"{indent}{value}, {comment}"

    if not value:
        return f"{indent}[], {comment}"

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
    lines.append(f"{indent}], {comment}")
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
        description="Convertit un chart JSON FNF / Forever Engine vers le format Chart personnalisé."
    )
    parser.add_argument("input", type=Path, help="Fichier JSON source")
    parser.add_argument("-o", "--output", type=Path, help="Fichier de sortie (par défaut: <nom>_custom.py)")
    parser.add_argument("--name", help="Nom de la variable de chart, ex. frostbite_1")
    parser.add_argument("--chart-class", default="Chart", help="Nom de la fonction/classe wrapper (défaut: Chart)")
    args = parser.parse_args()

    try:
        with args.input.open("r", encoding="utf-8") as file:
            data = json.load(file)
        song = get_song_data(data)
        channels, bpm, stats = convert_chart(song)

        default_name = song.get("song") or args.input.stem
        name = safe_identifier(args.name or str(default_name).lower())
        chart_class = safe_identifier(args.chart_class)
        output_text = render_output(channels, bpm, name, chart_class)

        output_path = args.output or args.input.with_name(args.input.stem + "_custom.py")
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
