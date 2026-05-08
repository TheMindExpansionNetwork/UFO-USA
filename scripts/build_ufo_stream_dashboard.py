#!/usr/bin/env python3
"""Build a static UFO/UAP investigation stream dashboard from the converted archive.

The dashboard is public-safe: it treats repository transcripts as AI-assisted OCR
and preserves uncertainty. It does not claim sightings are proven; it creates a
streamable research surface, queue manifests, and analysis prompts.
"""
from __future__ import annotations

import csv
import html
import json
import pathlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = DOCS / "data"
STREAM = DOCS / "stream"

KEYWORDS = [
    "ufo", "uap", "unidentified", "flying", "disc", "disk", "saucer",
    "object", "light", "radar", "aircraft", "meteor", "balloon", "photograph",
    "film", "sighting", "witness", "air force", "fbi", "navy", "army",
    "oak ridge", "propulsion", "foo fighter", "project blue book",
]
STOPWORDS = set("""
the and for that with from this have were which would there their been page file
section report records record subject memorandum information unidentified flying
object objects ufo uap saucer saucers disc discs disk disks aircraft air force
""".split())


def read_inventory() -> list[dict[str, str]]:
    path = ROOT / "metadata" / "uap-csv.csv"
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


def page_records() -> list[dict]:
    records = []
    for p in sorted((ROOT / "converted").glob("*/*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        # strip frontmatter lightly
        body = re.sub(r"^---.*?---\s*", "", text, flags=re.S)
        title = p.parent.name
        page = int(re.search(r"page-(\d+)\.md$", p.name).group(1))
        lower = body.lower()
        counts = {k: lower.count(k) for k in KEYWORDS if lower.count(k)}
        score = sum(counts.values()) + min(len(body) // 1500, 8)
        snippet = re.sub(r"\s+", " ", body).strip()[:380]
        records.append({
            "id": f"{title}::{p.stem}",
            "asset": title,
            "page": page,
            "path": p.relative_to(ROOT).as_posix(),
            "chars": len(body),
            "keyword_counts": counts,
            "score": score,
            "snippet": snippet,
        })
    return records


def make_deck(records: list[dict], inventory: list[dict[str, str]]) -> dict:
    by_asset = defaultdict(list)
    for r in records:
        by_asset[r["asset"]].append(r)
    top_pages = sorted(records, key=lambda r: (r["score"], r["chars"]), reverse=True)[:40]
    inv_types = Counter((row.get("Type") or "unknown").strip() or "unknown" for row in inventory)
    inv_agencies = Counter((row.get("Agency") or "unknown").strip() or "unknown" for row in inventory)
    all_text = " ".join(r["snippet"].lower() for r in records)
    words = Counter(w for w in re.findall(r"[a-z][a-z\-]{3,}", all_text) if w not in STOPWORDS)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "archive": {
            "source_repo": "https://github.com/DenisSergeevitch/UFO-USA",
            "fork_repo": "https://github.com/TheMindExpansionNetwork/UFO-USA",
            "source_page_claimed_by_repo": "https://www.war.gov/UFO/",
            "converted_pages_present": len(records),
            "inventory_rows": len(inventory),
            "asset_count_present": len(by_asset),
            "types": inv_types,
            "agencies": inv_agencies,
            "license_note": "No LICENSE file detected in the upstream clone at build time; use as a forked archive/research surface and preserve source attribution.",
        },
        "top_terms": words.most_common(40),
        "top_pages": top_pages,
        "assets": [
            {
                "asset": asset,
                "page_count_present": len(pages),
                "total_chars": sum(p["chars"] for p in pages),
                "max_score": max(p["score"] for p in pages),
                "sample_path": sorted(pages, key=lambda r: r["page"])[0]["path"],
            }
            for asset, pages in sorted(by_asset.items())
        ],
    }


def write_html(deck: dict) -> None:
    top_pages = deck["top_pages"][:24]
    terms = deck["top_terms"][:24]
    cards = "\n".join(
        f"""
        <article class='case-card'>
          <div class='score'>signal {r['score']}</div>
          <h3>{html.escape(r['asset'])}</h3>
          <p class='meta'>page {r['page']} · {r['chars']} OCR chars · <a href='../{html.escape(r['path'])}'>open transcript</a></p>
          <p>{html.escape(r['snippet'] or 'No readable OCR snippet available.')}</p>
          <code>{html.escape(', '.join(f'{k}:{v}' for k,v in r['keyword_counts'].items()) or 'keyword scan pending')}</code>
        </article>
        """ for r in top_pages
    )
    term_cloud = "\n".join(f"<span>{html.escape(w)} <b>{c}</b></span>" for w, c in terms)
    assets = deck["archive"]
    html_text = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>UFO/UAP Archive Investigation Stream Kit</title>
<style>
:root {{ color-scheme: dark; --bg:#050712; --panel:#0e1326; --line:#43f7ff; --pink:#ff3df2; --lime:#b7ff38; --text:#edf7ff; --muted:#9bb3c8; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, sans-serif; background:radial-gradient(circle at top left,#172045,#050712 55%); color:var(--text); }}
header {{ min-height:52vh; display:grid; place-items:center; padding:56px 22px; text-align:center; border-bottom:1px solid rgba(67,247,255,.22); }}
.badge {{ color:var(--lime); border:1px solid rgba(183,255,56,.45); display:inline-block; padding:8px 12px; border-radius:999px; letter-spacing:.13em; text-transform:uppercase; font-size:12px; }}
h1 {{ font-size:clamp(38px,8vw,92px); line-height:.9; margin:18px auto; max-width:1100px; text-shadow:0 0 28px rgba(67,247,255,.4); }}
.subtitle {{ max-width:920px; margin:auto; color:var(--muted); font-size:20px; }}
.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; max-width:1180px; margin:26px auto 0; }}
.stat {{ background:rgba(14,19,38,.78); border:1px solid rgba(67,247,255,.24); padding:18px; border-radius:18px; }}
.stat b {{ display:block; font-size:30px; color:#fff; }}
section {{ max-width:1240px; margin:0 auto; padding:36px 22px; }}
h2 {{ font-size:34px; margin:0 0 14px; }}
.pipeline {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }}
.step {{ background:linear-gradient(180deg,rgba(255,61,242,.14),rgba(67,247,255,.08)); border:1px solid rgba(255,255,255,.13); padding:16px; border-radius:18px; min-height:132px; }}
.step b {{ color:var(--line); }}
.case-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
.case-card {{ background:rgba(14,19,38,.86); border:1px solid rgba(67,247,255,.20); border-radius:18px; padding:16px; box-shadow:0 12px 40px rgba(0,0,0,.28); }}
.case-card h3 {{ font-size:15px; overflow-wrap:anywhere; }}
.meta,.case-card p {{ color:var(--muted); }}
.score {{ float:right; color:var(--pink); font-weight:800; font-size:12px; text-transform:uppercase; }}
a {{ color:var(--line); }}
code {{ display:block; white-space:normal; color:var(--lime); font-size:12px; }}
.terms {{ display:flex; flex-wrap:wrap; gap:10px; }}
.terms span {{ border:1px solid rgba(255,255,255,.15); border-radius:999px; padding:9px 12px; background:rgba(255,255,255,.05); }}
.warning {{ border-left:4px solid var(--pink); background:rgba(255,61,242,.10); padding:16px; border-radius:12px; color:#ffd7fb; }}
footer {{ color:var(--muted); padding:40px 22px; text-align:center; }}
@media(max-width:900px) {{ .grid,.pipeline,.case-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <div>
    <div class='badge'>Jimsky / Hermes investigation stream kit</div>
    <h1>UFO/UAP Archive Signal Room</h1>
    <p class='subtitle'>A stream-ready dashboard for exploring a public UFO/UAP markdown archive: searchable records, OCR caveats, AI-analysis queues, enhancement lanes, and viewer-safe investigation cards.</p>
    <div class='grid'>
      <div class='stat'><b>{assets['converted_pages_present']}</b>converted pages present</div>
      <div class='stat'><b>{assets['inventory_rows']}</b>inventory rows</div>
      <div class='stat'><b>{assets['asset_count_present']}</b>record folders present</div>
      <div class='stat'><b>{len(deck['top_pages'])}</b>high-signal cards</div>
    </div>
  </div>
</header>
<section>
  <h2>Stream format</h2>
  <div class='pipeline'>
    <div class='step'><b>1. Source Wall</b><br>Show source URL, repo, document title, page path, and OCR status.</div>
    <div class='step'><b>2. AI Read</b><br>Summarize claim, entities, locations, dates, agencies, and uncertainty.</div>
    <div class='step'><b>3. Evidence Split</b><br>Separate direct document text from speculation, lore, and chat ideas.</div>
    <div class='step'><b>4. Enlarge / Enhance</b><br>Route images/pages to ComfyUI upscaling, OCR cleanup, contrast, crop, and comparison panels.</div>
    <div class='step'><b>5. Viewer Queue</b><br>Chat can request pages/topics; no shell, no claims of proof, no doxxing.</div>
  </div>
</section>
<section>
  <h2>High-signal archive cards</h2>
  <p class='warning'>Important: generated Markdown is AI-assisted OCR. Use original PDFs/images as authoritative records when exact wording matters. This show investigates documents; it does not claim any sighting is proven.</p>
  <div class='case-grid'>{cards}</div>
</section>
<section>
  <h2>Term cloud for episode hooks</h2>
  <div class='terms'>{term_cloud}</div>
</section>
<section>
  <h2>Data feeds for OBS / Program Deck</h2>
  <ul>
    <li><a href='data/ufo_stream_deck.json'>Stream deck JSON</a></li>
    <li><a href='stream/queue_seed.json'>Queue seed JSON</a></li>
    <li><a href='stream/comfyui_enhancement_plan.json'>ComfyUI enhancement plan</a></li>
    <li><a href='stream/episode_clock.json'>Episode clock JSON</a></li>
  </ul>
</section>
<footer>Generated {html.escape(deck['generated_at'])}. Fork: TheMindExpansionNetwork/UFO-USA. Preserve attribution and uncertainty.</footer>
</body>
</html>"""
    (DOCS / "index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STREAM.mkdir(parents=True, exist_ok=True)
    inventory = read_inventory()
    records = page_records()
    deck = make_deck(records, inventory)
    (DATA / "ufo_stream_deck.json").write_text(json.dumps(deck, indent=2, default=dict), encoding="utf-8")
    queue = {
        "allowed_to_execute": False,
        "chat_to_shell": False,
        "public_claims_require_source": True,
        "cards": [
            {
                "id": f"ufo-card-{i+1:03d}",
                "status": "ready_for_stream_review",
                "asset": r["asset"],
                "page": r["page"],
                "path": r["path"],
                "prompt": "Summarize the document page, extract dates/agencies/locations, label uncertainty, and suggest one visual crop/enhancement if source imagery exists.",
            }
            for i, r in enumerate(deck["top_pages"][:30])
        ],
    }
    (STREAM / "queue_seed.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
    comfy = {
        "mode": "template_waiting_for_endpoint",
        "requires": ["COMFYUI_BASE_URL or COMFY_CLOUD_API_KEY", "API-format workflow JSON"],
        "tasks": [
            "upscale scanned document crops",
            "contrast/denoise old document images",
            "crop suspected object regions for side-by-side comparison",
            "make stream-safe comparison panels: original vs enhanced vs OCR text",
            "generate visual episode cards that are clearly labeled as illustrative, not evidence",
        ],
        "safety": {
            "no_fake_evidence": True,
            "label_ai_enhanced": True,
            "keep_original_visible": True,
            "do_not_present_generated_art_as_source": True,
        },
    }
    (STREAM / "comfyui_enhancement_plan.json").write_text(json.dumps(comfy, indent=2), encoding="utf-8")
    clock = {
        "cycle_minutes": 60,
        "blocks": [
            {"minute": 0, "title": "Open the vault", "action": "Show source/repo/inventory stats."},
            {"minute": 10, "title": "Case card deep read", "action": "AI summary with uncertainty labels."},
            {"minute": 25, "title": "Enhancement bench", "action": "Crop/upscale/contrast queued source imagery; original stays on screen."},
            {"minute": 40, "title": "Cross-reference sprint", "action": "Search agencies, dates, locations, repeated terms."},
            {"minute": 55, "title": "Viewer queue / next anomaly", "action": "Pick next source-backed card."},
        ],
    }
    (STREAM / "episode_clock.json").write_text(json.dumps(clock, indent=2), encoding="utf-8")
    write_html(deck)
    print(json.dumps({"ok": True, "pages": len(records), "docs": str(DOCS), "top_cards": len(deck["top_pages"])}, indent=2))


if __name__ == "__main__":
    main()
