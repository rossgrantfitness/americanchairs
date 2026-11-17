#!/usr/bin/env python3
"""Generate AI concept renders of the chairs with Google Gemini.

Reads prompts from tools/chair_prompts.json and writes JPEGs to img/chairs/.
Tries Gemini's native API first (key in the x-goog-api-key header), then the
OpenAI-compatible endpoint (key as a Bearer token), then Imagen:

    GEMINI_API_KEY=your-key python3 tools/gen_chair_images.py            # all
    GEMINI_API_KEY=your-key python3 tools/gen_chair_images.py slug1 slug2

In the Claude cloud environment the key is injected by the network proxy, so
GEMINI_API_KEY can be any placeholder there.

These are ILLUSTRATIONS, not product photos. The site labels them as AI
concept renders. Replace them with the manufacturer's official dealer
photography once a dealer agreement is in place.
"""
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROMPTS = os.path.join(ROOT, "tools", "chair_prompts.json")
OUT = os.path.join(ROOT, "img", "chairs")
BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
KEY = os.environ.get("GEMINI_API_KEY", "proxy-injected")

# Gemini image model first; Imagen (also served by the Gemini API) as fallback.
CHAT_MODELS = [m for m in os.environ.get("GEMINI_IMAGE_MODELS", "").split(",") if m] or [
    "gemini-2.5-flash-image",
]
IMAGEN_MODELS = ["imagen-4.0-generate-001", "imagen-3.0-generate-002"]

STYLE = (
    "Professional e-commerce studio product photograph. Three-quarter front view, "
    "the entire chair visible including headrest, arms, five-star base and casters, "
    "centered on a seamless pure white background, soft even lighting with a faint "
    "floor shadow, photorealistic, sharp detail. No text, no logos, no labels, no "
    "watermark, no people."
)


def post(path, body):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def find_b64(obj):
    """Dig a base64 image out of a chat-completions response, whatever shape it takes."""
    if isinstance(obj, dict):
        for k in ("b64_json", "data"):
            v = obj.get(k)
            if isinstance(v, str) and len(v) > 1000:
                return v
        url = obj.get("url")
        if isinstance(url, str) and url.startswith("data:image"):
            return url.split(",", 1)[1]
        for v in obj.values():
            found = find_b64(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_b64(v)
            if found:
                return found
    elif isinstance(obj, str) and obj.startswith("data:image"):
        return obj.split(",", 1)[1]
    return None


def post_native(model, prompt):
    """Gemini's native API, which takes the key in the x-goog-api-key header."""
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        }).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def generate(prompt):
    errors = []
    for model in CHAT_MODELS:
        try:
            b64 = find_b64(post_native(model, prompt).get("candidates", []))
            if b64:
                return base64.b64decode(b64), model
            errors.append(f"{model} (native): no image in response")
        except urllib.error.HTTPError as e:
            errors.append(f"{model} (native): HTTP {e.code} {e.read()[:300]!r}")
    for model in CHAT_MODELS:
        try:
            r = post("/chat/completions", {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "modalities": ["image", "text"],
            })
            b64 = find_b64(r.get("choices", r))
            if b64:
                return base64.b64decode(b64), model
            errors.append(f"{model}: no image in response")
        except urllib.error.HTTPError as e:
            errors.append(f"{model}: HTTP {e.code} {e.read()[:300]!r}")
    for model in IMAGEN_MODELS:
        try:
            r = post("/images/generations", {
                "model": model, "prompt": prompt, "n": 1, "response_format": "b64_json",
            })
            return base64.b64decode(r["data"][0]["b64_json"]), model
        except urllib.error.HTTPError as e:
            errors.append(f"{model}: HTTP {e.code} {e.read()[:300]!r}")
    raise RuntimeError("; ".join(errors))


def main():
    with open(PROMPTS) as f:
        items = json.load(f)
    wanted = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    for item in items:
        if wanted and item["slug"] not in wanted:
            continue
        prompt = item["prompt"] if item.get("raw") else f"{item['prompt']} {STYLE}"
        print(f"-> {item['slug']} ...", flush=True)
        for attempt in range(3):
            try:
                data, model = generate(prompt)
                break
            except Exception as e:  # noqa: BLE001
                print(f"   attempt {attempt + 1} failed: {e}", flush=True)
                time.sleep(5 * (attempt + 1))
        else:
            continue
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail((item.get("max", 900), item.get("max", 900)))
        path = os.path.join(OUT, f"{item['slug']}.jpg")
        img.save(path, quality=86, optimize=True, progressive=True)
        print(f"   saved {path} ({img.width}x{img.height}) via {model}", flush=True)


if __name__ == "__main__":
    main()
