#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_serenity.py — Serenity Bilibili explainer renderer

Builds a 1280×720 30fps H.264 + AAC video from still images and 曼波 TTS
chunks. Voiceover starts after a 1.5s silent lead (cover on screen, no
subtitle). Image cuts and subtitles are timed from speech pauses in the
TTS, not from ASR. Subtitles use the script's own wording.

USAGE
=====
  python3 /workspace/serenity/render_serenity.py --dir FOLDER --output out.mp4

FOLDER is scanned for:

  01_*.png, 02_*.png, ...   stills (zero-padded index prefix); scaled to 1280×720
  c1.txt, c2.txt, ...       voiceover script per chunk (exact subtitle wording)
  tts1.mp3, tts2.mp3, ...   matching TTS (Bcut 曼波; WAV-in-.mp3 is fine)
  cuts.txt                  optional cut list; see CUTS below

Override any of those with flags when the names differ (e.g. a replacement
clip):

  python3 /workspace/serenity/render_serenity.py \\
      --dir /workspace/serenity/20261111_crwv/v2 \\
      --images 01_Neocloud需求是产能10倍_封面.png 02_Neocloud需求是产能10倍_拼图_1.png \\
      --chunks c1.txt c2.txt c3.txt \\
      --tts tts1_v3.mp3 tts2.mp3 tts3.mp3 \\
      --cut-after "14点42分。" \\
      --output serenity_crwv_20261111_v3.mp4

CUTS
====
The first image always starts at t=0, which is the silent lead. Each later
image needs one rule, given either as a repeated flag or as a line in
cuts.txt (one rule per image after the first):

  --cut-after "14点42分。"     start the next image at the pause after this
                               exact script phrase (including its punctuation).
                               A marker may span several phrases (e.g. a
                               sentence that contains commas).
  --cut-sentence 5             1-based phrase index across the concatenated
                               script (phrases are split on ，。：、；)
  --cut-time 9.100             seconds into the concatenated TTS, *before*
                               the lead is added; the lead is applied after

  cuts.txt lines (equivalent):
    after:14点42分。
    sentence:5
    time:9.100

--lead defaults to 1.5 seconds. Use --lead 0 to start speech immediately.

SUBTITLES
=========
White Noto Sans CJK SC, 40px, black outline, bottom-centered, sitting in
the lower ~125px band. Phrases follow the script punctuation and are split
further if they run longer than about 18 Chinese characters. Timing follows
the speech pauses; each cue holds until the next one starts.

OUTPUT
======
1280×720, 30fps, H.264 CBR (bitrate chosen to stay under 100MB, around
7 Mbps for a ~100s video), AAC 192 kbps, 48 kHz stereo. No music,
transitions, or SFX. Next to the mp4 the tool also writes timing.json,
subs.ass, and check_*.png frames (midpoint of each image, 0.5s if there
is a lead, each cut, and a few subtitle samples).

DEPENDENCIES
============
ffmpeg, ffprobe, Python 3 with numpy and Pillow. Noto Sans CJK SC must be
available via fontconfig (Debian: fonts-noto-cjk).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image

FPS = 30
WIDTH, HEIGHT = 1280, 720
FONT_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_NAME = "Noto Sans CJK SC"
DEFAULT_LEAD = 1.5
SIZE_CAP_MIB = 95.0  # stay comfortably under 100MB


# ---------------------------------------------------------------------------
# Audio / script alignment
# ---------------------------------------------------------------------------

def load_wav(path: Path):
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(
            np.float32
        ) / 32768.0
        if nch > 1:
            audio = audio.reshape(-1, nch).mean(axis=1)
        return audio, sr


def ensure_wav(src: Path, dest: Path, sr: int) -> Path:
    """Decode src (wav, or Bcut's WAV-in-.mp3) to a mono wav at sr Hz."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-ac", "1", "-ar", str(sr),
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg failed to decode {src}:\n{r.stderr[-2000:]}")
    return dest


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def speech_islands(audio: np.ndarray, sr: int, min_sil: float = 0.15):
    frame = int(0.02 * sr)
    n = len(audio) // frame
    if n == 0:
        return []
    rms = np.array(
        [np.sqrt(np.mean(audio[i * frame : (i + 1) * frame] ** 2)) for i in range(n)]
    )
    p95 = float(np.percentile(rms, 95))
    thr = max(0.012, 0.08 * p95)
    speech = rms >= thr
    raw = []
    i = 0
    while i < len(speech):
        j = i
        while j < len(speech) and speech[j] == speech[i]:
            j += 1
        typ = "speech" if speech[i] else "sil"
        raw.append((typ, i * 0.02, j * 0.02))
        i = j
    islands = []
    cur_s = cur_e = None
    for typ, s, e in raw:
        if typ == "speech":
            if cur_s is None:
                cur_s, cur_e = s, e
            else:
                cur_e = e
        else:
            if cur_s is None:
                continue
            if (e - s) < min_sil:
                pass
            else:
                islands.append((round(cur_s, 3), round(cur_e, 3)))
                cur_s = cur_e = None
    if cur_s is not None:
        islands.append((round(cur_s, 3), round(cur_e, 3)))
    return islands


def split_phrases(text: str):
    parts = re.findall(r"[^，。：、；]+[，。：、；]?", text)
    return [p.strip() for p in parts if p.strip()]


def visual_len(s: str) -> float:
    n = 0.0
    for ch in s:
        if ch in "，。：、；！？,.:;!?" or ord(ch) > 0x7F:
            n += 1.0
        else:
            n += 0.55
    return n


def align_phrases(islands, phrases):
    """Assign consecutive speech islands to phrases by span vs visual length."""
    M, N = len(islands), len(phrases)
    if M == 0 or N == 0:
        return None
    if M == N:
        return [(p, s, e) for p, (s, e) in zip(phrases, islands)]
    if M < N:
        return None
    vis = [visual_len(p) for p in phrases]
    total_d = islands[-1][1] - islands[0][0]
    total_v = sum(vis) or 1
    expected = [total_d * v / total_v for v in vis]
    INF = 1e18
    dp = [[INF] * (N + 1) for _ in range(M + 1)]
    back = [[-1] * (N + 1) for _ in range(M + 1)]
    dp[0][0] = 0.0
    for n in range(1, N + 1):
        for m in range(n, M - (N - n) + 1):
            max_k = m - (n - 1)
            for k in range(1, max_k + 1):
                span = islands[m - 1][1] - islands[m - k][0]
                cost = dp[m - k][n - 1] + (span - expected[n - 1]) ** 2
                if cost < dp[m][n]:
                    dp[m][n] = cost
                    back[m][n] = m - k
    if back[M][N] < 0:
        return None
    groups = []
    m, n = M, N
    while n:
        prev = back[m][n]
        groups.append((prev, m))
        m, n = prev, n - 1
    groups.reverse()
    out = []
    for (i, j), p in zip(groups, phrases):
        out.append((p, islands[i][0], islands[j - 1][1]))
    return out


def fallback_align(islands, phrases, dur):
    if islands:
        span_s, span_e = islands[0][0], islands[-1][1]
    else:
        span_s, span_e = 0.0, dur
    total = sum(visual_len(p) for p in phrases) or 1
    t0 = span_s
    aligned = []
    for p in phrases:
        dt = (span_e - span_s) * visual_len(p) / total
        aligned.append((p, t0, t0 + dt))
        t0 += dt
    return aligned


def maybe_split_long(text: str, start: float, end: float):
    """Split a long phrase into <= ~18-char lines, timed by visual length."""
    if visual_len(text) <= 18.5:
        return [(text, start, end)]
    candidates = set()
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isascii() and ch.isalnum():
            j = i
            while j < len(text) and text[j].isascii() and text[j].isalnum():
                j += 1
            candidates.add(j)
            i = j
        else:
            i += 1
    for i, ch in enumerate(text):
        if ch in "的了是和与在等会到对把被就还但":
            candidates.add(i + 1)
    best = None
    for i in sorted(candidates):
        if i <= 0 or i >= len(text):
            continue
        left, right = text[:i], text[i:]
        if visual_len(left) < 6 or visual_len(right) < 4:
            continue
        over = max(0, visual_len(left) - 18) + max(0, visual_len(right) - 18)
        balance = abs(visual_len(left) - visual_len(right))
        bonus = 0
        if text[i - 1].isascii() and text[i - 1].isalnum() and (
            not right[0].isascii() or not right[0].isalnum()
        ):
            bonus = -3
        score = over * 10 + balance + bonus
        if best is None or score < best[0]:
            best = (score, left, right)
    if best is None:
        return [(text, start, end)]
    _, left, right = best
    mid = start + (end - start) * (visual_len(left) / visual_len(text))
    return [(left, start, mid), (right, mid, end)]


# ---------------------------------------------------------------------------
# Cuts
# ---------------------------------------------------------------------------

def parse_cuts_file(path: Path):
    rules = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("after:"):
            rules.append(("after", line[len("after:"):].strip()))
        elif line.startswith("sentence:"):
            rules.append(("sentence", int(line[len("sentence:"):].strip())))
        elif line.startswith("time:"):
            rules.append(("time", float(line[len("time:"):].strip())))
        else:
            raise SystemExit(f"Unrecognized cuts.txt line: {raw!r}")
    return rules


def resolve_cut(rule, alignment, lead: float) -> float:
    """Return a global *output* timestamp (lead already added)."""
    kind, val = rule
    if kind == "after":
        marker = val
        ordered = sorted(alignment, key=lambda r: r["tts_start"])
        n = len(ordered)
        end_rec = None
        for i in range(n):
            acc = ""
            for j in range(i, n):
                acc += ordered[j]["text"]
                if acc == marker:
                    end_rec = ordered[j]
                    break
                if not marker.startswith(acc):
                    break
            if end_rec is not None:
                break
        if end_rec is None:
            raise SystemExit(f"cut phrase not found in script: {marker!r}")
        nxt = None
        for rec2 in ordered:
            if rec2["tts_start"] > end_rec["tts_start"] + 1e-6:
                nxt = rec2["tts_start"]
                break
        tts_t = nxt if nxt is not None else end_rec["tts_end"]
        return lead + tts_t
    if kind == "sentence":
        idx = val
        if idx < 1 or idx > len(alignment):
            raise SystemExit(f"cut sentence index {idx} out of range 1..{len(alignment)}")
        # next image starts at this phrase (1-based) — i.e. at its start
        return lead + alignment[idx - 1]["tts_start"]
    if kind == "time":
        return lead + float(val)
    raise SystemExit(f"unknown cut rule: {rule}")


# ---------------------------------------------------------------------------
# Discovery / I/O helpers
# ---------------------------------------------------------------------------

def discover_numbered(folder: Path, pattern_prefix: str, suffix: str):
    """Find c1.txt / tts1.mp3 / 01_*.png style files, sorted by index."""
    found = {}
    if pattern_prefix in {"c", "tts"}:
        rx = re.compile(rf"^{re.escape(pattern_prefix)}(\d+){re.escape(suffix)}$")
        for p in folder.iterdir():
            m = rx.match(p.name)
            if m:
                found[int(m.group(1))] = p
    else:
        rx = re.compile(r"^(\d+)_.+\.png$", re.IGNORECASE)
        for p in folder.iterdir():
            m = rx.match(p.name)
            if m:
                found[int(m.group(1))] = p
    if not found:
        return []
    keys = sorted(found)
    if keys != list(range(keys[0], keys[-1] + 1)):
        raise SystemExit(f"Non-contiguous {pattern_prefix} files: {keys}")
    return [found[k] for k in keys]


def ass_time(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc_ass(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def video_bitrate_bps(duration: float) -> int:
    audio_bps = 192_000
    overhead = 0.5 * 1024 * 1024
    budget = SIZE_CAP_MIB * 1024 * 1024 - overhead
    total_bps = budget * 8 / max(duration, 0.5)
    video_bps = total_bps - audio_bps
    video_bps = max(2_000_000, min(video_bps, 10_000_000))
    return int(video_bps)


def write_ass(path: Path, cues):
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT_NAME},40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,40,40,36,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Default,,0,0,0,,{esc_ass(text)}"
        for text, s, e in cues
    ]
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def extract_frame(mp4: Path, dest: Path, t: float):
    subprocess.check_call(
        ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(dest)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Render a Serenity explainer (720p30, 1.5s lead, pause-aligned cuts).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See the module docstring for a full usage guide.",
    )
    p.add_argument("--dir", required=True, type=Path, help="Asset folder")
    p.add_argument("--output", required=True, help="Output mp4 path (relative to --dir unless absolute)")
    p.add_argument("--images", nargs="+", default=None, help="Image filenames (default: 01_*.png …)")
    p.add_argument("--chunks", nargs="+", default=None, help="Script txt files (default: c1.txt …)")
    p.add_argument("--tts", nargs="+", default=None, help="TTS audio files (default: tts1.mp3 …)")
    p.add_argument("--cut-after", action="append", default=[], metavar="PHRASE",
                   help="Next image starts at the pause after this phrase (repeatable)")
    p.add_argument("--cut-sentence", action="append", default=[], type=int, metavar="N",
                   help="Next image starts at 1-based phrase N (repeatable)")
    p.add_argument("--cut-time", action="append", default=[], type=float, metavar="SEC",
                   help="Next image starts at this TTS time, before lead (repeatable)")
    p.add_argument("--cuts-file", type=Path, default=None, help="cuts.txt (default: --dir/cuts.txt if present)")
    p.add_argument("--lead", type=float, default=DEFAULT_LEAD, help="Silent lead-in seconds (default 1.5)")
    p.add_argument("--no-check", action="store_true", help="Skip writing check_*.png frames")
    return p.parse_args(argv)


def collect_cut_rules(args, folder: Path, n_images: int):
    rules = []
    # flags first, in the order the user would naturally write them:
    # we interleave by collecting after/sentence/time separately, which
    # only works cleanly if the user uses one flag type. Prefer cuts-file
    # or a single type. If several types are used together, apply them in
    # after, then sentence, then time — warn.
    types_used = sum(bool(x) for x in (args.cut_after, args.cut_sentence, args.cut_time))
    cuts_file = args.cuts_file
    if cuts_file is None and (folder / "cuts.txt").is_file() and types_used == 0:
        cuts_file = folder / "cuts.txt"
    if cuts_file:
        rules = parse_cuts_file(cuts_file)
    if args.cut_after:
        rules.extend(("after", s) for s in args.cut_after)
    if args.cut_sentence:
        rules.extend(("sentence", n) for n in args.cut_sentence)
    if args.cut_time:
        rules.extend(("time", t) for t in args.cut_time)
    if len(rules) != n_images - 1:
        raise SystemExit(
            f"Need {n_images - 1} cut rule(s) for {n_images} image(s); got {len(rules)}. "
            f"Pass --cut-after / --cut-sentence / --cut-time or a cuts.txt."
        )
    return rules


def main(argv=None):
    args = parse_args(argv)
    folder: Path = args.dir.resolve()
    if not folder.is_dir():
        raise SystemExit(f"--dir is not a folder: {folder}")

    work = folder / "_render_work"
    work.mkdir(exist_ok=True)

    if args.images:
        images = [folder / n for n in args.images]
    else:
        images = discover_numbered(folder, "img", ".png")
        if not images:
            raise SystemExit("No 01_*.png stills found; pass --images")
    for p in images:
        if not p.is_file():
            raise SystemExit(f"missing image: {p}")

    if args.chunks:
        chunks = [folder / n for n in args.chunks]
    else:
        chunks = discover_numbered(folder, "c", ".txt")
    if args.tts:
        tts_files = [folder / n for n in args.tts]
    else:
        tts_files = discover_numbered(folder, "tts", ".mp3")
        if not tts_files:
            tts_files = discover_numbered(folder, "tts", ".wav")
    if len(chunks) != len(tts_files) or not chunks:
        raise SystemExit(
            f"Need matching cN.txt and ttsN audio; got {len(chunks)} scripts and {len(tts_files)} clips"
        )
    for p in chunks + tts_files:
        if not p.is_file():
            raise SystemExit(f"missing input: {p}")

    lead = float(args.lead)
    if lead < 0:
        raise SystemExit("--lead must be >= 0")

    texts = [p.read_text(encoding="utf-8").strip() for p in chunks]
    durs = [probe_duration(p) for p in tts_files]
    audio_dur = sum(durs)
    out_dur = lead + audio_dur

    print(f"folder: {folder}")
    print(f"images: {[p.name for p in images]}")
    print(f"chunks: {[p.name for p in chunks]}  durs={['%.3f' % d for d in durs]}")
    print(f"lead={lead:.3f}s  voiceover={audio_dur:.6f}s  output={out_dur:.6f}s")

    # Align each chunk
    alignment = []  # tts-timeline (no lead yet)
    offsets = [0.0]
    for d in durs[:-1]:
        offsets.append(offsets[-1] + d)

    for ci, (text, src, dur, off) in enumerate(zip(texts, tts_files, durs, offsets), 1):
        wav16 = ensure_wav(src, work / f"chunk{ci}_16k.wav", 16000)
        audio, sr = load_wav(wav16)
        islands = speech_islands(audio, sr)
        phrases = split_phrases(text)
        print(f"\n===== chunk {ci}  raw_islands={len(islands)} phrases={len(phrases)} dur={dur:.3f} =====")
        aligned = align_phrases(islands, phrases)
        if aligned is None:
            print("WARNING: DP align failed; falling back to character-proportional timing")
            aligned = fallback_align(islands, phrases, dur)
        for p, s, e in aligned:
            print(f"  [{s:6.3f}-{e:6.3f}] ({e-s:5.2f}s, vis={visual_len(p):4.1f}) {p}")
            alignment.append(
                {
                    "chunk": ci,
                    "text": p,
                    "tts_start": off + s,
                    "tts_end": off + e,
                    "local_start": s,
                    "local_end": e,
                }
            )

    # Subtitle cues on the TTS timeline, then shift by lead
    raw_cues = []
    for rec in alignment:
        for sub, ss, ee in maybe_split_long(rec["text"], rec["tts_start"], rec["tts_end"]):
            raw_cues.append((sub, ss, ee))
    cues = []
    for i, (text, s, e) in enumerate(raw_cues):
        end = raw_cues[i + 1][1] if i + 1 < len(raw_cues) else audio_dur
        if end < s + 0.12:
            end = min(s + 0.12, audio_dur)
        cues.append((text, lead + s, lead + end))

    rules = collect_cut_rules(args, folder, len(images))
    cut_times = [0.0] + [resolve_cut(r, alignment, lead) for r in rules] + [out_dur]
    # sanity: strictly increasing
    for a, b in zip(cut_times, cut_times[1:]):
        if b <= a + 1e-3:
            raise SystemExit(f"cut times are not increasing: {cut_times}")

    print("\n===== raw cut times (output clock, includes lead) =====")
    for i, (a, b) in enumerate(zip(cut_times, cut_times[1:])):
        print(f"  {images[i].name}: {a:.6f} -> {b:.6f}  ({b-a:.3f}s)")

    # Snap to frames. Interior cuts floor so the new image appears at or
    # just before the next sentence, still inside the preceding pause.
    start_frames = [0]
    for t in cut_times[1:-1]:
        start_frames.append(int(np.floor(t * FPS + 1e-9)))
    total_frames = int(np.ceil(out_dur * FPS - 1e-9))
    if total_frames <= start_frames[-1]:
        total_frames = start_frames[-1] + 1
    start_frames.append(total_frames)

    print("\n===== frame-snapped cuts =====")
    segments = []
    for i, (f0, f1) in enumerate(zip(start_frames, start_frames[1:])):
        t0, t1 = f0 / FPS, f1 / FPS
        print(f"  {images[i].name}: frames {f0}-{f1}  {t0:.6f}s -> {t1:.6f}s  ({f1-f0} frames, {t1-t0:.3f}s)")
        segments.append(
            {
                "image": images[i].name,
                "start": t0,
                "end": t1,
                "start_frame": f0,
                "end_frame": f1,
                "frames": f1 - f0,
            }
        )

    print("\n===== subtitles =====")
    for i, (text, s, e) in enumerate(cues):
        print(f"  {i:02d} {s:7.3f}-{e:7.3f} ({e-s:5.2f}) vis={visual_len(text):4.1f} {text}")

    out_mp4 = Path(args.output)
    if not out_mp4.is_absolute():
        out_mp4 = folder / out_mp4

    ass_path = folder / (out_mp4.stem + ".ass")
    write_ass(ass_path, cues)
    print(f"\nWrote {ass_path} with {len(cues)} cues")

    meta = {
        "lead": lead,
        "audio_duration": audio_dur,
        "output_duration": out_dur,
        "chunk_durations": durs,
        "raw_cuts": cut_times,
        "segments": segments,
        "subtitles": [{"text": t, "start": s, "end": e} for t, s, e in cues],
        "alignment": alignment,
    }
    timing_path = folder / (out_mp4.stem + "_timing.json")
    timing_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Scale images
    scaled = []
    for img in images:
        im = Image.open(img).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        outp = work / f"scaled_{img.stem}.png"
        im.save(outp, "PNG")
        scaled.append(outp)

    # Concatenate TTS with lead silence, 48 kHz mono then we'll encode stereo
    concat_wav = work / "voiceover_with_lead.wav"
    # Decode each clip to 48k and concat, prepending silence
    parts_48 = []
    for i, src in enumerate(tts_files, 1):
        p = work / f"chunk{i}_48k.wav"
        ensure_wav(src, p, 48000)
        parts_48.append(p)
    # Build filter: anullsrc + concat
    silence = work / "lead_silence.wav"
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=48000:cl=mono",
            "-t", f"{lead:.6f}",
            str(silence),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    all_audio = [silence] + parts_48
    inputs_a = []
    labels = []
    for i, p in enumerate(all_audio):
        inputs_a += ["-i", str(p)]
        labels.append(f"[{i}:a]")
    filt = "".join(labels) + f"concat=n={len(all_audio)}:v=0:a=1[a]"
    r = subprocess.run(
        ["ffmpeg", "-y", *inputs_a, "-filter_complex", filt, "-map", "[a]", str(concat_wav)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"audio concat failed:\n{r.stderr[-2000:]}")
    concat_dur = probe_duration(concat_wav)
    print(f"concat audio duration={concat_dur:.6f}s (expected {out_dur:.6f}s)")

    # Render
    vbps = video_bitrate_bps(out_dur)
    print(f"video bitrate={vbps} bps ({vbps/1e6:.2f} Mbps)")

    ff_inputs = []
    filters = []
    for i, (p, seg) in enumerate(zip(scaled, segments)):
        n = seg["frames"]
        dur = n / FPS + 0.1
        ff_inputs += ["-loop", "1", "-t", f"{dur:.6f}", "-i", str(p)]
        filters.append(
            f"[{i}:v]fps={FPS},setsar=1,format=yuv420p,trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]"
        )
    audio_idx = len(images)
    ff_inputs += ["-i", str(concat_wav)]
    concat_in = "".join(f"[v{i}]" for i in range(len(images)))
    filters.append(f"{concat_in}concat=n={len(images)}:v=1:a=0[vcat]")
    ass_esc = str(ass_path).replace("\\", "\\\\").replace(":", "\\:")
    fonts = FONT_TTC.rsplit("/", 1)[0].replace("\\", "\\\\").replace(":", "\\:")
    filters.append(f"[vcat]ass='{ass_esc}':fontsdir='{fonts}'[vout]")

    kbps = max(1, int(round(vbps / 1000)))
    cmd = [
        "ffmpeg", "-y", *ff_inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-preset", "medium", "-profile:v", "high", "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-b:v", f"{kbps}k", "-minrate", f"{kbps}k", "-maxrate", f"{kbps}k",
        "-bufsize", f"{kbps}k",
        "-x264-params", "nal-hrd=cbr:force-cfr=1",
        "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
        "-t", f"{out_dur:.6f}",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    print("\nRunning ffmpeg...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-4000:])
        raise SystemExit(f"ffmpeg failed: {r.returncode}")
    print(r.stderr[-800:])

    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration,size,bit_rate",
                "-show_entries", "stream=codec_name,width,height,avg_frame_rate,nb_frames,sample_rate,channels,bit_rate",
                "-of", "json", str(out_mp4),
            ]
        )
    )
    size = int(probe["format"]["size"])
    print("\n===== output =====")
    print(json.dumps(probe, indent=2))
    print(f"size_mb={size/1024/1024:.2f}  duration={probe['format']['duration']}")
    if size >= 100 * 1024 * 1024:
        raise SystemExit(f"output is {size} bytes, over the 100MB cap")
    (folder / (out_mp4.stem + "_ffprobe.json")).write_text(json.dumps(probe, indent=2), encoding="utf-8")

    check_paths = []
    if not args.no_check:
        print("\n===== check frames =====")
        # 0.5s lead frame if the lead is long enough
        wanted = []
        if lead >= 0.5:
            wanted.append((folder / "check_lead_0p5.png", 0.5, "lead 0.5s (no subtitle)"))
        for i, seg in enumerate(segments):
            mid = (seg["start"] + min(seg["end"], out_dur)) / 2
            wanted.append((folder / f"check_img{i+1}_mid.png", mid, f"image {i+1} mid"))
            if i > 0:
                # just after the cut
                t = seg["start"] + 0.15
                wanted.append((folder / f"check_cut{i}.png", t, f"cut to image {i+1}"))
        # a few subtitle samples: first, one mid-video, last, plus any cue
        # whose start is just after the first cut (to confirm the shift)
        if cues:
            wanted.append((folder / "check_sub_first.png", (cues[0][1] + cues[0][2]) / 2, "first subtitle"))
            mid_i = len(cues) // 2
            wanted.append((folder / "check_sub_mid.png", (cues[mid_i][1] + cues[mid_i][2]) / 2, "mid subtitle"))
            wanted.append((folder / "check_sub_last.png", (cues[-1][1] + cues[-1][2]) / 2, "last subtitle"))
        for dest, t, label in wanted:
            t = min(max(0.0, t), max(0.0, out_dur - 0.04))
            extract_frame(out_mp4, dest, t)
            print(f"  {dest.name}  t={t:.3f}s  {label}")
            check_paths.append({"path": str(dest), "time": t, "label": label})
        meta["check_frames"] = check_paths
        timing_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDone: {out_mp4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
