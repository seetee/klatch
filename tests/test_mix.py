"""Checks the mix step end to end, using test tones made by ffmpeg."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from klatch.mix import find_tracks, measure_loudness, mix_episode, run_ffmpeg


def make_tone(target: Path, seconds: int, volume_db: int) -> None:
    run_ffmpeg(
        [
            *["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"],
            *["-af", f"volume={volume_db}dB", str(target)],
        ]
    )


def make_silence(target: Path, seconds: int) -> None:
    run_ffmpeg(["-f", "lavfi", "-i", "anullsrc", "-t", str(seconds), str(target)])


def length_in_seconds(audio: Path) -> float:
    result = subprocess.run(
        [
            *["ffprobe", "-v", "error", "-show_entries", "format=duration"],
            *["-of", "csv=p=0", str(audio)],
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout)


class MixTest(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.episode = Path(folder.name)
        self.tracks = self.episode / "tracks"
        self.tracks.mkdir()
        make_tone(self.tracks / "loud.flac", seconds=10, volume_db=0)
        make_tone(self.tracks / "quiet.flac", seconds=10, volume_db=-25)
        make_silence(self.tracks / "muted.flac", seconds=10)
        make_tone(self.episode / "intro.flac", seconds=2, volume_db=-10)
        make_tone(self.episode / "outro.flac", seconds=2, volume_db=-10)

    def test_silent_track_is_left_out(self) -> None:
        names = [track.stem for track in find_tracks(self.tracks)]
        self.assertEqual(names, ["loud", "quiet"])

    def test_mix_is_at_target_loudness_with_intro_and_outro(self) -> None:
        config = {
            "intro": str(self.episode / "intro.flac"),
            "outro": str(self.episode / "outro.flac"),
        }
        mix_episode(self.episode, config)

        for name in ("episode.mp3", "episode.opus"):
            episode = self.episode / name
            self.assertAlmostEqual(measure_loudness(episode), -16.0, delta=1.0)
            # 2 s intro + 10 s talk + 2 s outro
            self.assertAlmostEqual(length_in_seconds(episode), 14.0, delta=0.5)

    def test_one_track_and_no_music(self) -> None:
        (self.tracks / "quiet.flac").unlink()
        mix_episode(self.episode, {})
        self.assertTrue((self.episode / "episode.mp3").exists())

    def test_negative_offset_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            mix_episode(self.episode, {"offsets": {"loud": -1}})


if __name__ == "__main__":
    unittest.main()
