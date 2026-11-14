"""Mix step: per-person tracks in, one finished episode out (MP3 and Opus).

Reads   <episode>/tracks/<name>.<audio>   one file per person, all starting together
Writes  <episode>/episode.mp3 and <episode>/episode.opus

The file name without its ending is the person's identity: `henrik.flac` is henrik.
"""

import json
import subprocess
from pathlib import Path

TARGET_LUFS = -16.0  # Apple's loudness target for podcasts
TRUE_PEAK_DB = -1.0
# A track quieter than this holds no speech (muted or absent). Boosting it to the
# target would only amplify noise, so it is left out.
SILENT_BELOW_LUFS = -50.0
AUDIO_ENDINGS = {".flac", ".wav", ".ogg", ".opus", ".mp3", ".m4a", ".mka"}

# Every input is converted to this before anything is combined.
SAME_SHAPE = "aformat=sample_rates=48000:channel_layouts=stereo"


def run_ffmpeg(arguments: list[str]) -> str:
    """Run ffmpeg and return what it printed. Stop with its error if it fails."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-y", *arguments],
        capture_output=True,
        text=True,
        check=False,  # the failure is reported below, with ffmpeg's own message
    )
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg failed:\n{result.stderr[-2000:]}")
    return result.stderr


def read_loudness_report(ffmpeg_output: str) -> dict[str, float]:
    """Pick out the measurements that ffmpeg's loudnorm filter prints as JSON."""
    start = ffmpeg_output.rindex("{")
    end = ffmpeg_output.rindex("}") + 1
    report = json.loads(ffmpeg_output[start:end])
    return {
        name: float(value)
        for name, value in report.items()
        if name != "normalization_type"
    }


def measure_loudness(audio: Path) -> float:
    """Return how loud a file is overall, in LUFS. Silence gives minus infinity."""
    output = run_ffmpeg(
        ["-i", str(audio), "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    )
    return read_loudness_report(output)["input_i"]


def find_tracks(tracks_folder: Path) -> dict[Path, float]:
    """Return each track that contains speech, with its loudness."""
    tracks = {}
    for audio in sorted(tracks_folder.iterdir()):
        if audio.suffix.lower() not in AUDIO_ENDINGS:
            continue
        loudness = measure_loudness(audio)
        if loudness < SILENT_BELOW_LUFS:
            print(f"  {audio.stem}: silent, left out")
            continue
        print(f"  {audio.stem}: {loudness:.1f} LUFS")
        tracks[audio] = loudness
    return tracks


def build_filter_graph(
    track_gains: list[float],
    track_delays: list[float],
    intro_gain: float | None,
    outro_gain: float | None,
    final_filter: str,
) -> str:
    """Describe the whole mix to ffmpeg.

    Inputs are numbered in the order they are given to ffmpeg: the tracks first,
    then the intro, then the outro. Each gets its own volume change so everything
    sits at the same loudness, the tracks are laid on top of each other, and
    intro + talk + outro are joined end to end.
    """
    steps = []
    for number, (gain, delay) in enumerate(zip(track_gains, track_delays)):
        milliseconds = round(delay * 1000)
        steps.append(
            f"[{number}:a]{SAME_SHAPE},volume={gain:.2f}dB,"
            f"adelay={milliseconds}:all=1[track{number}]"
        )
    track_labels = "".join(f"[track{n}]" for n in range(len(track_gains)))
    # normalize=0: amix would otherwise turn every track down as more people join.
    steps.append(f"{track_labels}amix=inputs={len(track_gains)}:normalize=0[talk]")

    parts = ["[talk]"]
    next_input = len(track_gains)
    if intro_gain is not None:
        steps.append(f"[{next_input}:a]{SAME_SHAPE},volume={intro_gain:.2f}dB[intro]")
        parts.insert(0, "[intro]")
        next_input += 1
    if outro_gain is not None:
        steps.append(f"[{next_input}:a]{SAME_SHAPE},volume={outro_gain:.2f}dB[outro]")
        parts.append("[outro]")

    steps.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1[show]")
    steps.append(f"[show]{final_filter}")
    return ";".join(steps)


def mix_episode(episode: Path, config: dict) -> None:
    """Mix one episode folder into episode.mp3 and episode.opus."""
    tracks_folder = episode / "tracks"
    if not tracks_folder.is_dir():
        raise SystemExit(f"No tracks folder: {tracks_folder}")

    print("Measuring tracks")
    tracks = find_tracks(tracks_folder)
    if not tracks:
        raise SystemExit(f"No tracks with sound in {tracks_folder}")

    offsets = config.get("offsets", {})
    delays = [float(offsets.get(track.stem, 0)) for track in tracks]
    if min(delays) < 0:
        raise SystemExit("Offsets cannot be negative. Delay the other tracks instead.")

    inputs = list(tracks)
    gains: dict[str, float | None] = {"intro": None, "outro": None}
    for part in gains:
        if part in config:
            audio = Path(config[part])
            gains[part] = TARGET_LUFS - measure_loudness(audio)
            inputs.append(audio)

    input_arguments = []
    for audio in inputs:
        input_arguments += ["-i", str(audio)]

    def graph(final_filter: str) -> str:
        return build_filter_graph(
            [TARGET_LUFS - loudness for loudness in tracks.values()],
            delays,
            gains["intro"],
            gains["outro"],
            final_filter,
        )

    # Loudness is set in two passes: first measure the finished mix, then apply the
    # exact correction. One pass would have to guess and can make the level pump.
    target = f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK_DB}:LRA=20"

    print("Measuring the mix")
    output = run_ffmpeg(
        [
            *input_arguments,
            "-filter_complex",
            graph(f"{target}:print_format=json[out]"),
            "-map",
            "[out]",
            "-f",
            "null",
            "-",
        ]
    )
    measured = read_loudness_report(output)

    print("Writing episode.mp3 and episode.opus")
    correction = (
        f"{target}:linear=true"
        f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
        f":measured_LRA={measured['input_lra']}"
        f":measured_thresh={measured['input_thresh']}"
        f":offset={measured['target_offset']}"
    )
    run_ffmpeg(
        [
            *input_arguments,
            "-filter_complex",
            graph(f"{correction},asplit=2[mp3][opus]"),
            # 44.1 kHz and a constant bitrate: the form every old MP3 player reads.
            *["-map", "[mp3]", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "128k"],
            str(episode / "episode.mp3"),
            *["-map", "[opus]", "-ar", "48000", "-c:a", "libopus", "-b:a", "64k"],
            str(episode / "episode.opus"),
        ]
    )
    print(f"Done: {episode / 'episode.mp3'}")
