"""The `klatch` command: one sub-command per pipeline step."""

import argparse
import tomllib
from pathlib import Path

from klatch.mix import mix_episode


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="klatch", description="An automatic podcast pipeline."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("klatch.toml"),
        help="settings file (default: klatch.toml in the current folder)",
    )
    steps = parser.add_subparsers(dest="step", required=True)

    mix = steps.add_parser("mix", help="mix the per-person tracks into MP3 and Opus")
    mix.add_argument("episode", type=Path, help="the episode folder")

    args = parser.parse_args()
    # A missing settings file is fine: every setting has a default.
    config = tomllib.loads(args.config.read_text()) if args.config.exists() else {}

    mix_episode(args.episode, config)
