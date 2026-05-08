# ComfyUI Enhancement Workflow Contract

Use this when a ComfyUI endpoint/API key is available.

## Environment

Preferred variables:

```bash
export COMFYUI_BASE_URL="https://..."          # local or hosted ComfyUI base URL
export COMFY_CLOUD_API_KEY="..."              # if using Comfy Cloud
export COMFYUI_WORKFLOW="workflows/ufo_enhance_api.json"
```

Do not commit endpoint URLs, API keys, cookies, or signed output URLs.

## Input contract

Each queued item should include:

```json
{
  "id": "ufo-card-001-enhance-001",
  "source_page": "converted/.../page-0001.md",
  "source_image_or_pdf": "downloads/...pdf or extracted page image",
  "page": 1,
  "crop": {"x": 0, "y": 0, "w": 1024, "h": 1024},
  "operation": "upscale_contrast_compare",
  "label": "AI-enhanced readability pass; original remains authoritative"
}
```

## Recommended workflow stages

1. Load original page/crop.
2. Optional grayscale/contrast preprocessing.
3. Upscale 2x or 4x.
4. Denoise lightly; avoid hallucination-heavy settings.
5. Save enhanced image.
6. Render comparison panel with original + enhanced + source metadata.

## Prompting rules for generated/illustrative cards

Positive direction:

```text
investigative archive dashboard, declassified document table, blue-green radar glow, source-backed research wall, forensic comparison panel, labeled AI-enhanced crop, serious documentary tone
```

Negative prompt:

```text
fake evidence, fake government seal, unreadable text, invented document, alien body, sensational hoax poster, watermark, logo, celebrity, gore
```

## Output contract

```json
{
  "prompt_id": "...",
  "source_id": "ufo-card-001",
  "outputs": [
    {"type": "comparison_panel", "path": "outputs/ufo-card-001-panel.png"}
  ],
  "labels": ["AI-enhanced", "source transcript available", "original required for exact wording"]
}
```
