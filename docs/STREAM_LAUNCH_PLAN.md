# UFO/UAP Stream Launch Plan

## Goal

Turn the public archive into a compelling research show:

- source-backed case cards;
- visible AI reasoning and uncertainty labels;
- enhancement bench for crops/pages/images;
- chat-safe viewer queue;
- recurring episode clock.

## OBS / Restreamer scene map

1. **Signal Room Dashboard**
   - Browser source: `docs/index.html` or GitHub Pages URL once enabled.
   - Shows archive stats, cards, term cloud, and links to queue JSON.

2. **Case Deep Read**
   - Browser/text source backed by `docs/stream/queue_seed.json`.
   - AI reads one card: summary, entities, uncertainty, next action.

3. **Enhancement Bench**
   - Side-by-side: original page/crop, enhanced result, OCR snippet.
   - Use ComfyUI queue when endpoint is available.

4. **Viewer Queue**
   - Chat suggestions become JSON cards only.
   - No direct shell, no external posting, no claims of proof.

5. **Break / Bumper**
   - HyperFrames/Program Deck bumper: “Signal Room — next document loading”.

## Run locally

```bash
python3 scripts/build_ufo_stream_dashboard.py
python3 -m http.server 8766 --directory docs
# open http://127.0.0.1:8766/
```

## Publish as GitHub Pages

This repo has `docs/index.html`, so Pages can use:

```text
branch: main
folder: /docs
```

## Claims language

Use:

- “public archive says…”
- “OCR transcript suggests…”
- “source image needs review…”
- “AI-enhanced for readability, not new evidence…”

Avoid:

- “proof of aliens”
- “confirmed craft”
- “government admits…” unless exact source text supports it
- presenting generated/illustrative images as original records
