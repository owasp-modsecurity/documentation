---
title: Miscellaneous Topics
weight: 9
---

The topics on this page apply to ModSecurity v2 running as an Apache module. libModSecurity v3 has no Apache dependency; the equivalent integration points belong to the connector (for example the `modsecurity_transaction_id` directive of ModSecurity-nginx, which ties the audit log entry to the NGINX access log).

## Logging in Apache via mod_log_config

ModSecurity v2 registers the `M` log handler with mod_log_config, so any ModSecurity variable can be written to the Apache access log as `%{VARIABLE}M`. A collection member is addressed with a dot, as in `%{TX.ANOMALY_SCORE}M`; the colon form used in rules is not accepted there. ModSecurity asks Apache to run its logging hook before mod_log_config, so the access log entry is written after phase 5 has run and the audit log record has been written, and every variable set during the transaction is available to it.

Example Apache mod_log_config:

``` apache
LogFormat "%t %{UNIQUE_ID}e %{MULTIPART_STRICT_ERROR}M %{TX.ANOMALY_SCORE}M" custom-format
```

## Precedence of ModSecurity over other Apache modules

ModSecurity rules run in one of five phases. Phase 1 runs once the request headers have been read and Apache has mapped the request, phase 2 after ModSecurity has read the request body, phases 3 and 4 in an output filter while the response is being generated, and phase 5 in Apache's logging hook after the response has been sent, before the access log entry is written.

The various phases are hooked into the Apache request lifecycle together with the other Apache modules. On each hook, there can be more than one module being executed. This is where precedence comes into play.

Precedence is assigned at compile time and hard-coded into the ModSecurity source code. Phase 1 runs in the *fixups* hook by default, ahead of mod_env, and the compile-time option `--enable-request-early` moves it to the *post-read-request* hook (see [Processing Phases]({{% relref "3-reference-manual/3-1-processing-phases" %}})). ModSecurity's startup runs after mod_unique_id and mod_ssl, and its logging hook runs before mod_log_config.

When examining the response, ModSecurity tries to be as early as possible: its output filter is registered ahead of the content-set filters of mod_headers, mod_deflate, mod_cache and mod_expires, so phases 3 and 4 see the response before mod_headers applies its _Header_ directive, before compression and before caching. However, when calling _Header_ with the keyword _early_, the precedence is raised and the directive is executed before ModSecurity phase 3. So if you want to edit HTTP response headers with mod_headers (adding the secure-flag to cookies springs to mind), you will usually have to wait until ModSecurity phase 5, before you can examine the effect of the header manipulation with ModSecurity.
