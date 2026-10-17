#!/usr/bin/env python3
"""Generate the AI Library static site using the "Mastering System Design" design
system *verbatim* — its real assets (assets/system-design.css + system-design.js),
its Inter/JetBrains-Mono typography, Prism code highlighting, topbar + theme toggle,
hero + stat cards, chapter-card grids, and the chapter reading layout (TOC sidebar +
reading-progress bar).

Two content types, both markdown-sourced:

  1. TOOLS  — README.md tables between <!-- TOOLS:START --> / <!-- TOOLS:END -->.
              Output: index.html  (their home-hero + section/chapter-card grid)

  2. NOTES  — notes/<subject>/markdown/*.md (+ _subject.json). Output: notes.html,
              notes/<subject>/html/index.html (course landing), and
              notes/<subject>/html/<chapter>.html (their reading layout).
              A subject with "layout": "course" (System Design) is generated in its
              own course look instead: notes/<subject>/index.html + chapters/*.html
              (see render_course). A subject with "prebuilt": "<file>" ships its own
              ready-made HTML and is linked as-is instead of generated.

Their CSS/JS are linked from /assets (a copy lives in each prebuilt subject too).

Usage:  python scripts/build.py   (or: py scripts/build.py)
"""

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
NOTES_DIR = ROOT / "notes"
PROJECTS_DIR = ROOT / "projects"   # projects/<slug>/_project.json (+ prebuilt writeup)

START = "<!-- TOOLS:START -->"
END = "<!-- TOOLS:END -->"
LINK_RE = re.compile(r"\[(?P<name>.+?)\]\((?P<url>.+?)\)")
TAG_RE = re.compile(r"`([^`]+)`")
NUM_RE = re.compile(r"^\s*(\d+)\s*[-.]?\s*(.*)$")
BUILD_DATE = date.today().isoformat()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def h(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def chapter_meta(stem: str):
    m = NUM_RE.match(stem)
    if m and m.group(2).strip():
        return m.group(1), m.group(2).strip()
    return "", stem


def chapter_sort_key(path):
    m = NUM_RE.match(path.stem)
    if m and m.group(1):
        return (0, int(m.group(1)), path.stem.lower())
    return (1, 0, path.stem.lower())


def embed_md(text: str) -> str:
    return json.dumps(text, ensure_ascii=False).replace("</", "<\\/")


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_tools(md: str):
    if START not in md or END not in md:
        raise SystemExit("Could not find TOOLS markers in README.md")
    section = md.split(START, 1)[1].split(END, 1)[0]
    tools, current, subcat = [], None, None
    for raw in section.splitlines():
        line = raw.strip()
        heading = re.match(r"^##\s+(.*)$", line)
        if heading:
            current = heading.group(1).strip()
            subcat = None
            continue
        sub = re.match(r"^###\s+(.*)$", line)
        if sub:
            subcat = sub.group(1).strip()
            continue
        if not (line.startswith("|") and current):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "tool" or set(cells[0]) <= set("-: "):
            continue
        link = LINK_RE.search(cells[0])
        if not link:
            continue
        stars = ""
        sm = re.search(r"⭐\s*([\d,]+)", cells[0])
        if sm:
            stars = sm.group(1).replace(",", "")
        tags = [t.lstrip("#").strip() for t in TAG_RE.findall(cells[2]) if t.strip()]
        tools.append({
            "category": current, "subcategory": subcat,
            "name": link.group("name").strip(),
            "url": link.group("url").strip(), "description": cells[1].strip(),
            "tags": tags, "added": cells[3].strip(),
            "stars": stars,
        })
    return tools


def parse_subjects():
    subjects = []
    if not NOTES_DIR.exists():
        return subjects
    for sub in sorted(p for p in NOTES_DIR.iterdir() if p.is_dir()):
        meta_file = sub / "_subject.json"
        meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
        md_dir = sub / "markdown"
        md_files = list(md_dir.glob("*.md")) if md_dir.exists() else list(sub.glob("*.md"))
        md_files.sort(key=chapter_sort_key)
        chapters = []
        for md in md_files:
            num, title = chapter_meta(md.stem)
            chapters.append({"num": num, "title": title, "slug": slugify(md.stem),
                             "stem": md.stem, "text": md.read_text(encoding="utf-8")})
        subjects.append({
            "slug": sub.name,
            "title": meta.get("title", sub.name.replace("-", " ").title()),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "added": meta.get("added", ""),
            "prebuilt": meta.get("prebuilt"),
            # layout "course": the System Design course look (see render_course).
            "layout": meta.get("layout"),
            "course_title": meta.get("course_title"),
            "author": meta.get("author"),
            "intro": meta.get("intro"),
            "chapter_info": meta.get("chapters", {}),
            # library: generated like a subject, but surfaced from the Library catalogue
            # (a README entry links to it) and hidden from the Notes index.
            "library": meta.get("library", False),
            "eyebrow": meta.get("eyebrow"),
            "tagline": meta.get("tagline"),
            "stats": meta.get("stats", []),
            "learn": meta.get("learn", []),
            "phases": meta.get("phases", []),
            "cta_secondary": meta.get("cta_secondary"),
            "chapters": chapters,
        })
    return subjects


def parse_projects():
    """Each project = projects/<slug>/_project.json with a prebuilt writeup HTML
    that lives in the same folder; the source code stays in its own GitHub repo."""
    projects = []
    if not PROJECTS_DIR.exists():
        return projects
    for p in sorted(x for x in PROJECTS_DIR.iterdir() if x.is_dir()):
        meta_file = p / "_project.json"
        if not meta_file.exists():
            continue
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        projects.append({
            "slug": p.name,
            "title": meta.get("title", p.name),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "added": meta.get("added", ""),
            "repo": meta.get("repo", ""),
            "writeup": meta.get("writeup"),
        })
    return projects


def group_phases(s):
    chapters = s["chapters"]
    groups, used = [], set()
    info = s.get("chapter_info", {})

    def in_phase(c, ph):
        # A chapter's own "phase" (keyed by title, so it survives renumbering) wins
        # over the phase's numeric from/to range.
        named = info.get(c["title"], {}).get("phase")
        if named:
            return named == ph.get("title")
        frm, to = ph.get("from", 0), ph.get("to", 10**9)
        return c["num"].isdigit() and frm <= int(c["num"]) <= to

    for ph in s["phases"]:
        items = [c for c in chapters if c["slug"] not in used and in_phase(c, ph)]
        used.update(c["slug"] for c in items)
        groups.append([ph, items])
    leftovers = [c for c in chapters if c["slug"] not in used]
    if leftovers:
        (groups[-1][1].extend(leftovers) if groups else groups.append([{"title": "Chapters"}, leftovers]))
    return groups


# --------------------------------------------------------------------------- #
# Shared markup — their design system, linked verbatim
# --------------------------------------------------------------------------- #
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900'
         '&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">')
PRISM_CSS = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">'
PRISM_JS = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>')

# Entrance reveal + stat count-up. Bails out under reduced-motion; only hides elements
# once it has run (html.anim), so content is never stuck invisible if JS fails.
ANIM_JS = ('<script>(function(){'
           'if(window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches)return;'
           'document.documentElement.classList.add("anim");'
           'var io=new IntersectionObserver(function(es){es.forEach(function(e){'
           'if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);}});},'
           '{rootMargin:"0px 0px -6% 0px",threshold:.08});'
           'document.querySelectorAll(".chapter-card,.feed-card,.subcat-header,.home-section-header,.home-intro-card")'
           '.forEach(function(el,i){el.style.transitionDelay=((i%6)*45)+"ms";io.observe(el);});'
           'document.querySelectorAll(".home-stat-num").forEach(function(el){'
           'var m=el.textContent.trim().match(/^(\\D*)(\\d+)(.*)$/);if(!m)return;'
           'var pre=m[1],t=parseInt(m[2],10),post=m[3],s=null,dur=900;el.textContent=pre+"0"+post;'
           'function f(ts){if(!s)s=ts;var p=Math.min((ts-s)/dur,1);'
           'el.textContent=pre+Math.round(t*p)+post;if(p<1)requestAnimationFrame(f);else el.textContent=pre+t+post;}'
           'requestAnimationFrame(f);});'
           '})();</script>')

# Minimal glue so our nav/back links sit inside their topbar/sidebar using their tokens.
GLUE = (".topbar-actions .tnav{font-family:'Inter',sans-serif;font-weight:600;font-size:13px;"
        "color:var(--text-muted);text-decoration:none;padding:7px 12px;border-radius:8px;transition:all .2s}"
        ".topbar-actions .tnav:hover{color:var(--text);background:var(--bg-muted)}"
        ".topbar-actions .tnav.active{color:var(--primary)}"
        ".toc-back{display:inline-block;margin-bottom:14px;font-family:'JetBrains Mono',monospace;"
        "font-size:12px;color:var(--primary);text-decoration:none}.toc-back:hover{text-decoration:underline}"
        ".section-nav{display:flex;justify-content:center;gap:8px;padding:22px 0 4px}"
        ".section-nav a{font-family:'Inter',sans-serif;font-weight:600;font-size:14px;color:var(--text-muted);"
        "text-decoration:none;padding:9px 20px;border-radius:999px;border:1px solid var(--border);transition:all .2s}"
        ".section-nav a:hover{color:var(--text);background:var(--bg-muted)}"
        ".section-nav a.active{color:#fff;background:var(--primary);border-color:var(--primary)}"
        ".chapter-nav{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:52px 0 8px;padding-top:26px;border-top:1px solid var(--border)}"
        ".chapter-nav a{display:flex;flex-direction:column;gap:5px;max-width:48%;text-decoration:none;"
        "border:1px solid var(--border);border-radius:12px;padding:14px 18px;background:var(--bg-elevated);"
        "transition:border-color .2s,background .2s,transform .2s}"
        ".chapter-nav a:hover{border-color:var(--primary);background:var(--bg-muted);transform:translateY(-2px)}"
        ".chapter-nav .cn-next{margin-left:auto;text-align:right;align-items:flex-end}"
        ".chapter-nav span{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.06em;"
        "text-transform:uppercase;color:var(--text-muted)}"
        ".chapter-nav strong{font-family:'Inter',sans-serif;font-weight:600;font-size:15px;color:var(--text)}"
        ".repo-badge{display:inline-flex;align-items:center;gap:5px;font-family:'JetBrains Mono',monospace;"
        "font-size:10px;font-weight:600;letter-spacing:.04em;color:var(--text);background:var(--bg-muted);"
        "border:1px solid var(--border);border-radius:999px;padding:3px 9px;line-height:1}"
        ".repo-badge svg{flex:none}"
        # --- entrance + scroll-reveal animations (respect reduced-motion; safe without JS) ---
        "@media(prefers-reduced-motion:no-preference){"
        "@keyframes ail-rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}"
        ".home-hero>*{animation:ail-rise .7s cubic-bezier(.2,.8,.2,1) both}"
        ".home-hero>*:nth-child(2){animation-delay:.07s}.home-hero>*:nth-child(3){animation-delay:.14s}"
        ".home-hero>*:nth-child(4){animation-delay:.21s}.home-hero>*:nth-child(5){animation-delay:.28s}"
        "html.anim .subcat-header,html.anim .chapter-card,html.anim .feed-card,html.anim .home-section-header,html.anim .home-intro-card{"
        "opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s cubic-bezier(.2,.8,.2,1)}"
        "html.anim .chapter-card.in,html.anim .feed-card.in,html.anim .subcat-header.in,html.anim .home-section-header.in,html.anim .home-intro-card.in{opacity:1;transform:none}"
        ".chapter-card,.feed-card{transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s,border-color .25s,opacity .6s ease}"
        "}")


def head(title, desc, root, extra_head=""):
    return ("".join([
        '<!doctype html><html lang="en" data-theme="light"><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>{h(title)}</title><meta name=\"description\" content=\"{h(desc)}\">",
        FONTS, PRISM_CSS,
        f'<link rel="stylesheet" href="{root}assets/system-design.css">',
        f"<style>{GLUE}</style>{extra_head}</head>",
    ]))


def topbar(root, active, menu=False, nav=True):
    lib = " active" if active == "library" else ""
    nts = " active" if active == "notes" else ""
    prj = " active" if active == "projects" else ""
    menubtn = ('<button class="icon-btn menu-btn" id="menuBtn" aria-label="Open menu">&#9776;</button>'
               if menu else "")
    links = ""
    if nav:
        links = (f'<a class="tnav{lib}" href="{root}index.html">Library</a>'
                 f'<a class="tnav{nts}" href="{root}notes.html">Notes</a>'
                 f'<a class="tnav{prj}" href="{root}projects.html">Projects</a>')
    return ("".join([
        '<header class="topbar"><a class="brand" href="', root, 'index.html">',
        '<span class="brand-icon">AI</span><span>AI Library</span></a><div class="topbar-actions">',
        links,
        '<button class="icon-btn" id="themeToggle" aria-label="Toggle theme">&#127769;</button>',
        menubtn, '</div></header>',
    ]))


def section_nav(root, active):
    lib = " active" if active == "library" else ""
    nts = " active" if active == "notes" else ""
    prj = " active" if active == "projects" else ""
    return (f'<nav class="section-nav"><a class="{lib.strip()}" href="{root}index.html">Library</a>'
            f'<a class="{nts.strip()}" href="{root}notes.html">Notes</a>'
            f'<a class="{prj.strip()}" href="{root}projects.html">Projects</a></nav>')


def page_scripts(root):
    return PRISM_JS + f'<script src="{root}assets/system-design.js"></script>' + ANIM_JS


def shell_page(title, desc, root, active, hero, main_html, extra_head=""):
    # home.css holds their landing-specific styles (.home-hero/.home-stats/.chapter-card/…),
    # which live inline in their index.html rather than in system-design.css.
    extra_head = f'<link rel="stylesheet" href="{root}assets/home.css">' + extra_head
    return ("".join([
        head(title, desc, root, extra_head),
        '<body><div class="progress-bar" id="progressBar"></div>',
        topbar(root, active, menu=False, nav=False),
        hero,
        section_nav(root, active),
        f'<main class="home-container">{main_html}</main>',
        page_scripts(root), "</body></html>",
    ]))


# --------------------------------------------------------------------------- #
# Cards
# --------------------------------------------------------------------------- #
# GitHub octocat mark, shown as a badge on cards that link to a github.com repo.
GH_SVG = ('<svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor" aria-hidden="true"><path d="'
          'M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49'
          '-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58'
          ' 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31'
          '-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09'
          ' 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87'
          ' 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 '
          '0016 8c0-4.42-3.58-8-8-8z"/></svg>')


def head_marker(url):
    """Top-right card marker: a GitHub badge for repo links, else a directional arrow."""
    if "github.com" in url:
        return f'<span class="repo-badge">{GH_SVG} GitHub</span>'
    return '<span class="chapter-icon">&#8599;</span>' if url.startswith("http") else '<span class="chapter-icon">&rarr;</span>'


def tool_card(t):
    """Single-column feed card — purpose, audience, and a clear deep-dive CTA."""
    tags = "".join(f'<span class="feed-tag">#{h(x)}</span>' for x in t["tags"])
    tgt = ' target="_blank" rel="noopener"' if t["url"].startswith("http") else ''
    is_github = "github.com" in t["url"]
    badge = (f'<span class="feed-gh"><svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg> View on GitHub</span>' if is_github
         else '<span class="feed-gh" style="opacity:.6">Read in-library &rarr;</span>')
    stars = t.get("stars", "")
    stars_html = f'<div class="feed-stars">⭐ {int(stars):,}</div>' if stars.isdigit() else ''
    return ("".join([
        f'<a class="feed-card" href="{h(t["url"])}"{tgt}>',
        f'<div class="feed-top"><span class="feed-title">{h(t["name"])}</span>',
        f'<span class="feed-meta"><span class="feed-date">{h(t["added"])}</span></span></div>',
        stars_html,
        f'<div class="feed-desc">{h(t["description"])}</div>',
        f'<div class="feed-bottom"><div class="feed-tags">{tags}</div>',
        badge,
        '</div></a>',
    ]))


def subject_card(s):
    entry = s["prebuilt"] or ("index.html" if s["layout"] == "course" else "html/index.html")
    n = len(s["chapters"])
    return ("".join([
        f'<a class="chapter-card" href="notes/{h(s["slug"])}/{entry}">',
        f'<div class="chapter-card-head"><span class="chapter-num">{n} chapters</span></div>',
        f'<h3 class="chapter-title">{h(s["title"])}</h3>',
        f'<p class="chapter-desc">{h(s["description"])}</p>',
        '<div class="chapter-card-foot">Open &rarr;</div></a>',
    ]))


def project_card(p):
    tags = "  ".join("#" + x for x in p["tags"])
    raw = f'projects/{p["slug"]}/{p["writeup"]}' if p["writeup"] else p["repo"]
    tgt = ' target="_blank" rel="noopener"' if raw.startswith("http") else ''
    return ("".join([
        f'<a class="chapter-card" href="{h(raw)}"{tgt}>',
        f'<div class="chapter-card-head"><span class="chapter-num">{h(p["added"])}</span>'
        f'{head_marker(raw)}</div>',
        f'<h3 class="chapter-title">{h(p["title"])}</h3>',
        f'<p class="chapter-desc">{h(p["description"])}</p>',
        f'<div class="chapter-card-foot">{h(tags)}</div></a>',
    ]))


def chapter_card(c):
    label = ("Ch " + c["num"]) if c["num"] else "Ref"
    return ("".join([
        f'<a class="chapter-card" href="{h(c["slug"])}.html">',
        f'<div class="chapter-card-head"><span class="chapter-num">{h(label)}</span></div>',
        f'<h3 class="chapter-title">{h(c["title"])}</h3>',
        '<div class="chapter-card-foot">Read &rarr;</div></a>',
    ]))


def stats_block(stats):
    return ('<div class="home-stats">' + "".join(
        f'<div><div class="home-stat-num">{h(st["num"])}</div>'
        f'<div class="home-stat-label">{h(st["label"])}</div></div>' for st in stats) + '</div>')


# --------------------------------------------------------------------------- #
# Renderers
# --------------------------------------------------------------------------- #
def render_library(tools, subjects, projects):
    cats = sorted({t["category"] for t in tools}, key=str.lower)
    note_subjects = [s for s in subjects if not s["library"]]
    hero = ("".join([
        '<section class="home-hero"><span class="home-eyebrow">Curated archive</span>',
        '<h1>AI Library</h1>',
        '<p class="home-tagline">A living catalogue of open-source AI tools &amp; resources worth '
        'remembering — indexed, tagged, and dated, so the good ones never slip away.</p>',
        stats_block([{"num": str(len(tools)), "label": "Tools"},
                     {"num": str(len(cats)), "label": "Categories"},
                     {"num": str(len(note_subjects)), "label": "Note Subjects"},
                     {"num": str(len(projects)), "label": "Projects"}]),
        '</section>',
    ]))
    sections = []
    for cat in cats:
        items = [t for t in tools if t["category"] == cat]
        # Group by subcategory, preserving order of first appearance
        subcats = []
        seen = set()
        for t in items:
            s = t.get("subcategory") or ""
            if s not in seen:
                seen.add(s)
                subcats.append(s)
        if subcats == [""]:
            # No sub-headings — render as flat list
            cards = "".join(tool_card(t) for t in items)
            sections.append(
                f'<section><div class="home-section-header"><h2>{h(cat)}</h2>'
                f'<span class="count">{len(items)} {"tool" if len(items)==1 else "tools"}</span></div>'
                f'<div class="feed-list">{cards}</div></section>')
        else:
            parts = []
            for sc in subcats:
                sc_items = [t for t in items if (t.get("subcategory") or "") == sc]
                cards = "".join(tool_card(t) for t in sc_items)
                if sc:
                    parts.append(
                        f'<h3 class="subcat-header">{h(sc)}</h3>'
                        f'<div class="feed-list">{cards}</div>')
                else:
                    parts.append(f'<div class="feed-list">{cards}</div>')
            sections.append(
                f'<section><div class="home-section-header"><h2>{h(cat)}</h2>'
                f'<span class="count">{len(items)} {"tool" if len(items)==1 else "tools"}</span></div>'
                + "".join(parts) + '</section>')
    html = shell_page("AI Library — curated open-source AI tools",
                      "A living, curated catalogue of open-source AI tools and resources.",
                      "", "library", hero, "".join(sections))
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def render_notes_index(subjects):
    note_subjects = [s for s in subjects if not s["library"]]
    total_ch = sum(len(s["chapters"]) for s in note_subjects)
    hero = ("".join([
        '<section class="home-hero"><span class="home-eyebrow">Field notes</span>',
        '<h1>Notes</h1>',
        '<p class="home-tagline">Long-form study notes, language references, and cheatsheets — '
        'organised by subject and chapter, rendered for reading.</p>',
        stats_block([{"num": str(len(note_subjects)), "label": "Subjects"},
                     {"num": str(total_ch), "label": "Chapters"}]),
        '</section>',
    ]))
    cards = "".join(subject_card(s) for s in note_subjects) or '<p>No notes yet.</p>'
    main = (f'<section><div class="home-section-header"><h2>Subjects</h2>'
            f'<span class="count">{len(note_subjects)} subjects</span></div>'
            f'<div class="chapter-list">{cards}</div></section>')
    html = shell_page("Notes — AI Library", "Long-form study notes, references, and cheatsheets.",
                      "", "notes", hero, main)
    (ROOT / "notes.html").write_text(html, encoding="utf-8")


def render_projects_index(projects):
    hero = ("".join([
        "<section class=\"home-hero\"><span class=\"home-eyebrow\">Things I've built</span>",
        '<h1>Projects</h1>',
        '<p class="home-tagline">Hands-on AI projects — each with a full writeup here in the library, '
        'and the source code on GitHub.</p>',
        stats_block([{"num": str(len(projects)), "label": "Projects"}]),
        '</section>',
    ]))
    cards = "".join(project_card(p) for p in projects) or '<p>No projects yet.</p>'
    main = (f'<section><div class="home-section-header"><h2>All Projects</h2>'
            f'<span class="count">{len(projects)} {"project" if len(projects)==1 else "projects"}</span></div>'
            f'<div class="chapter-list">{cards}</div></section>')
    html = shell_page("Projects — AI Library", "Hands-on AI projects with writeups and source code.",
                      "", "projects", hero, main)
    (ROOT / "projects.html").write_text(html, encoding="utf-8")


def render_subject(s):
    root = "../../../"
    chapters = s["chapters"]
    first = chapters[0]["slug"] if chapters else ""
    eyebrow = s.get("eyebrow") or f"A {len(chapters)}-chapter reference"
    tagline = s.get("tagline") or s.get("description", "")
    cta = f'<a class="home-btn home-btn-primary" href="{h(first)}.html">Start reading &rarr;</a>'
    if s.get("cta_secondary"):
        cta += (f'<a class="home-btn home-btn-secondary" href="{h(s["cta_secondary"]["slug"])}.html">'
                f'{h(s["cta_secondary"]["label"])}</a>')
    stats = s["stats"] or [{"num": str(len(chapters)), "label": "Chapters"}]
    hero = ("".join([
        f'<section class="home-hero"><span class="home-eyebrow">{h(eyebrow)}</span>',
        f'<h1>{h(s["title"])}</h1><p class="home-tagline">{h(tagline)}</p>',
        f'<div class="home-cta-row">{cta}</div>', stats_block(stats), '</section>',
    ]))
    main = ""
    if s["learn"]:
        items = "".join(f"<li>{h(x)}</li>" for x in s["learn"])
        main += ('<div class="home-intro-card"><div><h3>What you&rsquo;ll learn</h3></div>'
                 f'<ul class="home-intro-list">{items}</ul></div>')
    if s["phases"]:
        for ph, items in group_phases(s):
            if not items:
                continue
            cards = "".join(chapter_card(c) for c in items)
            title = (ph.get("icon", "") + " " + ph.get("title", "")).strip()
            rng = ph.get("range") or f'{len(items)} chapters'
            main += (f'<section><div class="home-section-header"><h2>{h(title)}</h2>'
                     f'<span class="count">{h(rng)}</span></div>'
                     f'<div class="chapter-list">{cards}</div></section>')
    else:
        cards = "".join(chapter_card(c) for c in chapters)
        main += (f'<section><div class="home-section-header"><h2>Chapters</h2>'
                 f'<span class="count">{len(chapters)} chapters</span></div>'
                 f'<div class="chapter-list">{cards}</div></section>')
    html = shell_page(f'{s["title"]} — Notes', s["description"], root, "notes", hero, main)
    out = NOTES_DIR / s["slug"] / "html"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")


def render_chapter(s, idx):
    root = "../../../"
    chapters = s["chapters"]
    ch = chapters[idx]
    label = ("Chapter " + ch["num"]) if ch["num"] else s["title"]
    prev_ch = chapters[idx - 1] if idx > 0 else None
    next_ch = chapters[idx + 1] if idx < len(chapters) - 1 else None
    chapter_nav = ""
    if prev_ch or next_ch:
        prev_html = (f'<a class="cn-prev" href="{h(prev_ch["slug"])}.html"><span>&larr; Previous</span>'
                     f'<strong>{h(prev_ch["title"])}</strong></a>' if prev_ch else "<span></span>")
        next_html = (f'<a class="cn-next" href="{h(next_ch["slug"])}.html"><span>Next &rarr;</span>'
                     f'<strong>{h(next_ch["title"])}</strong></a>' if next_ch else "")
        chapter_nav = f'<nav class="chapter-nav">{prev_html}{next_html}</nav>'
    sidebar = (f'<a class="toc-back" href="index.html">&larr; {h(s["title"])}</a>'
               '<h3>On this page</h3><ul class="toc-list" id="tocList"></ul>')
    hero = (f'<section class="hero"><span class="chapter-label">{h(label)}</span>'
            f'<h1>{h(ch["title"])}</h1></section>')
    # Render markdown into <main> as direct children (so their .main element styles apply),
    # then build the TOC from the H2s. Runs before their system-design.js (Prism + TOC observer).
    render_js = ("".join([
        '<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>',
        '<script>const MD=', embed_md(ch["text"]),
        ';marked.setOptions({gfm:true,breaks:false});',
        'var m=document.getElementById("main");m.insertAdjacentHTML("beforeend",marked.parse(MD));',
        'var _h=document.querySelector(".hero h1"),_c=m.querySelector(":scope > h1");'
        'if(_h&&_c&&_c.textContent.trim().toLowerCase()===_h.textContent.trim().toLowerCase())_c.remove();',
        'var toc=document.getElementById("tocList"),seen={};',
        'm.querySelectorAll("h2").forEach(function(hd){',
        'var id=hd.id||hd.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");',
        'if(seen[id]){id=id+"-"+(++seen[id])}else{seen[id]=1}hd.id=id;',
        'var li=document.createElement("li"),a=document.createElement("a");',
        'a.href="#"+id;a.textContent=hd.textContent;li.appendChild(a);toc.appendChild(li);});',
        (f'm.insertAdjacentHTML("beforeend",{embed_md(chapter_nav)});' if chapter_nav else ''),
        '</script>',
    ]))
    html = ("".join([
        head(f'{ch["title"]} — {s["title"]}', f'{s["title"]}: {ch["title"]}', root),
        '<body><div class="progress-bar" id="progressBar"></div>',
        topbar(root, "notes", menu=True),
        '<div class="overlay" id="overlay"></div>',
        f'<div class="layout"><aside class="sidebar" id="sidebar">{sidebar}</aside>',
        f'<main class="main" id="main">{hero}</main></div>',
        render_js, page_scripts(root), "</body></html>",
    ]))
    out = NOTES_DIR / s["slug"] / "html"
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{ch["slug"]}.html').write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Course layout — the System Design subject's own look (layout: "course").
# Writes notes/<subject>/index.html + chapters/<md stem>.html, styled by the
# subject's assets/system-design.css (+ assets/home.css for the landing page).
# Per-chapter card data (icon, short title, summary, subtitle, phase) lives in
# _subject.json "chapters", keyed by chapter title so renumbering keeps it.
# --------------------------------------------------------------------------- #
COURSE_FONTS = FONTS.replace("800;900", "800")
BACK_PILL = ('<a href="{root}notes.html" data-ailib-back style="position:fixed;left:16px;bottom:16px;'
             'z-index:99999;font-family:Inter,system-ui,sans-serif;font-size:12px;font-weight:600;'
             'background:#0f172a;color:#fff;padding:9px 14px;border-radius:999px;text-decoration:none;'
             'box-shadow:0 6px 20px rgba(0,0,0,.28)">&#8592; AI Library</a>')
COURSE_CSS = (".main .mermaid{display:flex;justify-content:center;margin:24px 0;padding:20px;"
              "background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);"
              "overflow-x:auto}.main .mermaid svg{max-width:100%;height:auto}")
MARKED_JS = "https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"
MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
PRISM_AUTOLOADER = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/'
                    'prism-autoloader.min.js"></script>')

# Runs after marked has rendered the chapter into <main>: GitHub-style heading ids
# (so in-page links work), sidebar TOC from the H2s, drop the markdown's own
# "Table of Contents" section (the sidebar replaces it), wrap tables, style the
# Learning Outcomes list, open external links in a new tab, and turn ```mermaid
# blocks into diagrams that re-render when the theme is toggled.
COURSE_RENDER_JS = r"""
var m=document.getElementById("main"),nav=m.querySelector(":scope > .chapter-nav");
var tmp=document.createElement("div");tmp.innerHTML=marked.parse(MD,{gfm:true,breaks:false});
while(tmp.firstChild){m.insertBefore(tmp.firstChild,nav);}
var seen={};
m.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach(function(hd){
 if(hd.closest(".hero"))return;
 var id=hd.textContent.trim().toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu,"").replace(/\s/g,"-");
 if(seen[id]!==undefined){id=id+"-"+(++seen[id]);}else{seen[id]=0;}hd.id=id;});
m.querySelectorAll(":scope > h2").forEach(function(hd){
 if(!/^table of contents$/i.test(hd.textContent.trim()))return;
 var n=hd.nextElementSibling;
 while(n&&n.tagName!=="H2"&&n!==nav){var x=n.nextElementSibling;n.remove();n=x;}
 var p=hd.previousElementSibling;if(p&&p.tagName==="HR")p.remove();hd.remove();});
var toc=document.getElementById("tocList");
m.querySelectorAll(m.querySelector(":scope > h2")?":scope > h2":":scope > h1").forEach(function(hd){
 var li=document.createElement("li"),a=document.createElement("a");
 a.href="#"+hd.id;a.textContent=hd.textContent;li.appendChild(a);toc.appendChild(li);});
m.querySelectorAll("table").forEach(function(t){
 var w=document.createElement("div");w.className="table-wrapper";t.parentNode.insertBefore(w,t);w.appendChild(t);});
m.querySelectorAll(":scope > h2").forEach(function(hd){
 if(!/learning outcomes/i.test(hd.textContent))return;
 var n=hd.nextElementSibling;while(n&&n.tagName==="P")n=n.nextElementSibling;
 if(!n||n.tagName!=="OL")return;n.className="outcomes-list";
 Array.prototype.forEach.call(n.children,function(li,i){
  var s=document.createElement("span");s.innerHTML=li.innerHTML;li.innerHTML="";
  var k=document.createElement("span");k.className="outcome-num";k.textContent=i+1;
  li.appendChild(k);li.appendChild(s);});});
m.querySelectorAll("a[href]").forEach(function(a){var u=a.getAttribute("href");
 if(!/^[a-z][a-z0-9+.-]*:|^\/\//i.test(u))a.setAttribute("href",u.replace(/\.md(?=[?#]|$)/i,".html"));});
m.querySelectorAll('a[href^="http"]').forEach(function(a){a.target="_blank";a.rel="noopener";});
var dia=[];
m.querySelectorAll("pre > code.language-mermaid").forEach(function(c){
 var d=document.createElement("div");d.className="mermaid";d.textContent=c.textContent;
 c.parentNode.replaceWith(d);dia.push([d,c.textContent]);});
async function drawMermaid(){
 if(!dia.length||typeof mermaid==="undefined")return;
 var dark=document.documentElement.getAttribute("data-theme")==="dark";
 mermaid.initialize({startOnLoad:false,securityLevel:"strict",theme:dark?"dark":"default"});
 var nodes=[];
 for(var i=0;i<dia.length;i++){var p=dia[i];
  if(!p[2]&&!(await mermaid.parse(p[1],{suppressErrors:true}))){
   // Invalid diagram source: show it as a code block instead of mermaid's error box.
   var pre=document.createElement("pre"),code=document.createElement("code");
   code.textContent=p[1];pre.appendChild(code);p[0].replaceWith(pre);dia.splice(i--,1);continue;}
  p[2]=true;p[0].removeAttribute("data-processed");p[0].textContent=p[1];nodes.push(p[0]);}
 if(nodes.length)mermaid.run({nodes:nodes});}
window.addEventListener("load",function(){drawMermaid();
 new MutationObserver(drawMermaid).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});});
"""


def fill_counts(text, counts):
    """Expand {chapters} and {count:<phase title>} placeholders in _subject.json text."""
    return re.sub(r"\{(chapters|count:[^}]+)\}", lambda m: str(counts.get(m.group(1), m.group(0))), text)


def course_phase_range(items):
    nums = [int(c["num"]) for c in items if c["num"]]
    rng = ""
    if nums:
        rng = (f"Chapter {nums[0]}" if len(nums) == 1 else f"Chapters {min(nums)}–{max(nums)}")
    extras = [c["title"] for c in items if not c["num"]]
    return " + ".join(([rng] if rng else []) + extras)


def course_href(c):
    return "chapters/" + quote(c["stem"]) + ".html"


def course_index(s, groups, counts):
    title = s["course_title"] or s["title"]
    info = s["chapter_info"]
    chapters = s["chapters"]
    ctas = ""
    if chapters:
        ctas += (f'<a class="home-btn home-btn-primary" href="{h(course_href(chapters[0]))}">'
                 'Start the Course →</a>')
    sec = s.get("cta_secondary") or {}
    target = next((c for c in chapters if c["title"] == sec.get("chapter")), None)
    if target:
        ctas += (f'<a class="home-btn home-btn-secondary" href="{h(course_href(target))}">'
                 f'{h(sec["label"])}</a>')
    stats = [{"num": fill_counts(st["num"], counts), "label": st["label"]} for st in s["stats"]]
    intro = ""
    if s["learn"]:
        items = "".join(f"<li>{h(x)}</li>" for x in s["learn"])
        para = f'<p>{h(s["intro"])}</p>' if s["intro"] else ""
        intro = (f'<div class="home-intro-card"><div><h3>What you\'ll learn</h3>{para}</div>'
                 f'<ul class="home-intro-list">{items}</ul></div>')
    sections = []
    for ph, items in groups:
        if not items:
            continue
        cards = []
        for c in items:
            ci = info.get(c["title"], {})
            label = f'CH {int(c["num"]):02d}' if c["num"] else "REF"
            foot = "Start here →" if c is chapters[0] else ph.get("foot", "Read chapter →")
            desc = f'<p class="chapter-desc">{h(ci["summary"])}</p>' if ci.get("summary") else ""
            cards.append("".join([
                f'<a class="chapter-card" href="{h(course_href(c))}">',
                f'<div class="chapter-card-head"><span class="chapter-num">{label}</span>',
                f'<span class="chapter-icon">{h(ci.get("icon", "📄"))}</span></div>',
                f'<h3 class="chapter-title">{h(ci.get("short") or c["title"])}</h3>', desc,
                f'<div class="chapter-card-foot">{h(foot)}</div></a>',
            ]))
        heading = (ph.get("icon", "") + " " + ph.get("title", "")).strip()
        style = ' style="margin-top: 64px;"' if sections else ""
        sections.append(f'<section{style}><div class="home-section-header"><h2>{h(heading)}</h2>'
                        f'<span class="count">{h(course_phase_range(items))}</span></div>'
                        f'<div class="chapter-list">{"".join(cards)}</div></section>')
    footer = (f'<footer class="home-footer"><p>Course content by {h(s["author"])} · '
              'Built with the system-design HTML framework</p></footer>' if s["author"] else "")
    return "".join([
        '<!DOCTYPE html><html lang="en" data-theme="light"><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{h(title)} — Course Home</title><meta name="description" content="{h(s["description"])}">',
        FONTS, '<link rel="stylesheet" href="assets/system-design.css">',
        '<link rel="stylesheet" href="assets/home.css"></head><body>',
        BACK_PILL.format(root="../../"),
        '<header class="topbar"><a class="brand" href="index.html"><span class="brand-icon">SD</span>',
        f'<span>{h(title)}</span></a><div class="topbar-actions">',
        '<button class="icon-btn" id="themeToggle" aria-label="Toggle theme">🌙</button></div></header>',
        f'<section class="home-hero"><span class="home-eyebrow">{h(fill_counts(s["eyebrow"] or "", counts))}</span>',
        f'<h1>{h(title)}</h1><p class="home-tagline">{h(s["tagline"] or s["description"])}</p>',
        f'<div class="home-cta-row">{ctas}</div>', stats_block(stats), '</section>',
        f'<main class="home-container">{intro}{"".join(sections)}</main>', footer,
        '<script src="assets/system-design.js"></script></body></html>',
    ])


def course_chapter(s, idx, phase_of):
    title = s["course_title"] or s["title"]
    chapters = s["chapters"]
    ch = chapters[idx]
    ci = s["chapter_info"].get(ch["title"], {})
    short = ci.get("short") or ch["title"]
    name = f'Chapter {ch["num"]}' if ch["num"] else short
    ph = phase_of.get(ch["slug"], {})
    label = name + (f' · {ph["label"]}' if ch["num"] and ph.get("label") else "")
    # A numbered chapter's leading "# Heading" becomes the hero title; unnumbered pages
    # (e.g. Resources) use their short title and keep their headings in the body.
    text = ch["text"].lstrip("﻿")
    hm = re.match(r"\s*#\s+(.+?)\s*#*\s*(?:\n|$)", text) if ch["num"] else None
    heading = hm.group(1) if hm else short
    if hm:
        text = text[hm.end():]

    def nav_card(c, cls, word):
        cname = f'Chapter {c["num"]} — ' if c["num"] else ""
        cshort = s["chapter_info"].get(c["title"], {}).get("short") or c["title"]
        return (f'<a class="chapter-nav-card{cls}" href="{h(quote(c["stem"]))}.html">'
                f'<div class="chapter-nav-label">{word}</div>'
                f'<div class="chapter-nav-title">{h(cname + cshort)}</div></a>')

    nav = ""
    if idx > 0:
        nav += nav_card(chapters[idx - 1], "", "← Previous")
    if idx < len(chapters) - 1:
        nav += nav_card(chapters[idx + 1], " next", "Next chapter →")
    subtitle = f'<p class="hero-subtitle">{h(ci["subtitle"])}</p>' if ci.get("subtitle") else ""
    author = f'<div class="hero-author">By {h(s["author"])}</div>' if s["author"] else ""
    toc_head = f"{name} — On This Page" if ch["num"] else "On This Page"
    return "".join([
        '<!DOCTYPE html><html lang="en" data-theme="light"><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{h(name if not ch["num"] else name + " — " + short)}</title>',
        COURSE_FONTS, PRISM_CSS, '<link rel="stylesheet" href="../assets/system-design.css">',
        f'<style>{COURSE_CSS}</style></head><body>',
        BACK_PILL.format(root="../../../"),
        '<div class="progress-bar" id="progressBar"></div>',
        '<header class="topbar"><a class="brand" href="../index.html"><span class="brand-icon">SD</span>',
        f'<span>{h(title)}</span></a><div class="topbar-actions">',
        '<button class="icon-btn menu-btn" id="menuBtn" aria-label="Open menu">☰</button>',
        '<button class="icon-btn" id="themeToggle" aria-label="Toggle theme">🌙</button></div></header>',
        '<div class="overlay" id="overlay"></div>',
        f'<div class="layout"><aside class="sidebar" id="sidebar"><h3>{h(toc_head)}</h3>',
        '<ul class="toc-list" id="tocList"></ul></aside>',
        '<main class="main" id="main"><section class="hero">',
        f'<span class="chapter-label">{h(label)}</span><h1>{h(heading)}</h1>{subtitle}{author}</section>',
        f'<nav class="chapter-nav">{nav}</nav></main></div>',
        f'<script src="{MARKED_JS}"></script><script src="{MERMAID_JS}"></script>',
        f'<script>const MD={embed_md(text)};{COURSE_RENDER_JS}</script>',
        PRISM_JS, PRISM_AUTOLOADER, '<script src="../assets/system-design.js"></script>',
        '</body></html>',
    ])


def render_course(s):
    groups = group_phases(s) if s["phases"] else [[{"title": "Chapters"}, s["chapters"]]]
    counts = {"chapters": sum(1 for c in s["chapters"] if c["num"])}
    phase_of = {}
    for ph, items in groups:
        counts["count:" + ph.get("title", "")] = len(items)
        phase_of.update((c["slug"], ph) for c in items)
    for c in s["chapters"]:
        if c["title"] not in s["chapter_info"]:
            print(f'  note: {s["slug"]}: no _subject.json "chapters" entry for "{c["title"]}" (using defaults)')
    base = NOTES_DIR / s["slug"]
    (base / "index.html").write_text(course_index(s, groups, counts), encoding="utf-8")
    out = base / "chapters"
    out.mkdir(parents=True, exist_ok=True)
    keep = set()
    for i, c in enumerate(s["chapters"]):
        (out / f'{c["stem"]}.html').write_text(course_chapter(s, i, phase_of), encoding="utf-8")
        keep.add(f'{c["stem"]}.html')
    # Drop pages whose markdown is gone (renamed, renumbered or removed chapters).
    for old in out.glob("*.html"):
        if old.name not in keep:
            old.unlink()
            print(f"  removed stale {old.relative_to(ROOT)}")


def main():
    tools = parse_tools(README.read_text(encoding="utf-8"))
    subjects = parse_subjects()
    projects = parse_projects()
    render_library(tools, subjects, projects)
    render_notes_index(subjects)
    render_projects_index(projects)
    gen = 0
    for s in subjects:
        if s["prebuilt"]:
            continue
        if s["layout"] == "course":
            render_course(s)
            gen += 1
            continue
        render_subject(s)
        for i in range(len(s["chapters"])):
            render_chapter(s, i)
        gen += 1
    cats = len({t["category"] for t in tools})
    chs = sum(len(s["chapters"]) for s in subjects)
    print(f"Built (System Design theme): {len(tools)} tools / {cats} categories  +  "
          f"{len(subjects)} subjects ({gen} generated) / {chs} chapters  +  {len(projects)} projects")


if __name__ == "__main__":
    main()
