# UFO/UAP Investigation Stream Kit

This fork adds a stream-ready investigation layer on top of the converted `war.gov/UFO` markdown archive.

## What we are building

A live “Signal Room” that can run as an OBS/browser-source or Program Deck scene:

```text
public archive transcripts
  -> source-backed case cards
  -> AI summary / entity extraction / uncertainty labels
  -> original-vs-enhanced visual bench
  -> viewer-safe investigation queue
  -> stream dashboard / episode clock
```

This is designed for high-retention live analysis without overclaiming. The show investigates documents and metadata; it does **not** claim that any sighting is proven.

## Stream surfaces

Build the static dashboard:

```bash
python3 scripts/build_ufo_stream_dashboard.py
```

Outputs:

```text
docs/index.html
docs/data/ufo_stream_deck.json
docs/stream/queue_seed.json
docs/stream/comfyui_enhancement_plan.json
docs/stream/episode_clock.json
```

Use `docs/index.html` as:

- GitHub Pages proof hub;
- OBS browser source;
- Program Deck iframe/browser scene;
- source of stream queue cards.

## Episode format

Every 60-minute cycle:

1. **Open the vault** — source/repo/inventory stats.
2. **Case card deep read** — AI summarizes one page with uncertainty labels.
3. **Enhancement bench** — crop/upscale/contrast source images/pages; original remains visible.
4. **Cross-reference sprint** — agencies, locations, dates, repeated terms.
5. **Viewer queue** — chat requests pages/topics; everything stays source-backed.

## AI analysis rules

For each page/card, AI should output:

- `direct_text_summary`: what the OCR/transcript says;
- `entities`: agencies, people, places, dates, document IDs;
- `claim_type`: sighting, memo, media report, technical proposal, correspondence, unknown;
- `evidence_level`: transcript-only, source-image-needed, original-PDF-needed;
- `uncertainty`: OCR caveats, redactions, missing context;
- `stream_hook`: one viewer-friendly question;
- `next_action`: read adjacent pages, search by agency/date/location, or enhance a crop.

## ComfyUI enhancement lane

When the operator provides a ComfyUI endpoint/API key and a workflow, route source images/pages through a queue for:

- upscaling old scanned document crops;
- contrast/denoise/OCR readability passes;
- suspected-object crop comparison panels;
- side-by-side layouts: original, enhanced, OCR text;
- clearly labeled illustrative episode cards.

Hard rules:

- Never present AI-generated art as original evidence.
- Keep original source visible beside any enhancement.
- Label all enhanced/generated imagery.
- Preserve source URL/path/page metadata.

## Viewer safety

- `allowed_to_execute=false`
- `chat_to_shell=false`
- No doxxing, harassment, or claims of proof without source support.
- Viewer prompts become queue cards only.
- Exact wording should be checked against original PDFs/images because Markdown is AI-assisted OCR.
