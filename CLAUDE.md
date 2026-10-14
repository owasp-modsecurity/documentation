# CLAUDE.md

Hugo + Relearn documentation site for OWASP ModSecurity (v2 and libModSecurity v3). Modeled on
`coreruleset/documentation`.

## Commands

- `hugo serve` — dev server at http://localhost:1313/documentation/
- `hugo --minify` — production build into `public/`
- Theme: Hugo module `github.com/McShelby/hugo-theme-relearn`, pinned in `go.mod` (needs Go). No submodule.

## Conventions

- Content lives in `content/<n>-<chapter>/<n>-<m>-<page>.md`; ordering by `weight` in front matter.
- American English, LF line endings, final newline, no trailing whitespace.
- Reference-manual entries are `## EntryName` headings followed by a `{{< secmeta ... >}}` block
  (see `layouts/shortcodes/secmeta.html` for the parameter names), then prose. Anchors are the
  lowercased entry names, e.g. `3-reference-manual/3-2-configuration-directives#secruleengine`.
- Version metadata: `v2="2.7.0"` means "available in ModSecurity v2 since 2.7.0"; `v3` is
  `yes`, `no`, `tbi` (to be implemented) or a version string.
- Code fences: rules and ModSecurity directives use ```` ``` seclang ```` (rendered by
  `layouts/_default/_markup/render-codeblock-seclang.html`, a regex colorizer on top of Chroma's text lexer
  since Chroma has no SecLang lexer); httpd config uses `apache`, log excerpts `text`, Lua scripts `lua`.
  Inline code that is a `Sec*` directive with arguments is colored the same way by
  `layouts/partials/content.html` (Hugo has no code span render hook); the tokenizer is
  `layouts/partials/seclang-highlight.html`.
- Callouts: `{{% notice note %}}…{{% /notice %}}` (also `warning`, `info`, `tip`).
- Cross references: `{{% relref "3-reference-manual/3-5-actions#ctl" %}}` style links.
- `<!-- TODO(v3-merge) -->` marks text auto-merged from the v3 wiki manual that still needs
  editorial review against the source code.
