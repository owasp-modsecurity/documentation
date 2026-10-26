---
title: Tools
weight: 3
---

Tools that are useful when writing, testing and operating ModSecurity rules. Projects are listed with the
organization that maintains them; the OWASP CRS project and the digitalwave team (one of the ModSecurity
maintainers) produce most of the current tooling.

## Rule sets

- [OWASP CRS](https://coreruleset.org/) - the rule set almost every ModSecurity deployment runs. [Repository](https://github.com/coreruleset/coreruleset),
  [documentation](https://coreruleset.org/docs/),
  [plugin registry](https://github.com/coreruleset/plugin-registry) for application-specific exclusions
  (WordPress, Nextcloud, Drupal, phpBB, phpMyAdmin, DokuWiki, cPanel, XenForo) and add-ons such as the
  DoS-protection, antivirus, body-decompress, fake-bot and auto-decoding plugins.
- [Comodo free ModSecurity rules](https://web.archive.org/web/20260212164915/https://waf.comodo.com/) - a commercial vendor's free rule set.

## Writing and checking rules

- [SecLang specification](https://seclang.org/) - the engine-independent specification of the rules
  language, with a [compatibility matrix](https://seclang.org/compat/matrix/) for ModSecurity v2, libModSecurity
  v3 and Coraza.
- [Coraza playground](https://playground.coraza.io/) - run a rule against a request in the browser.
- [crs-toolchain](https://github.com/coreruleset/crs-toolchain) - the CRS developers' command-line tool:
  assembles regular expressions from `.ra` files, renumbers and updates rules. Installable from the
  [CRS Homebrew tap](https://github.com/coreruleset/homebrew-tap).
- [crs-linter](https://github.com/coreruleset/crs-linter) - checks rules files against the CRS formatting
  and naming conventions.
- [msc_pyparser](https://github.com/digitalwave/msc_pyparser) - a Python parser for SecLang that produces an
  abstract syntax tree and writes rules back, for bulk edits, linting and analysis.
- [secrules_parsing](https://github.com/coreruleset/secrules_parsing) and
  [seclang_parser](https://github.com/coreruleset/seclang_parser) - the CRS project's Python and ANTLR parsers
  for the language.
- [msc_retest](https://github.com/digitalwave/msc_retest) - measures how long a regular expression takes in
  the PCRE and PCRE2 engines, for spotting patterns that are slow or vulnerable to regular-expression denial of
  service.
- [vscode-language-modsecurity](https://github.com/irvinlim/vscode-language-modsecurity) - SecLang
  syntax highlighting for Visual Studio Code, and
  [regexp-assemble-syntax](https://github.com/coreruleset/regexp-assemble-syntax) for the `.ra` files.

## Testing rules and engines

- [go-ftw](https://github.com/coreruleset/go-ftw) - the Framework for Testing WAFs: sends the HTTP requests
  described in YAML test files to a web server running ModSecurity and checks the logs for the expected rule
  matches. It is how the CRS test suite runs; the YAML format is defined by
  [ftw-tests-schema](https://github.com/coreruleset/ftw-tests-schema). The older Python
  [ftw](https://github.com/coreruleset/ftw) is no longer developed.
- [ftwrunner](https://github.com/digitalwave/ftwrunner) - runs the same FTW test files directly against
  libModSecurity, without a web server.
- [secrules-language-tests](https://github.com/owasp-modsecurity/secrules-language-tests) - the regression
  test cases shared by ModSecurity v2 and v3 (a git submodule of the engine) that any SecLang implementation can
  use to check itself.
- [MRTS](https://github.com/owasp-modsecurity/MRTS) - the ModSecurity Regression Test Set.
- [modsecurity-crs-docker](https://github.com/coreruleset/modsecurity-crs-docker) - the official container
  images with ModSecurity v2 on Apache httpd or libModSecurity on NGINX and the OWASP CRS preinstalled, the
  quickest way to get a test instance.
- The engine's own test tools: `tests/msc_test` and `run-unit-tests.pl` in the v2 tree, `test/regression_tests`,
  `test/unit_tests` and `test/benchmark` in the v3 tree (see [Contributing]({{% relref "7-1-contributing" %}})).

## Working with logs

- [libmsclogparser](https://github.com/digitalwave/libmsclogparser) - a C library (with Python bindings) that
  parses ModSecurity audit and error log entries.
- [modsecurity-parser](https://github.com/molu8bits/modsecurity-parser) - analyzes native and JSON audit logs
  and produces JSON, Excel and chart summaries.
- [ModSecurity-log-utilities](https://github.com/SpiderLabs/ModSecurity-log-utilities) - command-line tools
  from the former maintainer that turn audit logs into summaries.
- [logstash-modsecurity](https://github.com/bitsofinfo/logstash-modsecurity) - Logstash filters for the native
  audit log format. With `SecAuditLogFormat JSON` most log pipelines need no special parser.
- [modsec-sdbm-util](https://github.com/owasp-modsecurity/modsec-sdbm-util) - inspects and shrinks the SDBM
  files that ModSecurity v2 uses for persistent collections.
- [WAF-FLE](https://github.com/klaubert/waf-fle) - a web console for audit logs; no longer maintained but still
  used.

## Integrating the engine

- Connectors: [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx) (NGINX) and
  [ModSecurity-apache](https://github.com/owasp-modsecurity/ModSecurity-apache) (Apache httpd, not production
  ready); see the [installation chapter]({{% relref "2-installation" %}}).
- Bindings for libModSecurity: [pymodsecurity](https://github.com/pymodsecurity/pymodsecurity) (Python),
  [rust-modsecurity](https://github.com/rkrishn7/rust-modsecurity) (Rust),
  [vmod-modsecurity](https://github.com/xdecock/vmod-modsecurity) (Varnish).
- Proxies and gateways: [modsecurity-spoa](https://github.com/jcmoraisjr/modsecurity-spoa) runs libModSecurity
  as an HAProxy stream-processing agent; [traefik-modsecurity-plugin](https://github.com/acouvreur/traefik-modsecurity-plugin)
  forwards Traefik requests to the CRS container image; [modsecurity-wasm-filter](https://github.com/intel/modsecurity-wasm-filter)
  packages the engine as a WebAssembly filter for Envoy and Istio.
- [OWASP Coraza](https://coraza.io/) - a Go implementation of SecLang that runs the OWASP CRS and ships its own
  connectors (Caddy, proxy-wasm for Envoy, HTTP middleware), for environments where a C++ library does not fit.
