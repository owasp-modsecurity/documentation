---
title: Contributing
weight: 1
---

ModSecurity was transferred from Trustwave to OWASP in January 2024 and is developed by a small group of
maintainers together with the community. Contributions of every kind are welcome: bug reports, fixes,
features, tests, packaging, documentation and help for other users. This page explains how the project works and
what a good contribution looks like.

## Where things happen

- Code: <https://github.com/owasp-modsecurity/ModSecurity>, with the v2 engine on the `v2/master` branch and
  the v3 library on `v3/master` (the default branch). The connectors are separate repositories:
  [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx) and
  [ModSecurity-apache](https://github.com/owasp-modsecurity/ModSecurity-apache).
- This documentation: <https://github.com/owasp-modsecurity/documentation> (every page has an edit link).
- Discussion: the `#project-modsecurity` channel on the [OWASP Slack](https://owasp.org/slack/invite) and
  the GitHub issue tracker. Questions about configuration and rules are best asked on Slack or as a
  [GitHub discussion](https://github.com/owasp-modsecurity/ModSecurity/discussions) before opening an issue.
- Project page: <https://owasp.org/www-project-modsecurity/>, which lists the project leaders. They review
  and merge every pull request.

## Reporting a bug

Open an issue at <https://github.com/owasp-modsecurity/ModSecurity/issues> after checking that it has not been
reported. Include the engine version (`2.9.x` or `3.0.x`), the connector and its version for v3, the web server
version, the operating system or package, the smallest rule that reproduces the problem, the request that
triggers it, and the relevant debug log at level 9 (`SecDebugLogLevel 9`). A failing regression test case
(see below) is the most useful report of all, since it becomes the test that keeps the bug fixed.

## Reporting a security issue

Do not open a public issue, pull request or mailing list thread for a vulnerability. Report it privately through
a [draft security advisory](https://github.com/owasp-modsecurity/ModSecurity/security/advisories/new) on
GitHub, where the maintainers triage it, coordinate the fix with you and publish the advisory together with the
fixed release, crediting the reporter. If you cannot use GitHub, email <modsecurity@owasp.org>. The current
policy is in [SECURITY.md](https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/SECURITY.md).

## Proposing a feature

Open an issue describing the problem the feature solves and, if you have one, the SecLang syntax you propose.
Both engines are maintained in parallel, so a new directive, variable, operator or action normally has to be
implemented in both v2 and v3 and reflected in the [SecLang specification](https://seclang.org/); say early
which parts you can take on. Discussing the design before writing code saves everyone time.

## Sending a pull request

- Fork the repository and branch from `v2/master` or `v3/master`. A fix that applies to both engines is two
  pull requests, one per branch; link them to each other.
- One logical change per commit, and nothing outside the scope of the change (no drive-by reformatting). The
  first line of the commit message says what changed; the body says why and how, since that is what reviewers
  and future maintainers read.
- Reference the issue with `Fixes #NNN` in the pull request description.
- Add or update tests (see the next section). Pull requests without a test for the change need a reason.
- CI runs the build and the test suites on Linux (gcc and clang, 32 and 64 bit, with every optional dependency
  on and off), macOS and Windows, plus cppcheck. All checks must pass; the cppcheck job is the one most often
  surprised by new code.
- Expect review comments and a request or two for changes; that is the normal course of a pull request.
- The release notes are written from the pull requests, so a clear title matters.

## Coding guidelines

### ModSecurity v2

- C, built with autotools against the Apache APR and httpd headers; the module must keep building against
  Apache 2.4 and the IIS module in `iis/` against Visual Studio (CMake).
- Memory comes from APR pools; follow the existing allocation pattern of the function you are changing and
  never mix pool and malloc memory.
- New directives are registered in `apache2/apache2_config.c`, variables in `apache2/re_variables.c`, actions
  in `apache2/re_actions.c`, operators in `apache2/re_operators.c` and transformations in `apache2/re_tfns.c`;
  each registry entry needs a unit test under `tests/` and an entry in this documentation.
- Keep changes free of compiler warnings and run `make test` (unit tests via `tests/msc_test`) and
  `make test-regression` (the Apache-based regression suite, which needs a local httpd) before sending.

### libModSecurity v3

- C++17, built with autotools (`./build.sh`, `./configure`, `make`), CMake on Windows. The code follows the
  [Chromium C++ style](https://www.chromium.org/blink/coding-style) that the project adopted; `make
  check-static` runs cppcheck and `cpplint` is part of the lint target.
- The SecLang grammar lives in `src/parser/seclang-scanner.ll` and `src/parser/seclang-parser.yy`; the
  generated parser is committed, so regenerate it with `./configure --enable-parser-generation` (Flex and
  Bison required) and commit the result together with the grammar change.
- Operators are classes under `src/operators/`, transformations under `src/actions/transformations/`, actions
  under `src/actions/`, variables under `src/variables/`. Each is registered in the parser and, for operators
  and transformations, in the factory in `operator.cc` or `transformation.cc`.
- The public API lives in `headers/modsecurity/`; changes there affect every connector and binding, so keep
  binary compatibility whenever possible and say so in the pull request when you cannot.
- Use assertions for invariants and build with `--enable-assertions` while developing; `CFLAGS="-g -O0"` gives
  readable backtraces in gdb and Valgrind.

## Tests

Both trees carry their tests in the repository and in the shared
[secrules-language-tests](https://github.com/owasp-modsecurity/secrules-language-tests) submodule, so a clone
needs `git submodule update --init --recursive`.

- **v2:** `make test` builds `tests/msc_test` and runs the unit tests in `tests/op/*.t`, `tests/tfn/*.t` and
  `tests/action/*.t` (Perl hashes with `input`, `output` and `ret`). `make test-regression` runs
  `tests/regression/*.t` through a local Apache httpd.
- **v3:** `make check` builds and runs `test/unit_tests` (JSON cases under `test/test-cases/unit/`) and
  `test/regression_tests` (JSON cases under `test/test-cases/regression/`, each a request, a response, the rules
  to load and the expected `http_code`, `debug_log`, `error_log`, `audit_log` or `parser_error`). A single file
  can be run with `test/regression_tests test/test-cases/regression/<file>.json`, and `test/benchmark` measures
  throughput against a rule set.
- A new operator or transformation needs a unit test; any other change is expected to come with a regression
  test that fails before the fix and passes after it. State in the pull request that you ran it both ways.

## Documentation

This site is built with Hugo from Markdown in the [documentation repository](https://github.com/owasp-modsecurity/documentation);
`hugo serve` renders it locally. Every reference-manual entry carries metadata saying in which v2 and v3
versions it is available, so a code change that adds, removes or alters a directive, variable, action,
operator or transformation should come with a pull request here, and corrections to the text are welcome on
their own. The conventions (American English, the `secmeta` block, the `seclang` code fences formatted per
the CRS guidelines) are described in the repository's `CLAUDE.md` and enforced by its CI.

## Packaging and bindings

Packages for the major distributions and the [digitalwave repository]({{% relref "2-installation/2-4-distribution-recipes#the-digitalwave-repository" %}})
are maintained by community members and the maintainers; if you package ModSecurity for another distribution,
tell the project so it can be listed. The same goes for bindings to libModSecurity: the C and C++ API is kept
stable so that bindings keep working across releases.
