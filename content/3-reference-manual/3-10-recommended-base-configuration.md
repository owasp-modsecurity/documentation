---
title: Recommended Base Configuration
weight: 10
---

The recommended configuration file which handles the main ModSecurity directives/settings is shipped in the source archive of each release as `modsecurity.conf-recommended`. Each code line has its own copy:

- ModSecurity v2: <https://github.com/owasp-modsecurity/ModSecurity/blob/v2/master/modsecurity.conf-recommended>
- libModSecurity v3: <https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/modsecurity.conf-recommended>

Copy the file to your configuration directory as `modsecurity.conf`, together with `unicode.mapping` from the same tree, and include it before any rule set. The items listed in this recommended configuration are the items that the administrator should handle and configure for their own site. These settings should not be included within third-party rules files.

Both files set `SecRuleEngine DetectionOnly`, enable request and response body access, register the XML and JSON request body processors, set body limits, enable the audit log in `RelevantOnly` mode and set `SecStatusEngine Off`. The differences between the two files as of v{{< param modsec_v2_latest >}} and v{{< param modsec_v3_latest >}}:

| Setting | v2 | v3 |
|---|---|---|
| `SecRequestBodyInMemoryLimit 131072` | present | absent: the directive is rejected by v3, which follows the web server's own buffering settings |
| `SecArgumentsLimit 1000` plus rule 200007 (deny when `&ARGS` reaches the limit) | absent | present |
| Rule 200003 (multipart strict validation message) | reports `RE %{REQBODY_ERROR}` | reports `PE %{REQBODY_PROCESSOR_ERROR}` |
| Rule 200004 (`MULTIPART_UNMATCHED_BOUNDARY`) | `!@eq 0` | `@eq 1` |
| `SecDataDir /tmp/` | used for the SDBM collection files | accepted but ignored (see [Persistent Storage]({{% relref "3-reference-manual/3-8-persistent-storage" %}})) |

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
