# klatch — project plan

An automatic podcast pipeline: a Friday 20:00–21:00 hangout, recorded per-person,
mixed with intro/outro music, rendered as a bobbing-cartoon video, and published to
YouTube, archive.org and a podcast RSS feed. It has to run without anyone tending it.

Regulars: Kenneth, Henrik, Joel, Robin, Jesper, Cornelia. Occasional drop-ins.

## Core architectural decision: the adapter contract

The output is cartoon avatars, so **the camera feed never reaches the pipeline** —
video is for the participants during the call, not for the product. The recorder only
needs audio, which means the call platform and the pipeline are separate decisions.

The pipeline's input contract:

> a directory of per-person audio files + a session start timestamp + a stable
> identity→track map

Everything downstream — mix, video, transcribe, publish — knows nothing about where
those came from. The call platform is a swappable ~200-line adapter.

Consequence: **build the pipeline first, against files dropped in by hand.** The
platform choice gets made by trying one on a real Friday, not by betting the project
on it up front.

## Call platform

|  | Video | Per-track audio | Bot + chat | Self-host |
|---|---|---|---|---|
| **LiveKit** | yes | yes — Track Egress, per-participant, no transcoding | yes — Python Agents SDK | yes, Docker, designed for it |
| Discord + Craig | yes | yes, battle-tested | yes, native | possible but heavy |
| Jitsi | yes | **no** | no | yes |
| Mumble | no | you write it | yes (pymumble) | trivial |

**Chosen target: LiveKit.** Track Egress exports individual participant tracks with
no transcoding (the cheapest recording path) and runs as its own container next to
`livekit-server`. The Python Agents SDK provides the bot. Cost: it's assembling a
product rather than installing one — the LiveKit Meet sample app is the starting UI.

**Jitsi is ruled out.** Jibri records a single mixed stereo stream; per-participant
recording has been an open request for years (jibri#523). Multitrack out of Jitsi
means writing a headless-Chrome bot that subscribes to each remote track — its
hardest path — and its chat has no real bot API either. Wrong two out of three.

**Discord + Craig is rejected but kept as a known fallback.** It is by far the least
code — video, chat, bots and per-speaker FLAC all native — but the call layer is as
proprietary as it gets and has a reputation for instability, and self-hosting Craig
is Postgres + Redis + Node + PM2 + Docker. If LiveKit proves too much work, this is
the escape hatch; the adapter contract makes the swap cheap.

**Mumble stays the audio-only fallback.** Best per-track audio story, no video.

## Open questions

### Recording

1. Where does the LiveKit stack run — the Proxmox box, or a VPS with a public IP?
   (WebRTC wants reachable ports and a TLS cert.)
2. Late joins, drops, rejoins mid-session — one track per person, or per connection?
3. Hard stop at 21:00 mid-sentence, or 21:00-or-empty-channel-whichever, with a cap?
   (`!extend` covers the good nights; see the bot.)
4. Recorder dies at 20:30 — publish the half, or hold it?

### Editing & publishing policy

5. Intro/outro music licensing. If it isn't ours or explicitly CC/royalty-free,
   Content ID will claim the video every week.
6. Trim dead air, or leave the raw hour?
7. Release slot for `publishAt` — Monday 08:00 is the assumed default.

### Things that can never change later — decide before episode 1

8. **The RSS feed URL.** Once Apple/Spotify have it, it's permanent.
9. Show name, artwork (square, 1400–3000px), category, explicit flag, owner email.
   Apple rejects feeds missing these.
10. archive.org identifier scheme (`klatch-2026-09-11`) and item license.
11. GUID scheme for episodes. Stable, non-URL, never reused.

### Consent & privacy

Everyone must know it's recorded and published publicly, and we need an agreed answer
for "please cut that bit" and "please take episode 12 down". The publish delay makes
this cheap; retroactive takedown from Apple's cache does not exist.

### Ops

12. Where do secrets live?
13. Keep the raw per-person tracks? ~350 MB/person/hour as WAV, ~half as FLAC.

## Settled decisions

- **Absent regulars are hidden**, not greyed out — a three-person episode should not
  be half empty boxes.
- **Silence is consent.** The bot posts its summary after rendering and publishes on
  schedule unless someone replies `!hold`.
- **Guest avatars recycle** from the generic pool.
- Whisper runs overnight. The GPU is modest, nothing is time-critical, publishing is
  Monday.

## Avatars

Config, not code:

```toml
[people.henrik]
avatar = "henrik.png"
slot = 2
```

Six named regulars with fixed slots. Guests draw from a pool of generic avatars in
join order, remembered per-identity in a JSON so a repeat guest keeps theirs; the pool
recycles. Absent regulars are not rendered. Guests occupy a second row that only
exists when it's occupied.

**The identity key must be stable** — LiveKit participant identity, never the display
name.

## The bot

The "works without me" lever. Not a command framework: a dict of `{name: callable}`
and a `startswith("!")` check is about twenty lines.

| Command | Effect |
|---|---|
| `!title <text>` | Set the episode title; stops the AI guessing |
| `!highlight <note>` | Stamp a timestamp with a note |
| `!cut` | Drop from the previous `!cut` to now |
| `!stop` | End the recording early |
| `!extend 30` | Keep going past 21:00 |
| `!cancel` | Bin the episode |
| `!hold` | Stop a rendered episode from publishing |
| `!status` | What is the pipeline doing |

`!highlight` is the highest-value command by a distance: free, human-curated markers
that become YouTube chapters, show-note anchors, and title fodder simultaneously.

After rendering, the bot posts: *"Ep 37 rendered, 58 min. Title: X. Notes: …
Publishing Monday 08:00 — reply `!hold` to stop it."*

## Show notes and titles

The multitrack architecture pays off twice: separate tracks mean **transcription gives
speaker labels for free — no diarization**.

- `faster-whisper` on the kitchen server, run overnight.
- One Claude API call over the transcript *plus the `!highlight` stamps* for a title
  shortlist and show notes. Human markers beat pure-AI summarization.
- Model `claude-opus-5` with `thinking: {type: "adaptive"}`. ~13k input tokens per
  episode at $5/$25 per MTok is roughly **$0.10 an episode**. Not worth self-hosting
  an LLM to avoid.

## Stack

| Job | Tool | Why not the alternative |
|---|---|---|
| Call + recording | **LiveKit** + Track Egress | Only self-hostable option with video, per-participant tracks and a bot SDK. |
| Bot | **LiveKit Python Agents SDK** | Same process family as the recorder adapter. |
| All audio/video muxing | **ffmpeg via subprocess** | No pydub, no moviepy. moviepy is slow and drags in a dependency swamp for what is one ffmpeg command. |
| Video frames | **Pillow → raw frames piped to ffmpeg stdin** | Not ffmpeg `overlay` expressions — with a segment list per person the filter string becomes unmaintainable. |
| Transcription | **faster-whisper**, overnight | Per-track input means no diarization step at all. |
| Notes & titles | **Claude API**, `claude-opus-5` | ~$0.10/episode. |
| YouTube | `google-api-python-client` + `google-auth-oauthlib` | `videos.insert` with `privacyStatus=private` + `publishAt` is exactly "queue for release". |
| archive.org | `internetarchive` | Official lib, 3 lines. |
| RSS | f-string or `xml.etree` template | Feed shape never changes. A library for one static template is a dependency we'd be pinning in 2029. |
| Hosting | archive.org serves the MP3, GitHub Pages serves the XML | Zero servers, zero cost, zero renewal. |
| Scheduling | **systemd timer**, not cron | `OnCalendar=Fri 20:00`, journald logs for free, `systemctl start klatch.service` reruns by hand. |
| State | A directory per episode + one JSON | No database, no queue. |
| Config | one TOML, `tomllib` | stdlib since 3.11. |

## Packaging

One image for the pipeline (adapter + post + publish), one volume for episodes, one
env file for secrets. The LiveKit stack gets its **own** compose file — don't merge
someone else's images into ours. On Proxmox: Docker inside one LXC or a small VM.

**"Anyone can host it" is not "anyone can take over publishing it."** The YouTube
OAuth token, the archive.org keys and the feed domain *are* the show's identity. The
real bus-factor fix is those secrets in a shared password manager and the feed domain
not owned by one person alone.

## The two things that will actually bite us

**Track sync.** Whatever the platform, participants only transmit while talking, so
per-user streams arrive as chunks with holes. Each chunk must be placed on an absolute
timeline and the gaps padded with silence, per user, from t=0. Get this wrong and
everyone drifts apart over an hour. Leave a per-track offset knob in the config —
clocks drift and it will need tuning.

**YouTube OAuth.** If the consent screen stays in *Testing* mode, the refresh token
dies every 7 days and the pipeline silently stops. Push the app to *Production*
(self-use needs no verification, just accept the unverified warning). The channel must
be phone-verified for videos over 15 minutes, and `selfDeclaredMadeForKids` is a
required field.

## Phasing — each phase ships something usable

- **Phase 0 — decisions.** The "never change later" list. No code.
- **Phase 1 — the pipeline, against hand-dropped files.** Mix, `loudnorm` to -16 LUFS,
  intro/outro concat → MP3. Record a test session however is easiest. *Deliberately
  before any platform work — it de-risks the platform choice to zero.*
- **Phase 2 — publish.** archive.org upload + RSS to Pages. This is the point where
  the project has delivered its actual value: a real, subscribable podcast.
- **Phase 3 — the recorder adapter.** Stand up LiveKit, wire Track Egress to the
  contract. Verify sync by clapping.
- **Phase 4 — the bot.** Commands, `!highlight`, the post-render summary.
- **Phase 5 — video.** Cartoons, bobbing, YouTube. Most work, least value, hence late.
- **Phase 6 — automation.** systemd timer + failure notification. After the pipeline
  has run manually 3–4 times, because you can't automate a process whose failure modes
  you haven't met yet.

The video-render trick: at 10–12 fps the frame is purely a function of (who's
speaking, bob phase). That's a handful of distinct images — render them once into a
dict, then the "renderer" is a lookup in a loop. 720p, mostly-static footage encodes
tiny and fast.

## Deliberately out of scope

No queue, no database, no web UI, no per-episode config schema, no command framework.
Add when there's more than one show.
