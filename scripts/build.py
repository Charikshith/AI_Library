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
              A subject with "prebuilt": "<file>" ships its own ready-made HTML
              (e.g. System Design) and is linked as-is instead of generated.

Their CSS/JS are linked from /assets (a copy lives in each prebuilt subject too).

Usage:  python scripts/build.py   (or: py scripts/build.py)
"""

import json
import re
from datetime import date
from pathlib import Path

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
    tools, current = [], None
    for raw in section.splitlines():
        line = raw.strip()
        heading = re.match(r"^##\s+(.*)$", line)
        if heading:
            current = heading.group(1).strip()
            continue
        if not (line.startswith("|") and current):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "tool" or set(cells[0]) <= set("-: "):
            continue
        link = LINK_RE.search(cells[0])
        if not link:
            continue
        tags = [t.lstrip("#").strip() for t in TAG_RE.findall(cells[2]) if t.strip()]
        tools.append({
            "category": current, "name": link.group("name").strip(),
            "url": link.group("url").strip(), "description": cells[1].strip(),
            "tags": tags, "added": cells[3].strip(),
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
                             "text": md.read_text(encoding="utf-8")})
        subjects.append({
            "slug": sub.name,
            "title": meta.get("title", sub.name.replace("-", " ").title()),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "added": meta.get("added", ""),
            "prebuilt": meta.get("prebuilt"),
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
    for ph in s["phases"]:
        frm, to = ph.get("from", 0), ph.get("to", 10**9)
        items = [c for c in chapters if c["num"].isdigit() and frm <= int(c["num"]) <= to]
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
           'document.querySelectorAll(".chapter-card,.home-section-header,.home-intro-card")'
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
        # --- entrance + scroll-reveal animations (respect reduced-motion; safe without JS) ---
        "@media(prefers-reduced-motion:no-preference){"
        "@keyframes ail-rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}"
        ".home-hero>*{animation:ail-rise .7s cubic-bezier(.2,.8,.2,1) both}"
        ".home-hero>*:nth-child(2){animation-delay:.07s}.home-hero>*:nth-child(3){animation-delay:.14s}"
        ".home-hero>*:nth-child(4){animation-delay:.21s}.home-hero>*:nth-child(5){animation-delay:.28s}"
        "html.anim .chapter-card,html.anim .home-section-header,html.anim .home-intro-card{"
        "opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s cubic-bezier(.2,.8,.2,1)}"
        "html.anim .chapter-card.in,html.anim .home-section-header.in,html.anim .home-intro-card.in{opacity:1;transform:none}"
        ".chapter-card{transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s,border-color .25s,opacity .6s ease}"
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
def tool_card(t):
    tags = "  ".join("#" + x for x in t["tags"])
    ext = t["url"].startswith("http")
    tgt = ' target="_blank" rel="noopener"' if ext else ''
    arrow = "&#8599;" if ext else "&rarr;"
    return ("".join([
        f'<a class="chapter-card" href="{h(t["url"])}"{tgt}>',
        f'<div class="chapter-card-head"><span class="chapter-num">{h(t["added"])}</span>'
        f'<span class="chapter-icon">{arrow}</span></div>',
        f'<h3 class="chapter-title">{h(t["name"])}</h3>',
        f'<p class="chapter-desc">{h(t["description"])}</p>',
        f'<div class="chapter-card-foot">{h(tags)}</div></a>',
    ]))


def subject_card(s):
    entry = s["prebuilt"] or "html/index.html"
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
    if p["writeup"]:
        href, tgt, arrow = f'projects/{h(p["slug"])}/{h(p["writeup"])}', "", "&rarr;"
    else:
        href, tgt, arrow = h(p["repo"]), ' target="_blank" rel="noopener"', "&#8599;"
    return ("".join([
        f'<a class="chapter-card" href="{href}"{tgt}>',
        f'<div class="chapter-card-head"><span class="chapter-num">{h(p["added"])}</span>'
        f'<span class="chapter-icon">{arrow}</span></div>',
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
        cards = "".join(tool_card(t) for t in items)
        sections.append(
            f'<section><div class="home-section-header"><h2>{h(cat)}</h2>'
            f'<span class="count">{len(items)} {"tool" if len(items)==1 else "tools"}</span></div>'
            f'<div class="chapter-list">{cards}</div></section>')
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
