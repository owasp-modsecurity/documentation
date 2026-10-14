---
title: SecLang specification
weight: 3
---

The rules language that ModSecurity v2 and libModSecurity v3 implement, usually called SecLang, is also
implemented by other engines, most notably [OWASP Coraza](https://coraza.io/). Rather than a porting checklist
maintained here, the language is specified independently of any engine at <https://seclang.org/>:

- The [specification](https://seclang.org/) describes every directive, variable, operator, action and
  transformation with its syntax and semantics.
- The [compatibility matrix](https://seclang.org/compat/matrix/) records, for each item, whether ModSecurity v2,
  libModSecurity v3 and Coraza implement it, and marks the items that are deprecated. It is the authoritative
  answer to "will this rule work on engine X" and the source of the lists in
  [Migrating from v2 to v3]({{% relref "6-migration/6-1-migrating-from-2x-to-3x" %}}).
- The [Coraza playground](https://playground.coraza.io/) runs a rule against a request in the browser and is a
  quick way to check syntax before deploying.

If you are porting the language to a new engine, start from the matrix: the items every engine implements
(`SecRule`, `SecRuleEngine`, the request and response variables, `@rx` and the numeric operators, the core
actions and transformations) are the ones rule sets such as the OWASP CRS depend on everywhere, and the rest can
follow the matrix's deprecation marks.
