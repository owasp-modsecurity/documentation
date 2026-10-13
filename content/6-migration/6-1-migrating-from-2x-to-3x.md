---
title: Migrating from v2 to v3
weight: 1
---

This page is for administrators moving a working ModSecurity v2 (Apache `mod_security2` or IIS) deployment to libModSecurity v3, typically because the web server changes to NGINX. Both versions are maintained by OWASP and implement the same rule language, so rule sets such as the OWASP CRS run on both; the differences are in the architecture, in a few evaluation details and in the legacy features v3 does not implement. If you stay on Apache httpd or IIS there is no need to migrate: v2 remains the supported choice there (current release {{< param modsec_v2_latest >}}).

## What changed architecturally

**Library plus connectors.** v2 is a web server module and contains the engine, the Apache glue and the IIS module in one tree. v3 (current release {{< param modsec_v3_latest >}}) is only the engine, `libmodsecurity`, with a C and a C++ API. The web server integration is a separate *connector* project with its own release cycle: [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx) for NGINX (production ready) and [ModSecurity-apache](https://github.com/owasp-modsecurity/ModSecurity-apache) (not production ready, so Apache users should stay on v2). All Apache dependencies (APR, apxs) are gone from the engine. See [Building libModSecurity v3 from source]({{% relref "2-installation/2-1-building-libmodsecurity" %}}) and [libModSecurity v3 with NGINX]({{% relref "2-installation/2-2-libmodsecurity-v3-nginx" %}}).

**Configuration scopes.** In v2 the rules live in Apache's configuration and inherit through `<VirtualHost>`, `<Location>`, `<Directory>` and `.htaccess` contexts. In v3 the connector loads the rules: with ModSecurity-nginx you point `modsecurity_rules_file` (or `modsecurity_rules` / `modsecurity_rules_remote`) at a file in an `http`, `server` or `location` block, and you can refine the global set per location with `SecRuleRemoveById` and similar directives. [SecRuleInheritance]({{% relref "3-reference-manual/3-2-configuration-directives#secruleinheritance" %}}) `On` is rejected by the v3 parser.

**Persistent storage.** v2 keeps the `IP`, `GLOBAL`, `RESOURCE`, `SESSION` and `USER` collections in SDBM files under `SecDataDir`, shared by all worker processes. v3 keeps them in memory per process by default; the data is not shared between NGINX workers and is lost on restart. Build with `--with-lmdb` for an LMDB-backed shared store. [SecDataDir]({{% relref "3-reference-manual/3-2-configuration-directives#secdatadir" %}}) is accepted but ignored. See [Persistent Storage]({{% relref "3-reference-manual/3-8-persistent-storage" %}}).

**Request body buffering.** [SecRequestBodyInMemoryLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secrequestbodyinmemorylimit" %}}) is rejected at load time by v3, which follows the web server's own buffering configuration (`client_body_buffer_size` in NGINX). Remove the directive from a configuration copied from v2.

**Logging.** v3 writes the same audit log formats (native and JSON, serial and concurrent) and a debug log, but there is no Apache error log: alerts go through the connector to the web server's error log. mlogc, the v2 log collector, is not part of v3; ship the JSON audit log with a generic log forwarder instead. See [Logging and Data Formats]({{% relref "4-logging" %}}).

**Base configuration.** Start from the v3 `modsecurity.conf-recommended`, not the v2 file; the differences are listed in [Recommended Base Configuration]({{% relref "3-reference-manual/3-10-recommended-base-configuration" %}}).

## Rule evaluation differences to check in custom rules

- **Default phase.** A rule without `phase:` runs in phase 2 in v2 but in phase 1 in v3. Set `phase:` on every rule.
- **`SecDefaultAction`.** v3 allows one `SecDefaultAction` per phase and rejects a second one; it also applies the inherited disruptive action only to rules that carry `block`. v2 lets a later `SecDefaultAction` replace an earlier one.
- **Phase 4 without body inspection.** v2 runs phase 4 rules with an empty `RESPONSE_BODY`; v3 skips phase 4 when `SecResponseBodyAccess` is Off or the MIME type is not inspected.
- **`skipAfter`.** If the named `SecMarker` does not exist, v3 skips every remaining rule of every later phase; v2 ends the skip with the phase.
- **`ctl:ruleEngine=Off`.** v2 stops the current phase immediately; v3 only checks the engine state when a phase starts.
- **`SecRuleRemoveByTag` / `SecRuleRemoveByMsg`.** v2 matches the parameter as an unanchored regular expression; v3 compares the whole tag or message literally.
- **`initcol` and `setvar` in one rule.** v3 runs `setvar` before `initcol` within the same rule; initialize the collection in a separate, earlier rule.
- **`SecUploadKeepFiles RelevantOnly`** is rejected by v3; use `On` or `Off`.
- **`SecCookieFormat 1`** is not supported by v3.

See [Processing Phases]({{% relref "3-reference-manual/3-1-processing-phases" %}}) for details.

## Not supported in v3

The lists below contain the v2 features that libModSecurity v3 does not implement, taken from the compatibility matrix of the [SecLang specification](https://seclang.org/compat/matrix/) (`compat/matrix.json`, entries with `v2: true, v3: false`; see [Rules language porting specification]({{% relref "6-migration/6-3-rules-language-porting" %}})). Most of them are tied to Apache internals or to retired services and are marked deprecated in the specification; no current rule set uses them.

### Directives

Rejected by the v3 parser at load time (remove them from the configuration):

- [SecCacheTransformations]({{% relref "3-reference-manual/3-2-configuration-directives#seccachetransformations" %}}) - experimental in v2, dropped.
- [SecChrootDir]({{% relref "3-reference-manual/3-2-configuration-directives#secchrootdir" %}})
- [SecConnReadStateLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secconnreadstatelimit" %}}) and [SecConnWriteStateLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secconnwritestatelimit" %}}) - Apache connection-state limits; use the web server's own limits (for example `limit_conn` in NGINX). The older spellings [SecReadStateLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secreadstatelimit" %}}) and [SecWriteStateLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secwritestatelimit" %}}) are unknown to v3.
- [SecGsbLookupDb]({{% relref "3-reference-manual/3-2-configuration-directives#secgsblookupdb" %}}) and the `@gsbLookup` operator - the Google Safe Browsing v1 API they used no longer exists.
- [SecGuardianLog]({{% relref "3-reference-manual/3-2-configuration-directives#secguardianlog" %}})
- [SecHashEngine]({{% relref "3-reference-manual/3-2-configuration-directives#sechashengine" %}}) `On`, [SecHashKey]({{% relref "3-reference-manual/3-2-configuration-directives#sechashkey" %}}), [SecHashParam]({{% relref "3-reference-manual/3-2-configuration-directives#sechashparam" %}}), [SecHashMethodRx]({{% relref "3-reference-manual/3-2-configuration-directives#sechashmethodrx" %}}), [SecHashMethodPm]({{% relref "3-reference-manual/3-2-configuration-directives#sechashmethodpm" %}})
- [SecRequestBodyInMemoryLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secrequestbodyinmemorylimit" %}})
- [SecServerSignature]({{% relref "3-reference-manual/3-2-configuration-directives#secserversignature" %}})
- [SecStreamInBodyInspection]({{% relref "3-reference-manual/3-2-configuration-directives#secstreaminbodyinspection" %}}) and [SecStreamOutBodyInspection]({{% relref "3-reference-manual/3-2-configuration-directives#secstreamoutbodyinspection" %}}), with the `STREAM_INPUT_BODY` / `STREAM_OUTPUT_BODY` variables and the `@rsub` operator that depends on them.
- [SecUnicodeCodePage]({{% relref "3-reference-manual/3-2-configuration-directives#secunicodecodepage" %}}) - use the code page argument of `SecUnicodeMapFile` instead.
- [SecRequestEncoding]({{% relref "3-reference-manual/3-2-configuration-directives#secrequestencoding" %}}) - accepted by v2 but never implemented.
- `On` is rejected for [SecConnEngine]({{% relref "3-reference-manual/3-2-configuration-directives#secconnengine" %}}), [SecContentInjection]({{% relref "3-reference-manual/3-2-configuration-directives#seccontentinjection" %}}), [SecDisableBackendCompression]({{% relref "3-reference-manual/3-2-configuration-directives#secdisablebackendcompression" %}}), [SecInterceptOnError]({{% relref "3-reference-manual/3-2-configuration-directives#secinterceptonerror" %}}) and [SecRuleInheritance]({{% relref "3-reference-manual/3-2-configuration-directives#secruleinheritance" %}}); `Off` is accepted. [SecSensorId]({{% relref "3-reference-manual/3-2-configuration-directives#secsensorid" %}}) and [SecRulePerfTime]({{% relref "3-reference-manual/3-2-configuration-directives#secruleperftime" %}}) are rejected.

### Variables

- [MULTIPART_CRLF_LINE]({{% relref "3-reference-manual/3-3-variables#multipart_crlf_line" %}})
- `PERF_*` rule-timing variables: [PERF_ALL]({{% relref "3-reference-manual/3-3-variables#perf_all" %}}), [PERF_COMBINED]({{% relref "3-reference-manual/3-3-variables#perf_combined" %}}), [PERF_GC]({{% relref "3-reference-manual/3-3-variables#perf_gc" %}}), [PERF_LOGGING]({{% relref "3-reference-manual/3-3-variables#perf_logging" %}}), [PERF_PHASE1]({{% relref "3-reference-manual/3-3-variables#perf_phase1" %}}) through `PERF_PHASE5`, [PERF_RULES]({{% relref "3-reference-manual/3-3-variables#perf_rules" %}}), [PERF_SREAD]({{% relref "3-reference-manual/3-3-variables#perf_sread" %}}), [PERF_SWRITE]({{% relref "3-reference-manual/3-3-variables#perf_swrite" %}})
- `SCRIPT_*` variables (Apache file metadata): [SCRIPT_BASENAME]({{% relref "3-reference-manual/3-3-variables#script_basename" %}}), [SCRIPT_FILENAME]({{% relref "3-reference-manual/3-3-variables#script_filename" %}}), [SCRIPT_GID]({{% relref "3-reference-manual/3-3-variables#script_gid" %}}), [SCRIPT_GROUPNAME]({{% relref "3-reference-manual/3-3-variables#script_groupname" %}}), [SCRIPT_MODE]({{% relref "3-reference-manual/3-3-variables#script_mode" %}}), [SCRIPT_UID]({{% relref "3-reference-manual/3-3-variables#script_uid" %}}), [SCRIPT_USERNAME]({{% relref "3-reference-manual/3-3-variables#script_username" %}})
- [SDBM_DELETE_ERROR]({{% relref "3-reference-manual/3-3-variables#sdbm_delete_error" %}}) - no SDBM in v3.
- [STATUS_LINE]({{% relref "3-reference-manual/3-3-variables#status_line" %}}) - use `RESPONSE_STATUS` and `RESPONSE_PROTOCOL`.
- [STREAM_INPUT_BODY]({{% relref "3-reference-manual/3-3-variables#stream_input_body" %}}) and [STREAM_OUTPUT_BODY]({{% relref "3-reference-manual/3-3-variables#stream_output_body" %}})
- [USERAGENT_IP]({{% relref "3-reference-manual/3-3-variables#useragent_ip" %}})
- [WEBSERVER_ERROR_LOG]({{% relref "3-reference-manual/3-3-variables#webserver_error_log" %}}) - Apache error log messages are not visible to the library.

### Actions

- [append]({{% relref "3-reference-manual/3-5-actions#append" %}}) and [prepend]({{% relref "3-reference-manual/3-5-actions#prepend" %}}) (content injection)
- [deprecatevar]({{% relref "3-reference-manual/3-5-actions#deprecatevar" %}})
- [marker]({{% relref "3-reference-manual/3-5-actions#marker" %}})
- [pause]({{% relref "3-reference-manual/3-5-actions#pause" %}})
- [proxy]({{% relref "3-reference-manual/3-5-actions#proxy" %}}) - relied on Apache mod_proxy.
- [sanitiseArg]({{% relref "3-reference-manual/3-5-actions#sanitisearg" %}}), [sanitiseMatched]({{% relref "3-reference-manual/3-5-actions#sanitisematched" %}}), [sanitiseMatchedBytes]({{% relref "3-reference-manual/3-5-actions#sanitisematchedbytes" %}}), [sanitiseRequestHeader]({{% relref "3-reference-manual/3-5-actions#sanitiserequestheader" %}}), [sanitiseResponseHeader]({{% relref "3-reference-manual/3-5-actions#sanitiseresponseheader" %}}) - audit log masking.
- The following [ctl]({{% relref "3-reference-manual/3-5-actions#ctl" %}}) options: `debugLogLevel`, `hashEnforcement`, `hashEngine`, `requestBodyLimit`, `responseBodyAccess`, `responseBodyLimit`, `ruleRemoveByMsg`, `ruleRemoveTargetByMsg`. v3 implements `auditEngine`, `auditLogParts`, `requestBodyAccess`, `requestBodyProcessor`, `ruleEngine`, `ruleRemoveById`, `ruleRemoveByTag`, `ruleRemoveTargetById` and `ruleRemoveTargetByTag`.

### Operators

- [gsbLookup]({{% relref "3-reference-manual/3-6-operators#gsblookup" %}}) and [rsub]({{% relref "3-reference-manual/3-6-operators#rsub" %}}) load but have nothing to operate on in v3, because the directive and the variables they depend on are not supported (see above). No other v2 operator is missing.

### Transformations

All v2 transformation functions are available in v3. (`t:uppercase` exists in v3 but not in v2.)

## Checklist

1.  Install libmodsecurity and the connector for your web server.
2.  Start from the v3 `modsecurity.conf-recommended`; copy only your site-specific values (limits, audit log location, MIME types) from the old file.
3.  Remove the directives listed above from your configuration; the v3 parser refuses to load a file that contains most of them.
4.  Grep your custom rules for the variables, actions and `ctl` options listed above and for rules without `phase:`.
5.  If you depend on `IP`, `GLOBAL` or other persistent collections (for example the CRS DoS-protection plugin), build with `--with-lmdb` or accept per-worker counters.
6.  Run in `SecRuleEngine DetectionOnly`, compare the audit log with the v2 deployment, then switch to `On`.
7.  Report anything that behaves differently and is not listed here at <https://github.com/owasp-modsecurity/ModSecurity/issues>.
