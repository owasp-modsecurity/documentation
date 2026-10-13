---
title: Configuration Directives
weight: 2
---

The following section outlines all of the ModSecurity directives. Most of the ModSecurity directives can be used inside the various Apache Scope Directives such as VirtualHost, Location, LocationMatch, Directory, etc... There are others, however, that can only be used once in the main configuration file. This information is specified in the Scope sections below. The first version to use a given directive is given in the Version sections below.

These rules, along with the Core rules files, should be contained in files outside of the httpd.conf file and called up with Apache "Include" directives. This allows for easier updating/migration of the rules. If you create your own custom rules that you would like to use with the Core rules, you should create a file called - modsecurity_crs_15_customrules.conf and place it in the same directory as the Core rules files. By using this file name, your custom rules will be called up after the standard ModSecurity Core rules configuration file but before the other Core rules. This allows your rules to be evaluated first which can be useful if you need to implement specific "allow" rules or to correct any false positives in the Core rules as they are applied to your site.

{{% notice note %}}

It is highly encouraged that you do not edit the Core rules files themselves but rather place all changes (such as SecRuleRemoveByID, etc...) in your custom rules file. This will allow for easier upgrading as newer Core rules are released.

{{% /notice %}}

## Include

Loads another configuration file in place, as if its contents had been written at the position of the directive.

{{< secmeta syntax="Include /path/to/file.conf" example="Include /etc/modsecurity/rules/*.conf" scope="Any" v2="yes" v3="3.0.0" >}}

In ModSecurity v2 this is the Apache httpd core `Include` directive; ModSecurity itself does not define it, and the rules files it names are processed by Apache. libModSecurity v3 implements its own `Include` in the SecLang parser: the parameter may be quoted, may contain a `*` wildcard matching several files, and may be a relative path, which is resolved against the directory of the file that contains the `Include`. Nested includes are permitted.

``` apache
Include modsecurity.conf
Include "/etc/modsecurity/crs/rules/*.conf"
```

## SecAction

Unconditionally processes the action list it receives as the first and only parameter. The syntax of the parameter is identical to that of the third parameter of `SecRule`.

{{< secmeta syntax=`SecAction "action1,action2,action3,..."` scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directive is commonly used to set variables and initialize persistent collections using the initcol action. For example:

``` apache
SecAction nolog,phase:1,initcol:RESOURCE=%{REQUEST_FILENAME}
```

## SecArgumentSeparator

Specifies which character to use as the separator for application/x-www-form- urlencoded content.

{{< secmeta syntax="SecArgumentSeparator character" default="&" scope="Main(< 2.7.0), Any(2.7.0)" v2="2.0.0" v3="3.0.0" >}}

This directive is needed if a backend web application is using a nonstandard argument separator. Applications are sometimes (very rarely) written to use a semicolon separator. You should not change the default setting unless you establish that the application you are working with requires a different separator. If this directive is not set properly for each web application, then ModSecurity will not be able to parse the arguments appropriately and the effectiveness of the rule matching will be significantly decreased.

## SecArgumentsLimit

Configures the maximum number of ARGS that will be accepted for processing.

{{< secmeta syntax="SecArgumentsLimit LIMIT" example="SecArgumentsLimit 1000" default="1000 (v2); no limit (v3)" scope="Any" v2="2.9.7" v3="3.0.5" >}}

Exceeding the limit will set the REQBODY_ERROR variable, and additional arguments beyond the limit will not be included. With JSON body processing, there is an additional short-circuit to halt parsing once the limit is breached. As with the enforcement of other issues that signal REQBODY_ERROR, a rule should be in place to test this value, like rule 200002 in modsecurity.conf-recommended.

In ModSecurity v2 the default is 1000. libModSecurity v3 applies no limit unless the directive is set.

When using this setting, it is recommended to accompany it with a rule that will test for that same integer value and deny the request if it is reached, like rule 200007 in modsecurity.conf-recommended:

``` apache
SecRule &ARGS "@ge 1000" "id:'200007', phase:2,t:none,log,deny,status:400,msg:'Failed to fully parse request body due to large argument count'"
```

Without such a matching rule, an attacker could potentially evade detection by placing the attack payload in a parameter occurring beyond the limit.

## SecAuditEngine

Configures the audit logging engine.

{{< secmeta syntax="SecAuditEngine RelevantOnly" default="Off" scope="Any" v2="2.0.0" v3="3.0.0" >}}

The SecAuditEngine directive is used to configure the audit engine, which logs complete transactions. ModSecurity is currently able to log most, but not all transactions. Transactions involving errors (e.g., 400 and 404 transactions) use a different execution path, which ModSecurity does not support.

The possible values for the audit log engine are as follows:

- **On**: log all transactions
- **Off**: do not log any transactions
- **RelevantOnly**: only the log transactions that have triggered a warning or an error, or have a status code that is considered to be relevant (as determined by the SecAuditLogRelevantStatus directive)

{{% notice note %}}

If you need to change the audit log engine configuration on a per-transaction basis (e.g., in response to some transaction data), use the ctl action.

{{% /notice %}}

The following example demonstrates how SecAuditEngine is used:

``` apache
SecAuditEngine RelevantOnly
SecAuditLog logs/audit/audit.log
SecAuditLogParts ABCFHZ 
SecAuditLogType concurrent 
SecAuditLogStorageDir logs/audit 
SecAuditLogRelevantStatus ^(?:5|4(?!04))
```

## SecAuditLog

Defines the path to the main audit log file (serial logging format), the concurrent logging index file (concurrent logging format) or, in libModSecurity v3, the destination URL (HTTPS logging format). When used in combination with mlogc (only possible with concurrent logging), this directive defines the mlogc location and command line.

{{< secmeta syntax="SecAuditLog /path/to/audit.log" scope="Any" v2="2.0.0" v3="3.0.0" >}}

This file will be used to store the audit log entries if serial audit logging format is used. If concurrent audit logging format is used this file will be used as an index, and contain a record of all audit log files created. If you are planning to use concurrent audit logging to send your audit log data off to a remote server you will need to deploy the ModSecurity Log Collector (mlogc), like this:

``` apache
SecAuditLog "|/path/to/mlogc /path/to/mlogc.conf"
```

libModSecurity v3 does not ship mlogc. When using `SecAuditLogType HTTPS` (v3 only), specify the destination URL instead of a path, e.g. `SecAuditLog https://xxx.xxx.xxx.xxx:port/`.

{{% notice note %}}

This audit log file is opened on startup when the server typically still runs as root. You should not allow non-root users to have write privileges for this file or for the directory.

{{% /notice %}}

## SecAuditLog2

Defines the path to the secondary audit log index file when concurrent logging is enabled. See SecAuditLog for more details.

{{< secmeta syntax="SecAuditLog2 /path/to/audit.log" scope="Any" v2="2.1.2" v3="3.0.0" >}}

The purpose of SecAuditLog2 is to make logging to two remote servers possible, which is typically achieved by running two instances of the mlogc tool, each with a different configuration (in addition, one of the instances will need to be instructed not to delete the files it submits). This directive can be used only if SecAuditLog was previously configured and only if concurrent logging format is used.

## SecAuditLogDirMode

Configures the mode (permissions) of any directories created for the concurrent audit logs, using an octal mode value as parameter (as used in chmod).

{{< secmeta syntax=`SecAuditLogDirMode octal_mode|"default"` example="SecAuditLogDirMode 02750" default="0600" scope="Any" v2="2.5.10" v3="3.0.0" >}}

The default mode for new audit log directories (0600) only grants read/write access to the owner (typically the account under which Apache is running, for example apache). If access from other accounts is needed (e.g., for use with mpm-itk), then you may use this directive to grant additional read and/or write privileges. You should use this directive with caution to avoid exposing potentially sensitive data to unauthorized users. Using the value default as parameter reverts the configuration back to the default setting. This feature is not available on operating systems not supporting octal file modes.

Example:

``` apache
SecAuditLogDirMode 02750
```

{{% notice note %}}

The process umask may still limit the mode if it is being more restrictive than the mode set using this directive.

{{% /notice %}}

## SecAuditLogFormat

Select the output format of the AuditLogs. The format can be either the native AuditLogs format or JSON.

{{< secmeta syntax="SecAuditLogFormat JSON|Native" default="Native" scope="Any" v2="2.9.1" v3="3.0.0" >}}

{{% notice note %}}

The JSON format is only available if ModSecurity was compiled with support to JSON via the YAJL library. During the compilation time, the yajl-dev package (or similar) must be part of the system. The configure scripts provides information if the YAJL support was enabled or not.

{{% /notice %}}

## SecAuditLogFileMode

Configures the mode (permissions) of any files created for concurrent audit logs using an octal mode (as used in chmod). See SecAuditLogDirMode for controlling the mode of created audit log directories.

{{< secmeta syntax=`SecAuditLogFileMode octal_mode|"default"` example="SecAuditLogFileMode 00640" default="0600" scope="Any" v2="2.5.10" v3="3.0.0" >}}

This feature is not available on operating systems not supporting octal file modes. The default mode (0600) only grants read/write access to the account writing the file. If access from another account is needed (using mpm-itk is a good example), then this directive may be required. However, use this directive with caution to avoid exposing potentially sensitive data to unauthorized users. Using the value “default” will revert back to the default setting.

{{% notice note %}}

The process umask may still limit the mode if it is being more restrictive than the mode set using this directive.

{{% /notice %}}

## SecAuditLogParts

Defines which parts of each transaction are going to be recorded in the audit log. Each part is assigned a single letter; when a letter appears in the list then the equivalent part will be recorded. See below for the list of all parts.

{{< secmeta syntax="SecAuditLogParts PARTLETTERS" example="SecAuditLogParts ABCFHZ" default="ABCFHZ" scope="Any" v2="2.0.0" v3="3.0.0" >}}

The format of the audit log format is documented in detail in the Audit Log Data Format Documentation.

Available audit log parts:

- A: Audit log header (mandatory).
- B: Request headers.
- C: Request body (present only if the request body exists and ModSecurity is configured to intercept it. This would require SecRequestBodyAccess to be set to on).
- D: Reserved for intermediary response headers; not implemented yet.
- E: Intermediary response body (present only if ModSecurity is configured to intercept response bodies, and if the audit log engine is configured to record it. Intercepting response bodies requires SecResponseBodyAccess to be enabled). Intermediary response body is the same as the actual response body unless ModSecurity intercepts the intermediary response body, in which case the actual response body will contain the error message (either the Apache default error message, or the ErrorDocument page).
- F: Final response headers (excluding the Date and Server headers, which are always added by Apache in the late stage of content delivery).
- G: Reserved for the actual response body; not implemented yet.
- H: Audit log trailer.
- I: This part is a replacement for part C. It will log the same data as C in all cases except when multipart/form-data encoding in used. In this case, it will log a fake application/x-www-form-urlencoded body that contains the information about parameters but not about the files. This is handy if you don’t want to have (often large) files stored in your audit logs. Not implemented in libModSecurity v3.
- J: This part contains information about the files uploaded using multipart/form-data encoding.
- K: This part contains a full list of every rule that matched (one per line) in the order they were matched. The rules are fully qualified and will thus show inherited actions and default operators. Supported as of v2.5.0. Not implemented in libModSecurity v3.
- Z: Final boundary, signifies the end of the entry (mandatory).

## SecAuditLogRelevantStatus

Configures which response status code is to be considered relevant for the purpose of audit logging.

{{< secmeta syntax="SecAuditLogRelevantStatus REGEX" example=`SecAuditLogRelevantStatus "^(?:5|4(?!04))"` scope="Any" v2="2.0.0" v3="3.0.0" >}}

**Dependencies/Notes:** Must have SecAuditEngine set to RelevantOnly. Additionally, the auditlog action is present by default in rules, this will make the engine bypass the 'SecAuditLogRelevantStatus' and send rule matches to the audit log regardless of status. You must specify noauditlog in the rules manually or set it in SecDefaultAction.

The main purpose of this directive is to allow you to configure audit logging for only the transactions that have the status code that matches the supplied regular expression. The example provided would log all 5xx and 4xx level status codes, except for 404s. Although you could achieve the same effect with a rule in phase 5, SecAuditLogRelevantStatus is sometimes better, because it continues to work even when SecRuleEngine is disabled.

## SecAuditLogStorageDir

Configures the directory where concurrent audit log entries are to be stored.

{{< secmeta syntax="SecAuditLogStorageDir /path/to/storage/dir" example="SecAuditLogStorageDir /usr/local/apache/logs/audit" scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directive is only needed when concurrent audit logging is used. The directory must already exist and must be writable by the web server user. Audit log entries are created at runtime, after Apache switches to a non-root account. As with all logging mechanisms, ensure that you specify a file system location that has adequate disk space and is not on the main system partition.

## SecAuditLogType

Configures the type of audit logging mechanism to be used.

{{< secmeta syntax="SecAuditLogType Serial|Concurrent|HTTPS" example="SecAuditLogType Serial" default="Serial" scope="Any" v2="2.0.0" v3="3.0.0" >}}

The possible values are:

- **Serial**: Audit log entries will be stored in a single file, specified by SecAuditLog. This is convenient for casual use, but it can slow down the server, because only one audit log entry can be written to the file at any one time.
- **Concurrent**: One file per transaction is used for audit logging. This approach is more scalable when heavy logging is required (multiple transactions can be recorded in parallel). In ModSecurity v2 it is also the only choice if you need to use remote logging (with mlogc). libModSecurity v3 also accepts `Parallel` as an alias.
- **HTTPS**: Only available in libModSecurity v3, and still considered experimental. Each audit log entry is POSTed to the URL given in SecAuditLog instead of being written to a file. Depending on the amount of requests that you have, it may be suitable.

{{% notice note %}}

The HTTPS audit log type is not supported by ModSecurity v2.

{{% /notice %}}

## SecAuditLogPrefix

Configures a text that will be prepended to each audit log line. This directive only exists in libModSecurity v3; ModSecurity v2 does not know it.

{{< secmeta syntax=`SecAuditLogPrefix "text"` example=`SecAuditLogPrefix "[audit.log]: "` scope="Any" v2="no" v3="3.0.15" >}}

This parameter is only used when audit log format is set to native. Intended to be used in situations where the log target receives entries from multiple log sources (for example when the audit log is written to stdout using `SecAuditLog /dev/stdout`).

**Example:**

``` apache
SecAuditEngine RelevantOnly
SecAuditLog /dev/stdout
SecAuditLogParts ABHZ
SecAuditLogType Serial
SecAuditLogRelevantStatus ^(?:5|4(?!04))
SecAuditLogPrefix "[audit.log]: "
```

**Audit log:**

``` json
[audit.log]: ---Lm20Vggw---A--
[audit.log]: [07/Aug/2025:18:00:57 +0200] 17545824577.300397 200.249.12.31 2313 200.249.12.31 80
[audit.log]: ---Lm20Vggw---B--
[audit.log]: GET /test.pl?param1=   test   ¶m2=test2 HTTP/1.1
[audit.log]: Host: www.modsecurity.org
[audit.log]: User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)
[audit.log]: Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
[audit.log]: Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
[audit.log]: Accept-Language: en-us,en;q=0.5
[audit.log]: Accept-Encoding: gzip,deflate
[audit.log]: Keep-Alive: 300
[audit.log]: Connection: keep-alive
[audit.log]: Pragma: no-cache
[audit.log]: Cache-Control: no-cache
[audit.log]:
[audit.log]:
[audit.log]: ---Lm20Vggw---H--
[audit.log]: ModSecurity: Access denied with code 403 (phase 1). Matched "Operator `Contains' with parameter `test' against variable `ARGS:param2' (Value: `test2' ) [file "auditlog.json"] [line "2"] [id "1"] [rev ""] [msg ""] [data ""] [severity "0"] [ver ""] [maturity "0"] [accuracy "0"] [hostname "200.249.12.31"] [uri "/test.pl"] [unique_id "17545824577.300397"] [ref "o0,4v20,10t:trimo0,4v38,5t:trim"]
[audit.log]:
[audit.log]: ---Lm20Vggw---Z--
```

## SecCacheTransformations

Controls the caching of transformations, which may speed up the processing of complex rule sets. Caching is off by default starting with 2.5.6, when it was deprecated and downgraded back to experimental.

{{< secmeta syntax="SecCacheTransformations On|Off [options]" example=`SecCacheTransformations On "minlen:64,maxlen:0"` scope="Any" v2="2.5.0" v3="no" >}}

The first directive parameter can be one of the following:

- **On**: Cache transformations (per transaction, per phase) allowing identical transforma- tions to be performed only once.
- **Off**: Do not cache any transformations, leaving all transformations to be performed every time they are needed.

The following options are allowed (multiple options must be comma-separated):

- **incremental:on\|off**: Enabling this option will cache every transformation instead of just the final transformation. The default is off.
- **maxitems:N**: Do not allow more than N transformations to be cached. Cache will be disabled once this number is reached. A zero value is interpreted as unlimited. This option may be useful to limit caching for a form with a large number of variables. The default value is 512.
- **minlen:N**: Do not cache the transformation if the variable’s length is less than N bytes. The default setting is 32.
- **maxlen:N**: Do not cache the transformation if the variable’s length is more than N bytes. A zero value is interpreted as unlimited. The default setting is 1024.

## SecChrootDir

Configures the directory path that will be used to jail the web server process.

{{< secmeta syntax="SecChrootDir /path/to/chroot/dir" example="SecChrootDir /chroot" scope="Main" v2="2.0.0" v3="no" >}}

This feature is not available on Windows builds. The internal chroot functionality provided by ModSecurity works great for simple setups. One example of a simple setup is Apache serving only static files, or running applications using built-in modules. Some problems you might encounter with more complex setups:

1.  DNS lookups do not work (this is because this feature requires a shared library that is loaded on demand, after chroot takes place).
2.  You cannot send email from PHP, because it wants to use sendmail and sendmail re- sides outside the jail.
3.  In some cases, when you separate Apache from its configuration, restarts and graceful reloads no longer work.

The best way to use SecChrootDir is the following:

1.  Create /chroot to be your main jail directory.
2.  Create /chroot/opt/apache inside jail.
3.  Create a symlink from /opt/apache to /chroot/opt/apache.
4.  Now install Apache into /chroot/opt/apache.

You should be aware that the internal chroot feature might not be 100% reliable. Due to the large number of default and third-party modules available for the Apache web server, it is not possible to verify the internal chroot works reliably with all of them. A module, working from within Apache, can do things that make it easy to break out of the jail. In particular, if you are using any of the modules that fork in the module initialization phase (e.g., mod_fastcgi, mod_fcgid, mod_cgid), you are advised to examine each Apache process and observe its current working directory, process root, and the list of open files. Consider what your options are and make your own decision.

{{% notice note %}}

This directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

## SecCollectionTimeout

Specifies the collections timeout. Default is 3600 seconds.

libModSecurity v3 accepts the directive (so that crs-setup.conf loads) but ignores it: v3 collections do not expire through this setting.

{{< secmeta syntax="SecCollectionTimeout seconds" default="3600" scope="Any" v2="2.6.3" v3="no" v3note="(accepted by the parser but ignored)" >}}

## SecComponentSignature

Appends component signature to the ModSecurity signature.

{{< secmeta syntax=`SecComponentSignature "COMPONENT_NAME/X.Y.Z (COMMENT)"` example=`SecComponentSignature "core ruleset/2.1.3"` scope="Main" v2="2.5.0" v3="3.0.0" >}}

This directive should be used to make the presence of significant rule sets known. The entire signature will be recorded in the transaction audit log.

{{% notice note %}}

In libModSecurity v3 the component signature is currently only included in the audit log output when the JSON option is used with the SecAuditLogFormat directive.

{{% /notice %}}

## SecConnEngine

Configures the connections engine. This directive affect the directives: SecConnReadStateLimit and SecConnWriteStateLimit.

{{< secmeta syntax="SecConnEngine On|Off|DetectionOnly" example="SecConnEngine On" scope="Any" v2="2.8.0" v3="no" >}}

Possible values are (Same as SecRuleEngine):

- **On**: process SecConn[Read\|Write]StateLimit.
- **Off**: Ignore the directives SecConn[Read\|Write]StateLimit
- **DetectionOnly**: process SecConn[Read\|Write]StateLimit definitions in verbose mode but never executes any disruptive actions

## SecContentInjection

Enables content injection using actions append and prepend.

{{< secmeta syntax="SecContentInjection On|Off" example="SecContentInjection On" scope="Any" v2="2.5.0" v3="no" >}}

This directive provides an easy way to control content injection, no matter what the rules want to do. It is not necessary to have response body buffering enabled in order to use content injection.

{{% notice note %}}

This directive must be enabled if you want to use @rsub + the STREAM_ variables to manipulate live transactional data.

{{% /notice %}}

## SecCookieFormat

Selects the cookie format that will be used in the current configuration context.

{{< secmeta syntax="SecCookieFormat 0|1" example="SecCookieFormat 0" default="0" scope="Any" v2="2.0.0" v3="3.0.0" v3note="(value `0` only)" >}}

The possible values are:

- **0**: Use version 0 (Netscape) cookies. This is what most applications use. It is the default value.
- **1**: Use version 1 cookies.

{{% notice note %}}

Only version 0 (Netscape) cookies is currently supported on libModSecurity (v3)

{{% /notice %}}

## SecCookieV0Separator

Specifies which character to use as the separator for cookie v0 content.

{{< secmeta syntax="SecCookieV0Separator character" scope="Any" v2="2.7.0" v3="no" >}}

## SecDataDir

Path where persistent data (e.g., IP address data, session data, and so on) is to be stored.

{{< secmeta syntax="SecDataDir /path/to/dir" example="SecDataDir /usr/local/apache/logs/data" scope="Main" v2="2.0.0" v3="no" v3note="(accepted by the parser but ignored)" >}}

This directive must be provided before initcol, setsid, and setuid can be used. The directory to which the directive points must be writable by the web server user.

libModSecurity v3 accepts the directive (so that modsecurity.conf-recommended loads) but ignores it: collections are kept in memory per process, or, when a backend such as LMDB is compiled in, the storage path is defined by the backend.

{{% notice note %}}

This directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

## SecDebugLog

Path to the ModSecurity debug log file.

{{< secmeta syntax="SecDebugLog /path/to/modsec-debug.log" example="SecDebugLog /usr/local/apache/logs/modsec-debug.log" scope="Any" v2="2.0.0" v3="3.0.0" >}}

## SecDebugLogLevel

Configures the verboseness of the debug log data.

{{< secmeta syntax="SecDebugLogLevel 0|1|2|3|4|5|6|7|8|9" example="SecDebugLogLevel 4" scope="Any" v2="2.0.0" v3="3.0.0" >}}

In ModSecurity v2, messages at levels 1–3 are always copied to the Apache error log. Therefore you can always use level 0 as the default logging level in production if you are very concerned with performance. Having said that, the best value to use is 3. Higher logging levels are not recommended in production, because the heavy logging affects performance adversely. In libModSecurity v3, always having the debug log active in a production environment is typically not advised; even when investigating a specific issue be aware that using a value of 4 or higher can impact performance significantly.

The possible values for the debug log level are:

- 0: no logging
- 1: errors (intercepted requests) only
- 2: warnings
- 3: notices
- 4: details of how transactions are handled
- 5: as above, but including information about each piece of information handled
- 9: log everything, including very detailed debugging information

## SecDefaultAction

Defines the default list of actions for a particular phase, which will be inherited by the rules in the same phase and in the same configuration context.

{{< secmeta syntax=`SecDefaultAction "action1,action2,action3"` example=`SecDefaultAction "phase:2,log,auditlog,deny,status:403,tag:'SLA 24/7'"` default="phase:2,log,auditlog,pass" scope="Any" v2="2.0.0" v3="3.0.0" >}}

Every rule following a previous `SecDefaultAction` directive in the same configuration context will inherit its settings unless more specific actions are used. Every `SecDefaultAction` directive must specify a disruptive action and a processing phase and cannot contain metadata actions.

{{% notice warning %}}

`SecDefaultAction` is not inherited across configuration contexts. (For an example of why this may be a problem, read the following ModSecurity Blog entry <https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/three-modsecurity-rule-language-annoyances/> .)

{{% /notice %}}

## SecDisableBackendCompression

Disables backend compression while leaving the frontend compression enabled.

{{< secmeta syntax="SecDisableBackendCompression On|Off" default="Off" scope="Any" v2="2.6.0" v3="no" >}}

This directive is necessary in reverse proxy mode when the backend servers support response compression, but you wish to inspect response bodies. Unless you disable backend compression, ModSecurity will only see compressed content, which is not very useful. This directive is not necessary in embedded mode, because ModSecurity performs inspection before response compression takes place.

## SecHashEngine

Configures the hash engine.

{{< secmeta syntax="SecHashEngine On|Off" example="SecHashEngine On" default="Off" scope="Any" v2="2.7.1" v3="no" >}}

The possible values are:

- **On**: Hash engine can process the request/response data.
- **Off**: Hash engine will not process any data.

{{% notice note %}}

Users must enable stream output variables and content injection.

{{% /notice %}}

## SecHashKey

Define the key that will be used by HMAC.

{{< secmeta syntax="SecHashKey rand|TEXT KeyOnly|SessionID|RemoteIP" example=`SecHashKey "this_is_my_key" KeyOnly` scope="Any" v2="2.7.1" v3="no" >}}

ModSecurity hash engine will append, if specified, the user's session id or remote ip to the key before the MAC operation. If the first parameter is "rand" then a random key will be generated and used by the engine.

## SecHashParam

Define the parameter name that will receive the MAC hash.

{{< secmeta syntax="SecHashParam TEXT" example=`SecHashParam "hmac"` scope="Any" v2="2.7.1" v3="no" >}}

ModSecurity hash engine will add a new parameter to protected HTML elements containing the MAC hash.

## SecHashMethodRx

Configures what kind of HTML data the hash engine should sign based on regular expression.

{{< secmeta syntax="SecHashMethodRx TYPE REGEX" example=`SecHashMethodRx HashHref "product_info|list_product"` scope="Any" v2="2.7.1" v3="no" >}}

As a initial support is possible to protect HREF, FRAME, IFRAME and FORM ACTION html elements as well response Location header when http redirect code are sent.

The possible values for TYPE are:

- **HashHref**: Used to sign href= html elements
- **HashFormAction**: Used to sign form action= html elements
- **HashIframeSrc**: Used to sign iframe src= html elements
- **HashframeSrc**: Used to sign frame src= html elements
- **HashLocation**: Used to sign Location response header

{{% notice note %}}

This directive is used to sign the elements however user must use the @validateHash operator to enforce data integrity.

{{% /notice %}}

## SecHashMethodPm

Configures what kind of HTML data the hash engine should sign based on string search algorithm.

{{< secmeta syntax=`SecHashMethodPm TYPE "string1 string2 string3..."` example=`SecHashMethodPm HashHref "product_info list_product"` scope="Any" v2="2.7.1" v3="no" >}}

As a initial support is possible to protect HREF, FRAME, IFRAME and FORM ACTION html elements as well response Location header when http redirect code are sent.

The possible values for TYPE are:

- **HashHref**: Used to sign href= html elements
- **HashFormAction**: Used to sign form action= html elements
- **HashIframeSrc**: Used to sign iframe src= html elements
- **HashframeSrc**: Used to sign frame src= html elements
- **HashLocation**: Used to sign Location response header

{{% notice note %}}

This directive is used to sign the elements however user must use the @validateHash operator to enforce data integrity.

{{% /notice %}}

## SecGeoLookupDb

Defines the path to the database that will be used for geolocation lookups.

{{< secmeta syntax="SecGeoLookupDb /path/to/db" example="SecGeoLookupDb /path/to/GeoLiteCity.dat" scope="Any" v2="2.5.0" v3="3.0.0" >}}

ModSecurity v2 relies on the free geolocation databases (GeoLite City and GeoLite Country) that can be obtained from MaxMind [1](http://www.maxmind.com). ModSecurity v2 only supports the legacy GeoIP format; MaxMind's newer GeoIP2 format is not supported there.

libModSecurity v3 supports the newer GeoIP2 (`.mmdb`) format through libmaxminddb (since 3.0.1), and the legacy GeoIP format when built with `--with-geoip`. The build must enable one of them, otherwise the directive fails to load.

{{% notice note %}}

Recent versions of libModSecurity v3 require libmaxminddb >= 1.4.2 (libmaxminddb-dev and libmaxminddb0 packages). Some users have reported difficulties if libgeoip-dev and libgeoip1 are also installed; removing these latter packages resolved the problem (see issue #2829).

{{% /notice %}}

## SecGsbLookupDb

Defines the path to the database that will be used for Google Safe Browsing (GSB) lookups.

{{< secmeta syntax="SecGsbLookupDb /path/to/db" example="SecGsbLookupDb /path/to/GsbMalware.dat" scope="Any" v2="2.6.0" v3="no" >}}

ModSecurity relies on the free Google Safe Browsing database that can be obtained from the Google GSB API [1](http://code.google.com/apis/safebrowsing/).

{{% notice note %}}

Deprecated in 2.7.0 after Google dev team decided to not allow the database download anymore. After registering and obtaining a Safe Browsing API key, you can automatically download the GSB using a tool like wget. For further information on how to proceed with the download, please visit Google's website: <https://developers.google.com/safe-browsing/v3/update-guide>

{{% /notice %}}

## SecGuardianLog

Configures an external program that will receive the information about every transaction via piped logging.

{{< secmeta syntax="SecGuardianLog |/path/to/httpd-guardian" example="SecGuardianLog |/usr/local/apache/bin/httpd-guardian" scope="Main" v2="2.0.0" v3="no" >}}

Guardian logging is designed to send the information about every request to an external program. Because Apache is typically deployed in a multiprocess fashion, which makes information sharing between processes difficult, the idea is to deploy a single external process to observe all requests in a stateful manner, providing additional protection.

Currently the only tool known to work with guardian logging is httpd-guardian, which is part of the Apache httpd tools project [1](http://apache-tools.cvs.sourceforge.net/viewvc/apache-tools/apache-tools/). The httpd-guardian tool is designed to defend against denial of service attacks. It uses the blacklist tool (from the same project) to interact with an iptables-based (on a Linux system) or pf-based (on a BSD system) firewall, dynamically blacklisting the offending IP addresses. It can also interact with SnortSam [2](http://www.snortsam.net). Assuming httpd-guardian is already configured (look into the source code for the detailed instructions), you only need to add one line to your Apache configuration to deploy it:

``` apache
SecGuardianLog |/path/to/httpd-guardian
```

{{% notice note %}}

This directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

## SecHttpBlKey

Configures the user's registered Honeypot Project HTTP BL API Key to use with @rbl.

{{< secmeta syntax="SecHttpBlKey [12 char access key]" example="SecHttpBlKey whdkfieyhtnf" scope="Main" v2="2.7.0" v3="3.0.0" >}}

If the @rbl operator uses the dnsbl.httpbl.org RBL (http://www.projecthoneypot.org/httpbl_api.php) you must provide an API key. This key is registered to individual users and is included within the RBL DNS requests.

## SecInterceptOnError

Configures how to respond when rule processing fails.

{{< secmeta syntax="SecInterceptOnError On|Off" example="SecInterceptOnError On" scope="Main" v2="2.6.0" v3="no" >}}

When an operator execution fails, that is it returns greater than 0, this directive configures how to react. When set to "Off", the rule is just ignored and the engine will continue executing the rules in phase. When set to "On", the rule will be just dropped and no more rules will be executed in the same phase, also no interception is made.

## SecMarker

Adds a fixed rule marker that can be used as a target in a skipAfter action. A SecMarker directive essentially creates a rule that does nothing and whose only purpose is to carry the given ID.

{{< secmeta syntax="SecMarker ID|TEXT" example="SecMarker 9999" scope="Any" v2="2.5.0" v3="3.0.0" >}}

The value can be either a number or a text string. The SecMarker directive is available to allow you to choose the best way to implement a skip-over. Here is an example used from the Core Rule Set:

``` apache
SecMarker BEGIN_HOST_CHECK

        SecRule &REQUEST_HEADERS:Host "@eq 0" \
                "skipAfter:END_HOST_CHECK,phase:2,rev:'2.1.1',t:none,block,msg:'Request Missing a Host Header',id:'960008',tag:'PROTOCOL_VIOLATION/MISSING_HEADER_HOST',tag:'WASCTC/WASC-21',tag:'OWASP_TOP_10/A7',tag:'PCI/6.5.10',severity:'5',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.notice_anomaly_score},setvar:tx.protocol_violation_score=+%{tx.notice_anomaly_score},setvar:tx.%{rule.id}-PROTOCOL_VIOLATION/MISSING_HEADER-%{matched_var_name}=%{matched_var}"
        SecRule REQUEST_HEADERS:Host "^$" \
                "phase:2,rev:'2.1.1',t:none,block,msg:'Request Missing a Host Header',id:'960008',tag:'PROTOCOL_VIOLATION/MISSING_HEADER_HOST',tag:'WASCTC/WASC-21',tag:'OWASP_TOP_10/A7',tag:'PCI/6.5.10',severity:'5',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.notice_anomaly_score},setvar:tx.protocol_violation_score=+%{tx.notice_anomaly_score},setvar:tx.%{rule.id}-PROTOCOL_VIOLATION/MISSING_HEADER-%{matched_var_name}=%{matched_var}"

SecMarker END_HOST_CHECK
```

## SecPcreMatchLimit

Sets the match limit in the PCRE library.

{{< secmeta syntax="SecPcreMatchLimit value" example="SecPcreMatchLimit 1500" default="1500 (v2); PCRE library default (v3)" scope="Main" v2="2.5.12" v3="3.0.10" >}}

In ModSecurity v2 the default can be changed when ModSecurity is prepared for compilation: the --enable-pcre-match-limit=val configure option will set a custom default and the --disable-pcre-match-limit option will revert back to the default of the PCRE library. For more information, refer to the pcre_extra field in the pcreapi man page.

{{% notice note %}}

In ModSecurity v2 this directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

libModSecurity v3 accepts the directive since 3.0.0 but only honors it since 3.0.10, where it sets the PCRE match limit for executions of the @rx and @rxGlobal operators. Unless the directive is set, the PCRE library default applies. If the configured limit is exceeded, the variable MSC_PCRE_LIMITS_EXCEEDED will be set.

## SecPcreMatchLimitRecursion

Sets the match limit recursion in the PCRE library.

{{< secmeta syntax="SecPcreMatchLimitRecursion value" example="SecPcreMatchLimitRecursion 1500" default="1500" scope="Main" v2="2.5.12" v3="no" >}}

The default can be changed when ModSecurity is prepared for compilation: the --enable-pcre-match-limit-recursion=val configure option will set a custom default and the --disable-pcre-match-limit-recursion option will revert back to the default of the PCRE library. For more information, refer to the pcre_extra field in the pcreapi man page.

{{% notice note %}}

This directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

## SecReadStateLimit

Establishes a per-IP address limit of how many connections are allowed to be in SERVER_BUSY_READ state.

{{< secmeta syntax="SecReadStateLimit LIMIT" example="SecReadStateLimit 50" default="0 (no limit)" scope="Main" v2="2.5.13" v3="no" >}}

For v2.8.0 or newest refer to SecConnReadStateLimit.

## SecConnReadStateLimit

Establishes a per-IP address limit of how many connections are allowed to be in SERVER_BUSY_READ state.

{{< secmeta syntax="SecConnReadStateLimit LIMIT OPTIONAL_IP_MATCH_OPERATOR" example=`SecConnReadStateLimit 50 "!@ipMatch 127.0.0.1"` default="0 (no limit)" scope="Main" v2="2.8.0" v3="no" >}}

This measure is effective against Slowloris-style attacks from a single IP address, but it may not be as good against modified attacks that work by slowly sending request body content. This is because Apache to switches state to SERVER_BUSY_WRITE once request headers have been read. As an alternative, consider mod_reqtimeout (part of Apache as of 2.2.15), which is expected be effective against both attack types. See Blog post on mitigating slow DoS attacks - <http://blog.spiderlabs.com/2010/11/advanced-topic-of-the-week-mitigating-slow-http-dos-attacks.html>. v2.8.0 and newest supports the @ipMatch, @ipMatchF and @ipMatchFromFile operator along with the its negative (e.g. !@ipMatch) these were used to create suspicious or whitelist. When a suspicious list is informed, just the IPs that belongs to the list will be filtered. A combination of suspicious and whitelist is possible by using multiple definitions of SecConnReadStateLimit, note, however, that the limit will be always overwrite by its successor.

**Note:** This functionality is Apache only.

**Note 2:** Make sure [SecConnEngine](#secconnengine) is on prior to use this feature.

## SecSensorId

Define a sensor ID that will be present into log part H.

{{< secmeta syntax="SecSensorId TEXT" example="SecSensorId WAFSensor01" scope="Main" v2="2.7.0" v3="no" >}}

## SecWriteStateLimit

Establishes a per-IP address limit of how many connections are allowed to be in SERVER_BUSY_WRITE state.

{{< secmeta syntax="SecWriteStateLimit LIMIT" example="SecWriteStateLimit 50" default="0 (no limit)" scope="Main" v2="2.6.0" v3="no" >}}

For v2.8.0 or newest refer to SecConnWriteStateLimit.

## SecConnWriteStateLimit

Establishes a per-IP address limit of how many connections are allowed to be in SERVER_BUSY_WRITE state.

{{< secmeta syntax="SecConnWriteStateLimit LIMIT OPTIONAL_IP_MATCH_OPERATOR" example=`SecConnWriteStateLimit 50 "!@ipMatch 127.0.0.1"` default="0 (no limit)" scope="Main" v2="2.8.0" v3="no" >}}

This measure is effective against Slow DoS request body attacks. v2.8.0 and newest supports the @ipMatch, @ipMatchF and @ipMatchFromFile operator along with the its negative (e.g. !@ipMatch) these were used to create suspicious or whitelist. When a suspicious list is informed, just the IPs that belongs to the list will be filtered. A combination of suspicious and whitelist is possible by using multiple definitions of SecConnReadStateLimit, note, however, that the limit will be always overwrite by its successor.

**Note:** This functionality is Apache only.

**Note 2:** Make sure [SecConnEngine](#secconnengine) is on prior to use this feature.

## SecParseXmlIntoArgs

Controls how XML processing is done. If you turn it on with `On` or `OnlyArgs`, then XML nodes will appear in `ARGS`.

{{< secmeta syntax="SecParseXmlIntoArgs Off|On|OnlyArgs" example="SecParseXmlIntoArgs Off" default="Off" scope="Any" v2="2.9.9" v3="3.0.15" >}}

In these cases, the [SecArgumentsLimit]({{% relref "3-reference-manual/3-2-configuration-directives#secargumentslimit" %}}) directive will set the limit to number of loadable arguments.

**NOTE:** You must enable this directive with `On` or `OnlyArgs` if you want to load XML nodes into `ARGS`.

This is an optional directive that allow the user to load XML payload's nodes into `ARGS` (and XML tags into `ARGS_NAMES`). The default value is `Off`. If the user set it to `On` then XML nodes will appear in `ARGS` collection with key `xml.tag.chain`, but the `XML` target will fill too. If the value is `OnlyArgs`, then `XML` will be empty. Notice that in this case the [@validateDTD](#validatedtd) and [@validateSchema]({{% relref "3-reference-manual/3-6-operators#validateschema" %}}) operators will return with false value (because the `XML` target is empty).

[`ctl:parseXmlIntoArgs`]({{% relref "3-reference-manual/3-5-actions#ctl" %}}) action's behavior is the same, you can control it during the transaction.

<b>Example</b> Consider the XML payload:

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <level1>
        <level2>foo</level2>
        <level2>bar</level2>
    </level1>
</root>
```

This payload will generate value for `XML` target like this: `foo bar`.

If you turn on this feature, the nodes will apear under `ARGS`:

``` apache
Adding XML argument 'xml.root.level1.level2' with value 'foo'
Adding XML argument 'xml.root.level1.level2' with value 'bar'
```

(These lines are from debug.log)

## SecRemoteRules

Load rules from a given file hosted on a HTTPS site.

{{< secmeta syntax="SecRemoteRules [crypto] key https://url" example="SecRemoteRules some-key https://www.yourserver.com/plain-text-rules.txt" scope="Any" v2="2.9.0" v3="3.0.0" >}}

This is an optional directive that allow the user to load rules from a remote server. Notice that besides the URL the user also needs to supply a key, which could be used by the target server to provide different content for different keys.

Along with the key, supplied by the users, ModSecurity will also send its Unique ID and the \`status call' in the format of headers to the target web server. The following headers are used:

`- ModSec-status`\
`- ModSec-unique-id`\
`- ModSec-key`

The optional option "crypto" tells ModSecurity to expect some encrypted content from server. The utilization of SecRemoteRules is only allowed over TLS, thus, this option may not be necessary.

{{% notice note %}}

A valid and trusted digital certificate is expected on the end server. It is also expected that the server uses TLS, preferable TLS 1.2.

{{% /notice %}}

## SecRemoteRulesFailAction

Action that will be taken if SecRemoteRules specify an URL that ModSecurity was not able to download.

{{< secmeta syntax="SecRemoteRulesFailAction Abort|Warn" example="SecRemoteRulesFailAction Abort" default="Abort" scope="Any" v2="2.9.0" v3="3.0.0" >}}

The default action is to Abort whenever there is a problem downloading a given URL.

{{% notice note %}}

This directive also influences the behavior of @ipMatchFromFile when used with a HTTPS URI to retrieve the remote file.

{{% /notice %}}

## SecRequestBodyAccess

Configures whether request bodies will be buffered and processed by ModSecurity.

{{< secmeta syntax="SecRequestBodyAccess On|Off" example="SecRequestBodyAccess On" default="Off" scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directive is required if you want to inspect the data transported request bodies (e.g., POST parameters). Request buffering is also required in order to make reliable blocking possible. The possible values are:

- On: buffer request bodies
- Off: do not buffer request bodies

## SecRequestBodyInMemoryLimit

Configures the maximum request body size that ModSecurity will store in memory.

{{< secmeta syntax="SecRequestBodyInMemoryLimit LIMIT_IN_BYTES" example="SecRequestBodyInMemoryLimit 131072" default="131072 (128 KB)" scope="Any" v2="2.0.0" v3="no" >}}

When a multipart/form-data request is being processed, once the in-memory limit is reached, the request body will start to be streamed into a temporary file on disk.

{{% notice note %}}

libModSecurity is able to deal with request body in a file or in a buffer (chunked or not). Web servers have properties which controls whenever a request should be saved to a file or used as a buffer (e.g. client_body_buffer_size [1](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_body_buffer_size)) . If it is a file, ModSecurity will use the file to perform the inspection. If not, the buffer will be used.

{{% /notice %}}

## SecRequestBodyJsonDepthLimit

Configures the maximum parsing depth that is allowed when parsing a JSON object.

{{< secmeta syntax="SecRequestBodyJsonDepthLimit LIMIT" example="SecRequestBodyJsonDepthLimit 5000" default="10000" scope="Any" v2="2.9.5" v3="3.0.6" >}}

During parsing of a JSON object, if nesting exceeds the configured depth limit then parsing will halt and REQBODY_ERROR will be set.

## SecRequestBodyLimit

Configures the maximum request body size ModSecurity will accept for buffering.

{{< secmeta syntax="SecRequestBodyLimit LIMIT_IN_BYTES" example="SecRequestBodyLimit 134217728" default="134217728 (128 MB) (v2); no limit (v3)" scope="Any" v2="2.0.0" v3="3.0.0" >}}

Anything over the limit will be rejected with status code 413 (Request Entity Too Large). There is a hard limit of 1 GB.

In ModSecurity v2 the default is 134217728 bytes (128 MB). libModSecurity v3 applies no limit unless the directive is set, and leaves the rejection status code to the connector.

{{% notice note %}}

In ModSecurity 2.5.x and earlier, SecRequestBodyLimit works only when used in the main server configuration, or a VirtualHost container. In these versions, request body limit is enforced immediately after phase 1, but before phase 2 configuration (i.e. whatever is placed in a Location container) is resolved. You can work around this limitation by using a phase 1 rule that changes the request body limit dynamically, using the ctl:requestBodyLimit action. ModSecurity 2.6.x (currently in the trunk only) and better do not have this limitation.

{{% /notice %}}

## SecRequestBodyNoFilesLimit

Configures the maximum request body size ModSecurity will accept for buffering, excluding the size of any files being transported in the request. This directive is useful to reduce susceptibility to DoS attacks when someone is sending request bodies of very large sizes. Web applications that require file uploads must configure SecRequestBodyLimit to a high value, but because large files are streamed to disk, file uploads will not increase memory consumption. However, it’s still possible for someone to take advantage of a large request body limit and send non-upload requests with large body sizes. This directive eliminates that loophole.

{{< secmeta syntax="SecRequestBodyNoFilesLimit NUMBER_IN_BYTES" example="SecRequestBodyNoFilesLimit 131072" default="1048576 (1 MB) (v2); no limit (v3)" scope="Any" v2="2.5.0" v3="3.0.7" >}}

Generally speaking, the default value is not small enough. For most applications, you should be able to reduce it down to 128 KB or lower. Anything over the limit will be rejected with status code 413 (Request Entity Too Large). There is a hard limit of 1 GB.

In ModSecurity v2 the default is 1048576 bytes (1 MB). libModSecurity v3 accepts the directive since 3.0.0 but only enforces it since 3.0.7, and applies no limit unless the directive is set.

## SecRequestBodyLimitAction

Controls what happens once a request body limit, configured with SecRequestBodyLimit, is encountered

{{< secmeta syntax="SecRequestBodyLimitAction Reject|ProcessPartial" example="SecRequestBodyLimitAction ProcessPartial" scope="Any" v2="2.6.0" v3="3.0.0" >}}

By default, ModSecurity will reject a request body that is longer than specified. This is problematic especially when ModSecurity is being run in DetectionOnly mode and the intent is to be totally passive and not take any disruptive actions against the transaction. With the ability to choose what happens once a limit is reached, site administrators can choose to inspect only the first part of the request, the part that can fit into the desired limit, and let the rest through. This is not ideal from a possible evasion issue perspective, however it may be acceptable under certain circumstances.

{{% notice note %}}

When the SecRuleEngine is set to DetectionOnly, SecRequestBodyLimitAction is automatically set to ProcessPartial in order to not cause any disruptions. If you want to know if/when a request body size is over your limit, you can create a rule to check for the existence of the INBOUND_DATA_ERROR variable.

{{% /notice %}}

## SecRequestEncoding

Declares the character encoding used in requests.

{{< secmeta syntax="SecRequestEncoding ENCODING" example="SecRequestEncoding utf-8" scope="Any" v2="yes" v3="no" >}}

ModSecurity v2 accepts and stores the value but never uses it: the encoding is not validated and no request processing depends on it, so the directive has no effect. libModSecurity v3 does not accept it. It is documented only because it still appears in old configurations.

## SecResponseBodyLimit

Configures the maximum response body size that will be accepted for buffering.

{{< secmeta syntax="SecResponseBodyLimit LIMIT_IN_BYTES" example="SecResponseBodyLimit 524228" default="524288 (512 KB) (v2); no limit (v3)" scope="Any" v2="2.0.0" v3="3.0.0" >}}

Anything over this limit will be rejected; ModSecurity v2 uses status code 500 (Internal Server Error). This setting will not affect the responses with MIME types that are not selected for buffering. There is a hard limit of 1 GB.

In ModSecurity v2 the default is 524288 bytes (512 KB). libModSecurity v3 applies no limit unless the directive is set.

## SecResponseBodyLimitAction

Controls what happens once a response body limit, configured with SecResponseBodyLimit, is encountered.

{{< secmeta syntax="SecResponseBodyLimitAction Reject|ProcessPartial" example="SecResponseBodyLimitAction ProcessPartial" default="Reject" scope="Any" v2="2.5.0" v3="3.0.0" >}}

By default, ModSecurity will reject a response body that is longer than specified. Some web sites, however, will produce very long responses, making it difficult to come up with a reasonable limit. Such sites would have to raise the limit significantly to function properly, defying the purpose of having the limit in the first place (to control memory consumption). With the ability to choose what happens once a limit is reached, site administrators can choose to inspect only the first part of the response, the part that can fit into the desired limit, and let the rest through. Some could argue that allowing parts of responses to go uninspected is a weakness. This is true in theory, but applies only to cases in which the attacker controls the output (e.g., can make it arbitrary long). In such cases, however, it is not possible to prevent leakage anyway. The attacker could compress, obfuscate, or even encrypt data before it is sent back, and therefore bypass any monitoring device.

## SecResponseBodyMimeType

Configures which MIME types are to be considered for response body buffering.

{{< secmeta syntax="SecResponseBodyMimeType MIMETYPE MIMETYPE ..." example="SecResponseBodyMimeType text/plain text/html text/xml" default="text/plain text/html (v2); all types (v3)" scope="Any" v2="2.0.0" v3="3.0.0" >}}

Multiple SecResponseBodyMimeType directives can be used to add MIME types. Use SecResponseBodyMimeTypesClear to clear previously configured MIME types and start over.

In ModSecurity v2 the default list is `text/plain text/html`. libModSecurity v3 has no default list: when the directive is not set, every response type is considered for buffering.

{{% notice note %}}

Users that wish to perform JSON body inspection on response (phase 4) need to add _application/json_ to SecResponseBodyMimeType.

{{% /notice %}}

## SecResponseBodyMimeTypesClear

Clears the list of MIME types considered for response body buffering, allowing you to start populating the list from scratch.

{{% notice note %}}

In libModSecurity v3 the clear is applied when configurations are merged, so it discards every SecResponseBodyMimeType of the same configuration, including those written after it. Put the directive in a parent configuration (e.g. modsecurity.conf) and the new MIME types in a later one.

{{% /notice %}}

{{< secmeta syntax="SecResponseBodyMimeTypesClear" example="SecResponseBodyMimeTypesClear" scope="Any" v2="2.0.0" v3="3.0.0" >}}

## SecResponseBodyAccess

Configures whether response bodies are to be buffered.

{{< secmeta syntax="SecResponseBodyAccess On|Off" example="SecResponseBodyAccess On" default="Off" scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directive is required if you plan to inspect HTML responses and implement response blocking. Possible values are:

- On: buffer response bodies (but only if the response MIME type matches the list configured with SecResponseBodyMimeType).
- Off: do not buffer response bodies.

## SecRule

Creates a rule that will analyze the selected variables using the selected operator.

{{< secmeta syntax="SecRule VARIABLES OPERATOR [ACTIONS]" example=`SecRule ARGS "@rx attack" "phase:1,log,deny,id:1"` scope="Any" v2="2.0.0" v3="3.0.0" >}}

Every rule must provide one or more variables along with the operator that should be used to inspect them. If no actions are provided, the default list will be used. (There is always a default list, even if one was not explicitly set with SecDefaultAction.) If there are actions specified in a rule, they will be merged with the default list to form the final actions that will be used. (The actions in the rule will overwrite those in the default list.) Refer to SecDefaultAction for more information.

## SecRuleInheritance

Configures whether the current context will inherit the rules from the parent context.

{{< secmeta syntax="SecRuleInheritance On|Off" example="SecRuleInheritance Off" default="On" scope="Any" v2="2.0.0" v3="no" >}}

Sometimes when you create a more specific configuration context (for example using the <Location> container), you may wish to use a different set of rules than those used in the parent context. By setting SecRuleInheritance to Off, you prevent the parent rules to be inherited, which allows you to start from scratch. In ModSecurity 2.5.x it is not possible to override phase 1 rules from a <Location> configuration context. There are no limitations in that respect in the current development version (and there won’t be in the next major version).

The possible values are:

- On: inherit rules from the parent context
- Off: do not inherit rules from the parent context

{{% notice note %}}

Configuration contexts are an Apache concept. Directives <Directory>, <Files>, <Location>, and <VirtualHost> are all used to create configuration contexts. For more information, please go to the Apache documentation, under Configuration Sections [1](http://httpd.apache.org/docs/2.0/sections.html). This directive does not affect how configuration options are inherited.

{{% /notice %}}

## SecRuleEngine

Configures the rules engine.

{{< secmeta syntax="SecRuleEngine On|Off|DetectionOnly" example="SecRuleEngine On" default="Off (v2); unset (v3)" scope="Any" v2="2.0.0" v3="3.0.0" >}}

The possible values are:

- **On**: process rules
- **Off**: do not process rules
- **DetectionOnly**: process rules but never executes any disruptive actions (block, deny, drop, allow, proxy and redirect)

In ModSecurity v2 the default is Off. libModSecurity v3 leaves the value unset, in which state rules are evaluated and logged but never interrupt the transaction (equivalent to DetectionOnly). Always set it explicitly.

## SecRulePerfTime

Set a performance threshold for rules. Rules that spend at least the time defined will be logged into audit log Part H as Rules-Performance-Info in the format id=usec, comma separated.

{{< secmeta syntax="SecRulePerfTime USECS" example="SecRulePerfTime 1000" scope="Any" v2="2.7.0" v3="no" >}}

The rules hitting the threshold can be accessed via the collection PERF_RULES.

## SecRuleRemoveById

Removes the matching rules from the current configuration context.

{{< secmeta syntax="SecRuleRemoveById ID ID RANGE ..." example=`SecRuleRemoveByID 1 2 "9000-9010"` scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directive supports multiple parameters, each of which can be a rule ID or a range. Parameters that contain spaces must be delimited using double quotes.

{{% notice note %}}

**This directive must be specified after the rule in which it is disabling**. This should be used within local custom rule files that are processed after third party rule sets. Example file - modsecurity_crs_60_customrules.conf.

{{% /notice %}}

## SecRuleRemoveByMsg

Removes the matching rules from the current configuration context.

{{< secmeta syntax="SecRuleRemoveByMsg REGEX" example=`SecRuleRemoveByMsg "FAIL"` scope="Any" v2="2.0.0" v3="3.0.0" >}}

Normally, you would use SecRuleRemoveById to remove rules, but that requires the rules to have IDs defined. If they don’t, then you can remove them with SecRuleRemoveByMsg, which matches a regular expression against rule messages.

{{% notice note %}}

In libModSecurity v3 the parameter is not a regular expression: it is compared against the rule's msg by case-sensitive string equality.

{{% /notice %}}

{{% notice note %}}

This directive must be specified after the rule in which it is disabling. This should be used within local custom rule files that are processed after third party rule sets. Example file - modsecurity_crs_60_customrules.conf.

{{% /notice %}}

## SecRuleRemoveByTag

Removes the matching rules from the current configuration context.

{{< secmeta syntax="SecRuleRemoveByTag REGEX" example=`SecRuleRemoveByTag "WEB_ATTACK/XSS"` scope="Any" v2="2.6.0" v3="3.0.0" >}}

Normally, you would use SecRuleRemoveById to remove rules, but that requires the rules to have IDs defined. If they don’t, then you can remove them with SecRuleRemoveByTag, which matches a regular expression against rule tag data. This is useful if you want to disable entire groups of rules based on tag data. Example tags used in the OWASP ModSecurity CRS include:

- AUTOMATION/MALICIOUS
- AUTOMATION/MISC
- AUTOMATION/SECURITY_SCANNER
- LEAKAGE/SOURCE_CODE_ASP_JSP
- LEAKAGE/SOURCE_CODE_CF
- LEAKAGE/SOURCE_CODE_PHP
- WEB_ATTACK/CF_INJECTION
- WEB_ATTACK/COMMAND_INJECTION
- WEB_ATTACK/FILE_INJECTION
- WEB_ATTACK/HTTP_RESPONSE_SPLITTING
- WEB_ATTACK/LDAP_INJECTION
- WEB_ATTACK/PHP_INJECTION
- WEB_ATTACK/REQUEST_SMUGGLING
- WEB_ATTACK/SESSION_FIXATION
- WEB_ATTACK/SQL_INJECTION
- WEB_ATTACK/SSI_INJECTION
- WEB_ATTACK/XSS

{{% notice note %}}

In libModSecurity v3 the parameter is not a regular expression: it is compared against each tag of the rule by case-sensitive string equality.

{{% /notice %}}

{{% notice note %}}

This directive must be specified after the rule in which it is disabling. This should be used within local custom rule files that are processed after third party rule sets. Example file - modsecurity_crs_60_customrules.conf.

{{% /notice %}}

## SecRuleScript

{{< secmeta syntax="SecRuleScript /path/to/script.lua [ACTIONS]" example=`SecRuleScript "/path/to/file.lua" "block"` scope="Any" v2="2.5.0" v3="3.0.0" >}}

Description: This directive creates a special rule that executes a Lua script to decide whether to match or not. The main difference from SecRule is that there are no targets nor operators. The script can fetch any variable from the ModSecurity context and use any (Lua) operator to test them. The second optional parameter is the list of actions whose meaning is identical to that of SecRule.

{{% notice note %}}

All Lua scripts are compiled at configuration time and cached in memory. To reload scripts you must reload the entire ModSecurity configuration by restarting the web server.

{{% /notice %}}

{{% notice note %}}

Although the software does not enforce including the 'id' action, including it is strongly advised. Omitting an id can cause problems.

{{% /notice %}}

Example script:

``` apache
-- Your script must define the main entry
-- point, as below.
function main()
    -- Log something at level 1. Normally you shouldn't be
    -- logging anything, especially not at level 1, but this is
    -- just to show you can. Useful for debugging.
    m.log(1, "Hello world!");

    -- Retrieve one variable.
    local var1 = m.getvar("REMOTE_ADDR");

    -- Retrieve one variable, applying one transformation function.
    -- The second parameter is a string.
    local var2 = m.getvar("ARGS", "lowercase");

    -- Retrieve one variable, applying several transformation functions.
    -- The second parameter is now a list. You should note that m.getvar()
    -- requires the use of comma to separate collection names from
    -- variable names. This is because only one variable is returned.
    local var3 = m.getvar("ARGS.p", { "lowercase", "compressWhitespace" } );

    -- If you want this rule to match return a string
    -- containing the error message. The message must contain the name
    -- of the variable where the problem is located.
    -- return "Variable ARGS:p looks suspicious!"

    -- Otherwise, simply return nil.
    return nil;
end
```

In this first example we were only retrieving one variable at the time. In this case the name of the variable is known to you. In many cases, however, you will want to examine variables whose names you won't know in advance, for example script parameters.

Example showing use of m.getvars() to retrieve many variables at once:

``` apache
function main()
    -- Retrieve script parameters.
    local d = m.getvars("ARGS", { "lowercase", "htmlEntityDecode" } );

    -- Loop through the parameters.
    for i = 1, #d do
        -- Examine parameter value.
        if (string.find(d[i].value, "<script")) then
            -- Always specify the name of the variable where the
            -- problem is located in the error message.
            return ("Suspected XSS in variable " .. d[i].name .. ".");
        end
    end

    -- Nothing wrong found.
    return nil;
end
```

{{% notice note %}}

Go to <http://www.lua.org/> to find more about the Lua programming language. The reference manual too is available online, at <http://www.lua.org/manual/5.1/> (ModSecurity v2) and <http://www.lua.org/manual/5.2/> (libModSecurity v3).

{{% /notice %}}

{{% notice note %}}

Lua support is marked as experimental as the way the programming interface may continue to evolve while we are working for the best implementation style. Any user input into the programming interface is appreciated.

{{% /notice %}}

{{% notice note %}}

libModSecurity (aka v3) is compatible with Lua 5.2+.

{{% /notice %}}

## SecRuleUpdateActionById

Updates the action list of the specified rule.

{{< secmeta syntax="SecRuleUpdateActionById RULEID[:offset] ACTIONLIST" example=`SecRuleUpdateActionById 12345 "deny,status:403"` scope="Any" v2="2.5.0" v3="3.0.0" >}}

This directive will overwrite the action list of the specified rule with the actions provided in the second parameter. It has two limitations: it cannot be used to change the ID or phase of a rule. Only the actions that can appear only once are overwritten. The actions that are allowed to appear multiple times in a list, will be appended to the end of the list.

``` apache
SecRule ARGS attack "phase:2,id:12345,t:lowercase,log,pass,msg:'Message text'"
SecRuleUpdateActionById 12345 "t:none,t:compressWhitespace,deny,status:403,msg:'New message text'"
```

The effective resulting rule in the previous example will be as follows:

``` apache
SecRule ARGS attack "phase:2,id:12345,t:lowercase,t:none,t:compressWhitespace,deny,status:403,msg:'New Message text'"
```

The addition of t:none will neutralize any previous transformation functions specified (t:lowercase, in the example).

{{% notice note %}}

In ModSecurity v2, if the target rule is a chained rule, you must currently specify chain in the SecRuleUpdateActionById action list as well. In libModSecurity v3, action updates to a chained rule may only be made to the main (first) rule in the chain.

{{% /notice %}}

## SecRuleUpdateTargetById

Updates the target (variable) list of the specified rule.

{{< secmeta syntax="SecRuleUpdateTargetById RULEID TARGET1[,TARGET2,TARGET3] REPLACED_TARGET" example=`SecRuleUpdateTargetById 12345 "!ARGS:foo"` scope="Any" v2="2.6.0" v3="3.0.0" >}}

This directive will append (or replace) variables to the current target list of the specified rule with the targets provided in the second parameter. Starting with 2.7.0 this feature supports id range.

**Explicitly Appending Targets**

This is useful for implementing exceptions where you want to externally update a target list to exclude inspection of specific variable(s).

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetById 958895 !ARGS:email
```

The effective resulting rule in the previous example will append the target to the end of the variable list as follows:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/*|!ARGS:email "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

Note that is is also possible to use regular expressions in the target specification:

``` apache
SecRuleUpdateTargetById 981172 "!REQUEST_COOKIES:/^appl1_.*/"
```

**Explicitly Replacing Targets**

You can also entirely replace the target list to something more appropriate for your environment. For example, lets say you want to inspect REQUEST_URI instead of REQUEST_FILENAME, you could do this:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetById 958895 REQUEST_URI REQUEST_FILENAME
```

The effective resulting rule in the previous example replaces the target in the begin of the variable list as follows:

``` apache
SecRule REQUEST_URI|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

{{% notice note %}}

You could also do the same by using the ctl action with the ruleRemoveById directive. That would be useful if you want to only update the targets for a particular URL, thus conditionally appending targets.

{{% /notice %}}

{{% notice note %}}

libModSecurity v3 takes only the rule ID and the target list; the third REPLACED_TARGET parameter is not supported. To replace a target in v3, negate the old one and add the new one in the same list, e.g. `SecRuleUpdateTargetById 958895 !REQUEST_FILENAME,REQUEST_URI`. If you want to use grouping in a regular expression target, you must enclose it in single quotes:

``` apache
SecRuleUpdateTargetById 981172 "!REQUEST_COOKIES:/^appl1_.*/"
SecRuleUpdateTargetById 981173 "!REQUEST_COOKIES:'/^(appl1_.*|foo_.*)/'"
```

{{% /notice %}}

## SecRuleUpdateTargetByMsg

Updates the target (variable) list of the specified rule by rule message.

{{< secmeta syntax="SecRuleUpdateTargetByMsg TEXT TARGET1[,TARGET2,TARGET3] REPLACED_TARGET" example=`SecRuleUpdateTargetByMsg "Cross-site Scripting (XSS) Attack" "!ARGS:foo"` scope="Any" v2="2.7.0" v3="3.0.0" >}}

This directive will append (or replace) variables to the current target list of the specified rule with the targets provided in the second parameter.

**Explicitly Appending Targets**

This is useful for implementing exceptions where you want to externally update a target list to exclude inspection of specific variable(s).

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetByMsg "System Command Injection" !ARGS:email
```

The effective resulting rule in the previous example will append the target to the end of the variable list as follows:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/*|!ARGS:email "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

**Explicitly Replacing Targets**

You can also entirely replace the target list to something more appropriate for your environment. For example, lets say you want to inspect REQUEST_URI instead of REQUEST_FILENAME, you could do this:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetByMsg "System Command Injection" REQUEST_URI REQUEST_FILENAME
```

The effective resulting rule in the previous example will append the target to the end of the variable list as follows:

``` apache
SecRule REQUEST_URI|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

{{% notice note %}}

libModSecurity v3 takes only the message and the target list; the third REPLACED_TARGET parameter is not supported. To replace a target in v3, negate the old one and add the new one in the same list, e.g. `SecRuleUpdateTargetByMsg "System Command Injection" !REQUEST_FILENAME|REQUEST_URI`. The message is compared by case-sensitive string equality.

{{% /notice %}}

## SecRuleUpdateTargetByTag

Updates the target (variable) list of the specified rule by rule tag.

{{< secmeta syntax="SecRuleUpdateTargetByTag TEXT TARGET1[,TARGET2,TARGET3] REPLACED_TARGET" example=`SecRuleUpdateTargetByTag "WEB_ATTACK/XSS" "!ARGS:foo"` scope="Any" v2="2.7.0" v3="3.0.0" >}}

This directive will append (or replace) variables to the current target list of the specified rule with the targets provided in the second parameter.

**Explicitly Appending Targets**

This is useful for implementing exceptions where you want to externally update a target list to exclude inspection of specific variable(s).

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetByTag "WASCTC/WASC-31" !ARGS:email
```

The effective resulting rule in the previous example will append the target to the end of the variable list as follows:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/*|!ARGS:email "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

**Explicitly Replacing Targets**

You can also entirely replace the target list to something more appropriate for your environment. For example, lets say you want to inspect REQUEST_URI instead of REQUEST_FILENAME, you could do this:

``` apache
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}"

SecRuleUpdateTargetByTag "WASCTC/WASC-31" REQUEST_URI REQUEST_FILENAME
```

The effective resulting rule in the previous example will append the target to the end of the variable list as follows:

``` apache
SecRule REQUEST_URI|ARGS_NAMES|ARGS|XML:/* "[\;\|\`]\W*?\bmail\b" \
     "phase:2,rev:'2.1.1',capture,t:none,t:htmlEntityDecode,t:compressWhitespace,t:lowercase,ctl:auditLogParts=+E,block,msg:'System Command Injection',id:'958895',tag:'WEB_ATTACK/COMMAND_INJECTION',tag:'WASCTC/WASC-31',tag:'OWASP_TOP_10/A1',tag:'PCI/6.5.2',logdata:'%{TX.0}',severity:'2',setvar:'tx.msg=%{rule.msg}',setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%
{tx.0}""
```

{{% notice note %}}

libModSecurity v3 takes only the tag and the target list; the third REPLACED_TARGET parameter is not supported. To replace a target in v3, negate the old one and add the new one in the same list, e.g. `SecRuleUpdateTargetByTag "WASCTC/WASC-31" !REQUEST_FILENAME|REQUEST_URI`. The tag is compared by case-sensitive string equality.

{{% /notice %}}

## SecServerSignature

Instructs ModSecurity to change the data presented in the "Server:" response header token.

{{< secmeta syntax=`SecServerSignature "WEB SERVER SOFTWARE"` example=`SecServerSignature "Microsoft-IIS/6.0"` scope="Main" v2="2.0.0" v3="no" >}}

In order for this directive to work, you must set the Apache ServerTokens directive to Full. ModSecurity will overwrite the server signature data held in this memory space with the data set in this directive. If ServerTokens is not set to Full, then the memory space is most likely not large enough to hold the new data we are looking to insert.

{{% notice note %}}

This directive is not allowed inside VirtualHosts. If enabled, it must be placed in a global server-wide configuration file such as your default modsecurity.conf.

{{% /notice %}}

## SecStatusEngine

Controls Status Reporting functionality. Uses DNS-based reporting to send software version information to the ModSecurity Project team.

{{< secmeta syntax="SecStatusEngine On|Off" example="SecStatusEngine On" default="Off" scope="Any" v2="2.8.0" v3="no" >}}

If SecStatusEngine directive is not present, it is disabled. If SecStatusEngine is marked as On, the following information will be shared with the ModSecurity project team when the web server is started:

- Anonymous unique id for the server
- Version of:
  - ModSecurity
  - Web Server Software (Apache, IIS, Nginx, Java)
  - APR
  - Libxml2
  - Lua
  - PCRE

{{% notice note %}}

This is an example of the information presented in the Apache error_log representing what data will be sent:

{{% /notice %}}

``` json
[Mon Jan 20 10:55:22.001020 2014] [:notice] [pid 18231:tid 140735189168512] ModSecurity: StatusEngine call: "2.7.7,Apache/2.4.4 (Unix),1.4.6/1.4.6, 8.32 /8.32 2012-11-30,Lua 5.1/(null),2.7.8/(null),96ce9ba3c2fb71f7a8bb92a88d560d44dbe459b8"
[Mon Jan 20 10:55:22.089012 2014] [:notice] [pid 18231:tid 140735189168512] ModSecurity: StatusEngine call successfully submitted.
```

## SecStreamInBodyInspection

Configures the ability to use stream inspection for inbound request data in a re-allocable buffer. For security reasons we are still buffering the stream.

{{< secmeta syntax="SecStreamInBodyInspection On|Off" example="SecStreamInBodyInspection On" default="Off" scope="Any" v2="2.6.0" v3="no" >}}

This feature enables the creation of the STREAM_INPUT_BODY variable and is useful for data modification or to match data in raw data for any content-types.

{{% notice note %}}

This directive provides full access to REQUEST_BODY payload data. It does not include REQUEST_URI or REQUEST_HEADER data. Also it provides data to all kind of content types, different than REQUEST_BODY.

{{% /notice %}}

{{% notice note %}}

This directive is NOT supported for libModSecurity (v3). Naturally, STREAM_INPUT_BODY is also NOT supported on libModSecurity.

{{% /notice %}}

{{% notice note %}}

This directive may significantly impact file upload times. The impact depends on server resources and the nature of operations being performed on the request bodies being streamed in.

{{% /notice %}}

## SecStreamOutBodyInspection

Configures the ability to use stream inspection for outbound request data in a re-allocable buffer. For security reasons we are still buffering the stream.

{{< secmeta syntax="SecStreamOutBodyInspection On|Off" example="SecStreamOutBodyInspection On" default="Off" scope="Any" v2="2.6.0" v3="no" >}}

This feature enables the creation of the STREAM_OUTPUT_BODY variable and is useful when you need to do data modification into response body.

{{% notice note %}}

This directive provides access to RESPONSE_BODY payload data. It does not include RESPONSE_HEADER data.

{{% /notice %}}

## SecTmpDir

Configures the directory where temporary files will be created.

{{< secmeta syntax="SecTmpDir /path/to/dir" example="SecTmpDir /tmp" scope="Any" v2="2.0.0" v3="no" v3note="(accepted by the parser but ignored)" >}}

The location specified needs to be writable by the Apache user process. This is the directory location where ModSecurity will swap data to disk if it runs out of memory (more data than what was specified in the SecRequestBodyInMemoryLimit directive) during inspection.

As of ModSecurity version 3.0, SecTmpDir is no longer supported. libModSecurity is able to deal with request body in a file or in a buffer (chunked or not). Web servers have properties which controls whenever a request should be saved to a file or used as a buffer (e.g. client_body_buffer_size <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_body_buffer_size>) . If it is a file, ModSecurity will use the file to perform the inspection. If not, the buffer will be used.

## SecTmpSaveUploadedFiles

Configures whether or not files uploaded via a multipart POST request will be temporarily saved to the file system.

{{< secmeta syntax="SecTmpSaveUploadedFiles On|Off" example="SecTmpSaveUploadedFiles On" default="Off" scope="Any" v2="yes" v3="3.0.0" >}}

When set to On, uploaded files are extracted to the upload directory (SecUploadDir) while the transaction is processed, even when SecUploadKeepFiles is Off, so that operators such as @inspectFile can examine them. The files are automatically deleted after the transaction is complete. If you wish to retain the files, see SecUploadKeepFiles. Both ModSecurity v2 and libModSecurity v3 implement this directive.

## SecUnicodeMapFile

Defines the path to the file that will be used by the urlDecodeUni transformation function to map Unicode code points during normalization and specifies the Code Point to use.

{{< secmeta syntax="SecUnicodeMapFile /path/to/unicode.mapping CODEPOINT" example="SecUnicodeMapFile unicode.mapping 20127" scope="Main" v2="2.6.1" v3="3.0.0" >}}

{{% notice note %}}

With libModSecurity v3 you may need to place the unicode.mapping file in the same directory where the modsecurity.conf file is located.

{{% /notice %}}

## SecUnicodeCodePage

Defines which Unicode code point will be used by the urlDecodeUni transformation function during normalization.

{{< secmeta syntax="SecUnicodeCodePage XXXXX" example="SecUnicodeCodePage 20127" scope="Any" v2="2.6.1" v3="no" >}}

Deprecated in ModSecurity 2.7.5: SecUnicodeMapFile now accepts the code page as its second parameter. libModSecurity v3 does not accept this directive.

## SecUploadDir

Configures the directory where intercepted files will be stored.

{{< secmeta syntax="SecUploadDir /path/to/dir" example="SecUploadDir /tmp" scope="Any" v2="2.0.0" v3="3.0.0" >}}

This directory must be on the same filesystem as the temporary directory defined with SecTmpDir. This directive is used with SecUploadKeepFiles.

## SecUploadFileLimit

Configures the maximum number of file uploads processed in a multipart POST.

{{< secmeta syntax="SecUploadFileLimit number" example="SecUploadFileLimit 10" default="100 (v2); no limit (v3)" scope="Any" v2="2.5.12" v3="3.0.0" >}}

In ModSecurity v2 the default is set to 100 files, but you are encouraged to reduce this value. libModSecurity v3 applies no limit unless the directive is set. Any file over the limit will not be extracted and the MULTIPART_FILE_LIMIT_EXCEEDED and MULTIPART_STRICT_ERROR flags will be set. To prevent bypassing any file checks, you must check for one of these flags.

{{% notice note %}}

If the limit is exceeded, the part name and file name will still be recorded in FILES_NAME and FILES, the file size will be recorded in FILES_SIZES, but there will be no record in FILES_TMPNAMES as a temporary file was not created.

{{% /notice %}}

## SecUploadFileMode

Configures the mode (permissions) of any uploaded files using an octal mode (as used in chmod).

{{< secmeta syntax=`SecUploadFileMode octal_mode|"default"` example="SecUploadFileMode 0640" default="0600" scope="Any" v2="2.1.6" v3="3.0.0" >}}

This feature is not available on operating systems not supporting octal file modes. The default mode (0600) only grants read/write access to the account writing the file. If access from another account is needed (using clamd is a good example), then this directive may be required. However, use this directive with caution to avoid exposing potentially sensitive data to unauthorized users. Using the value "default" will revert back to the default setting.

{{% notice note %}}

The process umask may still limit the mode if it is being more restrictive than the mode set using this directive.

{{% /notice %}}

## SecUploadKeepFiles

Configures whether or not the intercepted files will be kept after transaction is processed.

{{< secmeta syntax="SecUploadKeepFiles On|Off|RelevantOnly" example="SecUploadKeepFiles On" default="Off" scope="Any" v2="2.0.0" v3="3.0.0" v3note="(`RelevantOnly` is rejected)" >}}

This directive requires the storage directory to be defined (using SecUploadDir).

Possible values are:

- **On** - Keep uploaded files.
- **Off** - Do not keep uploaded files.
- **RelevantOnly** - This will keep only those files that belong to requests that are deemed relevant.

{{% notice note %}}

RelevantOnly is not yet supported on libModSecurity

{{% /notice %}}

## SecWebAppId

Creates an application namespace, allowing for separate persistent session and user storage.

{{< secmeta syntax=`SecWebAppId "NAME"` example=`SecWebAppId "WebApp1"` default="default" scope="Any" v2="2.0.0" v3="3.0.0" >}}

Application namespaces are used to avoid collisions between session IDs and user IDs when multiple applications are deployed on the same server. If it isn’t used, a collision between session IDs might occur.

``` apache
<VirtualHost *:80> 
ServerName app1.example.com 
SecWebAppId "App1" ...
</VirtualHost>

<VirtualHost *:80> 
ServerName app2.example.com 
SecWebAppId "App2" ...
</VirtualHost>
```

In the two examples configurations shown, SecWebAppId is being used in conjunction with the Apache VirtualHost directives. Applications namespace information is also recorded in the audit logs (using the WebApp-Info header of the H part).

With libModSecurity v3 the same separation is achieved through the connector's configuration, for example nginx server blocks. The configured value is available in the WEBAPPID variable.

``` apache
server {
    listen 80;
    server_name app1.example.com;
    modsecurity_rules 'SecWebAppId "App1"';
    ...
}

server {
    listen 80;
    server_name app2.example.com;
    modsecurity_rules 'SecWebAppId "App2"';
    ...
}
```

## SecXmlExternalEntity

Enable or Disable the loading process of xml external entity. Loading external entity without correct verifying process can lead to a security issue.

{{< secmeta syntax="SecXmlExternalEntity On|Off" example="SecXmlExternalEntity Off" default="Off" scope="Any" v2="2.7.3" v3="3.0.0" >}}

**NOTE:** You must enable this directive if you need to use the `@validateSchema` or `@validateDtd` operators.
