# klatch — project plan

An automatic podcast pipeline: a Friday 20:00–21:00 hangout, recorded per-person,
mixed with intro/outro music, rendered as a bobbing-cartoon video, and published to
YouTube, archive.org and a podcast RSS feed. It has to run without anyone tending it.

klatch is the tool. The show it is built for is **Samkvämspodden**.

Regulars: Kenneth, Henrik, Joel, Robin, Jesper, Cornelia. Occasional drop-ins.
The show is in Swedish.

*Audited against current documentation on 2026-11-14. Phase 0 decisions taken on
2026-11-15. Claims marked **unverified** have not been tested or looked up yet.*

## The show (Phase 0 decisions)

Decided by Kenneth on 2026-11-15. Items marked *provisional* wait for the rest of the
group or for something that does not exist yet.

| Topic | Decision |
|---|---|
| Name | **Samkvämspodden**. No podcast by that name in Apple's Swedish directory or a web search on 2026-11-15. A neighbour exists: "Samkväm med Henrik". |
| Tagline | "Välkommen in till köksbordet! Vi sitter bara å tjötar lite!" *Provisional.* |
| Description | "I Samkvämspodden träffas ett gäng vänner runt ett köksbord en fredagskväll och behandlar vad som dykt upp under den gångna veckan. Allt från cykeldäcket som läcker och den nya mobilen till hur minnen egentligen fungerar!" |
| Author | **Samkvämsgänget** |
| Names | Each person chooses how they appear; first name is the default. |
| Guests | The guest chooses; **"Gäst"** is the default. |
| Category | **Technology** (main), **Society & Culture** (second). No subcategories. |
| Explicit | **No.** No per-episode switch is built. |
| Type | **Episodic** |
| Language | `sv` |
| Owner email | `podcast@samkvam.online`. *Provisional; the mailbox does not exist yet.* |
| Numbering | Season = year. Episode = one running number from 1, never reset. Shown zero-padded: `e0037`. |
| Episode title | `e0037 - Titel`, in the one plain title field. *Provisional.* |
| Episode ID | `samkvamspodden-2026v47`. See "Episode IDs". **Permanent.** |
| Cover | Henrik makes it. A typographic placeholder until then: made 2026-11-15 as `assets/cover.png`, black `#0b0c07` on yellow `#e5cf77` in Cheque Black, from Samkväm's design system. One cover for everything, no per-episode art. |
| Avatars | Henrik makes them. Initial-in-a-circle placeholders until then. |
| Licence | **[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/deed.sv)**, as All In IT Radio had. `© 2026 Samkvämsgänget. CC BY-ND 4.0.` **Permanent per released episode.** |
| Domain | `samkvam.online`, owned by Kenneth at Loopia, yearly renewal. Henrik is the backup. |
| Feed and site | `https://podcast.samkvam.online/feed.xml`, served by GitHub Pages from `samkvam/samkvamspodden`. A move to Codeberg Pages later is one DNS change. |
| archive.org | A new account for the show, registered on the role address. Uploads: the mix (MP3 and Opus), transcript, chapters, cover. Never the raw tracks. |
| YouTube | The existing channel `youtube.com/@samkvam.online`, managed by Kenneth and Henrik. Comments on, as on the rest of the channel. |
| Directories | Every directory that will take the show. Henrik handles Apple. |
| Music | None yet. Henrik may make an intro from public domain music. Wanted for the first release, but nothing waits for it. |
| Opening | A recorded monologue over the music, which ducks under as the talk starts. |
| Consent | Joining is the yes, for regulars and guests alike. See "Consent and the stop window". |
| Notes and titles | No AI. Written from what people type during the call. See "Show notes and titles". |
| Raw tracks | Kept until cartoon videos have been made from them. Removed by hand after that; no automatic deletion. |
| Release | Stop window closes **Sunday 20:00**. Released **Monday 07:42**. |
| A Friday without a recording | Nothing is published and nothing is announced. |
| Secrets | Bitwarden, where Kenneth and Henrik already share. |

The recording from 2026-11-04 (Kenneth and Henrik, 73 minutes) is **not** a
Samkvämspodden episode. It is a farewell to All In IT Radio and goes by hand to
archive.org and the old feed. klatch does not handle it.

What Henrik needs for the cover: square, 3000×3000 pixels preferred (1400×1400 is the
minimum), PNG or JPG, no transparency
([Apple's show cover specs](https://podcasters.apple.com/support/5514-show-cover-template)),
and readable at thumbnail size.

### Episode IDs

`samkvamspodden-2026v47`. The same string is the episode's `<guid>` in the feed, its
address at archive.org and the name of its folder, so it is never stored anywhere; it
is read off the folder.

- **Recording week, not publishing week.**
- **The week calendar's year.** A recording on Friday 1 January 2027 is `2026v53`,
  because that day belongs to week 53 of 2026.
- **Always two digits for the week**: `2027v07`.
- **The first episode of a week has no letter.** Further ones get `b`, `c`, `d`, …:
  `2026v47b`.

`podcast:guid`, the ID of the show itself, is a UUIDv5 derived from the feed URL.

### Consent and the stop window

- **Joining is the yes.** There is no separate sign-off.
- **The bot shows each person a notice when they join**, whenever that is, so late
  joiners see it too. It says: this is recorded and published, under which licence,
  what name you will appear under, and that you can say stop until Sunday 20:00.
- **Nothing leaves the home server before the window closes.** The episode is mixed,
  transcribed and prepared on Friday night, and stays there.
- **Until Sunday 20:00** anyone who was in the episode can say stop, to Kenneth or
  Henrik, with no reason given. A stop holds the whole episode; it is then cut and
  released, or binned.
- **A private listening link** in Saturday's summary, reachable only inside NetBird,
  lets every participant hear the result before the window closes.
- **After Sunday 20:00 it is final.** Uploads start then.

What can be withdrawn after release: the feed entry, the YouTube video and the
archive.org item can all be removed by us (archive.org lets the uploading account
[remove its own items](https://help.archive.org/help/removing-your-item-pages-from-archive-org/)).
Copies that subscribers have already downloaded cannot. A friend who asks for an old
episode to be taken down is handled by being a friend, not by a rule.

### Still to do before episode 1

1. Tell the other regulars about the project.
2. Create the mailbox or forwarding for `podcast@samkvam.online`. LoopiaDNS may not
   include mail (**unverified**).
3. Register the archive.org account on that address; put its keys in Bitwarden.
4. Create the repository `samkvam/samkvamspodden` and point `podcast.samkvam.online`
   at GitHub Pages.
5. Henrik: cover, avatars, intro.

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

## A week, for the people in the call

1. **Friday 19:55.** Open your personal link in a browser. No account. NetBird must be
   running (see "Network"). The bot shows you the notice.
2. **You see each other** in the normal video grid, chat at the side. Video is only
   for you; it is never recorded.
3. **20:00.** The bot counts down in the chat and the recording starts.
4. **During the hour**, talk. Anyone can type `!highlight <note>` or `!title <text>`.
5. **21:00.** Recording stops unless someone typed `!extend 30`. The bot confirms.
6. **Overnight** the pipeline mixes, transcribes and prepares the episode on the home
   server.
7. **Saturday.** Kenneth and Henrik get the summary, with the private listening link.
8. **Sunday 20:00.** The stop window closes and the uploads start.
9. **Monday 07:42.** The episode is released.

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
- **The private listening link** is served from the same box, inside NetBird only.

Whether Jitsi's media runs well over NetBird is **unverified** and is part of the test
evening.

*Alternative, if someone other than Kenneth pays for it:* the call server on a small
EU VPS with a public address, so joining is just a link and guests need nothing
installed. The pipeline stays at home and fetches the recording.

## Open questions

1. Late joins, drops, rejoins mid-session — the recorder starts a new track after a
   gap longer than five minutes. The adapter must merge a person's tracks into one.
2. Hard stop at 21:00 mid-sentence, or 21:00-or-empty-room-whichever, with a cap?
   (`!extend` covers the good nights; see the bot.)
3. Recorder dies at 20:30 — publish the half, or hold it?
4. Does the Jitsi recorder work, and does it work over NetBird? (The gate.)
5. Trim dead air, or leave the raw hour?
6. Does the Podlove Web Player embed on a plain static page? (**Unverified.**)
7. Which transcription model size runs acceptably overnight on the home server?
   `sixseven-subtitles` runs `kb-whisper-small` on the processor; start there.
8. Should Henrik have access to the raw tracks on the home server, as the backup?
9. Whose Google account issues the YouTube upload key, and does a key from a channel
   manager work as well as one from the owner? (Phase 5. **Unverified.**)
10. May the episode number run on across seasons? The feed rules only say both must be
    whole numbers above zero
    ([PSP-1](https://github.com/Podcast-Standards-Project/PSP-1-Podcast-RSS-Specification));
    how apps display it is **unverified**.

## Settled decisions

- **Absent regulars are hidden**, not greyed out — a three-person episode should not
  be half empty boxes.
- **Silence is consent, inside a window.** See "Consent and the stop window".
- **Guest avatars recycle** from the generic pool.
- Transcription runs overnight. Nothing is time-critical.
- **MP3 is the main audio file.** See "Feed".

## Avatars and people

Config, not code:

```toml
[people.henrik]
name = "Henrik"        # how this person appears in transcript, notes and credits
avatar = "henrik.png"
slot = 2
```

Six named regulars with fixed slots. Guests draw from a pool of generic avatars in
join order, remembered per-identity in a JSON so a repeat guest keeps theirs; the pool
recycles. Absent regulars are not rendered. Guests occupy a second row that only
exists when it's occupied. A guest's chosen name is remembered the same way, so a
returning guest is asked once.

**The identity key must be stable** — each regular gets a personal join link that
carries their identity. Never key on the display name; people change it.

The spoken audio is not affected by any of this. If someone says a guest's name on the
recording, only a cut removes it.

## The bot

The "works without me" lever. Not a command framework: a dict of `{name: callable}`
and a `startswith("!")` check is about twenty lines.

| Command | Effect |
|---|---|
| `!title <text>` | Set the episode title |
| `!highlight <note>` | Stamp a timestamp with a note |
| `!highlight * <note>` | The same, and make it a chapter |
| `!cut` | Drop from the previous `!cut` to now |
| `!stop` | End the recording early |
| `!extend 30` | Keep going past 21:00 |
| `!cancel` | Bin the episode |
| `!status` | What is the pipeline doing |

Besides commands, the bot does three things in the call: shows the notice to each
person who joins, asks a new guest what they want to be called, and counts down to
20:00.

`!highlight` is the highest-value command by a distance: free, human-curated markers
that become podcast chapters, YouTube chapters and the show notes.

**Between Fridays there is no chat.** A Jitsi call's chat disappears when the call
ends. So for now the summary goes by email to Kenneth and Henrik, and a stop or a cut
is asked of one of them, who holds the episode by hand. A klatch bot in Delta Chat,
where the group is moving, is a later addition; Delta Chat runs on email, so the same
summary message carries over.

## Show notes and titles

The multitrack architecture pays off: separate tracks mean **transcription gives
speaker labels for free — no diarization**.

**Transcription** runs at home and nothing is sent anywhere.

- `faster-whisper` with a **KB-Whisper** model, the National Library of Sweden's
  Swedish models. On Swedish test sets `kb-whisper-large` has a word error rate of
  5.4 / 4.1 / 5.2 against 7.8 / 9.5 / 11.3 for stock `whisper-large-v3`
  ([model card](https://huggingface.co/KBLab/kb-whisper-large), Apache-2.0).
- `vad_filter=True`. Per-person tracks are mostly silence, and Whisper invents text in
  silence.
- Borrow from `sixseven-subtitles`, which already transcribes these voices: its
  settings for detecting speech, its splitting of long lines at pauses, and its `[?]`
  mark on uncertain words so they can be fixed by hand before Sunday. Not its
  word-by-word timing engine; a transcript needs a time per line only.
- The transcript is saved as WebVTT with a speaker name on every line.

**Notes and titles** follow the method of `kuliss notes`, with **no AI**.

- The pipeline writes an `episode.md` per episode in the layout known from Kuliss:
  `**Titel:**`, `**Blurb:**`, `#### Noteworthy`, `#### Kapitel`.
- It is filled from what people typed during the call: `!title`, `!highlight`, and
  `!highlight *` for chapters.
- Kenneth or Henrik can edit the file by hand until Sunday 20:00. The feed step reads
  it.
- Saturday's summary says what is missing, as Kuliss does: "no title, 4 notes,
  2 chapters".
- With no title at all, the episode is released as just `e0037`.

`klatch notes` stays its own step, so a later version can fill a missing title or blurb
with Claude or a model on the home server without touching anything else. If it ever
sends the transcript out, it must run after the stop window closes.

## Feed

`https://podcast.samkvam.online/feed.xml`, one template, built by the pipeline and
pushed to `samkvam/samkvamspodden`.

The rule: **a universal base that every app since 2005 understands, plus modern
elements that old apps silently skip.** Nothing modern replaces anything old.

| Layer | What goes in | Who reads it |
|---|---|---|
| Base | RSS 2.0, `atom:link rel="self"`, `itunes:*` (category, explicit, image, author, duration, season, episode), `<enclosure>` with the MP3, `<guid>` | Everything. This is the required list in the Podcast Standards Project's [PSP-1](https://github.com/Podcast-Standards-Project/PSP-1-Podcast-RSS-Specification). |
| Identity | `podcast:guid`, `podcast:locked` | Protects the feed against hijacking and survives a move |
| Audio | `podcast:alternateEnclosure type="audio/opus"` | Podcasting 2.0 apps; others play the MP3 |
| Transcript | `podcast:transcript type="text/vtt"` | Apple shows speaker names from VTT ([Apple](https://podcasters.apple.com/support/5316-transcripts-on-apple-podcasts)); Podcasting 2.0 apps. Spotify: **unverified**. |
| Chapters | The chapter list, written four ways: ID3 chapter frames inside the MP3, `podcast:chapters` JSON, Podlove [`psc:chapters`](https://podlove.org/simple-chapters/), and `00:00:00 Title` lines in the description | Apple reads the description, the tag and ID3 since iOS 26.2; YouTube reads the description; Podlove-aware apps read `psc:` |
| People | `podcast:person`, from who actually joined, under their chosen names | Podcasting 2.0 apps |

**Why MP3 and not Ogg.** Apple Podcasts accepts only MP3 or AAC in feeds
([audio requirements](https://podcasters.apple.com/support/893-audio-requirements)),
and PSP-1 permits only MP3 and MPEG-4 in `<enclosure>`. MP3's patents have expired and
every player ever made reads it. Opus is the better codec, so it rides along as the
alternate.

**Encoding.** Each track is normalised before mixing; then the mix goes to −16 LUFS
with true peak at or below −1 dB (Apple's stated target). MP3 at 128 kbps constant
bitrate; Opus at 64 kbps. Both go to the same archive.org item.

**The opening.** The intro file holds the monologue and the music, with the music
already faded low at its end. One setting says how many seconds of the intro's end
overlap the start of the talk. Built when there is an intro to test with.

**Music and the licence.** An episode under CC BY-ND can carry music that is our own,
CC0 or CC BY. Share-alike (BY-SA) and non-commercial music probably cannot sit inside
it (reasoned from the licence texts, **unverified**). "Public domain" applies to a
composition and to a particular recording separately; a self-made performance of an
old piece is safe, an old recording may not be.

**The site.** A small static site beside the feed, one page per episode, with the
[Podlove Web Player](https://github.com/podlove/podlove-ui) (MIT) and Podlove
Subscribe Button. Embedding on a plain static page is **unverified**.

**Left out on purpose:** `podcast:value` (payments), `podcast:liveItem`,
`podcast:funding`, `podcast:socialInteract`, a separate `itunes:title`, per-episode
artwork. Add when wanted.

## Stack

| Job | Tool | Why not the alternative |
|---|---|---|
| Call + recording | **Jitsi** + jitsi-multitrack-recorder | Finished product, one file with every track on a shared clock. LiveKit is the fallback. |
| Private network | **NetBird** | Nothing exposed to the internet. |
| Bot | **XMPP chat client**, library chosen in Phase 4 | Jitsi chat is XMPP. Unverified. |
| All audio/video muxing | **ffmpeg via subprocess** | No pydub, no moviepy. moviepy is slow and drags in a dependency swamp for what is one ffmpeg command. |
| Audio formats | **MP3** main, **Opus** alternate | MP3 is the only format every directory accepts. |
| Video frames | **Pillow → raw frames piped to ffmpeg stdin** | Not ffmpeg `overlay` expressions — with a segment list per person the filter string becomes unmaintainable. |
| Transcription | **faster-whisper** + KB-Whisper, overnight | Per-track input means no diarization step at all. Stock Whisper is markedly worse on Swedish. |
| Notes & titles | **`episode.md`**, filled from chat marks, editable by hand | No AI: nothing leaves the house, no key, no cost. |
| YouTube | RSS ingestion first, then `google-api-python-client` + `google-auth-oauthlib` | See "YouTube" under the things that will bite us. |
| archive.org | `internetarchive` | Official lib, 3 lines. |
| RSS | f-string or `xml.etree` template | One template with the layers in "Feed". A library would be a dependency we'd be pinning in 2029. |
| Web player | **Podlove Web Player** | Open, built for podcasts, reads the same chapters and transcript. |
| Hosting | archive.org serves the audio; GitHub Pages serves the feed and site from `samkvam/samkvamspodden` at `podcast.samkvam.online` | Zero servers. Our own domain means the page service can be swapped. |
| Scheduling | **systemd timers**, not cron | Friday 20:00 record, Sunday 20:00 upload, Monday 07:42 release. journald logs for free, `systemctl start` reruns by hand. |
| State | A directory per episode | No database, no queue. |
| Config | one TOML, `tomllib` | stdlib since 3.11. |
| Secrets | **Bitwarden** for the humans, one env file for the pipeline | Kenneth and Henrik already share there. |

## Packaging

**Modules are pipeline steps.** One Python package, one command per step:

```
klatch ingest           # recorder output → the adapter contract
klatch mix              # normalise, mix, intro/outro → MP3 + Opus
klatch transcribe       # → VTT with speaker names
klatch notes            # → episode.md from the chat marks
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
`docker compose run --rm klatch <step>` fetches the code and builds it on first use.
Beside the compose file live `.env` (secrets), `klatch.toml` (config) and `assets/`
(avatars, music), plus the episodes folder. `#main` follows the latest commit; pin a
tag once episodes are public.

On Proxmox: Docker inside one LXC or a small VM.

**"Anyone can host it" is not "anyone can take over publishing it."** The YouTube
channel, the archive.org keys and the feed domain *are* the show's identity. Kenneth
owns the domain and the project does not continue without him; Henrik is the backup
for everything else, through the shared Bitwarden and the `samkvam` organisation on
GitHub.

## The three things that will actually bite us

**The recorder wiring.** The whole Jitsi choice rests on a recorder with no user
documentation. Until one test evening has produced a file with six tracks, it is a
hypothesis. This is why the pipeline is built first and the platform second.

**Track sync.** With Jitsi this is the recorder's job: one file, one clock, gaps
filled. Verify by clapping anyway, and keep a per-track offset knob in the config. If
we fall back to LiveKit, the old problem returns in full: separate files with holes
that must each be placed on an absolute timeline and padded with silence.

**YouTube.** The episodes go on an existing channel with four years of videos, so a
mistake costs more than on a fresh one.

- *Narrowest permission.* The upload key asks only for what uploading needs, so it
  cannot edit or delete what is already on the channel.
- *Nothing is uploaded before Sunday 20:00.* The video then goes up as private with
  `publishAt` set to Monday 07:42.
- *Uploads now default to public.* On 2026-11-02 YouTube dropped the rule that locked
  uploads from unaudited projects to private; if `privacyStatus` is missing, the video
  goes public immediately
  ([revision history](https://developers.google.com/youtube/v3/revision_history)).
  The upload code must refuse to send anything unless `privacyStatus == "private"`.
- *OAuth.* If the consent screen stays in *Testing* mode, the refresh token dies every
  7 days and the pipeline silently stops. Push the app to *Production* (self-use needs
  no verification, just accept the unverified warning). `selfDeclaredMadeForKids` is a
  required field. (Not re-checked in the November audit.)
- *The audience.* Subscribers who came for let's plays get an hour of talk every
  Monday. The podcast is a playlist on the channel, marked as a podcast.

## Phasing — each phase ships something usable

- **Phase 0 — decisions.** **Done 2026-11-15**, see "The show". What remains is the
  to-do list there.
- **Phase 1 — the pipeline, against hand-dropped files.** Normalise each track, mix,
  `loudnorm` to -16 LUFS, intro/outro concat → MP3 and Opus.
  **Status 2026-11-14:** `klatch mix` works and has mixed one real 73-minute
  two-person recording to −16.5 LUFS in about five minutes; the result sounds right.
  The single `docker-compose.yml` building from the GitHub URL is confirmed working.
  Still missing: the intro overlap, trimming dead air, `!cut`, and a session with all
  six.
- **Phase 2 — publish.** The placeholder cover, `klatch notes` writing `episode.md`,
  archive.org upload, the layered feed, the static site with the Podlove player. One
  automated check that every PSP-1 required element is in the feed. Then a checklist
  of directories to register with, each with a verified link, Podcast Index first; and
  hand the feed to YouTube, which makes a static-image video per episode
  ([help](https://support.google.com/youtube/answer/13525207)). This is the point
  where the project has delivered its actual value: a real, subscribable podcast.
  Registration needs one real episode, so it waits for the first group Friday.
- **Phase 3 — the recorder.** The Jitsi test evening over NetBird. If it passes, write
  the adapter from `.mka` to the contract. If it fails, LiveKit.
- **Phase 4 — the bot.** The notice at joining, the guest's name, the countdown, the
  commands, `!highlight` → chapters, the Saturday summary by email with the private
  listening link.
- **Phase 5 — video.** Cartoons, bobbing, uploaded to YouTube. Switch off YouTube's
  RSS ingestion at the same time, or every episode appears twice. Most work, least
  value, hence late. Raw tracks may be removed once their video exists.
- **Phase 6 — automation.** The three timers + failure notification. After the
  pipeline has run manually 3–4 times, because you can't automate a process whose
  failure modes you haven't met yet.

Later, in no order:

- A klatch bot in Delta Chat, so the summary and a stop live in the group's own chat.
- A missing title or blurb filled by Claude or a local model, after the stop window.
- A person's own video (Kenneth's planned vtuber rig) replacing their cartoon. This
  extends the adapter contract with an optional video file per person.

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
- **Kuliss and sixseven-subtitles as dependencies** — their methods are borrowed,
  their code is not: both are built around Kdenlive and video.
