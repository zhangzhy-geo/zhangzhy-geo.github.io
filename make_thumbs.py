"""
make_thumbs.py: turn figure screenshots into website thumbnails.

1. Put your screenshots in the folder  thumbs_raw/  (inside this homepage folder).
   Name each one the way you want the thumbnail to be called, e.g. 2024_AFM_Zhang.png
2. Run in Terminal:
       python3 make_thumbs.py
3. Thumbnails are written to  assets/img/papers/ . The script prints the file name
   to type into the 'thumbnail' column of data/publications.csv.

What it does to every screenshot:
  - trims white / near-white margins around the figure
  - flattens transparency onto white
  - scales it down to 800 px wide (never scales up; warns if the screenshot is too small)
  - saves PNG (sharp text and lines); switches to JPG if the PNG would be over 300 KB
Only new or changed screenshots are processed; use --force to redo all.

Options:
  python3 make_thumbs.py --force          redo every screenshot
  python3 make_thumbs.py --width 1000     different maximum width (default 800)
  python3 make_thumbs.py --aspect 4:3     also pad with white to a fixed shape
                                          (no cropping), e.g. 4:3 or 16:9

Needs Pillow once:  python3 -m pip install pillow
"""
import argparse
import io
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageOps
except ImportError:
    sys.exit("Pillow is not installed. Run:  python3 -m pip install pillow")

ROOT = Path(__file__).parent
SRC = ROOT / "thumbs_raw"
DST = ROOT / "assets" / "img" / "papers"
TYPES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
MAX_KB = 300
MIN_WIDTH = 600        # below this the thumbnail may look soft on high-resolution screens


def flatten(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def trim(im, tol=12, pad=0.02):
    """Cut away uniform white-ish borders, keep a small white margin."""
    diff = ImageChops.difference(im, Image.new("RGB", im.size, "white")).convert("L")
    box = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    if not box:
        return im
    im = im.crop(box)
    m = round(max(im.size) * pad)
    return ImageOps.expand(im, border=m, fill="white")


def to_aspect(im, aspect):
    w, h = im.size
    a, b = (float(x) for x in aspect.split(":"))
    target = a / b
    if w / h > target:                     # too wide -> add white top/bottom
        new = (w, round(w / target))
    else:                                  # too tall -> add white left/right
        new = (round(h * target), h)
    canvas = Image.new("RGB", new, "white")
    canvas.paste(im, ((new[0] - w) // 2, (new[1] - h) // 2))
    return canvas


def encode(im):
    """PNG if small enough, otherwise JPG. Returns (bytes, extension)."""
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    if buf.tell() <= MAX_KB * 1024:
        return buf.getvalue(), ".png"
    for q in (88, 82, 75):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q >= 85 else 2)
        if buf.tell() <= MAX_KB * 1024:
            break
    return buf.getvalue(), ".jpg"


def main():
    ap = argparse.ArgumentParser(description="Turn screenshots in thumbs_raw/ into thumbnails.")
    ap.add_argument("--force", action="store_true", help="redo every screenshot")
    ap.add_argument("--width", type=int, default=800, help="maximum width in pixels (default 800)")
    ap.add_argument("--aspect", help="pad to a fixed shape with white, e.g. 4:3 or 16:9")
    args = ap.parse_args()

    SRC.mkdir(exist_ok=True)
    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SRC.iterdir() if p.suffix.lower() in TYPES)
    if not files:
        print(f"No screenshots found. Put them in: {SRC}")
        return

    done = 0
    for src in files:
        stem = src.stem.strip().replace(" ", "_")
        old = [DST / (stem + ext) for ext in (".png", ".jpg")]
        newest = max((p.stat().st_mtime for p in old if p.exists()), default=0)
        if not args.force and newest >= src.stat().st_mtime:
            continue
        im = trim(flatten(Image.open(src)))
        raw_w = im.width
        if args.aspect:
            im = to_aspect(im, args.aspect)
        if im.width > args.width:
            im = im.resize((args.width, round(im.height * args.width / im.width)), Image.LANCZOS)
        data, ext = encode(im)
        for p in old:                      # remove an older PNG/JPG of the same name
            if p.exists():
                p.unlink()
        out = DST / (stem + ext)
        out.write_bytes(data)
        done += 1
        note = ""
        if raw_w < MIN_WIDTH:
            note = f"  ! screenshot only {raw_w}px wide after trimming: zoom in and capture again for a sharper image"
        print(f"{src.name:<34} -> thumbnail: {out.name:<28} {im.width}x{im.height}, {len(data) // 1024} KB{note}")

    if done:
        print(f"\n{done} thumbnail(s) saved in assets/img/papers/.")
        print("Type the file name after 'thumbnail:' into the thumbnail column, then run: python3 build.py")
    else:
        print("Nothing new to process (use --force to redo all).")


if __name__ == "__main__":
    main()
