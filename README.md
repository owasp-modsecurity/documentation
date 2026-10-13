# ModSecurity Documentation

Source for the OWASP ModSecurity documentation site, built with [Hugo](https://gohugo.io/) and the
[Relearn](https://github.com/McShelby/hugo-theme-relearn) theme. It replaces the former GitHub wiki.

## Building locally

Requires Hugo *extended* >= 0.145 and Go (the theme is a [Hugo module](https://gohugo.io/hugo-modules/),
fetched on first build).

```bash
git clone https://github.com/owasp-modsecurity/documentation.git
cd documentation
hugo serve
```

The theme version is pinned in `go.mod`; Renovate opens PRs to bump it. To upgrade by hand:
`hugo mod get -u github.com/McShelby/hugo-theme-relearn && hugo mod tidy`.

Then open http://localhost:1313/documentation/.

## Layout

- `content/` — all pages, in numbered chapter directories (`1-introduction`, `2-installation`, …).
- `layouts/shortcodes/secmeta.html` — metadata table used by every reference-manual entry.
- `config/_default/hugo.toml` — site config (theme module import, params); `modsec_v2_latest`, `modsec_v3_latest` and `modsec_nginx_latest` are kept current by Renovate (`renovate.json`) and referenced
  from content with `{{< param modsec_v3_latest >}}`.
- `tools/migrate-wiki.py` — the one-off converter from the old wiki, kept for reference. The content was hand-edited after conversion, so it refuses to run without `--force`.
