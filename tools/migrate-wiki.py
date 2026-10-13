#!/usr/bin/env python3
"""One-off converter: owasp-modsecurity/ModSecurity.wiki -> Hugo (Relearn) content.

    tools/migrate-wiki.py ../ModSecurity.wiki content

The generated files were hand-edited afterwards (source review of v2/v3 metadata), so
re-running OVERWRITES that work. It refuses to run without --force. Kept for reference
and for re-converting individual wiki pages. Needs pandoc on PATH.
"""
import html
import pathlib
import re
import subprocess
import sys
import urllib.parse

if "--force" not in sys.argv:
    sys.exit("refusing to overwrite hand-edited content; pass --force to re-run the conversion")
WIKI = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])

REF = "3-reference-manual"

# wiki page name -> hugo content path (used for [[links]] and github wiki URLs)
PAGES = {
    "Reference-Manual-(v2.x)": REF,
    "Reference-Manual-(v3.x)": REF,
    "Reference-Manual-(v2.x)-(Split)": REF,
    "Reference-Manual-(v2.x)-Configuration-Directives": f"{REF}/3-2-configuration-directives",
    "Reference-Manual-(v2.x)-Processing-Phases": f"{REF}/3-1-processing-phases",
    "Reference-Manual-(v2.x)-Variables": f"{REF}/3-3-variables",
    "Reference-Manual-(v2.x)-Transformation-Functions": f"{REF}/3-4-transformation-functions",
    "Reference-Manual-(v2.x)-Actions": f"{REF}/3-5-actions",
    "Reference-Manual-(v2.x)-Operators": f"{REF}/3-6-operators",
    "Compilation-recipes-for-v3.x": "2-installation/2-3-distribution-recipes",
    "IIS-Troubleshooting": "5-troubleshooting/5-2-iis-troubleshooting",
    "Debugging-ModSecurity": "5-troubleshooting/5-1-debugging",
    "ModSecurity-Frequently-Asked-Questions-(FAQ)": "1-introduction/1-1-faq",
    "ModSecurity-2-Data-Formats": "4-logging",
    "ModSecurity-Migration-Matrix": "6-migration/6-2-migrating-from-1x-to-2x",
    "ModSecurity-Rules-Language-Porting-Specification": "6-migration/6-3-rules-language-porting",
    "ModSecurity-version-3-RC1": "6-migration/6-1-migrating-from-2x-to-3x",
    "ModSecurity-version-3-(earlier-release-candidate-1)": "8-archive/8-2-v3-earlier-rc1-notes",
    "OWASP-ModSecurity-Contributing": "7-development/7-1-contributing",
    "RoadMap": "7-development/7-2-roadmap",
    "Package-Generation": "2-installation/2-6-package-generation",
    "Tools": "7-development/7-3-tools",
    "Ideas-for-Google-Summer-of-Code-2016": "8-archive/8-1-gsoc-2016-ideas",
}

# entry-metadata labels that go into the secmeta shortcode, label -> param
META = {
    "syntax": "syntax",
    "example usage": "example",
    "default": "default",
    "scope": "scope",
    "action group": "group",
    "processing phases": "phases",
}
RE_META = re.compile(r"^'''(?P<k>[A-Za-z /]+?):?'''\s*:?\s*(?P<v>.*)$")
RE_NOTE = re.compile(r"^;\s*(?P<k>Notes?(?: II)?|NOTE|Warning)\s*:\s*(?P<v>.*)$")
RE_DEF = re.compile(r"^;\s*(?P<k>[^:]+?)\s*:\s*(?P<v>.*)$")
RE_STUB = re.compile(r"Not\s+s?u?p?ported\s+in\s+v3", re.I)


# ---------------------------------------------------------------- mediawiki helpers
def pandoc(text, fmt="mediawiki"):
    r = subprocess.run(["pandoc", "-f", fmt, "-t", "gfm", "--wrap=none"],
                       input=text, capture_output=True, text=True, check=True)
    return r.stdout


def code_lang(body):
    b = body.lstrip()
    if b.startswith("<?xml") or b.startswith("<") and not b.startswith("<Virtual") and not b.startswith("<Loc") and not b.startswith("<Dir") and not b.startswith("<IfMod") and not b.startswith("<Files"):
        return "xml"
    if b.startswith("#!/usr/bin/perl") or b.startswith("#!/usr/bin/env perl"):
        return "perl"
    if b.startswith("#!/bin/") or b.startswith("$ ") or b.startswith("$git") or b.startswith("$cd"):
        return "bash"
    if b.startswith("{") or b.startswith("["):
        return "json"
    return "apache"


def pre_mw(text):
    """Pre-process mediawiki so pandoc emits what we want."""
    # <pre> -> <source lang=..> so pandoc emits fenced blocks
    def repl(m):
        body = html.unescape(m.group(1))
        return f'<source lang="{code_lang(body)}">{body}</source>'
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", repl, text, flags=re.S)
    text = re.sub(r"</?(span|div|p)(\s[^>]*)?>", "", text)  # docbook export noise
    text = re.sub(r"^```\w*\n(.*?)^```\s*$", lambda m: repl(m), text, flags=re.S | re.M)  # markdown fences in wiki text
    text = re.sub(r"<code>\s*((?:[^<]|<(?!/code>))*\n(?:[^<]|<(?!/code>))*)</code>", repl, text, flags=re.S)  # multi-line inline code
    # pandoc mangles these C escapes in prose
    text = text.replace(r"\a, \b, \f, \n, \r, \t, \v, \\, \?, \', \", \xHH (hexadecimal), \0OOO (octal)",
                        "<code>\\a</code>, <code>\\b</code>, <code>\\f</code>, <code>\\n</code>, <code>\\r</code>, <code>\\t</code>, <code>\\v</code>, <code>\\\\</code>, <code>\\?</code>, <code>\\'</code>, <code>\\\"</code>, <code>\\xHH</code> (hexadecimal), <code>\\0OOO</code> (octal)")
    out = []
    for line in text.split("\n"):
        m = RE_NOTE.match(line)
        if m:
            style = "warning" if m.group("k").lower().startswith("warn") else "note"
            out += ["", f"{{{{% notice {style} %}}}}", "", m.group("v"), "", "{{% /notice %}}", ""]
            continue
        m = RE_DEF.match(line)
        if m:  # other definition lists -> bold term bullets
            out.append(f"* '''{m.group('k')}''': {m.group('v')}")
            continue
        out.append(line)
    return "\n".join(out)


def post_md(md):
    """Clean up pandoc's gfm output."""
    # pandoc escapes these, we do not want that in prose
    md = md.replace("\\_", "_").replace("\\*", "*").replace("\\[", "[").replace("\\]", "]")
    md = md.replace("\\<", "<").replace("\\>", ">").replace("\\~", "~").replace("\\#", "#")
    # wikilinks pandoc could not resolve
    def wl(m):
        href, txt = m.group(1), m.group(2)
        if href.startswith("#"):
            href = resolve(href[1:])
        return f"[{txt}]({href})"
    md = re.sub(r'<a href="([^"]+)" class="wikilink" title="[^"]*">([^<]*)</a>', wl, md)
    # ./#user-content-SecFoo and ./Reference-Manual-(v2.x)#user-content-SecFoo anchors from the wiki
    md = re.sub(r'<a href="[^"#]*#([^">]+)"?>([^<]*)</a>', lambda m: f"[{m.group(2)}]({resolve(m.group(1))})", md)
    md = github_wiki_links(md)
    # pandoc autolinks URLs inside <code>: `SecAuditLog `[`http://x`](http://x) -> `SecAuditLog http://x`
    md = re.sub(r"`([^`\n]*)`\[`([^`\n]*)`\]\([^)\n]*\)", r"`\1\2`", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def anchor(name):
    """Hugo/Goldmark auto heading id."""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s]+", "-", s)


ENTRY_INDEX = {}  # entry name -> reference chapter file (filled before rendering)


def resolve(frag):
    """'#SecFoo' style fragment -> link target, cross-page when the entry lives in another chapter"""
    name = re.sub(r"^(user-content-|wiki-)", "", frag.strip('"')).split("#")[-1]
    page = ENTRY_INDEX.get(name)
    if page:
        return "{{% relref \"" + f"{REF}/{page}#{anchor(name)}" + "\" %}}"
    return "#" + anchor(name)


def github_wiki_links(md):
    def repl(m):
        page = urllib.parse.unquote(m.group(1))
        frag = m.group(2) or ""
        if page.startswith("Reference-Manual") and frag:
            return resolve(frag[1:])
        if page in PAGES:
            return "{{% relref \"" + PAGES[page] + frag + "\" %}}"
        return m.group(0)
    return re.sub(r"https?://github\.com/(?:SpiderLabs|owasp-modsecurity)/ModSecurity/wiki/([^\s)#\"]+)(#[^\s)\"]+)?",
                  repl, md)


def chapters(path):
    """mediawiki file -> ordered {chapter_title: text}"""
    out, cur = {}, None
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^=([^=].*?)=\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
            continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def entries(chapter):
    """chapter text -> (intro, ordered {entry: text})"""
    intro, out, cur = [], {}, None
    for line in chapter.split("\n"):
        m = re.match(r"^==([^=].*?)==\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
            continue
        (out[cur] if cur is not None else intro).append(line)
    return "\n".join(intro).strip(), {k: "\n".join(v).strip() for k, v in out.items()}


def blocks(text):
    """split mediawiki text into paragraph-ish blocks, keeping <pre> whole"""
    out, cur, inpre = [], [], False
    for line in text.split("\n"):
        if "<pre" in line:
            inpre = True
        if not line.strip() and not inpre:
            if cur:
                out.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
        if "</pre>" in line:
            inpre = False
    if cur:
        out.append("\n".join(cur))
    return out


def norm(block):
    return re.sub(r"\s+", " ", block).strip().lower()


def parse_entry(text):
    """entry text -> (meta dict, description, body-mediawiki)"""
    meta, desc, body = {}, "", []
    for line in text.split("\n"):
        m = RE_META.match(line)
        if m:
            k, v = m.group("k").strip().lower(), m.group("v").strip()
            if k == "description":
                desc = v
                continue
            if k == "version":
                meta["version"] = v
                continue
            if k == "supported on libmodsecurity":
                meta["supported"] = v
                continue
            if k in META and v and "<source" not in v and "<pre" not in v and len(v) < 160:
                meta[META[k]] = strip_code(v)
                continue
        body.append(line)
    return meta, desc, "\n".join(body).strip()


def strip_code(v):
    v = re.sub(r"</?code>", "", v)
    v = re.sub(r"</?(nowiki|tt)>", "", v)
    return html.unescape(v).strip().strip("`")


def v3_status(v2meta, v3text):
    """-> (v3 value, v3note, todo)"""
    sup = v2meta.get("supported", "")
    sup_l = sup.lower()
    if v3text is None:
        if sup_l.startswith("yes"):
            return "yes", "", False
        if sup_l.startswith("no"):
            return "no", "(deprecated)" if "deprec" in sup_l else "", False
        if sup_l.startswith("tb"):
            return "tbi", "", False
        return "", "", True
    if RE_STUB.search(v3text):
        return "no", "", False
    v3meta, _, _ = parse_entry(v3text)
    ver = v3meta.get("version", "").strip()
    note, todo = "", False
    m = re.search(r"as of\s+([0-9.]+)", sup_l)
    if m:
        ver = m.group(1)
    elif sup_l.startswith("yes") and not sup_l.startswith("yes "):
        pass
    elif sup_l.startswith("yes - as of"):
        note = html.unescape(re.sub(r"\[(https?://\S+)[^\]]*\]", r"([commit](\1))", sup[len("Yes - "):]))
    elif sup_l.startswith(("tb", "no")):
        note = f"<!-- TODO(v3-merge): v2 manual says \"{sup}\" but v3 manual documents it -->"
        todo = True
    val = ver if ver else "yes"
    if val.lower().startswith("3.0.0"):
        val = "3.0.0"
    return val, note, todo


def sc_param(k, v):
    v = v.replace("\n", " ").strip()
    if '"' in v or "\\" in v:
        if "`" in v:
            v = v.replace("`", "'")
        return f"{k}=`{v}`"
    return f'{k}="{v}"'


def render_entry(name, v2text, v3text):
    """-> markdown for one unified reference entry"""
    if v2text is None:  # v3-only entry
        meta, desc, body = parse_entry(v3text)
        v2, v3, note, todo = "", (meta.get("version") or "yes"), "", True
        if v3.lower().startswith("3.0.0"):
            v3 = "3.0.0"
        src_v3only = True
    else:
        meta, desc, body = parse_entry(v2text)
        v2 = meta.get("version", "").strip()
        v2 = re.sub(r"^v", "", v2)
        v3, note, todo = v3_status(meta, v3text)
        src_v3only = False
    params = [sc_param(k, meta[k]) for k in ("syntax", "example", "default", "scope", "group", "phases") if k in meta]
    params.append(sc_param("v2", v2))
    params.append(sc_param("v3", v3))
    if note:
        params.append(sc_param("v3note", note))
    out = [f"## {name}", ""]
    if src_v3only:
        out += ["<!-- TODO(v3-merge): entry only documented in the v3 wiki manual; check v2 source -->", ""]
    elif todo and not note:
        out += ["<!-- TODO(v3-merge): v3 support unknown; check v3 source -->", ""]
    if desc:
        out += [post_md(pandoc(pre_mw(desc))).strip(), ""]
    out += ["{{< secmeta " + " ".join(params) + " >}}", ""]
    if body:
        out += [post_md(pandoc(pre_mw(body))).strip(), ""]
    # v3 text that is not in v2 -> review notice
    if v2text is not None and v3text is not None and not RE_STUB.search(v3text):
        _, v3desc, v3body = parse_entry(v3text)
        v2blocks = {norm(b) for b in blocks(body)} | {norm(desc)}
        extra = [b for b in blocks(v3body) if norm(b) not in v2blocks and not re.match(r"^(\*\s*)?'''\w", b.strip()) or False]
        if v3desc and norm(v3desc) != norm(desc):
            extra.insert(0, v3desc)
        extra = [b for b in extra if norm(b) and norm(b) not in v2blocks]
        if extra:
            out += ["{{% notice info \"ModSecurity v3 (text from the v3 manual, pending merge)\" %}}",
                    "<!-- TODO(v3-merge) -->", "",
                    post_md(pandoc(pre_mw("\n\n".join(extra)))).strip(), "",
                    "{{% /notice %}}", ""]
    return "\n".join(out)


def front(title, weight, extra=None):
    fm = ["---", f"title: {title!r}" if ":" in title else f"title: {title}", f"weight: {weight}"]
    if extra:
        fm += extra
    return "\n".join(fm + ["---", ""])


def write(path, text):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n", encoding="utf-8")
    print("wrote", p)


# ---------------------------------------------------------------- reference manual
V2 = chapters(WIKI / "Reference-Manual-(v2.x).mediawiki")
V3 = chapters(WIKI / "Reference-Manual-(v3.x).mediawiki")

ENTRY_CHAPTERS = [
    # (v2 chapter, v3 chapter, out file, title, weight)
    ("Configuration Directives", "Configuration Directives", "3-2-configuration-directives", "Configuration Directives", 2),
    ("Variables", "Variables", "3-3-variables", "Variables", 3),
    ("Transformation functions", "Transformation functions", "3-4-transformation-functions", "Transformation Functions", 4),
    ("Actions", "Actions", "3-5-actions", "Actions", 5),
    ("Operators", "Operators", "3-6-operators", "Operators", 6),
]
PLAIN_CHAPTERS = [
    ("Processing Phases", "3-1-processing-phases", "Processing Phases", 1),
    ("Macro Expansion", "3-7-macro-expansion", "Macro Expansion", 7),
    ("Persistent Storage", "3-8-persistent-storage", "Persistent Storage", 8),
    ("Miscellaneous Topics", "3-9-miscellaneous-topics", "Miscellaneous Topics", 9),
    ("A Recommended Base Configuration", "3-10-recommended-base-configuration", "Recommended Base Configuration", 10),
]


def merged_plain(v2text, v3text):
    md = post_md(pandoc(pre_mw(v2text)))
    v2b = {norm(b) for b in blocks(v2text)}
    extra = [b for b in blocks(v3text or "") if norm(b) not in v2b]
    if extra:
        md += ("\n{{% notice info \"ModSecurity v3 (text from the v3 manual, pending merge)\" %}}\n"
               "<!-- TODO(v3-merge) -->\n\n" + post_md(pandoc(pre_mw("\n\n".join(extra)))) + "\n{{% /notice %}}\n")
    return md


def ordered_names(v2e, v3e):
    names = list(v2e)
    for i, n in enumerate(v3e):
        if n not in names:
            prev = list(v3e)[i - 1] if i else None
            names.insert(names.index(prev) + 1 if prev in names else len(names), n)
    return names


for c2, c3, fname, *_ in ENTRY_CHAPTERS:
    for n in list(entries(V2[c2])[1]) + list(entries(V3[c3])[1]):
        ENTRY_INDEX.setdefault(n, fname)

for c2, c3, fname, title, weight in ENTRY_CHAPTERS:
    intro2, e2 = entries(V2[c2])
    intro3, e3 = entries(V3[c3])
    parts = [front(title, weight), merged_plain(intro2, intro3)]
    for name in ordered_names(e2, e3):
        parts.append(render_entry(name, e2.get(name), e3.get(name)))
    write(f"{REF}/{fname}.md", "\n".join(parts))

for c, fname, title, weight in PLAIN_CHAPTERS:
    write(f"{REF}/{fname}.md", front(title, weight) + "\n" + merged_plain(V2[c], V3.get(c)))

# ---------------------------------------------------------------- introduction / installation
intro = V2["Introduction"]
write("1-introduction/_index.md",
      front("Introduction", 1, ['pre: "<b>1. </b>"', "chapter: true"]) + "\n" + merged_plain(intro, V3["Introduction"]))

write("2-installation/2-4-modsecurity-v2-apache.md",
      front("ModSecurity v2 for Apache", 4) + "\n" + post_md(pandoc(pre_mw(V2["Installation for Apache"]))))
write("2-installation/2-5-modsecurity-v2-iis.md",
      front("ModSecurity v2 for Microsoft IIS", 5) + "\n" + post_md(pandoc(pre_mw(V2["Installation for Microsoft IIS"]))))
# V3["Installation for NGINX"] described the obsolete v2 standalone build; 2-2 is hand-written from the connector README.


# ---------------------------------------------------------------- github-markdown pages
def gh_md(name, drop_toc=True):
    text = (WIKI / f"{name}.md").read_text(encoding="utf-8")
    text = re.sub(r"\[\[\s*([^\]|]+?)\s*\|\s*([^\]]+?)\s*\]\]",
                  lambda m: f"[{m.group(1)}]({link_target(m.group(2))})", text)
    text = re.sub(r"\[\[\s*([^\]|]+?)\s*\]\]", lambda m: f"[{m.group(1)}]({link_target(m.group(1))})", text)
    text = github_wiki_links(text)
    if drop_toc:
        text = re.sub(r"#+\s*Table of Contents\s*\n(?:\s*\d+\.\s.*\n)+", "", text)
    # normalize heading levels so the top level is H2 (H1 is the page title)
    lines, fence, levels = text.split("\n"), False, []
    for l in lines:
        if l.startswith("```"):
            fence = not fence
        elif not fence and (m := re.match(r"^(#{1,6}) ", l)):
            levels.append(len(m.group(1)))
    shift = 2 - min(levels) if levels else 0
    out, fence = [], False
    for l in lines:
        if l.startswith("```"):
            fence = not fence
        if not fence and (m := re.match(r"^(#{1,6}) ", l)):
            l = "#" * (len(m.group(1)) + shift) + l[len(m.group(1)):]
        out.append(l)
    return "\n".join(out).strip() + "\n"


def link_target(t):
    t = t.strip()
    if t.startswith("http"):
        return t
    page = t.replace(" ", "-")
    frag = ""
    if "#" in page:
        page, frag = page.split("#", 1)
        frag = "#" + frag
    if page in PAGES:
        return "{{% relref \"" + PAGES[page] + frag + "\" %}}"
    return t


write("2-installation/2-3-distribution-recipes.md", front("Distribution-specific build recipes", 3) + "\n" + gh_md("Compilation-recipes-for-v3.x"))
write("2-installation/2-6-package-generation.md", front("Building distribution packages", 6) + "\n" + gh_md("Package-Generation"))

write("5-troubleshooting/5-1-debugging.md", front("Debugging ModSecurity", 1) + "\n" + gh_md("Debugging-ModSecurity"))
write("5-troubleshooting/5-2-iis-troubleshooting.md", front("IIS Troubleshooting", 2) + "\n" + gh_md("IIS-Troubleshooting"))

write("6-migration/6-1-migrating-from-2x-to-3x.md", front("Migrating from v2 to v3", 1) + "\n" + gh_md("ModSecurity-version-3-RC1"))
write("7-development/7-1-contributing.md", front("Contributing", 1) + "\n" + gh_md("OWASP-ModSecurity-Contributing"))
write("7-development/7-3-tools.md", front("Tools", 3) + "\n" + gh_md("Tools"))
write("8-archive/8-1-gsoc-2016-ideas.md", front("Google Summer of Code 2016 ideas", 1) + "\n" + gh_md("Ideas-for-Google-Summer-of-Code-2016"))
write("8-archive/8-2-v3-earlier-rc1-notes.md", front("libModSecurity v3 early release-candidate notes", 2) + "\n"
      + gh_md("ModSecurity-version-3-(earlier-release-candidate-1)"))


# ---------------------------------------------------------------- remaining mediawiki pages
def mw_page(name):
    text = (WIKI / f"{name}.mediawiki").read_text(encoding="utf-8")
    text = re.sub(r"^=([^=].*?)=\s*$", "", text, count=1, flags=re.M)  # page title
    text = re.sub(r"^(Version \d|Copyright ).*$", "", text, flags=re.M)
    text = text.replace("\\\\\\\\", "\\\\")  # docbook export double-escaped backslashes in log samples
    if re.search(r"^=[^=]", text, re.M):  # remaining H1 chapters -> H2 (the page title is the H1)
        text = re.sub(r"^(=+)([^=].*?)(=+)\s*$", lambda m: "=" + m.group(1) + m.group(2) + m.group(3) + "=", text, flags=re.M)
    return post_md(pandoc(pre_mw(text)))


def matrix_page():
    """1.x -> 2.x migration matrix: one HTML table with paragraph cells -> one section per feature"""
    text = (WIKI / "ModSecurity-Migration-Matrix.mediawiki").read_text(encoding="utf-8")
    text = re.sub(r"^=([^=].*?)=\s*$", "", text, count=1, flags=re.M)
    head, table, tail = re.match(r"(.*?)(<table.*?</table>)(.*)", text, re.S).groups()
    rows = [re.findall(r"<td>(.*?)</td>", r, re.S) for r in re.findall(r"<tr>(.*?)</tr>", table, re.S)]
    cell = lambda h: post_md(pandoc(re.sub(r"</?(span|div)[^>]*>", "", h), "html")).strip()
    headers = [re.sub(r"<[^>]+>", "", h).strip() for h in rows[0]]
    out = [post_md(pandoc(pre_mw(head)))]
    for r in rows[1:]:
        out.append("## " + re.sub(r"<[^>]+>", "", r[0]).strip() + "\n")
        for h, c in zip(headers[1:], r[1:]):
            out.append(f"**{h}**\n\n{cell(c)}\n")
    out.append(post_md(pandoc(pre_mw(tail))))
    return "\n".join(out)


write("1-introduction/1-1-faq.md", front("Frequently Asked Questions", 1) + "\n" + mw_page("ModSecurity-Frequently-Asked-Questions-(FAQ)"))
write("4-logging/_index.md", front("Logging and Data Formats", 4, ['pre: "<b>4. </b>"', "chapter: true"]) + "\n" + mw_page("ModSecurity-2-Data-Formats"))
write("6-migration/6-2-migrating-from-1x-to-2x.md", front("Migrating from v1 to v2", 2) + "\n" + matrix_page())
write("6-migration/6-3-rules-language-porting.md", front("Rules language porting specification", 3) + "\n" + mw_page("ModSecurity-Rules-Language-Porting-Specification"))
write("7-development/7-2-roadmap.md", front("Roadmap", 2) + "\n" + mw_page("RoadMap"))
