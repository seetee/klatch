# klatch

An automatic podcast pipeline that handles all the boring stuff for you!

*klatch: a gathering characterized usually by informal conversation.*

The full design is in [PLAN.md](PLAN.md). What works today is the first step: mixing.

## What the mix step does

It takes one audio file per person and produces a finished episode:

1. Measures how loud each person is and evens them out.
2. Leaves out tracks that are silent.
3. Lays the tracks on top of each other.
4. Puts intro music before and outro music after, if you have any.
5. Sets the result to podcast loudness (−16 LUFS) and writes `episode.mp3` and
   `episode.opus`.

## Folder layout

```
your-folder/
├── docker-compose.yml
├── klatch.toml            optional settings
├── assets/
│   ├── intro.mp3          optional
│   └── outro.mp3          optional
└── episodes/
    └── 2026-11-20/
        └── tracks/
            ├── kenneth.flac
            ├── henrik.flac
            └── joel.flac
```

- One file per person. The file name is who it is.
- All files must start at the same moment.
- FLAC, WAV, Ogg, Opus, MP3, M4A and MKA all work.

## Run it

You need Docker. Download [docker-compose.yml](docker-compose.yml) into your folder,
then:

```bash
docker compose run --rm klatch mix episodes/2026-11-20
```

The first run fetches the code and builds it, which takes a few minutes. The finished
files appear next to the `tracks` folder.

To get the newest code later:

```bash
docker compose build --no-cache
```

## Settings

`klatch.toml` is optional. Paths are relative to your folder.

```toml
intro = "assets/intro.mp3"
outro = "assets/outro.mp3"

# If one person's track runs early, delay it. Seconds, per file name.
[offsets]
henrik = 0.35
```

## Working on the code

Without Docker you need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/) and
ffmpeg.

```bash
uvx --from . klatch mix episodes/2026-11-20        # run from the source
PYTHONPATH=src python3 -m unittest discover tests  # run the tests
uvx ruff format . && uvx ruff check .              # format and lint
```
