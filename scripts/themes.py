"""Theme registry for the AI Library site.

Each theme is a bundle of *design tokens* consumed by `scripts/build.py`. Themes only
change the LOOK (colours, fonts, grain, code/diagram palette) — never the structure or
layout, which lives in build.py. Swapping themes is therefore a one-flag rebuild.

    Build with a theme:   python scripts/build.py --theme ink
    Default theme:        "paper"  (also settable via the AI_LIBRARY_THEME env var)
    List available:       python scripts/build.py --theme ?

To add/test a new theme: copy a block below, rename the key, tweak the tokens, then
`python scripts/build.py --theme <yourname>` and open the site. Rebuild with the default
(`python scripts/build.py`) to restore "paper".

Token reference
---------------
display / body / mono : CSS font-family stacks (must be covered by `font_link`)
font_link             : <link> tags that load the fonts above
hljs_css              : highlight.js stylesheet URL — pick one that suits the bg (the
                        gruvbox/atom-one-dark blocks are dark; use a light one for
                        light-on-light code if preferred)
mermaid_theme         : mermaid base ('base' | 'dark' | 'neutral' | 'default')
mermaid_vars          : mermaid themeVariables overrides (diagram palette)
vars                  : CSS custom properties injected into :root. Key ones:
    --paper        page background          --ink / --ink-soft / --muted  text tiers
    --accent / --accent-soft               brand accent
    --line / --line-soft                   hairline rules
    --card                                 card / panel / diagram background
    --glow                                 radial tint behind the masthead
    --shadow-col                           colour used by card/pre drop-shadows
    --code-bg / --code-col                 inline `code` background + text
    --on-accent                            text colour on top of accent fills
    --accent-line                          translucent accent for hover borders
    --hover                                low-alpha overlay for row/nav hovers
    --grain-opacity / --grain-blend        film-grain overlay strength + blend mode
"""

# Shared font loading — all themes currently use the same trio. Give a theme its own
# `font_link` (and display/body/mono) to change the typography too.
_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900'
    '&family=Hanken+Grotesk:wght@300..800&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">'
)
_DISPLAY = "'Fraunces',Georgia,serif"
_BODY = "'Hanken Grotesk',system-ui,sans-serif"
_MONO = "'IBM Plex Mono',ui-monospace,monospace"

_HLJS_GRUVBOX = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/gruvbox-dark-medium.min.css"
_HLJS_ATOM_DARK = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css"


THEMES = {
    # --- current default: warm "archive / reading-room" paper -------------------------
    "paper": {
        "display": _DISPLAY, "body": _BODY, "mono": _MONO, "font_link": _FONTS,
        "hljs_css": _HLJS_GRUVBOX,
        "mermaid_theme": "base",
        "mermaid_vars": {
            "fontFamily": "IBM Plex Mono, monospace", "fontSize": "13px",
            "primaryColor": "#fbf4e8", "primaryBorderColor": "#b4582a",
            "primaryTextColor": "#2b2620", "lineColor": "#8a7f6d",
            "secondaryColor": "#efe6d6", "tertiaryColor": "#f4ede0",
        },
        "vars": {
            "--paper": "#f4ede0", "--ink": "#2b2620", "--ink-soft": "#5e564a", "--muted": "#988e7c",
            "--accent": "#b4582a", "--accent-soft": "#c2773f", "--gold": "#b9892f",
            "--line": "rgba(43,38,32,.16)", "--line-soft": "rgba(43,38,32,.08)", "--card": "#fffdf8",
            "--glow": "rgba(180,88,42,.08)", "--shadow-col": "rgba(74,52,24,.5)",
            "--code-bg": "rgba(43,38,32,.06)", "--code-col": "#8a3f1d", "--on-accent": "#fdf5e9",
            "--accent-line": "rgba(180,88,42,.42)", "--hover": "rgba(43,38,32,.04)",
            "--grain-opacity": ".22", "--grain-blend": "multiply",
        },
    },

    # --- dark "ink" reading-room (the original dark look, amber accent) ---------------
    "ink": {
        "display": _DISPLAY, "body": _BODY, "mono": _MONO, "font_link": _FONTS,
        "hljs_css": _HLJS_GRUVBOX,
        "mermaid_theme": "dark",
        "mermaid_vars": {
            "fontFamily": "IBM Plex Mono, monospace", "fontSize": "13px",
            "primaryColor": "#1f1b14", "primaryBorderColor": "#e0a93b",
            "primaryTextColor": "#ece3d2", "lineColor": "#8a8070",
            "secondaryColor": "#2a241a", "tertiaryColor": "#15120d",
        },
        "vars": {
            "--paper": "#100e0b", "--ink": "#ece3d2", "--ink-soft": "#b8ad99", "--muted": "#8a8070",
            "--accent": "#e0a93b", "--accent-soft": "#caa15a", "--gold": "#b9892f",
            "--line": "rgba(236,227,210,.14)", "--line-soft": "rgba(236,227,210,.07)", "--card": "#16130d",
            "--glow": "rgba(224,169,59,.10)", "--shadow-col": "rgba(0,0,0,.5)",
            "--code-bg": "rgba(224,169,59,.10)", "--code-col": "#e0c074", "--on-accent": "#1c1407",
            "--accent-line": "rgba(224,169,59,.5)", "--hover": "rgba(236,227,210,.05)",
            "--grain-opacity": ".06", "--grain-blend": "overlay",
        },
    },

    # --- cool, modern "slate" (crisp light, indigo accent) ----------------------------
    "slate": {
        "display": _DISPLAY, "body": _BODY, "mono": _MONO, "font_link": _FONTS,
        "hljs_css": _HLJS_ATOM_DARK,
        "mermaid_theme": "base",
        "mermaid_vars": {
            "fontFamily": "IBM Plex Mono, monospace", "fontSize": "13px",
            "primaryColor": "#ffffff", "primaryBorderColor": "#3b5bdb",
            "primaryTextColor": "#1b2230", "lineColor": "#8a91a0",
            "secondaryColor": "#eef1f6", "tertiaryColor": "#f5f6f8",
        },
        "vars": {
            "--paper": "#f5f6f8", "--ink": "#1b2230", "--ink-soft": "#46505f", "--muted": "#878fa0",
            "--accent": "#3b5bdb", "--accent-soft": "#5b76e0", "--gold": "#0e7c86",
            "--line": "rgba(27,34,48,.14)", "--line-soft": "rgba(27,34,48,.06)", "--card": "#ffffff",
            "--glow": "rgba(59,91,219,.07)", "--shadow-col": "rgba(20,30,60,.18)",
            "--code-bg": "rgba(27,34,48,.06)", "--code-col": "#3b5bdb", "--on-accent": "#ffffff",
            "--accent-line": "rgba(59,91,219,.4)", "--hover": "rgba(27,34,48,.04)",
            "--grain-opacity": ".10", "--grain-blend": "multiply",
        },
    },

    # --- the "System Design" site's design language: Inter + JetBrains Mono, white bg,
    #     slate text, blue primary. This is the project default. -----------------------
    "sysdesign": {
        "display": "'Inter', system-ui, -apple-system, sans-serif",
        "body": "'Inter', system-ui, -apple-system, sans-serif",
        "mono": "'JetBrains Mono', ui-monospace, monospace",
        "font_link": (
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900'
            '&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
        ),
        "hljs_css": _HLJS_ATOM_DARK,
        "mermaid_theme": "base",
        "mermaid_vars": {
            "fontFamily": "JetBrains Mono, monospace", "fontSize": "13px",
            "primaryColor": "#eff4ff", "primaryBorderColor": "#2563eb",
            "primaryTextColor": "#0f172a", "lineColor": "#94a3b8",
            "secondaryColor": "#f5f6f8", "tertiaryColor": "#ffffff",
        },
        "vars": {
            "--paper": "#ffffff", "--ink": "#0f172a", "--ink-soft": "#475569", "--muted": "#94a3b8",
            "--accent": "#2563eb", "--accent-soft": "#3b82f6", "--gold": "#f59e0b",
            "--line": "#e2e8f0", "--line-soft": "#eef2f7", "--card": "#fafbfc",
            "--glow": "rgba(37,99,235,.06)", "--shadow-col": "rgba(15,23,42,.13)",
            "--code-bg": "#eef2ff", "--code-col": "#1d4ed8", "--on-accent": "#ffffff",
            "--accent-line": "rgba(37,99,235,.4)", "--hover": "rgba(15,23,42,.04)",
            "--grain-opacity": "0", "--grain-blend": "multiply",
        },
    },
}

DEFAULT_THEME = "sysdesign"
