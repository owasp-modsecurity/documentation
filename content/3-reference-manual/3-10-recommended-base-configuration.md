---
title: Recommended Base Configuration
weight: 10
---

Each release ships a `modsecurity.conf-recommended` file with the engine settings an administrator is expected to
own: engine mode, body handling, limits, logging and file locations. Rule sets such as the OWASP CRS build on top
of it and must not repeat these settings. Both code lines carry their own copy:

- ModSecurity v2: [modsecurity.conf-recommended](https://github.com/owasp-modsecurity/ModSecurity/blob/v2/master/modsecurity.conf-recommended) (v{{< param modsec_v2_latest >}})
- libModSecurity v3: [modsecurity.conf-recommended](https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/modsecurity.conf-recommended) (v{{< param modsec_v3_latest >}})

Copy the file to your configuration directory as `modsecurity.conf`, together with `unicode.mapping` from the same
tree, and include it before any rule set. Distribution packages install both files for you (see the
[installation chapter]({{% relref "2-installation" %}})). The sections below walk through the file as shipped in
v{{< param modsec_v2_latest >}}; the examples are reformatted per the site's conventions and the v3 differences are
called out where they occur.

## Rule engine

``` seclang
SecRuleEngine DetectionOnly
```

The engine starts in detection-only mode so that a fresh installation cannot disrupt the application. Rules are
evaluated and logged but never block. Switch to `On` once the logs look clean. See
[SecRuleEngine]({{% relref "3-reference-manual/3-2-configuration-directives#secruleengine" %}}).

## Request body handling

``` seclang
SecRequestBodyAccess On

SecRule REQUEST_HEADERS:Content-Type "@rx ^(?:application(?:/soap\+|/)|text/)xml" \
    "id:'200000',\
    phase:1,\
    pass,\
    t:none,\
    t:lowercase,\
    nolog,\
    ctl:requestBodyProcessor=XML"

SecRule REQUEST_HEADERS:Content-Type "@rx ^application/json" \
    "id:'200001',\
    phase:1,\
    pass,\
    t:none,\
    t:lowercase,\
    nolog,\
    ctl:requestBodyProcessor=JSON"

#SecRule REQUEST_HEADERS:Content-Type "^application/[a-z0-9.-]+[+]json" \
#    "id:'200006',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"
```

Without request body access ModSecurity never sees POST parameters, which leaves a large hole, so it is on. The
engine selects the `application/x-www-form-urlencoded` and `multipart/form-data` parsers on its own; the XML and
JSON parsers must be chosen by a phase 1 rule from the `Content-Type` header, which rules 200000 and 200001 do.
Rule 200006 is shipped commented out; enable or adapt it if your application sends `+json` subtypes such as
`application/problem+json`. The JSON parser requires a build with YAJL.

``` seclang
SecRequestBodyLimit 13107200
SecRequestBodyNoFilesLimit 131072
SecRequestBodyInMemoryLimit 131072
SecRequestBodyLimitAction Reject
SecRequestBodyJsonDepthLimit 512
```

The first limit (12.5 MB) is the largest request body that will be buffered and must be as large as the biggest
file upload you accept; the second (128 KB) applies to bodies without file parts and should stay as low as the
application allows. `SecRequestBodyLimitAction Reject` rejects bodies over the limit, but the engine forces
`ProcessPartial` while `SecRuleEngine` is `DetectionOnly`, so nothing is rejected during the initial deployment.
The JSON depth limit keeps deeply nested documents from exhausting the parser.

{{% notice note "libModSecurity v3" %}}
`SecRequestBodyInMemoryLimit` is absent from the v3 file: the library does not buffer to disk and rejects the
directive. The v3 file instead adds `SecArgumentsLimit 1000` and rule 200007, which denies a request whose argument
count reaches that limit, because v3 stops parsing arguments silently once the limit is hit:

``` seclang
SecArgumentsLimit 1000

SecRule &ARGS "@ge 1000" \
    "id:'200007',\
    phase:2,\
    deny,\
    status:400,\
    t:none,\
    log,\
    msg:'Failed to fully parse request body due to large argument count',\
    severity:2"
```

ModSecurity v2 applies the same default limit of 1000 arguments without the directive, and also sets
`REQBODY_ERROR` when it is exceeded, so rule 200002 below covers it there.
{{% /notice %}}

``` seclang
SecRule REQBODY_ERROR "!@eq 0" \
    "id:'200002',\
    phase:2,\
    deny,\
    status:400,\
    t:none,\
    log,\
    msg:'Failed to parse request body.',\
    logdata:'%{reqbody_error_msg}',\
    severity:2"

SecRule MULTIPART_STRICT_ERROR "!@eq 0" \
    "id:'200003',\
    phase:2,\
    deny,\
    status:400,\
    t:none,\
    log,\
    msg:'Multipart request body failed strict validation: RE %{REQBODY_ERROR}, BQ %{MULTIPART_BOUNDARY_QUOTED}, BW %{MULTIPART_BOUNDARY_WHITESPACE}, DB %{MULTIPART_DATA_BEFORE}, DA %{MULTIPART_DATA_AFTER}, DH %{MULTIPART_DUPLICATE_PART_HEADER}, HF %{MULTIPART_HEADER_FOLDING}, LF %{MULTIPART_LF_LINE}, SM %{MULTIPART_MISSING_SEMICOLON}, IQ %{MULTIPART_INVALID_QUOTING}, IP %{MULTIPART_INVALID_PART}, IH %{MULTIPART_INVALID_HEADER_FOLDING}, FL %{MULTIPART_FILE_LIMIT_EXCEEDED}'"

SecRule MULTIPART_UNMATCHED_BOUNDARY "!@eq 0" \
    "id:'200004',\
    phase:2,\
    deny,\
    t:none,\
    log,\
    msg:'Multipart parser detected a possible unmatched boundary.'"
```

A request body the engine could not parse is a request the rules cannot inspect, so rule 200002 denies it with a
400 and logs the parser's message. Rule 200003 enforces strict `multipart/form-data` validation and lists every
[MULTIPART_* flag]({{% relref "3-reference-manual/3-3-variables#multipart_strict_error" %}}) in its message so the
audit log shows which check failed; if it proves too strict for an application, switch it to detection rather than
removing it. Rule 200004 catches lines that look like a boundary but do not match the declared one.

{{% notice note "libModSecurity v3" %}}
The v3 file's rule 200003 reports `PE %{REQBODY_PROCESSOR_ERROR}` instead of `RE %{REQBODY_ERROR}` (v2 removed
`REQBODY_PROCESSOR_ERROR` in 2.9.14) and has no `DH` item, since `MULTIPART_DUPLICATE_PART_HEADER` arrived in
3.0.17 after the file was last changed. Its rule 200004 is `@eq 1` rather than `!@eq 0`: since 3.0.3 the v3
parser sets the variable to 1 when a mandatory boundary line is missing or out of order and to 2 when extra lines
merely start with `--`, so `@eq 1` is the permissive form that lets PEM files and similar content through, and
`!@eq 0` is the strict form.
{{% /notice %}}

``` seclang
SecPcreMatchLimit 1000
SecPcreMatchLimitRecursion 1000

SecRule TX:/^MSC_/ "!@streq 0" \
    "id:'200005',\
    phase:2,\
    deny,\
    t:none,\
    log,\
    msg:'ModSecurity internal error flagged: %{MATCHED_VAR_NAME}'"
```

The PCRE limits cap the work a single regular expression may do, against regular-expression denial of service. When
a limit is hit the engine sets `TX:MSC_PCRE_LIMITS_EXCEEDED` instead of matching, and rule 200005 turns any such
`MSC_` flag into a denial. Since 2.9.16, v2 also sets `TX:MSC_PCRE_ERROR` when a pattern is invalid after macro
expansion, and this rule catches it too. In v3 `SecPcreMatchLimitRecursion` is accepted but ignored, and the match limit
is honored since 3.0.10. v3 sets `TX:MSC_PCRE_ERROR` on any regex error since 3.0.18. Earlier v3 releases report
these errors only in the standalone `MSC_PCRE_ERROR` variable, which `TX:/^MSC_/` does not see.

## Response body handling

``` seclang
SecResponseBodyAccess On
SecResponseBodyMimeType text/plain text/html text/xml
SecResponseBodyLimit 524288
SecResponseBodyLimitAction ProcessPartial
```

Response inspection is what catches error pages and data leakage, at the price of memory and latency. Only the
listed MIME types are buffered, so static files are not; adjust the list to the documents your application
produces (JSON responses need `application/json` added). Bodies over 512 KB are processed as far as the limit
and the rest is passed through, which is less secure but never breaks a legitimate page.

## File system locations

``` seclang
SecTmpDir /tmp/
SecDataDir /tmp/

#SecUploadDir /opt/modsecurity/var/upload/
#SecUploadKeepFiles RelevantOnly
#SecUploadFileMode 0600
```

Temporary files (request bodies over the in-memory limit) and persistent collections go to `/tmp` only because
every system has it; both should point at a directory private to the web server user. The upload directives are
commented out: set `SecUploadDir` to a private directory and `SecUploadKeepFiles RelevantOnly` when you add a file
inspection rule (`@inspectFile`), which is what decides which files are relevant.

{{% notice note "libModSecurity v3" %}}
v3 accepts `SecTmpDir` and `SecDataDir` but ignores them: collections live in process memory unless the library
was built with LMDB (see [Persistent Storage]({{% relref "3-reference-manual/3-8-persistent-storage" %}})), and
there is no disk buffering of request bodies. `SecUploadKeepFiles RelevantOnly` is rejected by v3; use `On`.
{{% /notice %}}

## Debug and audit logging

``` seclang
#SecDebugLog /opt/modsecurity/var/log/debug.log
#SecDebugLogLevel 3

SecAuditEngine RelevantOnly
SecAuditLogRelevantStatus "^(?:5|4(?!04))"
SecAuditLogParts ABIJDEFHZ
SecAuditLogType Serial
SecAuditLog /var/log/modsec_audit.log
#SecAuditLogStorageDir /opt/modsecurity/var/audit/
```

The debug log stays off; at level 3 it would only duplicate the error log. The audit log records the transactions
a rule marked as relevant plus every server error, meaning 5xx and 4xx responses except 404. All parts are logged,
including request and response bodies, to a single serial file, which is convenient to read but meant for
occasional use; switch to `Concurrent` with a storage directory for busy servers. Distribution packages change the
log path to their own log directory.

## Miscellaneous

``` seclang
SecArgumentSeparator &
SecCookieFormat 0
SecUnicodeMapFile unicode.mapping 20127
SecStatusEngine Off
```

The argument separator and cookie format match what almost every application uses; a wrong cookie format exposes
rules that examine named cookies to evasion. `unicode.mapping` with code page 20127 (US-ASCII) drives
`t:urlDecodeUni`; pick the code page of your application's language to reduce false positives and negatives. The
status engine, which used to report version information to the project, is off because there has been no receiver
for it since April 2022; v3 accepts the directive and ignores it.

## Differences between the two files

| Setting | v2 (v{{< param modsec_v2_latest >}}) | v3 (v{{< param modsec_v3_latest >}}) |
|---|---|---|
| `SecRequestBodyInMemoryLimit 131072` | present | absent; the directive is rejected by v3 |
| `SecArgumentsLimit 1000` plus rule 200007 | absent; v2 applies the limit by default | present |
| Rule 200003 message | `RE %{REQBODY_ERROR}` and a `DH` item | `PE %{REQBODY_PROCESSOR_ERROR}`, no `DH` item |
| Rule 200004 operator | `!@eq 0` | `@eq 1` (permissive mode) |
| `SecTmpDir`, `SecDataDir` | used | accepted but ignored |

Everything else is identical, including the rule IDs 200000 to 200007, which rule sets must not reuse.

## Impedance Mismatch

Web application firewalls have a difficult job trying to make sense of data that passes by, without any knowledge of the application and its business logic. The protection they provide comes from having an independent layer of security on the outside. Because data validation is done twice, security can be increased without having to touch the application. In some cases, however, the fact that everything is done twice brings problems. Problems can arise in the areas where the communication protocols are not well specified, or where either the device or the application do things that are not in the specification. In such cases it may be possible to design payload that will be interpreted in one way by one device and in another by the other device. This problem is better known as Impedance Mismatch. It can be exploited to evade the security devices.

While we will continue to enhance ModSecurity to deal with various evasion techniques the problem can only be minimized, but never solved. With so many different application backends chances are some will always do something completely unexpected. The only solution is to be aware of the technologies in the backend when writing rules, adapting the rules to remove the mismatch. See the next section for some examples.

### Impedance Mismatch with PHP Apps

When writing rules to protect PHP applications you need to pay attention to the following facts:

1.  When "register_globals" is set to "On" request parameters are automatically converted to script variables. In some PHP versions it is even possible to override the \$GLOBALS array.
2.  Whitespace at the beginning of parameter names is ignored. (This is very dangerous if you are writing rules to target specific named variables.)
3.  The remaining whitespace (in parameter names) is converted to underscores. The same applies to dots and to a "[" if the variable name does not contain a matching closing bracket. (Meaning that if you want to exploit a script through a variable that contains an underscore in the name you can send a parameter with a whitespace or a dot instead.)
4.  Cookies can be treated as request parameters.
5.  The discussion about variable names applies equally to the cookie names.
6.  The order in which parameters are taken from the request and the environment is EGPCS (environment, GET, POST, Cookies, built-in variables). This means that a POST parameter will overwrite the parameters transported on the request line (in QUERY_STRING).
7.  When "magic_quotes_gpc" is set to "On" PHP will use backslash to escape the following characters: single quote, double quote, backslash, and the nul byte.
8.  If "magic_quotes_sybase" is set to "On" only the single quote will be escaped using another single quote. In this case the "magic_quotes_gpc" setting becomes irrelevant. The "magic_quotes_sybase" setting completely overrides the "magic_quotes_gpc" behavior but "magic_quotes_gpc" still must be set to "On" for the Sybase-specific quoting to work.
9.  PHP will also automatically create nested arrays for you. For example "p[x][y]=1" results in a total of three variables.
