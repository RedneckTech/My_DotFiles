---
name: youtube-transcript-collection
description: "Use when bulk-collecting YouTube transcripts from playlists."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [YouTube, Transcripts, Playlists, Media]
    related_skills: [youtube-content]
---

# YouTube Transcript Collection (bulk / playlists / private)

## When to use

Use when the task is COLLECTING many transcripts at once — a playlist, a channel's uploads, or a set of video URLs — rather than transforming a single transcript into a summary/thread/blog (that is the `youtube-content` skill). This skill covers enumeration, authentication for private lists, batch fetching, and saving to disk.

## Core principle

Two different tools, two different auth requirements. Split the job:

- **Enumerating a playlist's video IDs** requires auth when the list is private/unlisted. Use `yt-dlp` with the user's browser cookies.
- **Fetching a transcript** needs no auth at all — `youtube-transcript-api` works even for videos inside a private playlist, once you have the video ID.

Do not try to download subtitles with `yt-dlp --write-auto-subs` / `--sub-langs`: YouTube's current player n-challenge bot check breaks that path ("nsig extraction failed" / "Did not get any data blocks" / "The page needs to be reloaded"), and it burns time. yt-dlp is for enumeration/metadata only; youtube-transcript-api is for transcript text.

## Setup

System pip is PEP 668 locked (externally-managed), so install into a scratch venv rather than raw `pip install`:

```bash
python3 -m venv "$HOME/.hermes/cache/scratch/ytvenv"
"$HOME/.hermes/cache/scratch/ytvenv/bin/pip" install -U yt-dlp youtube-transcript-api
YT="$HOME/.hermes/cache/scratch/ytvenv/bin/yt-dlp"
PY="$HOME/.hermes/cache/scratch/ytvenv/bin/python"
```

Keep yt-dlp current — versions older than ~a year fail on today's YouTube player (nsig/n-challenge errors). If enumeration returns incomplete/empty data, upgrade yt-dlp first.

## Workflow

1. **Enumerate** the video IDs + titles. For a public playlist, `--flat-playlist --print` works unauthenticated. For a private/unlisted list, add `--cookies-from-browser`:

```bash
"$YT" --flat-playlist --print "%(id)s|%(title)s" "https://www.youtube.com/playlist?list=LIST_ID"
# private/unlisted:
"$YT" --cookies-from-browser firefox --flat-playlist --print "%(id)s|%(title)s" "https://www.youtube.com/playlist?list=LIST_ID"
```

2. **Batch fetch** each transcript with youtube-transcript-api (or the `youtube-content` skill's `scripts/fetch_transcript.py` helper). Fetch all IDs in one loop, catching per-video errors, and write each to its own `.txt`.

3. **Save** one file per video with `MM:SS` timestamps per line plus a header (title + URL), and a small `_manifest.json` recording per-file status so partial failures are visible without re-running the whole batch.

## Pitfalls

- **"The playlist does not exist" on a URL the user swears is correct = private list, not a bad ID.** Enumerate with `--cookies-from-browser <firefox|chrome>`; the user must be logged into YouTube in that browser. Do not conclude the ID is invalid.
- **Playlist IDs are normally 34 chars, but short IDs can still be valid** (private lists can resolve with far fewer). Verify by authenticated fetch, not by length — a 13-char ID is not automatically truncated/broken.
- **Never assume the video needs auth for its transcript.** Only playlist enumeration is gated; transcript text is not. After enumerating IDs, fetch transcripts unauthenticated.
- **`youtube-transcript-api` returns `FetchedTranscriptSnippet` objects** in v1.x — access `.text`/`.start`/`.duration` attributes, they are not plain dicts.
- **Ask before `pip install` into the agent's own interpreter.** Use the scratch venv; system pip is PEP 668 locked and will refuse.
- **Persist the enumerated video-ID list (and the fetch script) to disk BEFORE fetching transcripts.** Enumeration (yt-dlp) and transcript fetch (youtube-transcript-api) hit different endpoints and rate-limit independently — enumeration can succeed while every transcript fetch is blocked. Saving the ID list first means a mid-batch block loses nothing.
- **A burst of ~15-20 transcript fetches can trip YouTube's IP rate limit; the same block surfaces as `IpBlocked` in youtube-transcript-api and `HTTP 429 Too Many Requests` in yt-dlp subtitle download.** One rate limit, two symptoms — do not chase it as a library bug or a broken video ID.
- **With no browser cookies or proxy available, use a bounded retry-with-backoff fetcher (e.g. 120s between passes, ~30 min ceiling, run background with notify) instead of hammering.** These blocks usually clear in minutes-to-hours; immediately re-running the same loop extends them.
