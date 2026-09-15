# mac111.nz

Static site for MAC111 Ltd, Nelson. No framework — plain HTML/CSS/JS with a tiny Python build step for shared header/footer. Hosted on **GitHub Pages**.

## Structure

```
src/
  layout.html          page shell (head, meta, scripts)
  partials/            header.html, footer.html (shared)
  pages/*.html         page content fragments; first lines are <!-- title: --> / <!-- description: -->
  assets/              css, js, img (copied to dist/assets)
  robots.txt, sitemap.xml, CNAME, .nojekyll
build.py               builds src → dist/  (also writes redirect stubs for the old WordPress URLs)
dist/                  generated output — gitignored, built by the GitHub Action
.github/workflows/deploy.yml   builds and deploys to GitHub Pages on every push to main
```

Pages are written as `dist/<slug>/index.html`, so `/mac-repairs/` works on GitHub Pages with no server config. `dist/404.html` is served for unknown URLs.

## Build locally

```
python build.py
python -m http.server -d dist 8000     # then open http://localhost:8000/
```

## Deploy (first time)

1. Create a repo (e.g. `CallaGeek/mac111`) and push this folder to `main`.
2. In the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The workflow runs on push and publishes `dist/`. Check the **Actions** tab for status.
4. Custom domain: **Settings → Pages → Custom domain** → `mac111.nz` (the `CNAME` file in `src/` is already set). Tick **Enforce HTTPS** once the certificate is issued.

DNS at the registrar:

```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
CNAME www  <github-username-or-org>.github.io
```

After that, every push to `main` redeploys automatically.

## Editing

- Phone / email / hours live in `src/partials/header.html`, `src/partials/footer.html`, `src/pages/contact.html` and the JSON-LD block in `src/layout.html`.
- Add a page: create `src/pages/my-page.html` with the two metadata comments at the top, add it to the nav in both partials and to `src/sitemap.xml`.
- Old-URL redirects: edit the `REDIRECTS` dict in `build.py`.
