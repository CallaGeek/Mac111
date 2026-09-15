#!/usr/bin/env python3
"""Static site builder for mac111.nz (GitHub Pages)

Usage:  python build.py
Reads src/pages/*.html (fragments with a small metadata header),
wraps each in src/layout.html with the shared header/footer partials,
copies src/assets → dist/assets and writes dist/<slug>/index.html
(so /mac-repairs/ resolves without any server config), plus dist/404.html,
dist/CNAME and meta-refresh redirect stubs for the old WordPress URLs.
"""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

META_RE = re.compile(r"<!--\s*(\w+):\s*(.*?)\s*-->")

def read(p): return p.read_text(encoding="utf-8")

def parse_page(path):
    text = read(path)
    meta, body_lines = {}, []
    for line in text.splitlines():
        m = META_RE.fullmatch(line.strip())
        if m and not body_lines:
            meta[m.group(1)] = m.group(2)
        else:
            body_lines.append(line)
    return meta, "\n".join(body_lines).strip()

LINK_RE = re.compile(r'((?:href|src|content)=")/(?!/)([^"]*)"')

def relativise(html, depth):
    """Rewrite root-absolute URLs (/assets/x, /about/) to relative ones so the
    site works at a sub-path (user.github.io/repo/), on the custom domain and
    from disk. depth = number of folders below dist/ the page sits in."""
    prefix = "../" * depth if depth else "./"
    def fix(m):
        path = m.group(2)
        if path.startswith("http"): return m.group(0)
        return f'{m.group(1)}{prefix}{path}"'
    return LINK_RE.sub(fix, html)

def render(template, ctx):
    for k, v in ctx.items():
        template = template.replace("{{" + k + "}}", v)
    return template

REDIRECTS = {
    "/about-mac111/": "/about/",
    "/apple-computer-repairs-nelson/": "/mac-repairs/",
    "/retina-macbook-screen-repairs/": "/mac-repairs/",
    "/chromebook-repairs-nelson/": "/chromebook-laptop-repairs/",
    "/smartphone-repairs-nelson/": "/smartphone-repairs/",
    "/samsung-galaxy-phone-repairs/": "/smartphone-repairs/",
    "/apple-macbook-iphone-logic-board-repairs/": "/logic-board-repairs/",
    "/xbox-playstation-console-repairs-nelson/": "/console-repairs/",
    "/contact-mac111/": "/contact/",
}

REDIRECT_TPL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="robots" content="noindex">
<script>location.replace("{target}")</script>
</head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
"""

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SRC / "assets", DIST / "assets")
    for extra in ("robots.txt", "sitemap.xml", "CNAME", ".nojekyll"):
        if (SRC / extra).exists(): shutil.copy(SRC / extra, DIST / extra)

    layout = read(SRC / "layout.html")
    header = read(SRC / "partials" / "header.html")
    footer = read(SRC / "partials" / "footer.html")

    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_page(page)
        slug = page.stem
        url = "/" if slug == "index" else f"/{slug}/"
        page_header = header.replace(f'href="{url}"', f'href="{url}" aria-current="page"')
        html = render(layout, {
            "title": meta.get("title", "MAC111"),
            "description": meta.get("description", ""),
            "canonical": "https://mac111.nz" + url,
            "bodyclass": meta.get("bodyclass", ""),
            "header": page_header,
            "footer": footer,
            "content": body,
        })
        if slug in ("index", "404"):
            out = DIST / f"{slug}.html"          # GitHub Pages serves /404.html for missing pages
            depth = 0
        else:
            (DIST / slug).mkdir(parents=True, exist_ok=True)
            out = DIST / slug / "index.html"
            depth = 1
        # canonical/og:url must stay absolute — protect them, relativise the rest
        html = html.replace('href="https://mac111.nz', 'href="ABS_KEEP').replace('content="https://mac111.nz', 'content="ABS_KEEP')
        html = relativise(html, depth).replace("ABS_KEEP", "https://mac111.nz")
        out.write_text(html, encoding="utf-8")
        print("built", url)

    # Redirect stubs for the old site's URLs (GitHub Pages has no server-side redirects)
    for old, new in REDIRECTS.items():
        d = DIST / old.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        target = "https://mac111.nz" + new
        (d / "index.html").write_text(REDIRECT_TPL.format(target=target), encoding="utf-8")
        print("redirect", old, "->", new)

if __name__ == "__main__":
    main()
