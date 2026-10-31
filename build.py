"""
Build index.html from template.html + data/*.csv

GitHub Pages can only show ready-made web pages, so this script turns the
spreadsheet (data/publications.csv) into the publication list inside index.html.
Run it after every change to the spreadsheet or template:

    python3 build.py

Spreadsheet columns (see 更新论文.md):
  no         number shown as [N]; papers are listed from the largest number down
  topic      coupled / agro / hydroclimate (several: agro;hydroclimate)
  status     published / review / chapter
  lead       y = show the "Lead author" tag
  year, authors, title, venue, details, link (DOI URL)
  pdf        file name in assets/papers/ or a web link
  thumbnail  file name in assets/img/papers/ (jpg/png/gif/mp4) or a web link
In authors, put * right after a name to underline it as corresponding author,
e.g.  Zhang, Z.*, Guan, K.   or   Wang, X., Zhang, Z., Kunstmann, H.*
Only the Python standard library is used.
"""
import csv
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
ME = "Zhang, Z."                      # how your name appears in author lists
STATUS_ORDER = {"review": 0, "published": 1, "chapter": 1}
SKIP = {"of", "and", "the", "for", "in", "on", "to"}


def read_csv(name):
    with open(ROOT / "data" / name, encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def abbrev(venue):
    """'Agricultural and Forest Meteorology' -> 'AFM' (used on placeholder thumbnails)."""
    if venue.lower().startswith(("under review", "submitted")):
        return "In review"
    if "ecological studies" in venue.lower() or "springer" in venue.lower():
        return "Chapter"
    venue = re.split(r"[(]", venue)[0]
    words = [w for w in re.split(r"[\s:–-]+", venue) if w and w.lower() not in SKIP]
    return "".join(w[0].upper() for w in words)[:5]


INITIALS = re.compile(r"[A-Z][A-Za-z]?\.(?:-?[A-Z][A-Za-z]?\.)*\*?")


def split_authors(text):
    """'Zhang, Z.*, Guan, K., et al.' -> ['Zhang, Z.*', 'Guan, K.', 'et al.']"""
    parts = [x.strip() for x in text.split(",") if x.strip()]
    names, i = [], 0
    while i < len(parts):
        if i + 1 < len(parts) and INITIALS.fullmatch(parts[i + 1]):
            names.append(f"{parts[i]}, {parts[i + 1]}")
            i += 2
        else:
            names.append(parts[i])
            i += 1
    return names


def authors_html(text):
    out = []
    for name in split_authors(text):
        corr = name.endswith("*")
        name = name.rstrip("*").strip()
        h = html.escape(name)
        if name == ME:
            h = f"<strong>{h}</strong>"
        if corr:
            h = f'<u class="corr" title="Corresponding author">{h}</u>'
        out.append(h)
    return ", ".join(out)


def number(pubs):
    """Order and number papers by the 'no' column you set in publications.csv
    (largest number shown first). Rows without a number go on top and get the
    next free numbers, with a warning so you can fill them in."""
    def num_of(p):
        try:
            return int(float(p.get("no", "")))
        except ValueError:
            return None
    have = [p for p in pubs if num_of(p) is not None]
    missing = [p for p in pubs if num_of(p) is None]
    for p in have:
        p["num"] = num_of(p)
    top = max([p["num"] for p in have], default=0)
    for i, p in enumerate(reversed(missing), 1):
        p["num"] = top + i
    if missing:
        print("WARNING: no number in column 'no' for:", "; ".join(p["title"][:50] for p in missing),
              f"-> shown on top as [{top + 1}]–[{top + len(missing)}]")
    seen = {}
    for p in pubs:
        seen.setdefault(p["num"], []).append(p["title"][:40])
    for n, titles in seen.items():
        if len(titles) > 1:
            print(f"WARNING: number {n} is used {len(titles)} times:", "; ".join(titles))
    return sorted(pubs, key=lambda p: -p["num"])


PDF_DIR = "assets/papers/"        # PDFs stored in the site itself
THUMB_DIR = "assets/img/papers/"  # thumbnails (jpg/png/gif/mp4)
VIDEO = (".mp4", ".webm", ".mov", ".m4v")


def local(value, folder):
    """'2024_AFM.pdf' -> 'assets/papers/2024_AFM.pdf'; full paths and web links are kept."""
    if not value or value.startswith(("http://", "https://", "/")) or "/" in value:
        return value
    return folder + value


DRIVE_ID = re.compile(r"drive\.google\.com/(?:open\?(?:.*&)?id=|file/d/|uc\?(?:.*&)?id=)([\w-]{20,})")


def drive_link(url):
    """Any Google Drive file link (open?id=..., file/d/.../view, uc?id=...) -> the standard preview link."""
    m = DRIVE_ID.search(url or "")
    return f"https://drive.google.com/file/d/{m.group(1)}/view" if m else url


def check_file(path, row):
    """Return the path if it is a web link or an existing file; otherwise warn and return ''."""
    if not path or path.startswith(("http://", "https://")) or (ROOT / path).exists():
        return path
    print(f"WARNING: file not found, not shown: {path}  ({row['title'][:50]})")
    return ""


def pub_html(p):
    e = html.escape
    num = f'<span class="pub-num">[{p["num"]}]</span> ' if p.get("num") else ""
    lead = p.get("lead", "").strip().lower() in ("y", "yes", "1", "x", "true")
    authors = authors_html(p["authors"])

    thumb_src = check_file(local(p["thumbnail"], THUMB_DIR), p)
    if thumb_src and thumb_src.lower().endswith(VIDEO):
        thumb = (f'<div class="pub-thumb media"><video src="{e(thumb_src)}" autoplay muted loop playsinline '
                 f'preload="metadata" aria-hidden="true"></video></div>')
    elif thumb_src:
        thumb = f'<div class="pub-thumb media"><img src="{e(thumb_src)}" alt="" loading="lazy" decoding="async"></div>'
    else:
        label = {"review": "In review", "chapter": "Chapter"}.get(p["status"]) or abbrev(p["venue"])
        small = p["year"] or ""
        thumb = f'<div class="pub-thumb ph" aria-hidden="true"><b>{e(label)}</b><small>{e(small)}</small></div>'

    if p["status"] == "review":
        # "Under review" is already shown as a badge; keep e.g. "Submitted to <journal>"
        venue = "" if p["venue"].lower().startswith("under review") else e(p["venue"])
    else:
        venue = f"<em>{e(p['venue'])}</em>"
    if p["details"] and p["status"] != "chapter":
        venue += f", {e(p['details'])}"
    if p["year"]:
        venue += f" ({e(p['year'])})"
    badges = ""
    if p["status"] == "review":
        badges += '<span class="badge review">Under review</span>'
    if p["status"] == "chapter":
        badges += '<span class="badge chapter">Book chapter</span>'
    if lead:
        badges += '<span class="badge lead">Lead author</span>'

    links = []
    if p["link"]:
        label = "DOI" if "doi.org/" in p["link"] else "Link"
        links.append(f'<a href="{e(p["link"])}" target="_blank" rel="noopener">{label}</a>')
    pdf = check_file(local(drive_link(p["pdf"]), PDF_DIR), p)
    if pdf:
        links.append(f'<a href="{e(pdf)}" target="_blank" rel="noopener">PDF</a>')
    links_html = f' <span class="pub-links">{"".join(links)}</span>' if links else ""

    tids = p["topics"]
    return f"""    <article class="pub topic-{tids[0]}" data-topics="{' '.join(tids)}" data-lead="{1 if lead else 0}">
      {thumb}
      <div>
        <div class="pub-title">{num}{e(p['title'])}</div>
        <div class="pub-authors">{authors}</div>
        <div class="pub-venue">{venue}{badges}{links_html}</div>
      </div>
    </article>"""


def main():
    topics = read_csv("topics.csv")
    pubs = read_csv("publications.csv")
    known = [t["topic_id"] for t in topics]

    # topic may list several topics separated by ";" (the first one sets the colour)
    for p in pubs:
        p["topics"] = [t.strip() for t in p.get("topic", "").split(";") if t.strip()]
    unknown = {t for p in pubs for t in p["topics"]} - set(known)
    if unknown:
        print("WARNING: unknown topic in publications.csv:", unknown)

    pubs = number(pubs)

    buttons = [f'<button type="button" class="on" data-topic="all">All topics <span>{len(pubs)}</span></button>']
    for t in topics:
        tid = t["topic_id"]
        n = sum(tid in p["topics"] for p in pubs)
        label = t.get("label") or t["title"]
        buttons.append(f'<button type="button" class="topic-{tid}" data-topic="{tid}" title="{html.escape(t["title"])}">'
                       f'{html.escape(label)} <span>{n}</span></button>')

    page = (ROOT / "template.html").read_text(encoding="utf-8")
    page = (page.replace("{{PUBLICATIONS}}", '  <div class="pub-list">\n' + "\n".join(pub_html(p) for p in pubs) + "\n  </div>")
                .replace("{{TOPIC_FILTER}}", "".join(buttons))
                .replace("{{UPDATED}}", date.today().strftime("%B %Y")))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html written: {len(pubs)} publications")


if __name__ == "__main__":
    main()
