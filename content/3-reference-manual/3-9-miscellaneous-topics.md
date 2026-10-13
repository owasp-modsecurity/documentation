---
title: Miscellaneous Topics
weight: 9
---

The topics on this page apply to ModSecurity v2 running as an Apache module. libModSecurity v3 has no Apache dependency; the equivalent integration points belong to the connector (for example the `modsecurity_transaction_id` directive of ModSecurity-nginx, which ties the audit log entry to the NGINX access log).

## Logging in Apache via mod_log_config

The ModSecurity variables are accessible from Apache's mod_log_config (Apache access log). The entries take the form `%{VARIABLE}M`. Apache writes these logs at the very end of a transaction after the record in the ModSecurity audit log has been written. It is thus possible to log variables that are only defined after the writing of the audit log.

Example Apache mod_log_config:

``` apache
LogFormat "%t %{UNIQUE_ID}e %{MULTIPART_STRICT_ERROR}M %{TX.ANOMALY_SCORE}M" custom-format
```

## Precedence of ModSecurity over other Apache modules

ModSecurity rules run in one of five phases. The first two phases are executed as the request is being read, the third and the fourth phase are executed after the response has been generated and the fifth phase when the response has been sent and the logfile has been written.

The various phases are hooked into the Apache request lifecycle together with the other Apache modules. On each hook, there can be more than one module being executed. This is where precedence comes into play.

Precedence is assigned at compile time and mostly hard-coded into the ModSecurity source code. Phase 1 runs in the *fixups* hook by default; the compile-time option `--enable-request-early` moves it to the *post-read-request* hook (see [Processing Phases]({{% relref "3-reference-manual/3-1-processing-phases" %}})).

When examining the response, ModSecurity tries to be as early as possible. For example, the phase 3 and phase 4 will run before mod_headers with its _Header_ directive. However, when calling _Header_ with the keyword _early_, the precedence is raised and the directive is executed before ModSecurity phase 3. So if you want to edit HTTP response headers with mod_headers (adding the secure-flag to cookies springs to mind), you will usually have to wait until ModSecurity phase 5, before you can examine the effect of the header manipulation with ModSecurity.
