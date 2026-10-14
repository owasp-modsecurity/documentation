---
title: Roadmap
weight: 2
---

ModSecurity has no separate roadmap document. Planned work, release targets and open design questions are
tracked in the open on GitHub, where you can comment and vote:

- [Issues](https://github.com/owasp-modsecurity/ModSecurity/issues) - bugs and feature requests for both
  code lines. Label `2.x` or `3.x` selects the engine, and the
  [help wanted](https://github.com/owasp-modsecurity/ModSecurity/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
  label marks items waiting for a contributor.
- [Milestones](https://github.com/owasp-modsecurity/ModSecurity/milestones) - what is scheduled for the next
  v2.9.x and v3.0.x releases.
- [Pull requests](https://github.com/owasp-modsecurity/ModSecurity/pulls) - work in progress.
- The connectors have their own trackers: [ModSecurity-nginx issues](https://github.com/owasp-modsecurity/ModSecurity-nginx/issues)
  and [ModSecurity-apache issues](https://github.com/owasp-modsecurity/ModSecurity-apache/issues).

Both engines are maintained: v2 for Apache httpd and IIS, v3 as the library behind the NGINX connector. There is
no plan to retire v2, and features are added to both when they make sense on both; the
[compatibility matrix](https://seclang.org/compat/matrix/) of the SecLang specification shows where they differ.
Larger discussions happen on the OWASP Slack in `#project-modsecurity` and at the project's monthly community
calls announced there; see [Contributing]({{% relref "7-1-contributing" %}}).

The roadmap that used to live on this page described the goals of the 2.6 to 3.0 era (stream inspection, IP
reputation, data modification, the connector architecture); all of it has either shipped or been superseded.
