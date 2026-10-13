# ModSecurity wiki → Hugo documentation site

Date: 2026-10-13. Status: approved by default (autonomous run; user reviews the result locally).

## Goal

Replace the GitHub wiki (`owasp-modsecurity/ModSecurity.wiki`) with a Hugo site built like
`coreruleset/documentation` (Hugo Relearn theme), with content restructured into a
single, versioned reference manual plus guides, and a migration path to update it from
the v2/v3 source trees and seclang.

## Decisions

- **Theme:** `hugo-relearn` as a git submodule, same commit as the CRS docs. Same config
  conventions (`config/_default/hugo.toml`, numbered content dirs, `weight` ordering).
- **One reference manual, not two.** The v2 and v3 wiki manuals share ~80% of their
  text; v2 already annotates "Supported on libModSecurity", and v3 marks unsupported
  entries with stubs. Each entry (directive, variable, transformation, action,
  operator) is emitted once, with a `secmeta` shortcode that renders a metadata table
  (syntax, default, scope, action group, "ModSecurity v2 since", "ModSecurity v3"
  status). Where the v3 wiki text differs, the v3-only lines are appended under a
  "ModSecurity v3" notice and tagged `<!-- TODO(v3-merge) -->` for editorial review.
- **Chapter pages, not per-entry pages.** 316 entries as pages would bloat the menu;
  one page per chapter with H2 per entry keeps the wiki's deep links (anchors are the
  lowercased entry names).
- **Mechanical conversion via pandoc** (`mediawiki → gfm`) driven by `tools/migrate-wiki.py`.
  Pre-processing: `; Note :` / `; Warning :` definition lists → Relearn `notice`
  shortcodes; `<pre>` → fenced `apache` code blocks; `[[Page|Title]]` wiki links → Hugo
  `relref`. The script is idempotent and re-runnable against a wiki checkout.
- **Archive, don't delete.** Pages the wiki marks "to be archived" land under
  `content/8-archive/` so nothing is lost; the user decides what to drop.

## Site map

```
1-introduction/        features, deployment modes, licensing, FAQ
2-installation/        v3 from source (recipes), v3 nginx, v2 apache, IIS, packages
3-reference-manual/    phases, directives, variables, transformations, actions,
                       operators, macro expansion, persistent storage, misc, base config
4-logging/             alert and audit log formats
5-troubleshooting/     debugging (gdb), IIS troubleshooting
6-migration/           v2→v3 notes (RC1 page), 1.x→2.x matrix, rules-language porting spec
7-development/         contributing, roadmap, package generation, tools
8-archive/             GSoC 2016 ideas, earlier RC notes
```

## Phase 2 (after migration)

Review each reference entry against `ModSecurity` `v2/master` (`apache2/`) and
`v3/master` (`src/`), and against `seclang/SPEC.md`, resolving every
`TODO(v3-merge)` marker and correcting version/support metadata.

## Out of scope for now

CI, publishing, custom logo/branding, multilingual.
