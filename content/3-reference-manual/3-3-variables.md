---
title: Variables
weight: 3
---

The following variables are supported in ModSecurity v2 and libModSecurity v3. Each entry states which engine supports it; where the two engines behave differently, the difference is described in the entry.

## ARGS

{{< secmeta v2="yes" v3="yes" >}}

ARGS is a collection and can be used on its own (means all arguments including the POST Payload), with a static parameter (matches arguments with that name), or with a regular expression (matches all arguments with name that matches the regular expression). To look at only the query string or body arguments, see the ARGS_GET and ARGS_POST collections.

Some variables are actually collections, which are expanded into more variables at runtime. The following example will examine all request arguments:

`SecRule ARGS dirty "id:7"`

Sometimes, however, you will want to look only at parts of a collection. This can be achieved with the help of the selection operator(colon). The following example will only look at the arguments named p (do note that, in general, requests can contain multiple arguments with the same name):

`SecRule ARGS:p dirty "id:8"`

It is also possible to specify exclusions. The following will examine all request arguments for the word dirty, except the ones named z (again, there can be zero or more arguments named z):

`SecRule ARGS|!ARGS:z dirty "id:9"`

There is a special operator that allows you to count how many variables there are in a collection. The following rule will trigger if there is more than zero arguments in the request (ignore the second parameter for the time being):

`SecRule &ARGS !^0$ "id:10"`

And sometimes you need to look at an array of parameters, each with a slightly different name. In this case you can specify a regular expression in the selection operator itself. The following rule will look into all arguments whose names begin with id_:

`SecRule ARGS:/^id_/ dirty "id:11"`

{{% notice note %}}

Using ARGS:p will not result in any invocations against the operator if argument p does not exist.

{{% /notice %}}

{{% notice note %}}

Matching in the selection operator (both string and regular expression forms) is performed in a case-insensitive manner.

{{% /notice %}}

In ModSecurity 1.X, the ARGS variable stood for QUERY_STRING + POST_PAYLOAD, whereas now it expands to individual variables.

## ARGS_COMBINED_SIZE

{{< secmeta v2="yes" v3="yes" >}}

Contains the combined size of all request parameters. Files are excluded from the calculation. This variable can be useful, for example, to create a rule to ensure that the total size of the argument data is below a certain threshold. The following rule detects a request whose parameters are more than 2500 bytes long:

`SecRule ARGS_COMBINED_SIZE "@gt 2500" "id:12"`

libModSecurity v3 renders the value as a floating-point number (for example 2512.000000), so compare it with numeric operators such as @gt rather than with @eq or a regular expression on the digits.

## ARGS_GET

{{< secmeta v2="2.5.0" v3="yes" >}}

ARGS_GET is similar to ARGS, but contains only query string parameters.

## ARGS_GET_NAMES

{{< secmeta v2="2.5.0" v3="yes" >}}

ARGS_GET_NAMES is similar to ARGS_NAMES, but contains only the names of query string parameters.

## ARGS_NAMES

{{< secmeta v2="yes" v3="yes" >}}

Contains all request parameter names. You can search for specific parameter names that you want to inspect. In a positive policy scenario, you can also whitelist (using an inverted rule with the exclamation mark) only the authorized argument names. This example rule allows only two argument names: p and a:

`SecRule ARGS_NAMES "!^(p|a)$" "id:13"`

## ARGS_POST

{{< secmeta v2="2.5.0" v3="yes" >}}

ARGS_POST is similar to ARGS, but only contains arguments from the POST body.

## ARGS_POST_NAMES

{{< secmeta v2="2.5.0" v3="yes" >}}

ARGS_POST_NAMES is similar to ARGS_NAMES, but contains only the names of request body parameters.

## AUTH_TYPE

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the authentication method used to validate a user, if any of the methods built into HTTP are used. In a reverse-proxy deployment, this information will not be available if the authentication is handled in the backend web server.

`SecRule AUTH_TYPE "Basic" "id:14"`

libModSecurity v3 takes the value from the request itself: the first word of the Authorization request header, if any.

## DURATION

{{< secmeta v2="2.6.0" v3="yes" >}}

Contains the time elapsed since the beginning of the current transaction. The unit differs between engines and versions: ModSecurity 2.6.0 reported milliseconds, ModSecurity 2.7.0 and later report microseconds, and libModSecurity v3 reports a floating-point number of seconds (CPU time consumed by the process since the transaction was created, not wall-clock time).

## ENV

{{< secmeta v2="yes" v3="yes" >}}

Collection that provides access to environment variables set by ModSecurity (via the setenv action) or other server modules. Requires a single parameter to specify the name of the desired variable; a regular-expression selector (ENV:/.../) is not accepted.

libModSecurity v3 reads the environment of its own process (plus anything written there by setenv); the name is matched case-sensitively, a bare ENV returns every environment variable, and ENV:/regex/ is accepted by the parser but treated as a literal name.

``` seclang
# Set environment variable
SecRule REQUEST_FILENAME "@rx printenv" \
    "id:15,phase:2,pass,setenv:tag=suspicious"

# Inspect environment variable
SecRule ENV:tag "@rx suspicious" "id:16"

# Reading an environment variable from other Apache module (mod_ssl)
SecRule TX:ANOMALY_SCORE "@gt 0" "id:16,phase:5,msg:'%{env.ssl_cipher}'"
```

{{% notice note %}}

Use setenv to set environment variables to be accessed by Apache.

{{% /notice %}}

## FILES

{{< secmeta v2="yes" v3="yes" >}}

Contains a collection of original file names (as they were called on the remote user’s filesystem). Available only on inspected multipart/form-data requests.

`SecRule FILES "@rx \.conf$" "id:17"`

{{% notice note %}}

Only available if files were extracted from the request body.

{{% /notice %}}

## FILES_COMBINED_SIZE

{{< secmeta v2="yes" v3="yes" >}}

Contains the total size of the files transported in request body. Available only on inspected multipart/form-data requests.

`SecRule FILES_COMBINED_SIZE "@gt 100000" "id:18"`

## FILES_NAMES

{{< secmeta v2="yes" v3="yes" >}}

Contains a list of form fields that were used for file upload. Available only on inspected multipart/form-data requests.

`SecRule FILES_NAMES "^upfile$" "id:19"`

## FULL_REQUEST

{{< secmeta v2="2.8.0" v3="yes" >}}

Contains the complete request: Request line, Request headers and Request body (if any). The last available only if SecRequestBodyAccess was set to On. Note that all properties of SecRequestBodyAccess will be respected here, such as: SecRequestBodyLimit.

`SecRule FULL_REQUEST "User-Agent: ModSecurity Regression Tests" "id:21"`

{{% notice note %}}

Available on version 2.8.0+

{{% /notice %}}

{{% notice note %}}

The libModSecurity v3 implementation omits the request line: FULL_REQUEST contains the request headers followed by the request body.

{{% /notice %}}

## FULL_REQUEST_LENGTH

{{< secmeta v2="2.8.0" v3="yes" >}}

Contains the size, in bytes, of the request headers plus the request body (the request line is not counted).

`SecRule FULL_REQUEST_LENGTH "@eq 205" "id:21"`

{{% notice note %}}

Available on version 2.8.0+

{{% /notice %}}

## FILES_SIZES

{{< secmeta v2="yes" v3="yes" >}}

Contains a list of individual file sizes. Useful for implementing a size limitation on individual uploaded files. Available only on inspected multipart/form-data requests.

`SecRule FILES_SIZES "@gt 100" "id:20"`

## FILES_TMPNAMES

{{< secmeta v2="yes" v3="yes" >}}

Contains a list of temporary files’ names on the disk. Useful when used together with @inspectFile: the executed script can use the provided filename to open the file and examine the contents. Available only on inspected multipart/form-data requests.

`SecRule FILES_TMPNAMES "@inspectFile /path/to/inspect_script.pl" "id:21"`

libModSecurity v3 writes temporary files only when SecUploadKeepFiles or SecTmpSaveUploadedFiles is On (RelevantOnly is rejected there); @inspectFile alone does not create them, so this collection is otherwise empty.

## FILES_TMP_CONTENT

{{< secmeta v2="2.9.0" v3="yes" >}}

Contains a key-value set where value is the content of the file which was uploaded. Useful when used together with @fuzzyHash.

`SecRule FILES_TMP_CONTENT "@fuzzyHash $ENV{CONF_DIR}/ssdeep.txt 1" "id:192372,log,deny"`

{{% notice note %}}

Available on version 2.9.0-RC1+

{{% /notice %}}

{{% notice note %}}

In ModSecurity v2 the temporary files only exist when SecUploadKeepFiles is On or RelevantOnly, or when a rule uses @inspectFile; otherwise this collection is empty. libModSecurity v3 keeps the file content in memory but only while it is also writing the temporary file, that is when SecUploadKeepFiles or SecTmpSaveUploadedFiles is On; the collection is keyed by the part name (since 3.0.9).

{{% /notice %}}

## GEO

{{< secmeta v2="2.5.0" v3="yes" >}}

GEO is a collection populated by the results of the last @geoLookup operator. The collection can be used to match geographical fields looked from an IP address or hostname.

Available since ModSecurity 2.5.0.

Fields:

- COUNTRY_CODE: Two character country code. EX: US, GB, etc.
- COUNTRY_CODE3: Up to three character country code.
- COUNTRY_NAME: The full country name.
- COUNTRY_CONTINENT: The two character continent that the country is located. EX: EU
- REGION: The two character region. For US, this is state. For Canada, providence, etc.
- CITY: The city name if supported by the database.
- POSTAL_CODE: The postal code if supported by the database.
- LATITUDE: The latitude if supported by the database.
- LONGITUDE: The longitude if supported by the database.
- DMA_CODE: The metropolitan area code if supported by the database. (US only)
- AREA_CODE: The phone system area code. (US only)

Example:

``` seclang
SecGeoLookupDb /usr/local/geo/data/GeoLiteCity.dat
...
SecRule REMOTE_ADDR "@geoLookup" "id:22,drop,msg:'Non-GB IP address',chain"
    SecRule GEO:COUNTRY_CODE "!@streq GB"
```

With libModSecurity v3 (MaxMind GeoLite2 database; a build that uses the legacy GeoIP library instead fills the full field list above, while the MaxMind lookup only sets COUNTRY_CODE, COUNTRY_NAME, COUNTRY_CONTINENT, CITY, POSTAL_CODE, LATITUDE and LONGITUDE):

``` seclang
SecGeoLookupDB /usr/share/GeoIP/GeoLite2-Country.mmdb
...
SecRule REMOTE_ADDR "@geoLookup" "id:22,drop,msg:'Non-GB IP address',chain"
    SecRule GEO:COUNTRY_CODE "!@streq GB" ""
```

## GLOBAL

{{< secmeta v2="yes" v3="yes" >}}

Persistent collection shared by all transactions, in the same configuration namespace (see SecWebAppId). It must be initialized with the initcol action before it can be read or written; the collection is stored by SecDataDir (v2) or the persistent storage backend (v3) and the values survive across requests. In ModSecurity v2 a selector is mandatory (GLOBAL:name or GLOBAL:/regex/).

libModSecurity v3 keeps GLOBAL, IP, RESOURCE, SESSION and USER in memory, per process, by default: the data is not shared between worker processes and is lost on restart. A build configured with --with-lmdb stores them in an LMDB database (./modsec-shared-collections in the working directory) instead. SecDataDir is rejected by the v3 parser, SecCollectionTimeout is not supported, and expirevar is the only expiry mechanism.

``` seclang
SecAction "id:91,phase:1,pass,nolog,initcol:global=global"
SecRule REQUEST_URI "@rx ^/login" \
    "id:92,phase:1,pass,nolog,setvar:global.login_attempts=+1"
```

## HIGHEST_SEVERITY

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the highest severity of any rules that have matched so far. Severities are numeric values and thus can be used with comparison operators such as @lt, and so on. A value of 255 indicates that no severity has been set. In ModSecurity v2 a severity of 0 (EMERGENCY) is never recorded, and within a chain only the final rule of the chain updates this variable.

`SecRule HIGHEST_SEVERITY "@le 2" "phase:2,id:23,deny,status:500,msg:'severity %{HIGHEST_SEVERITY}'"`

{{% notice note %}}

Higher severities have a lower numeric value.

{{% /notice %}}

## INBOUND_DATA_ERROR

{{< secmeta v2="yes" v3="yes" >}}

This variable will be set to 1 when the request body size is above the setting configured by SecRequestBodyLimit directive. libModSecurity v3 (3.0.7 and later) also sets it, together with REQBODY_ERROR, when a body without files exceeds SecRequestBodyNoFilesLimit. Your policies should always contain a rule to check this variable. Depending on the rate of false positives and your default policy you should decide whether to block or just warn when the rule is triggered.

The best way to use this variable is as in the example below:

`SecRule INBOUND_DATA_ERROR "@eq 1" "phase:2,id:24,t:none,log,pass,msg:'Request Body Larger than SecRequestBodyLimit Setting'"`

## IP

{{< secmeta v2="yes" v3="yes" >}}

Persistent collection keyed by a client address, typically initialized with the initcol action using REMOTE_ADDR. It is commonly used to track per-client state (for example, anomaly scores or request rates) across transactions. In ModSecurity v2 a selector is mandatory (IP:name or IP:/regex/). For where libModSecurity v3 stores the data, see GLOBAL.

``` seclang
SecAction "id:93,phase:1,pass,nolog,initcol:ip=%{REMOTE_ADDR}"
SecRule ARGS "@rx attack" \
    "id:94,phase:2,pass,nolog,setvar:ip.score=+5,expirevar:ip.score=3600"
SecRule IP:score "@gt 20" "id:95,phase:2,deny"
```

## MATCHED_VAR

{{< secmeta v2="2.5.0" v3="yes" >}}

This variable holds the value of the most-recently matched variable. It is similar to the TX:0, but it is automatically supported by all operators and there is no need to specify the capture action.

``` seclang
SecRule ARGS "@rx pattern" "id:25,deny,chain"
    SecRule MATCHED_VAR "@rx further scrutiny"
```

{{% notice note %}}

Be aware that this variable holds data for the ***last*** operator match. This means that if there are more than one matches, only the last one will be populated. Use MATCHED_VARS variable if you want all matches.

{{% /notice %}}

## MATCHED_VARS

{{< secmeta v2="2.6.0" v3="yes" >}}

Similar to MATCHED_VAR except that it is a collection of ***all matches*** for the current operator check.

``` seclang
SecRule ARGS "@rx pattern" "id:26,deny,chain"
    SecRule MATCHED_VARS "@eq ARGS:param"
```

## MATCHED_VAR_NAME

{{< secmeta v2="2.5.0" v3="yes" >}}

This variable holds the full name of the variable that was matched against.

``` seclang
SecRule ARGS "@rx pattern" "id:27,deny,chain"
    SecRule MATCHED_VAR_NAME "@eq ARGS:param"
```

{{% notice note %}}

Be aware that this variable holds data for the ***last*** operator match. This means that if there are more than one matches, only the last one will be populated. Use MATCHED_VARS_NAMES variable if you want all matches.

{{% /notice %}}

## MATCHED_VARS_NAMES

{{< secmeta v2="2.6.0" v3="yes" >}}

Similar to MATCHED_VAR_NAME except that it is a collection of ***all matches*** for the current operator check.

``` seclang
SecRule ARGS "@rx pattern" "id:28,deny,chain"
    SecRule MATCHED_VARS_NAMES "@eq ARGS:param"
```

## MODSEC_BUILD

{{< secmeta v2="2.5.0" v3="yes" >}}

This variable holds the ModSecurity build number. This variable is intended to be used to check the build number prior to using a feature that is available only in a certain build. Example:

``` seclang
SecRule MODSEC_BUILD "!@ge 02050102" "id:29,skipAfter:12345"
SecRule ARGS "@pm some key words" "id:12345,deny,status:500"
```

libModSecurity v3 build numbers follow the same scheme: two digits each for the major, minor and patch level, followed by the three-digit tag number 100 (for example 030017100 for 3.0.17):

``` seclang
SecRule MODSEC_BUILD "!@ge 030017100" "id:29,skipAfter:12345"
SecRule ARGS "@pm some key words" "id:12345,deny,status:500"
```

## MSC_PCRE_ERROR

{{< secmeta v2="no" v3="3.0.10" >}}

libModSecurity v3 only: set to 1 when the @rx or @rxGlobal operator fails with any PCRE error, for example an invalid pattern after macro expansion or a match-limit error (in the latter case MSC_PCRE_LIMITS_EXCEEDED is set as well). ModSecurity v2 has no equivalent variable.

## MSC_PCRE_LIMITS_EXCEEDED

{{< secmeta v2="no" v3="3.0.10" >}}

MSC_PCRE_LIMITS_EXCEEDED will be set to 1 if an execution of either the @rx or @rxGlobal operator exceeds the limits set by SecPcreMatchLimit.

ModSecurity v2 does not provide this as a standalone variable (`SecRule MSC_PCRE_LIMITS_EXCEEDED` is a configuration error). Since 2.5.12, when @rx, @validateHash or the hash engine (SecHashEngine) hits SecPcreMatchLimit or SecPcreMatchLimitRecursion, v2 sets the transaction variable TX:MSC_PCRE_LIMITS_EXCEEDED to 1; test it with `SecRule TX:/^MSC_/ "!@streq 0"`, as rule 200005 in modsecurity.conf-recommended does. For compatibility, libModSecurity v3 (since 3.0.10) also sets the synonym TX:MSC_PCRE_LIMITS_EXCEEDED.

## MULTIPART_BOUNDARY_QUOTED

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when the boundary parameter of the multipart/form-data Content-Type header was quoted. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_BOUNDARY_WHITESPACE

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when whitespace was found around the boundary parameter of the multipart/form-data Content-Type header. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_CRLF_LF_LINES

{{< secmeta v2="yes" v3="yes" >}}

This flag variable will be set to 1 whenever a multi-part request uses mixed line terminators. The multipart/form-data RFC requires CRLF sequence to be used to terminate lines. Since some client implementations use only LF to terminate lines you might want to allow them to proceed under certain circumstances (if you want to do this you will need to stop using MULTIPART_STRICT_ERROR and check each multi-part flag variable individually, avoiding MULTIPART_LF_LINE). However, mixing CRLF and LF line terminators is dangerous as it can allow for evasion. Therefore, in such cases, you will have to add a check for MULTIPART_CRLF_LF_LINES.

## MULTIPART_CRLF_LINE

{{< secmeta v2="yes" v3="no" >}}

Flag variable set to 1 when the multipart parser encountered a line terminated with CRLF. It is informational (the RFC requires CRLF) and is mainly useful together with MULTIPART_LF_LINE and MULTIPART_CRLF_LF_LINES. ModSecurity v2 only; libModSecurity v3 does not provide it.

## MULTIPART_DATA_AFTER

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when data was found after the final multipart boundary. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_DATA_BEFORE

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when data was found before the first multipart boundary. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_DUPLICATE_PART_HEADER

{{< secmeta v2="2.9.15" v3="3.0.17" >}}

Flag variable set to 1 when a multipart part repeats a part header, or when the Content-Disposition header repeats its name, filename or filename* parameter (a part carrying both filename and filename* is not flagged). The part is also rejected as a parsing error, so REQBODY_ERROR is set as well. One of the flags aggregated by MULTIPART_STRICT_ERROR. Added together with MULTIPART_FILENAME_CHARSET and MULTIPART_FILENAME_LANGUAGE in ModSecurity 2.9.15 and libModSecurity 3.0.17.

## MULTIPART_FILENAME

{{< secmeta v2="2.7.3" v3="yes" >}}

This variable contains the multipart data from field FILENAME. In ModSecurity 2.9.15 and later, when the part carries an RFC 5987 filename* parameter, its percent-decoded value is used instead of filename.

## MULTIPART_FILENAME_CHARSET

{{< secmeta v2="2.9.15" v3="3.0.17" >}}

Collection (keyed by part name) holding the charset given in an RFC 5987 filename* parameter of a multipart Content-Disposition header (for example UTF-8 in filename*=UTF-8''report.pdf). Only populated for parts that use filename*. Available in ModSecurity 2.9.15 and libModSecurity 3.0.17 and later.

## MULTIPART_FILENAME_LANGUAGE

{{< secmeta v2="2.9.15" v3="3.0.17" >}}

Collection (keyed by part name) holding the optional language tag given in an RFC 5987 filename* parameter of a multipart Content-Disposition header (for example en in filename*=UTF-8'en'report.pdf). Only populated for parts that use filename*; the value is empty when no language is given. Available in ModSecurity 2.9.15 and libModSecurity 3.0.17 and later.

## MULTIPART_FILE_LIMIT_EXCEEDED

{{< secmeta v2="yes" v3="yes" v3note="(accepted by the parser but never populated)" >}}

Flag variable set to 1 when the number of files in a multipart/form-data request exceeded SecUploadFileLimit. One of the flags aggregated by MULTIPART_STRICT_ERROR.

libModSecurity v3 accepts the variable but never assigns it a value: the condition is only visible through MULTIPART_STRICT_ERROR and REQBODY_ERROR, and it is only detected while files are being written to disk (SecUploadKeepFiles or SecTmpSaveUploadedFiles On).

## MULTIPART_HEADER_FOLDING

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when a multipart part header used header folding (a continuation line starting with whitespace). One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_INVALID_HEADER_FOLDING

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when a multipart part header used invalid header folding. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_INVALID_PART

{{< secmeta v2="2.7.0" v3="yes" >}}

Flag variable set to 1 when the multipart parser found a part it could not parse (for example a part without a proper header block). It is checked by rule 200002 in modsecurity.conf-recommended together with the other multipart flags.

## MULTIPART_INVALID_QUOTING

{{< secmeta v2="2.5.11" v3="yes" >}}

Flag variable set to 1 when invalid quoting was found in a multipart Content-Disposition header. One of the flags aggregated by MULTIPART_STRICT_ERROR.

## MULTIPART_LF_LINE

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when the multipart parser encountered a line terminated with a bare LF instead of CRLF. One of the flags aggregated by MULTIPART_STRICT_ERROR; see also MULTIPART_CRLF_LF_LINES.

## MULTIPART_MISSING_SEMICOLON

{{< secmeta v2="yes" v3="yes" >}}

Flag variable set to 1 when the Content-Disposition header of a multipart part lacked the semicolon after form-data. One of the flags aggregated by MULTIPART_STRICT_ERROR. libModSecurity v3 also accepts the misspelled alias MULTIPART_SEMICOLON_MISSING.

## MULTIPART_NAME

{{< secmeta v2="2.7.3" v3="yes" >}}

This variable contains the multipart data from field NAME.

## MULTIPART_PART_HEADERS

{{< secmeta v2="2.9.6" v3="3.0.8" >}}

This variable is a collection of all part headers found within the request body with Content-Type multipart/form-data. The key of each item in the collection is the name of the part in which it was found, while the value is the entire part-header line -- including both the part-header name and the part-header value.

`SecRule MULTIPART_PART_HEADERS:parm1 "@rx content-type:.*jpeg" "phase:2,deny,status:403,id:500074,t:lowercase"`

{{% notice note %}}

Available in ModSecurity v2.9.6 and libModSecurity v3.0.8 and later.

{{% /notice %}}

## MULTIPART_STRICT_ERROR

{{< secmeta v2="2.1.3" v3="yes" >}}

MULTIPART_STRICT_ERROR will be set to 1 when any of the following variables is also set to 1: REQBODY_ERROR, MULTIPART_BOUNDARY_QUOTED, MULTIPART_BOUNDARY_WHITESPACE, MULTIPART_DATA_BEFORE, MULTIPART_DATA_AFTER, MULTIPART_DUPLICATE_PART_HEADER, MULTIPART_HEADER_FOLDING, MULTIPART_LF_LINE, MULTIPART_MISSING_SEMICOLON, MULTIPART_INVALID_QUOTING, MULTIPART_INVALID_PART, MULTIPART_INVALID_HEADER_FOLDING, MULTIPART_FILE_LIMIT_EXCEEDED. Each of these variables covers one unusual (although sometimes legal) aspect of the request body in multipart/form-data format. Your policies should always contain a rule to check either this variable (easier) or one or more individual variables (if you know exactly what you want to accomplish). Depending on the rate of false positives and your default policy you should decide whether to block or just warn when the rule is triggered.

The best way to use this variable is as in the example below:

``` seclang
SecRule MULTIPART_STRICT_ERROR "!@eq 0" \
    "id:30,\
    phase:2,\
    deny,\
    t:none,\
    log,\
    msg:'Multipart request body failed strict validation: PE %{REQBODY_ERROR}, BQ %{MULTIPART_BOUNDARY_QUOTED}, BW %{MULTIPART_BOUNDARY_WHITESPACE}, DB %{MULTIPART_DATA_BEFORE}, DA %{MULTIPART_DATA_AFTER}, DH %{MULTIPART_DUPLICATE_PART_HEADER}, HF %{MULTIPART_HEADER_FOLDING}, LF %{MULTIPART_LF_LINE}, SM %{MULTIPART_MISSING_SEMICOLON}, IQ %{MULTIPART_INVALID_QUOTING}, IP %{MULTIPART_INVALID_PART}, IH %{MULTIPART_INVALID_HEADER_FOLDING}, FE %{MULTIPART_FILE_LIMIT_EXCEEDED}'"
```

{{% notice note %}}

Older versions of this example used REQBODY_PROCESSOR_ERROR, which ModSecurity v2 removed in 2.9.14; REQBODY_ERROR is the current name. libModSecurity v3 still accepts both names.

{{% /notice %}}

The multipart/form-data parser was upgraded in ModSecurity v2.1.3 to actively look for signs of evasion. Many variables (as listed above) were added to expose various facts discovered during the parsing process. The MULTIPART_STRICT_ERROR variable is handy to check on all abnormalities at once. The individual variables allow detection to be fine-tuned according to your circumstances in order to reduce the number of false positives.

## MULTIPART_UNMATCHED_BOUNDARY

{{< secmeta v2="yes" v3="yes" >}}

Set to 1 when, during the parsing phase of a multipart/request-body, ModSecurity encounters what feels like a boundary but it is not. Such an event may occur when evasion of ModSecurity is attempted.

The best way to use this variable is as in the example below:

``` seclang
SecRule MULTIPART_UNMATCHED_BOUNDARY "!@eq 0" \
    "id:31,\
    phase:2,\
    deny,\
    t:none,\
    log,\
    msg:'Multipart parser detected a possible unmatched boundary.'"
```

Change the rule from blocking to logging-only if many false positives are encountered.

The intention of this variable is to identify possible evasion attempts by identifying lines that begin with '--' but are followed by characters such that it is not a match to the boundary. Even in its original implementation (in ModSecurity v2) this detection was known to be prone to false positives. libModSecurity v3 sets the variable to either 1 or 2: a change made in v3 (3.0.3) resulted in two detection variations, one that is still prone to false positives (1) and a revised detection that will detect very little (2). The ongoing utility and suitability of this detection is subject to review. See the description of rule 200004 in modsecurity.conf-recommended for more detail.

## OUTBOUND_DATA_ERROR

{{< secmeta v2="yes" v3="yes" >}}

This variable will be set to 1 when the response body size is above the setting configured by SecResponseBodyLimit directive. Your policies should always contain a rule to check this variable. Depending on the rate of false positives and your default policy you should decide whether to block or just warn when the rule is triggered.

The best way to use this variable is as in the example below:

`SecRule OUTBOUND_DATA_ERROR "@eq 1" "phase:1,id:32,t:none,log,pass,msg:'Response Body Larger than SecResponseBodyLimit Setting'"`

## PATH_INFO

{{< secmeta v2="yes" v3="yes" >}}

Contains the extra request URI information, also known as path info. (For example, in the URI /index.php/123, /123 is the path info.) Available only in embedded deployments.

`SecRule PATH_INFO "^/(bin|etc|sbin|opt|usr)" "id:33"`

In libModSecurity v3 there is no embedded-mode path info; PATH_INFO instead contains the part of the request URI that precedes any '?' character.

`SecRule PATH_INFO "^/(php)" "id:33"`

## PERF_ALL

{{< secmeta v2="yes" v3="no" >}}

This special variable contains a string that’s a combination of all other performance variables, arranged in the same order in which they appear in the Stopwatch2 audit log header. It’s intended for use in custom Apache logs

## PERF_COMBINED

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent in ModSecurity during the current transaction. The value in this variable is arrived to by adding all the performance variables except PERF_SREAD (the time spent reading from persistent storage is already included in the phase measurements).

## PERF_GC

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent performing garbage collection.

## PERF_LOGGING

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent in audit logging. This value is known only after the handling of a transaction is finalized, which means that it can only be logged using mod_log_config and the %{VARNAME}M syntax.

## PERF_PHASE1

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent processing phase 1.

## PERF_PHASE2

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent processing phase 2.

## PERF_PHASE3

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent processing phase 3.

## PERF_PHASE4

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent processing phase 4.

## PERF_PHASE5

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent processing phase 5.

## PERF_RULES

{{< secmeta v2="2.7.0" v3="no" >}}

PERF_RULES is a collection, that is populated with the rules hitting the performance threshold defined with SecRulePerfTime. The collection contains the time, in microseconds, spent processing the individual rule. The various items in the collection can be accessed via the rule id.

``` seclang
SecRulePerfTime            100

SecRule FILES_TMPNAMES "@inspectFile /path/to/util/runav.pl" \
    "id:10001,phase:2,deny,log,msg:'Virus scan detected an error.'"

SecRule &PERF_RULES "@eq 0" \
    "id:95000,\
    phase:5,\
    pass,\
    log,\
    msg:'All rules performed below processing time limit.'"
SecRule PERF_RULES "@ge 1000" \
    "id:95001,\
    phase:5,\
    pass,\
    log,\
    msg:'Rule %{MATCHED_VAR_NAME} spent at least 1000 usec.'"
SecAction \
    "id:95002,\
    phase:5,\
    pass,\
    log,\
    msg:'File inspection took %{PERF_RULES.10001} usec.'"
```

The rule with id 10001 defines an external file inspection rule. The rule with id 95000 checks the size of the PERF_RULES collection. If the collection is empty, it writes a note in the logfile. Rule 95001 is executed for every item in the PERF_RULES collection. Every item is thus being checked against the limit of 1000 microseconds. If the rule spent at least that amount of time, then a note containing the rule id is being written to the logfile. The final rule 95002 notes the time spent in rule 10001 (the virus inspection).

## PERF_SREAD

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent reading from persistent storage.

## PERF_SWRITE

{{< secmeta v2="2.6.0" v3="no" >}}

Contains the time, in microseconds, spent writing to persistent storage.

## QUERY_STRING

{{< secmeta v2="yes" v3="yes" >}}

Contains the query string part of a request URI. The value in QUERY_STRING is always provided raw, without URL decoding taking place.

`SecRule QUERY_STRING "attack" "id:34"`

## REMOTE_ADDR

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the IP address of the remote client. In ModSecurity v2 on Apache 2.4 with mod_remoteip loaded, it holds the client address as determined by mod_remoteip (see USERAGENT_IP). In libModSecurity v3 it is whatever address the connector hands to the library when the connection is processed.

`SecRule REMOTE_ADDR "@ipMatch 192.168.1.101" "id:35"`

## REMOTE_HOST

{{< secmeta v2="yes" v3="yes" >}}

If the Apache directive HostnameLookups is set to On, then this variable will hold the remote hostname resolved through DNS. If the directive is set to Off, this variable it will hold the remote IP address (same as REMOTE_ADDR). Possible uses for this variable would be to deny known bad client hosts or network blocks, or conversely, to allow in authorized hosts.

`SecRule REMOTE_HOST "\.evil\.network\org$" "id:36"`

libModSecurity v3 performs no hostname lookup: there, this variable is a synonym for REMOTE_ADDR.

## REMOTE_PORT

{{< secmeta v2="yes" v3="yes" >}}

This variable holds information on the source port that the client used when initiating the connection to our web server.

In the following example, we are evaluating to see whether the REMOTE_PORT is less than 1024, which would indicate that the user is a privileged user:

`SecRule REMOTE_PORT "@lt 1024" "id:37"`

## REMOTE_USER

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the username of the authenticated user. If there are no password access controls in place (Basic or Digest authentication), then this variable will be empty.

`SecRule REMOTE_USER "@streq admin" "id:38"`

{{% notice note %}}

In a reverse-proxy deployment, this information will not be available if the authentication is handled in the backend web server.

{{% /notice %}}

libModSecurity v3 extracts the username from the Authorization request header (Basic authentication), if present.

## REQBODY_ERROR

{{< secmeta v2="yes" v3="yes" >}}

Contains the status of the request body processor used for request body parsing. The values can be 0 (no error) or 1 (error). This variable will be set by request body processors (typically the multipart/request-data parser, JSON or the XML parser) when they fail to do their work.

`SecRule REQBODY_ERROR "@eq 1" deny,phase:2,id:39`

{{% notice note %}}

Your policies must have a rule to check for request body processor errors at the very beginning of phase 2. Failure to do so will leave the door open for impedance mismatch attacks. It is possible, for example, that a payload that cannot be parsed by ModSecurity can be successfully parsed by more tolerant parser operating in the application. If your policy dictates blocking, then you should reject the request if error is detected. When operating in detection-only mode, your rule should alert with high severity when request body processing fails.

{{% /notice %}}

- **Related issues**: #1475

## REQBODY_ERROR_MSG

{{< secmeta v2="yes" v3="yes" >}}

If there has been an error during request body parsing that resulted in REQBODY_ERROR getting set to 1, this variable will contain a text message with additional information about the error that was encountered. The variable can be tested just as any other variable:

`SecRule REQBODY_ERROR_MSG "failed to parse" "id:40"`

It is more common, however, simply to output the content in a log line, as in rule 200002 in modsecurity.conf-recommended.

## REQBODY_PROCESSOR

{{< secmeta v2="yes" v3="yes" >}}

Contains the name of the currently used request body processor. If set, the possible values are URLENCODED, MULTIPART, XML, and JSON; it is an empty string when no processor is in use. Both engines select URLENCODED and MULTIPART automatically from the Content-Type; XML and JSON must be selected with ctl:requestBodyProcessor.

``` seclang
SecRule REQBODY_PROCESSOR "@rx ^XML$" "id:41,chain"
    SecRule XML "@validateDTD /opt/apache-frontend/conf/xml.dtd"
```

## REQBODY_PROCESSOR_ERROR

{{< secmeta v2="no" v3="yes" >}}

Older name for REQBODY_ERROR. ModSecurity v2 provided it as a deprecated alias up to 2.9.13; it was removed in 2.9.14, so use REQBODY_ERROR there. libModSecurity v3 still sets both names when a request body processor fails.

## REQBODY_PROCESSOR_ERROR_MSG

{{< secmeta v2="no" v3="yes" >}}

Older name for REQBODY_ERROR_MSG. ModSecurity v2 provided it as a deprecated alias up to 2.9.13; it was removed in 2.9.14, so use REQBODY_ERROR_MSG there. libModSecurity v3 still sets both names.

## REQUEST_BASENAME

{{< secmeta v2="yes" v3="yes" >}}

This variable holds just the filename part of REQUEST_FILENAME (e.g., index.php).

`SecRule REQUEST_BASENAME "^login\.php$" phase:2,id:42,t:none,t:lowercase`

{{% notice note %}}

Please note that anti-evasion transformations are not applied to this variable by default. REQUEST_BASENAME will recognize both / and \\ as path separators. You should understand that the value of this variable depends on what was provided in request, and that it does not have to correspond to the resource (on disk) that will be used by the web server.

{{% /notice %}}

## REQUEST_BODY

{{< secmeta v2="yes" v3="yes" >}}

Holds the raw request body. This variable is available only if the URLENCODED request body processor was used, which will occur by default when the application/x-www-form-urlencoded content type is detected, or if the use of the URLENCODED request body parser was forced.

`SecRule REQUEST_BODY "^username=\w{25,}\&password=\w{25,}\&Submit\=login$" "id:43"`

As of 2.5.7, it is possible to force the presence of the REQUEST_BODY variable, but only when there is no request body processor defined using the ctl:forceRequestBodyVariable option in the REQUEST_HEADERS phase.

libModSecurity v3 always fills REQUEST_BODY with the raw request body (subject to SecRequestBodyAccess and the body limits), whichever processor is in use; ctl:forceRequestBodyVariable is accepted by the parser but ignored.

## REQUEST_BODY_LENGTH

{{< secmeta v2="2.6.0" v3="yes" >}}

Contains the number of bytes read from a request body. Available starting with v2.6

## REQUEST_COOKIES

{{< secmeta v2="yes" v3="yes" >}}

This variable is a collection of all of request cookies (values only). Example: the following example is using the Ampersand special operator to count how many variables are in the collection. In this rule, it would trigger if the request does not include any Cookie headers.

`SecRule &REQUEST_COOKIES "@eq 0" "id:44"`

## REQUEST_COOKIES_NAMES

{{< secmeta v2="yes" v3="yes" >}}

This variable is a collection of the names of all request cookies. For example, the following rule will trigger if the JSESSIONID cookie is not present:

`SecRule &REQUEST_COOKIES_NAMES:JSESSIONID "@eq 0" "id:45"`

## REQUEST_FILENAME

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the relative request URL without the query string part (e.g., /index.php).

`SecRule REQUEST_FILENAME "^/cgi-bin/login\.php$" phase:2,id:46,t:none,t:normalizePath`

{{% notice note %}}

Please note that anti-evasion transformations are not used on REQUEST_FILENAME, which means that you will have to specify them in the rules that use this variable.

{{% /notice %}}

## REQUEST_HEADERS

{{< secmeta v2="yes" v3="yes" >}}

This variable can be used as either a collection of all of the request headers or can be used to inspect selected headers (by using the REQUEST_HEADERS:Header-Name syntax).

`SecRule REQUEST_HEADERS:Host "^[\d\.]+$" "deny,id:47,log,status:400,msg:'Host header is a numeric IP address'"`

{{% notice note %}}

ModSecurity will treat multiple headers that have identical names in accordance with how the webserver treats them. For Apache this means that they will all be concatenated into a single header with a comma as the deliminator. libModSecurity v3 stores every header the connector passes as a separate entry of the collection, so a repeated header name yields several values.

{{% /notice %}}

## REQUEST_HEADERS_NAMES

{{< secmeta v2="yes" v3="yes" >}}

This variable is a collection of the names of all of the request headers.

`SecRule REQUEST_HEADERS_NAMES "^x-forwarded-for" "log,deny,id:48,status:403,t:lowercase,msg:'Proxy Server Used'"`

## REQUEST_LINE

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the complete request line sent to the server (including the request method and HTTP version information).

``` seclang
# Allow only POST, GET and HEAD request methods, as well as only
# the valid protocol versions
SecRule REQUEST_LINE "!@rx (^((?:(?:POS|GE)T|HEAD))|HTTP/(0\.9|1\.0|1\.1)$)" \
    "id:49,phase:1,block,t:none,log"
```

## REQUEST_METHOD

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the request method used in the transaction.

`SecRule REQUEST_METHOD "^(?:CONNECT|TRACE)$" "id:50,t:none"`

## REQUEST_PROTOCOL

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the request protocol version information.

`SecRule REQUEST_PROTOCOL "!^HTTP/(0\.9|1\.0|1\.1)$" "id:51"`

## REQUEST_URI

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the full request URL including the query string data (e.g., /index.php? p=X). However, it will never contain a domain name, even if it was provided on the request line.

`SecRule REQUEST_URI "attack" "phase:1,id:52,t:none,t:urlDecode,t:lowercase,t:normalizePath"`

{{% notice note %}}

Please note that anti-evasion transformations are not used on REQUEST_URI, which means that you will have to specify them in the rules that use this variable.

{{% /notice %}}

## REQUEST_URI_RAW

{{< secmeta v2="yes" v3="yes" >}}

Same as REQUEST_URI but will contain the domain name if it was provided on the request line (e.g., <http://www.example.com/index.php?p=X>).

`SecRule REQUEST_URI_RAW "http:/``" "phase:1,id:53,t:none,t:urlDecode,t:lowercase,t:normalizePath"`

{{% notice note %}}

Please note that anti-evasion transformations are not used on REQUEST_URI_RAW, which means that you will have to specify them in the rules that use this variable.

{{% /notice %}}

## RESOURCE

{{< secmeta v2="yes" v3="yes" >}}

Persistent collection keyed by a resource identifier (typically the request path), within the namespace set by SecWebAppId. It is initialized with the setrsc action (ModSecurity 2.7.0 and later) or with initcol, and can be used to keep per-resource state across transactions. In ModSecurity v2 a selector is mandatory (RESOURCE:name or RESOURCE:/regex/). For where libModSecurity v3 stores the data, see GLOBAL.

``` seclang
SecAction "id:96,phase:1,pass,nolog,setrsc:%{REQUEST_FILENAME}"
SecRule RESPONSE_STATUS "@rx ^5" \
    "id:97,phase:3,pass,nolog,setvar:resource.errors=+1"
```

## RESPONSE_BODY

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the data for the response body, but only when response body buffering is enabled.

`SecRule RESPONSE_BODY "ODBC Error Code" "phase:4,id:54,t:none"`

## RESPONSE_CONTENT_LENGTH

{{< secmeta v2="yes" v3="yes" >}}

Response body length in bytes. Can be available starting with phase 3, but it does not have to be (as the length of response body is not always known in advance). If the size is not known, this variable will contain a zero. If RESPONSE_CONTENT_LENGTH contains a zero in phase 5 that means the actual size of the response body was 0. The value of this variable can change between phases if the body is modified. For example, in embedded mode, mod_deflate can compress the response body between phases 4 and 5.

libModSecurity v3 sets it only when the response body is processed (phase 4), to the number of buffered body bytes; it does not read the Content-Length response header.

## RESPONSE_CONTENT_TYPE

{{< secmeta v2="yes" v3="yes" >}}

Response content type. Available only starting with phase 3. The value available in this variable is taken directly from the internal structures of Apache, which means that it may contain the information that is not yet available in response headers. In embedded deployments, you should always refer to this variable, rather than to RESPONSE_HEADERS:Content-Type.

libModSecurity v3 derives it from the Content-Type response header passed by the connector, with the parameters (for example charset=UTF-8) stripped.

## RESPONSE_HEADERS

{{< secmeta v2="yes" v3="yes" >}}

This variable refers to response headers, in the same way as REQUEST_HEADERS does to request headers.

`SecRule RESPONSE_HEADERS:X-Cache "MISS" "id:55"`

This variable may not have access to some headers when running in embedded mode. Headers such as Server, Date, Connection, and Content-Type could be added just prior to sending the data to the client. This data should be available in phase 5 or when deployed in proxy mode.

## RESPONSE_HEADERS_NAMES

{{< secmeta v2="yes" v3="yes" >}}

This variable is a collection of the response header names.

`SecRule RESPONSE_HEADERS_NAMES "Set-Cookie" "phase:3,id:56,t:none"`

The same limitations apply as the ones discussed in RESPONSE_HEADERS.

## RESPONSE_PROTOCOL

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the HTTP response protocol information.

`SecRule RESPONSE_PROTOCOL "^HTTP\/0\.9" "phase:3,id:57,t:none"`

## RESPONSE_STATUS

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the HTTP response status code:

`SecRule RESPONSE_STATUS "^[45]" "phase:3,id:58,t:none"`

This variable may not work as expected in embedded mode, as Apache sometimes handles certain requests differently, and without invoking ModSecurity (all other modules).

## RULE

{{< secmeta v2="yes" v3="yes" >}}

This is a special collection that provides access to the id, rev, severity, msg, logdata, ver, maturity, and accuracy fields of the rule that triggered the action. It can be used to refer to only the same rule in which it resides; a field name is mandatory (RULE:id, or %{RULE.id} in macros), and inside a chain the fields are those of the chain starter.

libModSecurity v3 exposes only id, rev, severity, msg and logdata (ver, maturity and accuracy are not available); it also accepts a bare RULE, which returns all five, and a regular-expression selector.

`SecRule &REQUEST_HEADERS:Host "@eq 0" "log,deny,id:59,setvar:tx.varname=%{RULE.id}"`

## SCRIPT_BASENAME

{{< secmeta v2="yes" v3="no" >}}

This variable holds just the local filename part of SCRIPT_FILENAME.

`SecRule SCRIPT_BASENAME "^login\.php$" "id:60"`

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_FILENAME

{{< secmeta v2="yes" v3="no" >}}

This variable holds the full internal path to the script that will be used to serve the request.

`SecRule SCRIPT_FILENAME "^/usr/local/apache/cgi-bin/login\.php$" "id:61"`

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_GID

{{< secmeta v2="yes" v3="no" >}}

This variable holds the numerical identifier of the group owner of the script.

`SecRule SCRIPT_GID "!^46$" "id:62"`

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_GROUPNAME

{{< secmeta v2="yes" v3="no" >}}

This variable holds the name of the group owner of the script.

`SecRule SCRIPT_GROUPNAME "!^apache$" "id:63"`

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_MODE

{{< secmeta v2="yes" v3="no" >}}

This variable holds the script’s permissions mode data as four hexadecimal digits of the APR protection bits, which for ordinary Unix permissions reads like the octal mode with a leading zero (e.g., 0644).

``` seclang
# Do not allow scripts that can be written to by everyone
SecRule SCRIPT_MODE "@rx [2367]$" "id:64"
```

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_UID

{{< secmeta v2="yes" v3="no" >}}

This variable holds the numerical identifier of the owner of the script.

``` seclang
# Do not run any scripts that are owned
# by Apache (Apache's user id is 46)
SecRule SCRIPT_UID "!@rx ^46$" "id:65"
```

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SCRIPT_USERNAME

{{< secmeta v2="yes" v3="no" >}}

This variable holds the username of the owner of the script.

``` seclang
# Do not run any scripts owned by Apache
SecRule SCRIPT_USERNAME "@rx ^apache$" "id:66"
```

{{% notice note %}}

Not available in proxy mode.

{{% /notice %}}

## SDBM_DELETE_ERROR

{{< secmeta v2="2.7.4" v3="no" >}}

This variable is set to 1 when APR fails to delete SDBM entries.

## SERVER_ADDR

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the IP address of the server.

`SecRule SERVER_ADDR "@ipMatch 192.168.1.100" "id:67"`

## SERVER_NAME

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the transaction’s hostname or IP address, taken from the request itself (which means that, in principle, it should not be trusted).

`SecRule SERVER_NAME "hostname\.com$" "id:68"`

## SERVER_PORT

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the local port that the web server (or reverse proxy) is listening on.

`SecRule SERVER_PORT "^80$" "id:69"`

## SESSION

{{< secmeta v2="yes" v3="yes" >}}

This variable is a collection that contains session information. It becomes available only after setsid is executed. In ModSecurity v2 a selector is mandatory (SESSION:name or SESSION:/regex/). For where libModSecurity v3 stores the data, see GLOBAL.

The following example shows how to initialize SESSION using setsid, how to use setvar to increase the SESSION.score values, how to set the SESSION.blocked variable, and finally, how to deny the connection based on the <SESSION:blocked> value:

``` seclang
# Initialize session storage
SecRule REQUEST_COOKIES:PHPSESSID "!@rx ^$" \
    "id:70,phase:2,pass,nolog,setsid:%{REQUEST_COOKIES.PHPSESSID}"

# Increment session score on attack
SecRule REQUEST_URI "@rx ^/cgi-bin/finger$" \
    "id:71,\
    phase:2,\
    pass,\
    t:none,\
    t:lowercase,\
    t:normalizePath,\
    setvar:SESSION.score=+10"

# Detect too many attacks in a session
SecRule SESSION:score "@gt 50" "id:72,phase:2,pass,setvar:SESSION.blocked=1"

# Enforce session block
SecRule SESSION:blocked "@eq 1" "id:73,phase:2,deny,status:403"
```

## SESSIONID

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the value set with setsid. See SESSION (above) for a complete example.

## STATUS

{{< secmeta v2="no" v3="yes" >}}

libModSecurity v3 only: the HTTP response status code, the same value as RESPONSE_STATUS. STATUS_LINE is accepted by v3 as another alias of this variable. ModSecurity v2 does not have STATUS; use RESPONSE_STATUS there.

## STATUS_LINE

{{< secmeta v2="yes" v3="3.0.3" v3note="accepted as an alias of [STATUS](#status)" >}}

This variable holds the response status line generated by the server, that is the status code followed by the reason phrase (for example 500 Internal Server Error); the protocol version is not included. In libModSecurity v3 it is an alias of STATUS and therefore holds only the status code.

``` seclang
# Generate an alert when the application generates 500 errors.
SecRule STATUS_LINE "@contains 500" \
    "id:49,phase:3,pass,log,logdata:'Application error detected!,t:none"
```

## STREAM_INPUT_BODY

{{< secmeta v2="2.6.0" v3="no" >}}

This variable give access to the raw request body content. This variable is best used for two use-cases:

1.  For fast pattern matching - using @pm/@pmf to prequalify large text strings against any kind of content-type data. This is more performant vs. using REQUEST_BODY/ARGS_POST/ARGS_POST_NAMES as it happens before ModSecurity parsing in phase:2 variable population.
2.  For data substitution - using @rsub against this variable allows you to manipulate live request body data. Example - to remove offending payloads or to substitute benign data.

{{% notice note %}}

You must enable the SecStreamInBodyInspection directive

{{% /notice %}}

{{% notice note %}}

This variable is not supported by libModSecurity v3.

{{% /notice %}}

## STREAM_OUTPUT_BODY

{{< secmeta v2="2.6.0" v3="no" >}}

This variable give access to the raw response body content. This variable is best used for case:

1.  For data substitution - using @rsub against this variable allows you to manipulate live request body data. Example - to remove offending payloads or to substitute benign data.

{{% notice note %}}

You must enable the SecStreamOutBodyInspection directive

{{% /notice %}}

## TIME

{{< secmeta v2="yes" v3="yes" >}}

This variable holds a formatted timestamp. The format differs between the engines: in ModSecurity v2 it is the 14-digit local time YYYYMMDDHHMMSS (for example 20261013183045), not hour:minute:second as older manuals stated, while libModSecurity v3 produces the local time as HH:MM:SS (for example 18:30:45). The following rules match between 18:00 and 23:59.

ModSecurity v2:

`SecRule TIME "^\d{8}(1[89]|2[0-3])\d{4}$" "id:74"`

libModSecurity v3:

`SecRule TIME "^(1[89]|2[0-3]):" "id:74"`

## TIME_DAY

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current day of the month as two zero-padded digits (01–31). The following rule triggers on a transaction that’s happening anytime between the 10th and 20th in a month:

`SecRule TIME_DAY "^(([1](0|1|2|3|4|5|6|7|8|9))|20)$" "id:75"`

## TIME_EPOCH

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the time in seconds since 1970.

## TIME_HOUR

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current hour as two zero-padded digits (00–23). The following rule triggers when a request is made “off hours”:

`SecRule TIME_HOUR "^(0[0-6]|1[89]|2[0-3])$" "id:76"`

## TIME_MIN

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current minute as two zero-padded digits (00–59). The following rule triggers during the last half hour of every hour:

`SecRule TIME_MIN "^(3|4|5)" "id:77"`

## TIME_MON

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current month as two zero-padded digits (01–12). libModSecurity v3 does not zero-pad it (1–12; before 3.0.14 it was zero-based, 0–11). The following rule matches if the month is either November (value 11) or December (value 12):

`SecRule TIME_MON "^1[12]$" "id:78"`

## TIME_SEC

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current second as two zero-padded digits (00–59).

`SecRule TIME_SEC "@gt 30" "id:79"`

## TIME_WDAY

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current weekday value. The numbering differs between the engines: ModSecurity v2 uses 0–6 with Sunday as 0, while libModSecurity v3 uses 1–7 with Monday as 1. The following rules trigger only on Saturday and Sunday.

ModSecurity v2:

`SecRule TIME_WDAY "^(0|6)$" "id:80"`

libModSecurity v3:

`SecRule TIME_WDAY "^(6|7)$" "id:80"`

## TIME_YEAR

{{< secmeta v2="yes" v3="yes" >}}

This variable holds the current four-digit year value.

`SecRule TIME_YEAR "^2006$" "id:81"`

## TX

{{< secmeta v2="yes" v3="yes" >}}

This is the transient transaction collection, which is used to store pieces of data, create a transaction anomaly score, and so on. The variables placed into this collection are available only until the transaction is complete. In ModSecurity v2 a selector is mandatory (TX:name or TX:/regex/); a bare TX target is a configuration error.

``` seclang
# Increment transaction attack score on attack
SecRule ARGS "@rx attack" "id:82,phase:2,pass,nolog,setvar:TX.score=+5"

# Block the transactions whose scores are too high
SecRule TX:SCORE "@gt 20" "id:83,phase:2,deny,log"
```

Some variable names in the TX collection are reserved and cannot be used:

- TX:0: the matching value when using the @rx or @pm operator with the capture action
- TX:1-TX:9: the captured subexpression value when using the @rx operator with capturing parens and the capture action. ModSecurity v2 stores at most nine captures (TX:1 to TX:9); libModSecurity v3 stores every capturing group of the expression (the v3 manual documents TX:1 to TX:99).
- TX:MSC_.*: ModSecurity processing flags
- MSC_PCRE_LIMITS_EXCEEDED: Set to nonzero if PCRE match limits are exceeded. See SecPcreMatchLimit and SecPcreMatchLimitRecursion for more information.

## UNIQUE_ID

{{< secmeta v2="2.6.0" v3="yes" >}}

This variable holds the data created by mod_unique_id [1](http://httpd.apache.org/docs/2.2/mod/mod_unique_id.html). This module provides a magic token for each request which is guaranteed to be unique across "all" requests under very specific conditions. The unique identifier is even unique across multiple machines in a properly configured cluster of machines. The environment variable UNIQUE_ID is set to the identifier for each request. The UNIQUE_ID environment variable is constructed by encoding the 112-bit (32-bit IP address, 32 bit pid, 32 bit time stamp, 16 bit counter) quadruple using the alphabet [A-Za-z0-9@-] in a manner similar to MIME base64 encoding, producing 19 characters.

libModSecurity v3 does not depend on mod_unique_id: unless the connector supplies its own transaction identifier, it generates one made of the Unix timestamp in seconds immediately followed by a random floating-point number between 0 and 100 (for example 176020000042.123456). The random part was restored in 3.0.7; the value is not guaranteed to be unique.

## URLENCODED_ERROR

{{< secmeta v2="2.6.0" v3="yes" >}}

This variable is created when an invalid URL encoding is encountered during the parsing of a query string (on every request) or during the parsing of an application/x-www-form-urlencoded request body (only on the requests that use the URLENCODED request body processor).

## USER

{{< secmeta v2="yes" v3="yes" >}}

Persistent collection keyed by the user identifier set with setuid (see USERID). It must be initialized with setuid or initcol before it can be used. In ModSecurity v2 a selector is mandatory (USER:name or USER:/regex/). For where libModSecurity v3 stores the data, see GLOBAL.

``` seclang
SecAction "id:98,phase:1,pass,nolog,setuid:%{REMOTE_USER}"
SecRule ARGS "@rx attack" "id:99,phase:2,pass,nolog,setvar:user.score=+5"
SecRule USER:score "@gt 20" "id:100,phase:2,deny"
```

## USERID

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the value set with setuid.

``` seclang
# Initialize user tracking
SecAction "id:84,pass,nolog,setuid:%{REMOTE_USER}"

# Is the current user the administrator?
SecRule USERID "@rx admin" "id:85"
```

## USERAGENT_IP

{{< secmeta v2="2.7.0" v3="no" >}}

Only compiled in when ModSecurity v2 is built against Apache 2.4 or later. It holds Apache's useragent_ip, the client address after mod_remoteip has substituted the real client address in proxied connections (without mod_remoteip it equals REMOTE_ADDR). It contains 0.0.0.0 when Apache did not set the address.

## WEBAPPID

{{< secmeta v2="yes" v3="yes" >}}

This variable contains the current application name, which is set in configuration using SecWebAppId.

## WEBSERVER_ERROR_LOG

{{< secmeta v2="yes" v3="no" >}}

Contains zero or more error messages produced by the web server. This variable is best accessed from phase 5 (logging).

`SecRule WEBSERVER_ERROR_LOG "File does not exist" "phase:5,id:86,t:none,nolog,pass,setvar:TX.score=+5"`

libModSecurity v3 rejects any rule that uses this variable at configuration load ("Variable VARIABLE_WEBSERVER_ERROR_LOG is not supported by libModSecurity").

## XML

{{< secmeta v2="yes" v3="yes" >}}

Special collection used to interact with the XML parser. It can be used standalone as a target for the validateDTD and validateSchema operator. Otherwise, it must contain a valid XPath expression, which will then be evaluated against a previously parsed XML DOM tree.

libModSecurity v3 supports it only when built with libxml2; without it the variable parses but never yields a value. XPath selection works the same way (XML:/xpath, with namespaces registered through the xmlns action), and a bare XML yields a placeholder value for the validation operators.

``` seclang
SecDefaultAction "id:90,phase:2,deny,status:403,log"
SecRule REQUEST_HEADERS:Content-Type "@rx ^text/xml$" \
    "id:87,phase:1,pass,t:lowercase,nolog,ctl:requestBodyProcessor=XML"
SecRule REQBODY_PROCESSOR "!@rx ^XML$" "id:88,skipAfter:12345"

SecRule XML:/employees/employee/name/text() "@rx Fred" "id:89"
SecRule XML:/xq:employees/employee/name/text() "@rx Fred" \
    "id:12345,xmlns:xq=http://www.example.com/employees"
```

The first XPath expression does not use namespaces. It would match against payload such as this one:

``` xml
<employees>
    <employee>
        <name>Fred Jones</name>
        <address location="home">
            <street>900 Aurora Ave.</street>
            <city>Seattle</city>
            <state>WA</state>
            <zip>98115</zip>
        </address>
        <address location="work">
            <street>2011 152nd Avenue NE</street>
            <city>Redmond</city>
            <state>WA</state>
            <zip>98052</zip>
        </address>
        <phone location="work">(425)555-5665</phone>
        <phone location="home">(206)555-5555</phone>
        <phone location="mobile">(206)555-4321</phone>
    </employee>
</employees>
```

The second XPath expression does use namespaces. It would match the following payload:

``` xml
<xq:employees xmlns:xq="http://www.example.com/employees">
    <employee>
        <name>Fred Jones</name>
        <address location="home">
            <street>900 Aurora Ave.</street>
            <city>Seattle</city>
            <state>WA</state>
            <zip>98115</zip>
        </address>
        <address location="work">
            <street>2011 152nd Avenue NE</street>
            <city>Redmond</city>
            <state>WA</state>
            <zip>98052</zip>
        </address>
        <phone location="work">(425)555-5665</phone>
        <phone location="home">(206)555-5555</phone>
        <phone location="mobile">(206)555-4321</phone>
    </employee>
</xq:employees>
```

Note the different namespace used in the second example.
