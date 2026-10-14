---
title: Processing Phases
weight: 1
---

ModSecurity, in both v2 and v3, allows rules to be placed in one of the following five phases of an HTTP transaction:

| Phase | Name | Runs after | Data available |
|---|---|---|---|
| 1 | Request headers (`REQUEST_HEADERS`) | the request line and headers have been read | `REQUEST_*`, `ARGS_GET`, `REQUEST_HEADERS`, `REQUEST_COOKIES` |
| 2 | Request body (`REQUEST_BODY`) | the request body has been read, if `SecRequestBodyAccess` is On | everything in phase 1 plus `ARGS_POST`, `ARGS`, `REQUEST_BODY`, `FILES*`, `XML`, `JSON` |
| 3 | Response headers (`RESPONSE_HEADERS`) | the response status and headers are known | plus `RESPONSE_STATUS`, `RESPONSE_HEADERS` |
| 4 | Response body (`RESPONSE_BODY`) | the response body has been read, if `SecResponseBodyAccess` is On and the MIME type is inspected | plus `RESPONSE_BODY` |
| 5 | Logging (`LOGGING`) | the response has been sent | everything; disruptive actions have no effect |

In ModSecurity v2 the phases are hooks in the Apache request cycle. In libModSecurity v3 the phases are the `process*()` calls the connector (for example ModSecurity-nginx) makes on a transaction: `processConnection`, `processURI`, `processRequestHeaders`, `processRequestBody`, `processResponseHeaders`, `processResponseBody` and `processLogging`. The rule semantics are the same; the differences are listed at the end of this page.

In order to select the phase a rule executes during, use the phase action either directly in the rule or in the SecDefaultAction directive:

``` seclang
SecDefaultAction "log,pass,phase:2"
SecRule REQUEST_HEADERS:Host "!^$" "id:5,deny,phase:1"
```

The phase can be given by number or by name: `phase:request` is phase 2, `phase:response` is phase 4 and `phase:logging` is phase 5.

{{% notice note %}}

The data available in each phase is cumulative. This means that as you move onto later phases, you have access to more and more data from the transaction.

{{% /notice %}}

{{% notice note %}}

Keep in mind that rules are executed according to phases, so even if two rules are adjacent in a configuration file, but are set to execute in different phases, they would not happen one after the other. The order of rules in the configuration file is important only within the rules of each phase. This is especially important when using the skip and skipAfter actions.

{{% /notice %}}

{{% notice note %}}

The LOGGING phase is special. It is executed at the end of each transaction no matter what happened in the previous phases. This means it will be processed even if the request was intercepted or the allow action was used to pass the transaction through.

{{% /notice %}}

{{% notice warning %}}

Always set `phase` explicitly on every rule. A rule without a `phase` action runs in phase 2 in ModSecurity v2 (or in the phase named by the `SecDefaultAction` that precedes it), but in phase **1** in libModSecurity v3. The OWASP CRS sets the phase on every rule for this reason.

{{% /notice %}}

## Phase Request Headers

Rules in this phase are processed immediately after the request headers have been received. At this point the request body has not been read yet, meaning not all request arguments are available. Rules should be placed in this phase if you need to have them run early, to do something before the request body has been read, determine whether or not the request body should be buffered, or decide how you want the request body to be processed (e.g. whether to parse it as XML or JSON).

{{% notice note "ModSecurity v2 (Apache)" %}}

Since ModSecurity 2.6, phase 1 runs in Apache's *fixups* hook, after Apache has mapped the request to its `<Location>`, `<Directory>` or `<Files>` context, so rules placed inside those scopes work in phase 1. If ModSecurity was compiled with `--enable-request-early`, phase 1 runs in the earlier *post-read-request* hook instead; Apache has not evaluated scope directives at that point, and only `<VirtualHost>` scope is available. See [Miscellaneous Topics]({{% relref "3-reference-manual/3-9-miscellaneous-topics" %}}).

{{% /notice %}}

## Phase Request Body

This is the general-purpose input analysis phase. Most of the application-oriented rules should go here. In this phase you are guaranteed to have received the request arguments (provided the request body has been read). Both versions support four request body processors:

- **application/x-www-form-urlencoded** - used to transfer form data
- **multipart/form-data** - used for file transfers
- **XML** - used for passing XML data (`ctl:requestBodyProcessor=XML`)
- **JSON** - used for passing JSON data (`ctl:requestBodyProcessor=JSON`, requires a build with YAJL)

Other encodings are not used by most web applications. The XML and JSON processors are not selected automatically; `modsecurity.conf-recommended` contains phase 1 rules that enable them based on the `Content-Type` header.

{{% notice note %}}

In order to access the Request Body phase data, you must have [SecRequestBodyAccess]({{% relref "3-reference-manual/3-2-configuration-directives#secrequestbodyaccess" %}}) set to On.

{{% /notice %}}

## Phase Response Headers

This phase takes place just before response headers are sent back to the client. Run here if you want to observe the response before that happens, and if you want to use the response headers to determine if you want to buffer the response body.

{{% notice note "ModSecurity v2 (Apache)" %}}

Some response status codes (such as 404) are handled earlier in the request cycle by Apache and may not be able to be triggered as expected. Additionally, there are some response headers that are added by Apache at a later hook (such as Date, Server and Connection) that ModSecurity is not able to trigger on or sanitize. This should work appropriately in a proxy setup or within phase 5 (logging).

{{% /notice %}}

## Phase Response Body

This is the general-purpose output analysis phase. At this point you can run rules against the response body (provided it was buffered, of course). This is the phase where you would want to inspect the outbound HTML for information disclosure, error messages or failed authentication text.

{{% notice note %}}

In order to access the Response Body phase data, you must have [SecResponseBodyAccess]({{% relref "3-reference-manual/3-2-configuration-directives#secresponsebodyaccess" %}}) set to On and the response MIME type must be listed in [SecResponseBodyMimeType]({{% relref "3-reference-manual/3-2-configuration-directives#secresponsebodymimetype" %}}). When the body is not inspected, ModSecurity v2 still evaluates phase 4 rules with an empty `RESPONSE_BODY`; libModSecurity v3 does not evaluate phase 4 at all.

{{% /notice %}}

## Phase Logging

This phase is run just before logging takes place. The rules placed into this phase can only affect how the logging is performed. You cannot deny/block connections in this phase as it is too late. This phase also allows for inspection of other response headers that weren't available during phase 3 or phase 4. In ModSecurity v2 this phase can also inspect the error messages logged by Apache (`WEBSERVER_ERROR_LOG`). Note that you must be careful not to inherit a disruptive action into a rule in this phase as this is a configuration error in ModSecurity 2.5.0 and later versions.

## Differences between ModSecurity v2 and libModSecurity v3

- **Default phase.** v2: phase 2, or the phase of the preceding `SecDefaultAction`. v3: phase 1. Always write `phase:` explicitly.
- **Phase 4 without body inspection.** v2 runs phase 4 rules with an empty `RESPONSE_BODY`; v3 skips the phase entirely when `SecResponseBodyAccess` is not On or the MIME type is not inspected.
- **Phase 0.** v3 accepts `phase:0` (connection phase, evaluated when the connector calls `processConnection`, when only `REMOTE_ADDR`, `REMOTE_HOST`, `REMOTE_PORT`, `SERVER_ADDR`, `SERVER_PORT` and `UNIQUE_ID` are known). v2 has no phase 0.
- **`skipAfter` with a missing marker.** In v2 a skip ends with the current phase. In v3 the pending marker persists across phases: if no `SecMarker` of that name exists, every remaining rule of every later phase is skipped. Always define the marker.
- **`ctl:ruleEngine=Off` mid-phase.** v2 stops evaluating the rest of the current phase immediately; v3 checks the engine state only when a phase starts, so the remaining rules of the current phase are still evaluated (none of them can interrupt). Place such a rule last in its phase.
- **Web server scopes.** In v2 rules can be placed in Apache `<VirtualHost>`, `<Location>`, `<Directory>` and (with `--enable-htaccess-config`) `.htaccess` contexts and are merged by Apache's configuration inheritance. In v3 the connector decides the scopes: ModSecurity-nginx loads rules per `http`, `server` or `location` block via `modsecurity_rules_file`, `modsecurity_rules_remote` and `modsecurity_rules`.
