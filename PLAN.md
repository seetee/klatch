# klatch — project plan

An automatic podcast pipeline: a Friday 20:00–21:00 hangout, recorded per-person,
mixed with intro/outro music, rendered as a bobbing-cartoon video, and published to
YouTube, archive.org and a podcast RSS feed. It has to run without anyone tending it.

Regulars: Kenneth, Henrik, Joel, Robin, Jesper, Cornelia. Occasional drop-ins.
The show is in Swedish.

*Audited against current documentation on 2026-11-14. Claims marked **unverified**
have not been tested by anyone on this project yet.*

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
platform choice gets confirmed by trying it on a real Friday, not by betting the
project on it up front.

## Call platform

|  | Video | Per-track audio | Bot + chat | Self-host |
|---|---|---|---|---|
| **Jitsi** | yes, finished product | yes — [jitsi-multitrack-recorder](https://github.com/jitsi/jitsi-multitrack-recorder), wiring undocumented | chat is XMPP; bot **unverified** | yes, Docker |
| LiveKit | yes, but you assemble the UI | yes — one OGG per track, alignment undocumented | yes — Python SDK | yes, Docker |
| Discord + Craig | yes | **unverified** since mandatory call encryption | yes, native | possible but heavy |
| Mumble | no | you write it | yes (pymumble) | trivial |

**Chosen target: Jitsi**, with a one-evening test as the gate.

- It is a finished product: video grid, chat, mute buttons, phone support. Nothing to
  assemble.
- Nothing has to be split, because nothing is ever mixed. The Jitsi bridge forwards
  each person's audio as its own stream. The recorder gets a copy of each and writes
  one `.mka` file with one track per person.
- All tracks share one clock and gaps are filled by the recorder. That removes what
  used to be this plan's biggest risk (see "Track sync" below).
- The recorder is Jitsi's own, Apache-2.0, last commit 2026-07-21. It can run a script
  when a recording finishes, which is where the adapter hooks in.

**The gate — two things are unverified:**

1. *How a meeting gets sent to the recorder.* The recorder listens on a websocket
   (`:8989/record`) and the bridge has export code for it, but no user guide explains
   how to switch it on. It was found only by reading source.
2. *A chat bot.* Jitsi chat is XMPP underneath, so a bot should be able to join as a
   chat participant. Not tested.

If the test evening produces per-person tracks, Jitsi stays. If not, LiveKit takes
over and nothing else in this plan moves.

**LiveKit is the fallback.** Facts as of November 2026: `StartTrackEgress` is
deprecated in favour of `StartEgress` with a `MediaSource`; audio is always re-encoded
to stereo Opus in OGG; *auto egress* records every track when a room is created
([egress overview](https://docs.livekit.io/transport/media/ingress-egress/egress.md),
[track egress](https://docs.livekit.io/transport/media/ingress-egress/egress/track.md)).
Its docs do not say whether silence is padded or files are time-aligned, and there are
reports of dropped silence ([egress#142](https://github.com/livekit/egress/issues/142)).
Cost: it's assembling a product rather than installing one.

**Discord + Craig is no longer a known fallback.** Discord made end-to-end encryption
mandatory for calls in 2026
([Discord](https://discord.com/blog/every-voice-and-video-call-on-discord-is-now-end-to-end-encrypted)).
Whether Craig still records under it is unverified. Test once before relying on it.

**Mumble stays the audio-only fallback.** Best per-track audio story, no video.

## A Friday, for the people in the call

1. **19:55.** Open your personal link in a browser. No account. NetBird must be
   running (see "Network").
2. **You see each other** in the normal video grid, chat at the side. Video is only
   for you; it is never recorded.
3. **20:00.** A timer starts the recording. The bot writes "Recording" in the chat.
4. **During the hour**, talk. Anyone can type `!highlight <note>` or `!title <text>`.
5. **21:00.** Recording stops unless someone typed `!extend 30`. The bot confirms.
6. **Overnight** the pipeline mixes, transcribes, writes notes and builds the feed.
   The bot posts the summary. Silence means it publishes on Monday.

Two rules for participants:

- **Headphones.** Speakers leak everyone else's voice into your track, which ruins the
  per-person transcript.
- **What you hear is what gets recorded.** A choppy connection is baked into that
  person's track.

## Network

Everything runs at home on the Proxmox box. The call server is reachable only inside a
[NetBird](https://netbird.io/) private network; all regulars install the NetBird
client. Nothing in the call stack is exposed to the internet.

Consequences:

- **Guests must be added to NetBird before the Friday.** Phones need the NetBird app.
- **The private address still needs a real TLS certificate.** Browsers only allow
  microphone and camera on HTTPS. Use a real name such as `meet.samkvam.online` that
  points at the NetBird address, with a certificate issued through DNS.
- **The bridge must advertise its NetBird address**, or video and audio will not flow.
- **Publishing needs outbound internet only.** The feed is public and lives elsewhere.

Whether Jitsi's media runs well over NetBird is **unverified** and is part of the test
evening.

*Alternative, if someone other than Kenneth pays for it:* the call server on a small
EU VPS with a public address, so joining is just a link and guests need nothing
installed. The pipeline stays at home and fetches the recording.

## Open questions

### Recording

1. ~~Where does the stack run?~~ **Settled:** at home, over NetBird. See "Network".
2. Late joins, drops, rejoins mid-session — the recorder starts a new track after a
   gap longer than five minutes. The adapter must merge a person's tracks into one.
3. Hard stop at 21:00 mid-sentence, or 21:00-or-empty-room-whichever, with a cap?
   (`!extend` covers the good nights; see the bot.)
4. Recorder dies at 20:30 — publish the half, or hold it?
5. Does the Jitsi recorder work, and does it work over NetBird? (The gate.)

### Editing & publishing policy

6. Intro/outro music licensing. If it isn't ours or explicitly CC/royalty-free,
   Content ID will claim the video every week.
7. Trim dead air, or leave the raw hour?
8. Release slot — Monday 08:00 is the assumed default.

### Things that can never change later — decide before episode 1

9. ~~The RSS feed URL.~~ **Settled:** `https://podcast.samkvam.online/feed.xml`.
   Once Apple and Spotify have it, it's permanent.
10. Show name, artwork (square, 1400–3000px), category, explicit flag, owner email.
    Apple rejects feeds missing these.
11. archive.org identifier scheme (`klatch-2026-09-11`) and item license.
12. ~~GUID scheme.~~ **Settled:** see "Feed".

### Consent & privacy

Everyone must know it's recorded and published publicly, and we need an agreed answer
for "please cut that bit" and "please take episode 12 down". The publish delay makes
this cheap; retroactive takedown from Apple's cache does not exist.

### Ops

13. Where do secrets live?
14. ~~Keep the raw per-person tracks?~~ **Settled:** yes. They arrive as Opus, which is
    tens of megabytes per person per hour, not hundreds.
15. Which static-page service serves the feed repository under our domain?
16. Does the Podlove Web Player embed on a plain static page? (**Unverified.**)
17. Does the GPU hold `kb-whisper-large`? If not: `kb-whisper-medium`, or CPU overnight.

## Settled decisions

- **Absent regulars are hidden**, not greyed out — a three-person episode should not
  be half empty boxes.
- **Silence is consent.** The bot posts its summary after rendering and publishes on
  schedule unless someone replies `!hold`. Guests have not agreed to this rule, so the
  bot says one sentence about it when a non-regular joins.
- **Guest avatars recycle** from the generic pool.
- Whisper runs overnight. The GPU is modest, nothing is time-critical, publishing is
  Monday.
- **MP3 is the main audio file.** See "Feed".

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

**The identity key must be stable** — each regular gets a personal join link that
carries their identity. Never key on the display name; people change it.

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
that become podcast chapters, YouTube chapters, show-note anchors, and title fodder
simultaneously.

After rendering, the bot posts: *"Ep 37 rendered, 58 min. Title: X. Notes: …
Publishing Monday 08:00 — reply `!hold` to stop it."*

## Show notes and titles

The multitrack architecture pays off twice: separate tracks mean **transcription gives
speaker labels for free — no diarization**.

- `faster-whisper` with **`KBLab/kb-whisper-large`**, the National Library of Sweden's
  Swedish model, run overnight. On Swedish test sets its word error rate is
  5.4 / 4.1 / 5.2 against 7.8 / 9.5 / 11.3 for stock `whisper-large-v3`
  ([model card](https://huggingface.co/KBLab/kb-whisper-large), Apache-2.0).
- `vad_filter=True`. Per-person tracks are mostly silence, and Whisper invents text in
  silence.
- The transcript is saved as WebVTT with a speaker name on every line. That one file
  feeds the notes, the feed and the web player.
- One Claude API call over the transcript *plus the `!highlight` stamps* for a title
  shortlist and show notes. Human markers beat pure-AI summarization.
- Model `claude-opus-5-5` with `thinking: {type: "adaptive"}`. An hour of six people
  in Swedish is an estimated 20–25k input tokens; at $4/$20 per MTok that is roughly
  **$0.10–0.15 an episode**. Not worth self-hosting an LLM to avoid.

## Feed

`https://podcast.samkvam.online/feed.xml`, one template, built by the pipeline.

The rule: **a universal base that every app since 2005 understands, plus modern
elements that old apps silently skip.** Nothing modern replaces anything old.

| Layer | What goes in | Who reads it |
|---|---|---|
| Base | RSS 2.0, `atom:link rel="self"`, `itunes:*` (category, explicit, image, author, duration), `<enclosure>` with the MP3, `<guid>` | Everything. This is the required list in the Podcast Standards Project's [PSP-1](https://github.com/Podcast-Standards-Project/PSP-1-Podcast-RSS-Specification). |
| Identity | `podcast:guid`, `podcast:locked` | Protects the feed against hijacking and survives a move |
| Audio | `podcast:alternateEnclosure type="audio/opus"` | Podcasting 2.0 apps; others play the MP3 |
| Transcript | `podcast:transcript type="text/vtt"` | Apple shows speaker names from VTT ([Apple](https://podcasters.apple.com/support/5316-transcripts-on-apple-podcasts)); Podcasting 2.0 apps. Spotify: **unverified**. |
| Chapters | The `!highlight` list, written four ways: ID3 chapter frames inside the MP3, `podcast:chapters` JSON, Podlove [`psc:chapters`](https://podlove.org/simple-chapters/), and `00:00:00 Title` lines in the description | Apple reads the description, the tag and ID3 since iOS 26.2; YouTube reads the description; Podlove-aware apps read `psc:` |
| People | `podcast:person`, from who actually joined | Podcasting 2.0 apps |

**Why MP3 and not Ogg.** Apple Podcasts accepts only MP3 or AAC in feeds
([audio requirements](https://podcasters.apple.com/support/893-audio-requirements)),
and PSP-1 permits only MP3 and MPEG-4 in `<enclosure>`. MP3's patents have expired and
every player ever made reads it. Opus is the better codec, so it rides along as the
alternate.

**Encoding.** Each track is normalised before mixing; then the mix goes to −16 LUFS
with true peak at or below −1 dB (Apple's stated target). MP3 at 128 kbps constant
bitrate; Opus at 64 kbps. Both go to the same archive.org item.

**GUIDs.** `podcast:guid` is a UUIDv5 derived from the feed URL. Episode GUIDs are
`klatch-0001`, `klatch-0002`, … — never a URL, never reused.

**The site.** A small static site beside the feed, one page per episode, with the
[Podlove Web Player](https://github.com/podlove/podlove-ui) (MIT) and Podlove
Subscribe Button. Embedding on a plain static page is **unverified**.

**Left out on purpose:** `podcast:value` (payments), `podcast:liveItem`,
`podcast:funding`, `podcast:socialInteract`. Each needs an outside account or service.

## Stack

| Job | Tool | Why not the alternative |
|---|---|---|
| Call + recording | **Jitsi** + jitsi-multitrack-recorder | Finished product, one file with every track on a shared clock. LiveKit is the fallback. |
| Private network | **NetBird** | Nothing exposed to the internet. |
| Bot | **XMPP chat client**, library chosen in Phase 4 | Jitsi chat is XMPP. Unverified. |
| All audio/video muxing | **ffmpeg via subprocess** | No pydub, no moviepy. moviepy is slow and drags in a dependency swamp for what is one ffmpeg command. |
| Audio formats | **MP3** main, **Opus** alternate | MP3 is the only format every directory accepts. |
| Video frames | **Pillow → raw frames piped to ffmpeg stdin** | Not ffmpeg `overlay` expressions — with a segment list per person the filter string becomes unmaintainable. |
| Transcription | **faster-whisper** + `KBLab/kb-whisper-large`, overnight | Per-track input means no diarization step at all. Stock Whisper is markedly worse on Swedish. |
| Notes & titles | **Claude API**, `claude-opus-5-5` | ~$0.10–0.15/episode. |
| YouTube | RSS ingestion first, then `google-api-python-client` + `google-auth-oauthlib` | See "YouTube" under the two things that will bite us. |
| archive.org | `internetarchive` | Official lib, 3 lines. |
| RSS | f-string or `xml.etree` template | One template with the layers in "Feed". A library would be a dependency we'd be pinning in 2029. |
| Web player | **Podlove Web Player** | Open, built for podcasts, reads the same chapters and transcript. |
| Hosting | archive.org serves the audio; static pages from a git repo serve the feed and site at `podcast.samkvam.online` | Zero servers. Our own domain means the page service can be swapped. |
| Scheduling | **systemd timer**, not cron | `OnCalendar=Fri 20:00`, journald logs for free, `systemctl start klatch.service` reruns by hand. |
| State | A directory per episode + one JSON | No database, no queue. |
| Config | one TOML, `tomllib` | stdlib since 3.11. |

## Packaging

**Modules are pipeline steps.** One Python package, one command per step:

```
klatch ingest           # recorder output → the adapter contract
klatch mix              # normalise, mix, intro/outro → MP3 + Opus
klatch transcribe       # → VTT with speaker names
klatch notes            # → title shortlist, show notes
klatch feed             # → feed.xml, chapters, episode page
klatch publish-archive
klatch publish-youtube
klatch video
```

Each step reads and writes the episode directory and can be re-run on its own. Any
step can be replaced without touching the others.

**One `docker-compose.yml` is all you download.** Compose builds straight from the
repository ([Compose build reference](https://docs.docker.com/reference/compose-file/build/)):

```yaml
services:
  klatch:
    build: https://github.com/seetee/klatch.git#main
```

The Jitsi services and the recorder are upstream images named in the same file.
`docker compose up --build` fetches the code and builds it. Beside the compose file
live `.env` (secrets), `klatch.toml` (config) and `assets/` (avatars, music), plus one
volume for episodes. `#main` follows the latest commit; pin a tag once episodes are
public.

On Proxmox: Docker inside one LXC or a small VM.

**"Anyone can host it" is not "anyone can take over publishing it."** The YouTube
OAuth token, the archive.org keys and the feed domain *are* the show's identity. The
real bus-factor fix is those secrets in a shared password manager and the feed domain
not owned by one person alone.

## The three things that will actually bite us

**The recorder wiring.** The whole Jitsi choice rests on a recorder with no user
documentation. Until one test evening has produced a file with six tracks, it is a
hypothesis. This is why the pipeline is built first and the platform second.

**Track sync.** With Jitsi this is the recorder's job: one file, one clock, gaps
filled. Verify by clapping anyway, and keep a per-track offset knob in the config. If
we fall back to LiveKit, the old problem returns in full: separate files with holes
that must each be placed on an absolute timeline and padded with silence.

**YouTube.** Two parts.

- *OAuth.* If the consent screen stays in *Testing* mode, the refresh token dies every
  7 days and the pipeline silently stops. Push the app to *Production* (self-use needs
  no verification, just accept the unverified warning). The channel must be
  phone-verified for videos over 15 minutes, and `selfDeclaredMadeForKids` is a
  required field. (Not re-checked in the November audit.)
- *Uploads now default to public.* On 2026-11-02 YouTube dropped the rule that locked
  uploads from unaudited projects to private; if `privacyStatus` is missing, the video
  goes public immediately
  ([revision history](https://developers.google.com/youtube/v3/revision_history)).
  The upload code must refuse to send anything unless `privacyStatus == "private"`.

## Phasing — each phase ships something usable

- **Phase 0 — decisions.** The "never change later" list. No code.
- **Phase 1 — the pipeline, against hand-dropped files.** Normalise each track, mix,
  `loudnorm` to -16 LUFS, intro/outro concat → MP3 and Opus. Record a test session
  however is easiest. *Deliberately before any platform work.*
  **Status 2026-11-14:** `klatch mix` works and has mixed one real 73-minute
  two-person recording to −16.5 LUFS in about five minutes. The single
  `docker-compose.yml` building from the GitHub URL is confirmed working. Still
  missing: trimming dead air, `!cut`, and a session with all six.
- **Phase 2 — publish.** archive.org upload, the layered feed, the static site with
  the Podlove player. One automated check that every PSP-1 required element is in the
  feed. Then hand the feed to YouTube, which makes a static-image video per episode
  ([help](https://support.google.com/youtube/answer/13525207)). This is the point
  where the project has delivered its actual value: a real, subscribable podcast.
- **Phase 3 — the recorder.** The Jitsi test evening over NetBird. If it passes, write
  the adapter from `.mka` to the contract. If it fails, LiveKit.
- **Phase 4 — the bot.** Commands, `!highlight` → chapters, the post-render summary.
- **Phase 5 — video.** Cartoons, bobbing, uploaded to YouTube. Switch off YouTube's
  RSS ingestion at the same time, or every episode appears twice. Most work, least
  value, hence late.
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

Looked at in November 2026 and not used:

- **[Castopod](https://castopod.org/)** (AGPL-3.0) — would give the modern feed for
  free, but it is a PHP + MariaDB server to keep alive.
- **[Ennuicastr](https://github.com/Yahweasel/ennuicastr)** (ISC) — records lossless
  audio in each browser, the best design on paper, but has no documentation for
  running your own instance.
- **[Openside](https://github.com/rinkitadhana/openside)** (MIT) — needs Postgres,
  Redis, Cloudflare R2 and Clerk.
- **[Auphonic](https://auphonic.com/pricing)** — free multitrack is capped at
  20 minutes.
- **Podlove Publisher** — WordPress plugins. Only the player and button are used.
