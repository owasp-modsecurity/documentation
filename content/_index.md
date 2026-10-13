---
title: ModSecurity Documentation
---

**ModSecurity is an open source, cross-platform web application firewall (WAF) engine**, donated to OWASP in 2024.
It has a robust event-based programming language which provides protection from a range of attacks against web
applications and allows for HTTP traffic monitoring, logging and real-time analysis. Securing tens of millions of
domains, ModSecurity is the most widely deployed WAF engine in existence.

Two engine generations are maintained:

- **ModSecurity v2** (current release {{< param modsec_v2_latest >}}) — the classic Apache module (`mod_security2`), also packaged for IIS.
- **libModSecurity v3** (current release {{< param modsec_v3_latest >}}) — a standalone library used through connectors for [NGINX](https://github.com/owasp-modsecurity/ModSecurity-nginx) and [Apache](https://github.com/owasp-modsecurity/ModSecurity-apache).

{{% notice warning %}}
This site was migrated from the former GitHub wiki, which is partially outdated. Entries in the reference manual carry
version badges for v2 and v3; text still marked for review is being updated against the source code.
{{% /notice %}}

{{% children depth="1" description="false" %}}

## Links

- [ModSecurity on GitHub](https://github.com/owasp-modsecurity/ModSecurity) — v2 lives on the `v2/master` branch, v3 on `v3/master`
- [OWASP ModSecurity project page](https://owasp.org/www-project-modsecurity/)
- [OWASP CRS](https://coreruleset.org/) — the de facto rule set for ModSecurity
