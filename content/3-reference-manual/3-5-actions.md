---
title: Actions
weight: 5
---

Each action belongs to one of five groups:

- **Disruptive actions** - Cause ModSecurity to do something. In many cases something means block transaction, but not in all. For example, the allow action is classified as a disruptive action, but it does the opposite of blocking. There can only be one disruptive action per rule (if there are multiple disruptive actions present, or inherited, only the last one will take effect), or rule chain (in a chain, a disruptive action can only appear in the first rule).

{{% notice note %}}

**Disruptive actions will NOT be executed if the SecRuleEngine is set to DetectionOnly**. If you are creating exception/whitelisting rules that use the allow action, you should also add the ctl:ruleEngine=On action to execute the action.

{{% /notice %}}

- **Non-disruptive action**s - Do something, but that something does not and cannot affect the rule processing flow. Setting a variable, or changing its value is an example of a non-disruptive action. Non-disruptive action can appear in any rule, including each rule belonging to a chain.
- **Flow actions** - These actions affect the rule flow (for example chain, skip and skipAfter).
- **Meta-data actions** - Meta-data actions are used to provide more information about rules. Examples include id, rev, severity and msg.
- **Data actions** - Not really actions, these are mere containers that hold data used by other actions. For example, the status action holds the status that will be used for blocking (if it takes place).

## accuracy

Specifies the relative accuracy level of the rule related to false positives/negatives. The value is a string based on a numeric scale (1-9 where 9 is very strong and 1 has many false positives). libModSecurity v3 rejects a non-numeric value.

{{< secmeta group="Meta-data" v2="2.7" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx \bgetparentfolder\b" \
    "id:'958016',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:htmlEntityDecode,\
    t:compressWhiteSpace,\
    t:lowercase,\
    msg:'Cross-site Scripting (XSS) Attack',\
    logdata:'% {TX.0}',\
    tag:'WEB_ATTACK/XSS',\
    tag:'WASCTC/WASC-8',\
    tag:'WASCTC/WASC-22',\
    tag:'OWASP_TOP_10/A2',\
    tag:'OWASP_AppSensor/IE1',\
    tag:'PCI/6.5.1',\
    ctl:auditLogParts=+E,\
    ver:'CRS/2.2.4',\
    accuracy:'9',\
    maturity:'9',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.xss_score=+%{tx.critical_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/XSS-%{matched_var_name}=%{tx.0}"
```

## allow

Stops rule processing on a successful match and allows the transaction to proceed.

{{< secmeta group="Disruptive" v2="yes" v3="yes" >}}

Example:

``` seclang
# Allow unrestricted access from 192.168.1.100
SecRule REMOTE_ADDR "@rx ^192\.168\.1\.100$" "id:95,phase:1,allow,nolog"
```

Prior to ModSecurity 2.5 the allow action would only affect the current phase. An allow in phase 1 would skip processing the remaining rules in phase 1 but the rules from phase 2 would execute. Starting with v2.5.0 allow was enhanced to allow for fine-grained control of what is done. The following rules now apply:

1.  If used on its own, like in the example above, allow will affect the entire transaction, stopping processing of the current phase but also skipping over all other phases apart from the logging phase. (The logging phase is special; it is designed to always execute.)
2.  If used with parameter "phase", allow will cause the engine to stop processing the current phase. Other phases will continue as normal.
3.  If used with parameter "request", allow will cause the engine to stop processing the current phase. The next phase to be processed will be phase RESPONSE_HEADERS.

Examples:

``` seclang
# Do not process request but process response.
SecAction "id:96,phase:1,allow:request"

# Do not process transaction (request and response).
SecAction "id:97,phase:1,allow"
```

If you want to allow a response through, put a rule in phase RESPONSE_HEADERS and simply use allow on its own:

``` seclang
# Allow response through.
SecAction "id:98,phase:3,allow"
```

libModSecurity v3 implements the same three forms (`allow`, `allow:phase` and `allow:request`) with the same semantics.

## append

Appends text given as parameter to the end of response body. Content injection must be enabled (using the SecContentInjection directive). No content type checks are made, which means that before using any of the content injection actions, you must check whether the content type of the response is adequate for injection.

{{< secmeta group="Non-disruptive" phases="3 and 4." v2="yes" v3="no" >}}

Example:

``` seclang
SecRule RESPONSE_CONTENT_TYPE "@rx ^text/html" \
    "id:99,\
    pass,\
    nolog,\
    append:'<hr>Footer'"
```

A rule can carry only one append action (a second one replaces the first), and a later matching rule that uses append replaces the text set by an earlier one. libModSecurity v3 refuses the rule at configuration load (`Action: Append is not yet supported.`).

{{% notice warning %}}

Although macro expansion is allowed in the additional content, you are strongly cautioned against inserting user-defined data fields into output. Doing so would create a cross-site scripting vulnerability.

{{% /notice %}}

## auditlog

Marks the transaction for logging in the audit log.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

Example:

`SecRule REMOTE_ADDR "^192\.168\.1\.100$" auditlog,phase:1,id:100,allow`

{{% notice note %}}

The auditlog action is now explicit if log is already specified.

{{% /notice %}}

## block

Performs the disruptive action defined by the previous SecDefaultAction.

{{< secmeta group="Disruptive" v2="yes" v3="yes" >}}

This action is essentially a placeholder that is intended to be used by rule writers to request a blocking action, but without specifying how the blocking is to be done. The idea is that such decisions are best left to rule users, as well as to allow users, to override blocking if they so desire. In future versions of ModSecurity, more control and functionality will be added to define "how" to block.

Examples:

``` seclang
# Specify how blocking is to be done
SecDefaultAction "id:101,phase:2,deny,status:403,log,auditlog"

# Detect attacks where we want to block
SecRule ARGS "@rx attack1" "id:102,phase:2,block"

# Detect attacks where we want only to warn
SecRule ARGS "@rx attack2" "id:103,phase:2,pass"
```

It is possible to use the SecRuleUpdateActionById directive to override how a rule handles blocking. This is useful in three cases:

1.  If a rule has blocking hard-coded, and you want it to use the policy you determine
2.  If a rule was written to block, but you want it to only warn
3.  If a rule was written to only warn, but you want it to block

The following example demonstrates the first case, in which the hard-coded block is removed in favor of the user-controllable block:

``` seclang
# Specify how blocking is to be done
SecDefaultAction "id:104,phase:2,deny,status:403,log,auditlog"

# Detect attacks and block
SecRule ARGS "@rx attack1" "id:1,phase:2,deny"

# Change how rule ID 1 blocks
SecRuleUpdateActionById 1 "block"
```

libModSecurity v3 runs the disruptive action of the SecDefaultAction defined for the rule's phase; if there is none for that phase, block does nothing. v3 requires SecDefaultAction to name a real disruptive action (`block` is not accepted there) and allows it only once per phase.

## capture

When used together with the regular expression operator (@rx), the capture action will create copies of the regular expression captures and place them into the transaction variable collection.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

Example:

``` seclang
SecRule REQUEST_BODY "@rx ^username=(\w{25,})" \
    "id:105,\
    phase:2,\
    capture,\
    t:none,\
    chain"
    SecRule TX:1 "@rx (?:(?:a(dmin|nonymous)))"
```

The TX.0 variable always contains the entire area that the regular expression matched. All the other variables contain the captured values, in the order in which the capturing parentheses appear in the regular expression.

- **ModSecurity v2**: up to 10 captures are copied on a successful pattern match, each with a name consisting of a digit from 0 to 9.
- **libModSecurity v3**: every capturing group of the match is copied (TX.0, TX.1, TX.2, ...); there is no fixed limit of ten. Besides @rx, v3 honors capture for @rxGlobal, @pm, @detectSQLi, @detectXSS, @rbl, @verifyCC, @verifyCPF, @verifySSN and @verifySVNR.

## chain

Chains the current rule with the rule that immediately follows it, creating a rule chain. Chained rules allow for more complex processing logic.

{{< secmeta group="Flow" v2="yes" v3="yes" >}}

Example:

``` seclang
# Refuse to accept POST requests that do not contain Content-Length header.
# (Do note that this rule should be preceded by a rule
# that verifies only valid request methods are used.)
SecRule REQUEST_METHOD "@rx ^POST$" "id:105,phase:1,t:none,chain"
    SecRule &REQUEST_HEADERS:Content-Length "@eq 0" "t:none"
```

{{% notice note %}}

Rule chains allow you to simulate logical AND. The disruptive actions specified in the first portion of the chained rule will be triggered only if all of the variable checks return positive hits. If any one aspect of a chained rule comes back negative, then the entire rule chain will fail to match. Also note that disruptive actions, execution phases, metadata actions (id, rev, msg, tag, severity, logdata), skip, and skipAfter actions can be specified only by the chain starter rule.

{{% /notice %}}

The following directives can be used in rule chains:

- SecAction
- SecRule
- SecRuleScript

Special rules control the usage of actions in chained rules:

- Any actions that affect the rule flow (i.e., the disruptive actions, skip and skipAfter) can be used only in the chain starter. They will be executed only if the entire chain matches.
- Non-disruptive actions can be used in any rule; they will be executed if the rule that contains them matches and not only when the entire chain matches. In libModSecurity v3 this is true only for setvar: every other non-disruptive action in a chained rule (ctl, setenv, exec, log, ...) runs only once the whole chain has matched.
- The metadata actions (e.g., id, rev, msg) can be used only in the chain starter.

## ctl

Changes ModSecurity configuration on transient, per-transaction basis. Any changes made using this action will affect only the transaction in which the action is executed. The default configuration, as well as the other transactions running in parallel, will be unaffected.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Parse requests with Content-Type "text/xml" as XML
SecRule REQUEST_CONTENT_TYPE "@rx ^text/xml" \
    "id:106,\
    pass,\
    nolog,\
    ctl:requestBodyProcessor=XML"

# white-list the user parameter for rule #981260 when the REQUEST_URI is /index.php
SecRule REQUEST_URI "@beginsWith /index.php" \
    "phase:1,\
    pass,\
    t:none,\
    nolog,\
    ctl:ruleRemoveTargetById=981260;ARGS:user"
```

The following configuration options are supported. Unless noted otherwise an option is available in both ModSecurity v2 and libModSecurity v3:

1.  **auditEngine** - v2: yes. v3: since 3.0.7.
2.  **auditLogParts** - v2: yes. v3: yes, but only the `+`/`-` forms (`+E`, `-E`); an absolute part list is a parse error.
3.  **debugLogLevel** - v2: yes. v3: no.
4.  **forceRequestBodyVariable** - v2: since 2.5.7. v3: accepted by the parser but has no effect (REQUEST_BODY is always populated in v3).
5.  **hashEnforcement** - v2: since 2.7.1 (named `EncryptionEnforcement` in 2.7.0). v3: no.
6.  **hashEngine** - v2: since 2.7.1 (named `EncryptionEngine` in 2.7.0). v3: no.
7.  **parseXmlIntoArgs** - v2: since 2.9.9 (`On`, `Off` or `OnlyArgs`). v3: since 3.0.15. Controls XML nodes' parsing into `ARGS`, see [SecParseXmlIntoArgs]({{% relref "3-reference-manual/3-2-configuration-directives#secparsexmlintoargs" %}}).
8.  **requestBodyAccess** - v2: yes. v3: yes.
9.  **requestBodyLimit** - v2: yes. v3: no.
10. **requestBodyProcessor** - v2: yes. v3: yes (`XML`, `JSON`, and since 3.0.3 `URLENCODED`).
11. **responseBodyAccess** - v2: yes. v3: no.
12. **responseBodyLimit** - v2: yes. v3: no.
13. **ruleEngine** - v2: yes. v3: yes.
14. **ruleRemoveById** - v2: since 2.5.0; the value is a rule ID, a range (`1000-1999`) or a comma-separated list of IDs and ranges. v3: yes, but one ID or one range per action (no list); repeat the action to remove several (since 3.0.4). Since this action is triggered at run time, it should be specified **before** the rule which it is disabling.
15. **ruleRemoveByMsg** - v2: since 2.7.0; the value is a regular expression matched against the rule message. v3: no.
16. **ruleRemoveByTag** - v2: since 2.6.0; the value is a regular expression matched against the rule tags. v3: since 3.0.1, compared literally against each tag (not a regular expression).
17. **ruleRemoveTargetById** - v2: since 2.6.7. v3: yes, with the target compared literally against the variable name (`ARGS:user`; no regular-expression targets). Since this action is used to just remove targets, users don't need to use the char ! before the target list.
18. **ruleRemoveTargetByMsg** - v2: since 2.7.0. v3: no. Since this action is used to just remove targets, users don't need to use the char ! before the target list.
19. **ruleRemoveTargetByTag** - v2: since 2.7.0. v3: yes, with both the tag and the target compared literally. Since this action is used to just remove targets, users don't need to use the char ! before the target list.

`ctl:forceResponseBodyVariable` and `ctl:responseBodyProcessor` exist only in Coraza; neither ModSecurity v2 nor libModSecurity v3 accepts them. libModSecurity v3 recognizes only the options marked "v3: yes" above; any other `ctl` option (for example `ctl:responseBodyAccess=Off`) is a parse error that rejects the configuration.

With the exception of the requestBodyProcessor and forceRequestBodyVariable settings, each configuration option corresponds to one configuration directive and the usage is identical.

The requestBodyProcessor option allows you to configure the request body processor. By default, ModSecurity will use the URLENCODED and MULTIPART processors to process an application/x-www-form-urlencoded and a multipart/form-data body, respectively. Other two processors are also supported: JSON and XML, but they are never used implicitly. Instead, you must tell ModSecurity to use it by placing a few rules in the REQUEST_HEADERS processing phase. After the request body is processed as XML, you will be able to use the XML-related features to inspect it.

Request body processors will not interrupt a transaction if an error occurs during parsing. Instead, they will set the variables REQBODY_PROCESSOR_ERROR and REQBODY_PROCESSOR_ERROR_MSG. These variables should be inspected in the REQUEST_BODY phase and an appropriate action taken. The forceRequestBodyVariable option allows you to configure the REQUEST_BODY variable to be set when there is no request body processor configured. This allows for inspection of request bodies of unknown types.

{{% notice note %}}

There was a ctl:ruleUpdateTargetById introduced in 2.6.0 and removed from the code in 2.7.0. JSON was added as part of v2.8.0-rc1

{{% /notice %}}

## deny

Stops rule processing and intercepts transaction.

{{< secmeta group="Disruptive" v2="yes" v3="yes" >}}

Example: `SecRule REQUEST_HEADERS:User-Agent "nikto" "log,deny,id:107,msg:'Nikto Scanners Identified'"`

## deprecatevar

Decrements numerical value over time, which makes sense only applied to the variables stored in persistent storage.

{{< secmeta group="Non-disruptive" v2="yes" v3="no" >}}

Example: The following example will decrement the counter by 60 every 300 seconds.

``` seclang
SecAction "id:108,phase:5,pass,nolog,deprecatevar:SESSION.score=60/300"
```

Counter values are always positive, meaning that the value will never go below zero. Unlike expirevar, the deprecate action must be executed on every request. libModSecurity v3 refuses the rule at configuration load (`Action: DeprecateVar is not yet supported.`).

## drop

Initiates an immediate close of the TCP connection by sending a FIN packet.

{{< secmeta group="Disruptive" v2="yes" v3="3.0.4" v3note="(behaves like `deny`, see below)" >}}

**Example:** The following example initiates an IP collection for tracking Basic Authentication attempts. If the client goes over the threshold of more than 25 attempts in 2 minutes, it will DROP subsequent connections.

``` seclang
SecAction "id:109,phase:1,nolog,initcol:ip=%{REMOTE_ADDR}"
SecRule ARGS:login "!@rx ^$" \
    "id:110,\
    phase:1,\
    nolog,\
    setvar:ip.auth_attempt=+1,\
    deprecatevar:ip.auth_attempt=25/120"
SecRule IP:AUTH_ATTEMPT "@gt 25" \
    "id:111,\
    phase:1,\
    drop,\
    log,\
    msg:'Possible Brute Force Attack'"
```

{{% notice note %}}

This action is currently not available on Windows based builds.

{{% /notice %}}

This action is extremely useful when responding to both Brute Force and Denial of Service attacks in that, in both cases, you want to minimize both the network bandwidth and the data returned to the client. This action causes error message to appear in the log "(9)Bad file descriptor: core_output_filter: writing data to the network"

Unlike in v2, in libModSecurity v3 (since 3.0.4) this action currently functions the same as the deny action: the transaction is intercepted with a 403 status instead of the connection being closed.

## exec

Executes an external script/binary supplied as parameter. As of v2.5.0, if the parameter supplied to exec is a Lua script (detected by the .lua extension) the script will be processed internally. This means you will get direct access to the internal request context from the script. Please read the SecRuleScript documentation for more details on how to write Lua scripts.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" v3note="(Lua scripts only)" >}}

**Example:**

``` seclang
# Run external program on rule match
SecRule REQUEST_URI "@rx ^/cgi-bin/script\.pl" \
    "id:112,\
    phase:2,\
    block,\
    t:none,\
    t:lowercase,\
    t:normalizePath,\
    \ exec:/usr/local/apache/bin/test.sh"

# Run Lua script on rule match
SecRule ARGS:p "@rx attack" \
    "id:113,\
    phase:2,\
    block,\
    exec:/usr/local/apache/conf/exec.lua"
```

The exec action is executed independently from any disruptive actions specified. External scripts will always be called with no parameters. Some transaction information will be placed in environment variables. All the usual CGI environment variables will be there. You should be aware that forking a threaded process results in all threads being replicated in the new process. Forking can therefore incur larger overhead in a multithreaded deployment. The script you execute must write something (anything) to stdout; if it doesn’t, ModSecurity will assume that the script failed, and will record the failure.

libModSecurity v3 only supports Lua scripts (detected by the .lua extension); it does not fork external binaries. The library must be built with Lua support (`--with-lua`, detected automatically by configure), and the script is loaded when the configuration is parsed, so a missing or non-Lua script is a configuration error.

## expirevar

Configures a collection variable to expire after the given time period (in seconds).

{{< secmeta group="Non-disruptive" v2="yes" v3="3.0.11" >}}

**Example:**

``` seclang
SecRule REQUEST_COOKIES:JSESSIONID "!@rx ^$" \
    "id:114,\
    phase:1,\
    pass,\
    nolog,\
    setsid:%{REQUEST_COOKIES:JSESSIONID}"
SecRule REQUEST_URI "@rx ^/cgi-bin/script\.pl" \
    "id:115,\
    phase:2,\
    phase:1,\
    allow,\
    t:none,\
    t:lowercase,\
    t:normalizePath,\
    log,\
    setvar:session.suspicious=1,\
    expirevar:session.suspicious=3600"
```

You should use the expirevar actions at the same time that you use setvar actions in order to keep the intended expiration time. If they are used on their own (perhaps in a SecAction directive), the expire time will be reset.

libModSecurity v3 supports expirevar since 3.0.11, for the `ip`, `global`, `resource`, `session` and `user` collections.

## id

Assigns a unique, numeric ID to the rule or chain in which it appears. Starting with ModSecurity 2.7 this action is mandatory; libModSecurity v3 rejects any SecRule or SecAction without an id, and also rejects a rule whose id is already in use.

{{< secmeta group="Meta-data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule &REQUEST_HEADERS:Host "@eq 0" \
    "id:60008,\
    log,\
    msg:'Request Missing a Host Header',\
    severity:2"
```

{{% notice note %}}

The id action is required for all SecRule/SecAction directives as of v2.7.0

{{% /notice %}}

These are the reserved ranges:

- 1–99,999: reserved for local (internal) use. Use as you see fit, but do not use this range for rules that are distributed to others
- 100,000–199,999: reserved for rules published by Oracle
- 200,000–299,999: reserved for rules published Comodo
- 300,000–399,999: reserved for rules published at gotroot.com
- 400,000–419,999: unused (available for reservation)
- 420,000–429,999: reserved for ScallyWhack [1](http://projects.otaku42.de/wiki/Scally-Whack)
- 430,000–439,999: reserved for rules published by Flameeyes [2](http://www.flameeyes.eu/projects/modsec)
- 440.000-599,999: unused (available for reservation)
- 600,000-699,999: reserved for use by Akamai [3](http://www.akamai.com/html/solutions/waf.html)
- 700,000–799,999: reserved for Ivan Ristic
- 900,000–999,999: reserved for the OWASP ModSecurity Core Rule Set [4](http://www.owasp.org/index.php/Category:OWASP_ModSecurity_Core_Rule_Set_Project) project
- 1,000,000-1,009,999: reserved for rules published by Redhat Security Team
- 1,010,000-1,999,999: reserved for WAF \| Web Application Firewall and Load Balancer Security (kemptechnologies.com) [5](https://kemptechnologies.com/solutions/waf/)
- 2,000,000-2,999,999: reserved for rules from Trustwave's SpiderLabs Research team
- 3,000,000-3,999,999: reserved for use by Akamai [6](http://www.akamai.com/html/solutions/waf.html)
- 4,000,000-4,099,999 reserved: in use by AviNetworks [7](https://kb.avinetworks.com/docs/latest/vantage-web-app-firewall-beta/)
- 4,100,000-4,199,999 reserved: in use by Fastly [8](https://www.fastly.com/products/cloud-security/#products-cloud-security-web-application-firewall)
- 4,200,000-4,299,999 reserved: in use by CMS-Garden [9](https://www.cms-garden.org/en)
- 4,300,000-4,300,999 reserved: in use by Ensim.hu [10](http://ensim.hu/)
- 4,301,000-19,999,999: unused (available for reservation)
- 8,000,000-8,999,999 reserved: in use by Yandex
- 20,000,000-21,999,999: reserved for rules from Trustwave's SpiderLabs Research team
- 22,000,000-69,999,999: unused (available for reservation)
- 77,000,000-77,999,999 - reserved: in use by Imunify360 - production rules
- 88,000,000-88,999,999 - reserved: in use by Imunify360 - beta users
- 99,000,000-99,099,999 reserved for use by Microsoft <https://azure.microsoft.com/en-us/services/web-application-firewall/>
- 99,100,000-99,199,999 reserved for use by WPScan/Jetpack
- 99,200,000-99,209,999 reserved for use by SKUDONET [11](https://www.skudonet.com)

{{% notice note %}}

The id is an identifier only; it does not determine the relative order in which rules are executed. I.e. a rule with id 5001 will not be executed before rule 5002 just because the former is numerically smaller.

{{% /notice %}}

## initcol

Initializes a named persistent collection, either by loading data from storage or by creating a new collection in memory.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:** The following example initiates IP address tracking, which is best done in phase 1:

``` seclang
SecAction "id:116,phase:1,pass,nolog,initcol:ip=%{REMOTE_ADDR}"
```

Collections are loaded into memory on-demand, when the initcol action is executed. A collection will be persisted only if a change was made to it in the course of transaction processing.

libModSecurity v3 accepts only `ip`, `global` and `resource` as the collection name (SESSION and USER are initialized with setsid and setuid); any other name is a configuration error.

See the "Persistent Storage" section for further details.

## log

Indicates that a successful match of the rule needs to be logged.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecAction "id:117,phase:1,pass,log,initcol:ip=%{REMOTE_ADDR}"
```

This action will log matches to the web server's error log file (the Apache error log in v2) and the ModSecurity audit log.

## logdata

Logs a data fragment as part of the alert message.

{{< secmeta group="Non-disruptive" v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
SecRule ARGS:p "@rx <script>" "id:118,phase:2,pass,log,logdata:%{MATCHED_VAR}"
```

The logdata information appears in the error and/or audit log files. Macro expansion is performed, so you may use variable names such as %{TX.0} or %{MATCHED_VAR}. The information is properly escaped for use with logging of binary data.

## marker

Internal meta-data action created by the SecMarker directive; it carries the marker label used as a skipAfter target. It is never written by rule authors.

{{< secmeta group="Meta-data" v2="2.5.0" v3="no" >}}

In ModSecurity v2, `SecMarker LABEL` is expanded into the rule `SecRule REMOTE_ADDR "@noMatch" "t:none,pass,marker:LABEL"`, so `marker` shows up as an action in the rule set. libModSecurity v3 does not have a `marker` action: [SecMarker]({{% relref "3-reference-manual/3-2-configuration-directives#secmarker" %}}) is implemented as a dedicated marker rule, and the directive and [skipAfter]({{% relref "3-reference-manual/3-5-actions#skipafter" %}}) work the same way in both engines.

## maturity

Specifies the relative maturity level of the rule related to the length of time a rule has been public and the amount of testing it has received. The value is a string based on a numeric scale (1-9 where 9 is extensively tested and 1 is a brand new experimental rule). libModSecurity v3 rejects a non-numeric value.

{{< secmeta group="Meta-data" v2="2.7" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx \bgetparentfolder\b" \
    "id:'958016',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:htmlEntityDecode,\
    t:compressWhiteSpace,\
    t:lowercase,\
    msg:'Cross-site Scripting (XSS) Attack',\
    logdata:'% {TX.0}',\
    tag:'WEB_ATTACK/XSS',\
    tag:'WASCTC/WASC-8',\
    tag:'WASCTC/WASC-22',\
    tag:'OWASP_TOP_10/A2',\
    tag:'OWASP_AppSensor/IE1',\
    tag:'PCI/6.5.1',\
    ctl:auditLogParts=+E,\
    ver:'CRS/2.2.4',\
    accuracy:'9',\
    maturity:'9',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.xss_score=+%{tx.critical_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/XSS-%{matched_var_name}=%{tx.0}"
```

## msg

Assigns a custom message to the rule or chain in which it appears. The message will be logged along with every alert.

{{< secmeta group="Meta-data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule &REQUEST_HEADERS:Host "@eq 0" \
    "id:60008,\
    log,\
    msg:'Request Missing a Host Header',\
    severity:2"
```

{{% notice note %}}

The msg information appears in the error and/or audit log files and is not sent back to the client in response headers.

{{% /notice %}}

## multiMatch

If enabled, ModSecurity will perform multiple operator invocations for every target, before and after every anti-evasion transformation is performed.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule ARGS "@rx attack" \
    "id:119,\
    phase:1,\
    deny,\
    t:removeNulls,\
    t:lowercase,\
    log,\
    multiMatch"
```

Normally, variables are inspected only once per rule, and only after all transformation functions have been completed. With multiMatch, variables are checked against the operator before and after every transformation function that changes the input.

## noauditlog

Indicates that a successful match of the rule should not be used as criteria to determine whether the transaction should be logged to the audit log.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" "id:120,allow,noauditlog"
```

If the SecAuditEngine is set to On, all of the transactions will be logged. If it is set to RelevantOnly, then you can control the logging with the noauditlog action.

The noauditlog action affects only the current rule. If you prevent audit logging in one rule only, a match in another rule will still cause audit logging to take place. If you want to prevent audit logging from taking place, regardless of whether any rule matches, use ctl:auditEngine=Off.

## nolog

Prevents rule matches from appearing in both the error and audit logs.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" "id:121,allow,nolog"
```

Although nolog implies noauditlog, you can override the former by using nolog,auditlog.

## pass

Continues processing with the next rule in spite of a successful match.

{{< secmeta group="Disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" "id:122,pass,log"
```

When using pass with a SecRule with multiple targets, all variables will be inspected and all non-disruptive actions trigger for every match. In the following example, the TX.test variable will be incremented once for every request parameter:

``` seclang
# Set TX.test to zero
SecAction "id:123,phase:2,pass,nolog,setvar:TX.test=0"

# Increment TX.test for every request parameter
SecRule ARGS "@rx test" "id:124,phase:2,pass,log,setvar:TX.test=+1"
```

## pause

Pauses transaction processing for the specified number of milliseconds. Starting with ModSecurity 2.7 this feature also supports macro expansion.

{{< secmeta group="Disruptive" v2="yes" v3="no" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" "id:125,pause:5000,log"
```

In ModSecurity v2 pause is a disruptive action in its own right: when it is the disruptive action that takes effect, the transaction is paused and then allowed through, exactly like allow. To pause and then block, place pause before the blocking action, for example `pause:5000,deny`. Values that are not a positive integer result in no pause. libModSecurity v3 refuses the rule at configuration load (`Action: Pause is not yet supported.`).

{{% notice warning %}}

This feature can be of limited benefit for slowing down brute force authentication attacks, but use with care. If you are under a denial of service attack, the pause feature may make matters worse, as it will cause an entire Apache worker (process or thread, depending on the deployment mode) to sit idle until the pause is completed.

{{% /notice %}}

## phase

Places the rule or chain into one of five available processing phases. It can also be used in SecDefaultAction to establish the rule defaults for that phase. Internally ModSecurity v2 registers phase with the disruptive action type, which is why it is accepted only in the chain starter; it never intercepts the transaction.

{{< secmeta group="Meta-data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Initialize IP address tracking in phase 1
SecAction "id:126,phase:1,pass,nolog,initcol:IP=%{REMOTE_ADDR}"
```

libModSecurity v3 additionally accepts `phase:0`, a connection phase run when the connector calls `processConnection()`, before any request data has been read; only REMOTE_ADDR, REMOTE_HOST, REMOTE_PORT, SERVER_ADDR, SERVER_PORT and UNIQUE_ID are populated there.

Starting in ModSecurity version v2.7 (and in all libModSecurity v3 releases) there are aliases for three of the five phase numbers:

- **2 - request**
- **4 - response**
- **5 - logging**

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" "id:127,phase:2,deny,log"
```

{{% notice warning %}}

Keep in mind that if you specify the incorrect phase, the variable used in the rule may not yet be available. This could lead to a false negative situation where your variable and operator may be correct, but it misses malicious data because you specified the wrong phase.

{{% /notice %}}


## prepend

Prepends the text given as parameter to response body. Content injection must be enabled (using the SecContentInjection directive). No content type checks are made, which means that before using any of the content injection actions, you must check whether the content type of the response is adequate for injection.

{{< secmeta group="Non-disruptive" phases="3 and 4." v2="yes" v3="no" >}}

**Example:**

``` seclang
SecRule RESPONSE_CONTENT_TYPE "@rx ^text/html" \
    "id:128,\
    phase:3,\
    pass,\
    nolog,\
    prepend:'Header<br>'"
```

A rule can carry only one prepend action (a second one replaces the first), and a later matching rule that uses prepend replaces the text set by an earlier one. libModSecurity v3 refuses the rule at configuration load (`Action: Prepend is not yet supported.`).

{{% notice warning %}}

Although macro expansion is allowed in the injected content, you are strongly cautioned against inserting user defined data fields into output. Doing so would create a cross-site scripting vulnerability.

{{% /notice %}}

## proxy

Intercepts the current transaction by forwarding the request to another web server using the proxy backend. The forwarding is carried out transparently to the HTTP client (i.e., there’s no external redirection taking place).

{{< secmeta group="Disruptive" v2="yes" v3="no" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" \
    "id:129,\
    proxy:http://honeypothost/,\
    log"
SecRule REQUEST_URI "@streq /test.txt" \
    "id:500005,\
    phase:1,\
    proxy:'[nocanon]http://$ENV{SERVER_NAME}:$ENV{SERVER_PORT}/test.txt'"
```

For this action to work, mod_proxy must also be installed, and the rule must run in phase 1 or 2; in the output phases, or without mod_proxy, ModSecurity v2 responds with status 500 instead. This action is useful if you would like to proxy matching requests onto a honeypot web server, and especially in combination with IP address or session tracking. libModSecurity v3 refuses the rule at configuration load (`Action: Proxy is not yet supported.`).

{{% notice note %}}

As of v2.9.1 the proxy action can receive a special parameter named "[nocanon]". The "[nocanon]" parameter will make the url to be delivered to the backend on its original format (raw). Further information about "nocanon" is available here: <https://httpd.apache.org/docs/2.2/pt-br/mod/mod_proxy.html>.

{{% /notice %}}

## redirect

Intercepts transaction by issuing an external (client-visible) redirection to the given location..

{{< secmeta group="Disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:User-Agent "@rx Test" \
    "id:130,\
    phase:1,\
    redirect:http://www.example.com/failed.html,\
    log"
```

If the status action is present on the same rule, and its value can be used for a redirection (i.e., is one of the following: 301, 302, 303, or 307), the value will be used for the redirection status code. Otherwise, status code 302 will be used. libModSecurity v3 (since 3.0.3) keeps any status in the 301-307 range and macro-expands the location.

## rev

Specifies rule revision. It is useful in combination with the id action to provide an indication that a rule has been changed.

{{< secmeta group="Meta-data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx (?:(?:[\;\|\`]\W*?\bcc|\b(wget|curl))\b|\/cc(?:[\'\"\|\;\`\-\s]|$))" \
    "id:'950907',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:normalizePath,\
    t:lowercase,\
    msg:'System Command Injection',\
    logdata:'%{TX.0}',\
    tag:'WEB_ATTACK/COMMAND_INJECTION',\
    tag:'WASCTC/WASC-31',\
    tag:'OWASP_TOP_10/A1',\
    tag:'PCI/6.5.2',\
    ctl:auditLogParts=+E,\
    rev:'2.1.3',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.command_injection_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/COMMAND_INJECTION-%{matched_var_name}=%{tx.0},\
    skipAfter:END_COMMAND_INJECTION1"
```

{{% notice note %}}

This action is used in combination with the id action to allow the same rule ID to be used after changes take place but to still provide some indication the rule changed.

{{% /notice %}}

## sanitiseArg

Prevents sensitive request parameter data from being logged to audit log. Each byte of the named parameter(s) is replaced with an asterisk. Since 2.6.0 ModSecurity v2 also accepts the American spelling `sanitizeArg`.

{{< secmeta group="Non-disruptive" v2="yes" v3="no" >}}

**Example:**

``` seclang
# Never log passwords
SecAction \
    "id:131,\
    phase:2,\
    nolog,\
    sanitiseArg:password,\
    sanitiseArg:newPassword,\
    sanitiseArg:oldPassword"
```

libModSecurity v3 refuses the rule at configuration load (`Action: SanitiseArg is not yet supported.`).

{{% notice note %}}

The sanitize actions affect only the data as it is logged to audit log. High-level debug logs may contain sensitive data. Apache access log may contain sensitive data placed in the request URI.

{{% /notice %}}

## sanitiseMatched

Prevents the matched variable (request argument, request header, or response header) from being logged to audit log. Each byte of the named parameter(s) is replaced with an asterisk. Since 2.6.0 ModSecurity v2 also accepts the American spelling `sanitizeMatched`.

{{< secmeta group="Non-disruptive" v2="yes" v3="no" >}}

**Example:** This action can be used to sanitize arbitrary transaction elements when they match a condition. For example, the example below will sanitize any argument that contains the word password in the name.

``` seclang
SecRule ARGS_NAMES "@rx password" "id:132,pass,nolog,sanitiseMatched"
```

libModSecurity v3 refuses the rule at configuration load (`Action: SanitiseMatched is not yet supported.`).

{{% notice note %}}

The sanitize actions affect only the data as it is logged to audit log. High-level debug logs may contain sensitive data. Apache access log may contain sensitive data placed in the request URI.

{{% /notice %}}

## sanitiseMatchedBytes

Prevents the matched string in a variable from being logged to audit log. Each or a range of bytes of the named parameter(s) is replaced with an asterisk. ModSecurity v2 also accepts the American spelling `sanitizeMatchedBytes`.

{{< secmeta group="Non-disruptive" v2="2.6.0" v3="no" >}}

**Example:** This action can be used to sanitize arbitrary transaction elements when they match a condition. For example, the example below will sanitize the credit card number.

- sanitiseMatchedBytes -- This would x out only the bytes that matched.
- sanitiseMatchedBytes:1/4 -- This would x out the bytes that matched, but keep the first byte and last 4 bytes. Both numbers must be a single digit (0-9); any other parameter is ignored and the whole match is sanitized.

``` seclang
# Detect credit card numbers in parameters and
# prevent them from being logged to audit log
SecRule ARGS "@verifyCC \d{13,16}" \
    "id:133,\
    phase:2,\
    pass,\
    capture,\
    nolog,\
    msg:'Potential credit card number in request',\
    sanitiseMatchedBytes"
SecRule RESPONSE_BODY "@verifyCC \d{13,16}" \
    "id:134,\
    phase:4,\
    block,\
    capture,\
    t:none,\
    log,\
    msg:'Potential credit card number is response body',\
    sanitiseMatchedBytes:0/4"
```

libModSecurity v3 refuses the rule at configuration load (`Action: SanitiseMatchedBytes is not yet supported.`).

{{% notice note %}}

The sanitize actions affect only the data as it is logged to audit log. High-level debug logs may contain sensitive data. Apache access log may contain sensitive data placed in the request URI. You must use capture action with sanitiseMatchedBytes, so the operator must support capture action. ie: @rx, @verifyCC.

{{% /notice %}}

## sanitiseRequestHeader

Prevents a named request header from being logged to audit log. Each byte of the named request header is replaced with an asterisk. Since 2.6.0 ModSecurity v2 also accepts the American spelling `sanitizeRequestHeader`.

{{< secmeta group="Non-disruptive" v2="yes" v3="no" >}}

**Example:** This will sanitize the data in the Authorization header.

``` seclang
SecAction "id:135,phase:1,pass,nolog,sanitiseRequestHeader:Authorization"
```

libModSecurity v3 refuses the rule at configuration load (`Action: SanitiseRequestHeader is not yet supported.`).

{{% notice note %}}

The sanitize actions affect only the data as it is logged to audit log. High-level debug logs may contain sensitive data. Apache access log may contain sensitive data placed in the request URI.

{{% /notice %}}

## sanitiseResponseHeader

Prevents a named response header from being logged to audit log. Each byte of the named response header is replaced with an asterisk. Since 2.6.0 ModSecurity v2 also accepts the American spelling `sanitizeResponseHeader`.

{{< secmeta group="Non-disruptive" v2="yes" v3="no" >}}

**Example:** This will sanitize the Set-Cookie data sent to the client.

``` seclang
SecAction "id:136,phase:3,pass,nolog,sanitiseResponseHeader:Set-Cookie"
```

libModSecurity v3 refuses the rule at configuration load (`Action: SanitiseResponseHeader is not yet supported.`).

{{% notice note %}}

The sanitize actions affect only the data as it is logged to audit log. High-level debug logs may contain sensitive data. Apache access log may contain sensitive data placed in the request URI.

{{% /notice %}}

## severity

Assigns severity to the rule in which it is used.

{{< secmeta group="Meta-data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_METHOD "@rx ^PUT$" \
    "id:340002,\
    msg:'Restricted HTTP function',\
    rev:1,\
    severity:CRITICAL"
```

Severity values in ModSecurity follows the numeric scale of syslog (where 0 is the most severe). The data below is used by the OWASP ModSecurity Core Rule Set (CRS):

- **0 - EMERGENCY**: is generated from correlation of anomaly scoring data where there is an inbound attack and an outbound leakage.
- **1 - ALERT**: is generated from correlation where there is an inbound attack and an outbound application level error.
- **2 - CRITICAL**: Anomaly Score of 5. Is the highest severity level possible without correlation. It is normally generated by the web attack rules (40 level files).
- **3 - ERROR**: Error - Anomaly Score of 4. Is generated mostly from outbound leakage rules (50 level files).
- **4 - WARNING**: Anomaly Score of 3. Is generated by malicious client rules (35 level files).
- **5 - NOTICE**: Anomaly Score of 2. Is generated by the Protocol policy and anomaly files.
- **6 - INFO**
- **7 - DEBUG**

Both ModSecurity v2 (text values since 2.7.5, matched case-insensitively) and libModSecurity v3 accept either the numerical values or the text values, but you should always specify severity levels using the text values, because it is difficult to remember what a number stands for.

## setuid

Special-purpose action that initializes the USER collection using the username provided as parameter.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule ARGS:username "@rx .*" \
    "id:137,\
    phase:2,\
    pass,\
    capture,\
    t:none,\
    nolog,\
    noauditlog,\
    setuid:%{TX.0},\
    setvar:session.username=%{TX.0}"
```

After initialization takes place, the variable USERID will be available for use in the subsequent rules. This action understands application namespaces (configured using SecWebAppId), and will use one if it is configured.

## setrsc

Special-purpose action that initializes the RESOURCE collection using a key provided as parameter.

{{< secmeta group="Non-disruptive" v2="2.7.0" v3="yes" >}}

**Example:**

``` seclang
SecAction "id:3,phase:1,pass,log,setrsc:'abcd1234'"
```

This action understands application namespaces (configured using SecWebAppId), and will use one if it is configured.

## setsid

Special-purpose action that initializes the SESSION collection using the session token provided as parameter.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Initialize session variables using the session cookie value
SecRule REQUEST_COOKIES:PHPSESSID "!@rx ^$" \
    "id:138,\
    pass,\
    nolog,\
    setsid:%{REQUEST_COOKIES.PHPSESSID}"
```

Note

After the initialization takes place, the variable SESSION will be available for use in the subsequent rules. This action understands application namespaces (configured using SecWebAppId), and will use one if it is configured.

Setsid takes an individual variable, not a collection. Variables within an action, such as setsid, use the format [collection].[variable] .

## setenv

Creates, removes, and updates environment variables that can be accessed by the web server (Apache in v2; in libModSecurity v3, since 3.0.3, by both ModSecurity and the web server).

{{< secmeta group="Non-disruptive" v2="yes" v3="3.0.3" >}}

**Examples:**

``` seclang
SecRule RESPONSE_HEADERS:/Set-Cookie2?/ "@rx (?i:(j?sessionid|(php)?sessid|(asp|jserv|jw)?session[-_]?(id)?|cf(id|token)|sid))" \
    "id:139,\
    phase:3,\
    pass,\
    t:none,\
    nolog,\
    setvar:tx.sessionid=%{matched_var}"
SecRule TX:SESSIONID "!@rx (?i:\;? ?httponly;?)" \
    "id:140,\
    phase:3,\
    pass,\
    t:none,\
    log,\
    auditlog,\
    msg:'AppDefect: Missing HttpOnly Cookie Flag.',\
    setenv:httponly_cookie=%{matched_var}"

Header set Set-Cookie "%{httponly_cookie}e; HTTPOnly" env=httponly_cookie
```

{{% notice note %}}

In ModSecurity v2, when used in a chain this action will be executed when an individual rule matches and not the entire chain. In libModSecurity v3 only setvar runs independently of the chain result, so setenv on the first rule of a chain will only execute if the entire chain matches.

{{% /notice %}}

## setvar

Creates, removes, or updates a variable. Variable names are case-insensitive. libModSecurity v3 stores setvar only in the TX, IP, GLOBAL, RESOURCE, SESSION and USER collections; a setvar on any other variable is accepted by the parser but does nothing.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Examples:** To create a variable and set its value to 1 (usually used for setting flags), use: `setvar:TX.score`

To create a variable and initialize it at the same time, use: `setvar:TX.score=10`

To remove a variable, prefix the name with an exclamation mark: `setvar:!TX.score`

To increase or decrease variable value, use + and - characters in front of a numerical value: `setvar:TX.score=+5`

Example from OWASP CRS:

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx \bsys\.user_catalog\b" \
    "id:'959517',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:urlDecodeUni,\
    t:htmlEntityDecode,\
    t:lowercase,\
    t:replaceComments,\
    t:compressWhiteSpace,\
    msg:'Blind SQL Injection Attack',\
    logdata:'%{TX.0}',\
    tag:'WEB_ATTACK/SQL_INJECTION',\
    tag:'WASCTC/WASC-19',\
    tag:'OWASP_TOP_10/A1',\
    tag:'OWASP_AppSensor/CIE1',\
    tag:'PCI/6.5.2',\
    ctl:auditLogParts=+E,\
    rev:'2.1.3',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.sql_injection_score=+%{tx.critical_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/SQL_INJECTION-%{matched_var_name}=%{tx.0}"
```

{{% notice note %}}

When used in a chain this action will be executed when an individual rule matches and not the entire chain. This means that

{{% /notice %}}

``` seclang
SecRule REQUEST_FILENAME "@contains /test.php" \
    "id:7,\
    phase:1,\
    t:none,\
    nolog,\
    setvar:tx.auth_attempt=+1,\
    chain"
    SecRule ARGS_POST:action "@streq login" "t:none"
```

- **will increment every time that test.php is visited (regardless of the parameters submitted). If the desired goal is to set the variable only if the entire rule matches, it should be included in the last rule of the chain . For instance**:

``` seclang
SecRule REQUEST_FILENAME "@streq test.php" "id:7,phase:1,t:none,nolog,chain"
    SecRule ARGS_POST:action "@streq login" "t:none,setvar:tx.auth_attempt=+1"
```

## skip

Skips one or more rules (or chains) on successful match. Internally ModSecurity v2 registers skip with the disruptive action type (chain starter only, not allowed in SecDefaultAction), although it never intercepts the transaction; a value below 1 is treated as 1.

{{< secmeta group="Flow" v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Require Accept header, but not from access from the localhost
SecRule REMOTE_ADDR "@rx ^127\.0\.0\.1$" "id:141,phase:1,skip:1"

# This rule will be skipped over when REMOTE_ADDR is 127.0.0.1
SecRule &REQUEST_HEADERS:Accept "@eq 0" \
    "id:142,\
    phase:1,\
    deny,\
    msg:'Request Missing an Accept Header'"
```

The skip action works only within the current processing phase and not necessarily in the order in which the rules appear in the configuration file. If you place a phase 2 rule after a phase 1 rule that uses skip, it will not skip over the phase 2 rule. It will skip over the next phase 1 rule that follows it in the phase.

In libModSecurity v3 `skip:0` skips nothing, and the counter is not reset at the end of a phase: a count larger than the number of rules left in the phase carries over and skips the first rules of the next phase.

## skipAfter

{{< secmeta group="Flow" v2="2.5.0" v3="yes" >}}

Description: Skips one or more rules (or chains) on a successful match, resuming rule execution with the first rule that follows the rule (or marker created by SecMarker) with the provided ID. Internally ModSecurity v2 registers skipAfter with the disruptive action type (chain starter only, not allowed in SecDefaultAction), although it never intercepts the transaction.

**Example:** The following rules implement the same logic as the skip example, but using skipAfter:

``` seclang
# Require Accept header, but not from access from the localhost
SecRule REMOTE_ADDR "@rx ^127\.0\.0\.1$" \
    "id:143,\
    phase:1,\
    skipAfter:IGNORE_LOCALHOST"

# This rule will be skipped over when REMOTE_ADDR is 127.0.0.1
SecRule &REQUEST_HEADERS:Accept "@eq 0" \
    "id:144,\
    phase:1,\
    deny,\
    msg:'Request Missing an Accept Header'"
SecMarker IGNORE_LOCALHOST
```

Example from the OWASP ModSecurity CRS:

``` seclang
SecMarker BEGIN_HOST_CHECK

SecRule &REQUEST_HEADERS:Host "@eq 0" \
    "id:'960008',\
    phase:2,\
    block,\
    t:none,\
    msg:'Request Missing a Host Header',\
    tag:'PROTOCOL_VIOLATION/MISSING_HEADER_HOST',\
    tag:'WASCTC/WASC-21',\
    tag:'OWASP_TOP_10/A7',\
    tag:'PCI/6.5.10',\
    rev:'2.1.3',\
    severity:'5',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.anomaly_score=+%{tx.notice_anomaly_score},\
    setvar:tx.protocol_violation_score=+%{tx.notice_anomaly_score},\
    setvar:tx.%{rule.id}-PROTOCOL_VIOLATION/MISSING_HEADER-%{matched_var_name}=%{matched_var},\
    skipAfter:END_HOST_CHECK"

SecRule REQUEST_HEADERS:Host "@rx ^$" \
    "id:'960008',\
    phase:2,\
    block,\
    t:none,\
    msg:'Request Missing a Host Header',\
    tag:'PROTOCOL_VIOLATION/MISSING_HEADER_HOST',\
    tag:'WASCTC/WASC-21',\
    tag:'OWASP_TOP_10/A7',\
    tag:'PCI/6.5.10',\
    rev:'2.1.3',\
    severity:'5',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.anomaly_score=+%{tx.notice_anomaly_score},\
    setvar:tx.protocol_violation_score=+%{tx.notice_anomaly_score},\
    setvar:tx.%{rule.id}-PROTOCOL_VIOLATION/MISSING_HEADER-%{matched_var_name}=%{matched_var}"

SecMarker END_HOST_CHECK
```

The skipAfter action works only within the current processing phase and not necessarily the order in which the rules appear in the configuration file. If you place a phase 2 rule after a phase 1 rule that uses skipAfter, it will not skip over the phase 2 rule. It will skip over the next phase 1 rule that follows it in the phase.

libModSecurity v3 places every SecMarker in all phases and does not clear an active skipAfter at the end of a phase: if the marker is not reached in the current phase, the rules of the following phases are also skipped until it is.

## status

Specifies the response status code to use with actions deny and redirect. ModSecurity v2 registers status as a disruptive-type action (chain starter only) although it only stores the code; the default is 403.

{{< secmeta group="Data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Deny with status 403
SecDefaultAction "id:145,phase:1,deny,status:403,log"
```

Status actions defined in Apache scope locations (such as Directory, Location, etc...) may be superseded by phase:1 action settings. The Apache ErrorDocument directive will be triggered if present in the configuration. Therefore if you have previously defined a custom error page for a given status then it will be executed and its output presented to the user.

## t

This action is used to specify the transformation pipeline to use to transform the value of each variable used in the rule before matching.

{{< secmeta group="Non-disruptive" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule ARGS "@rx (asfunction|javascript|vbscript|data|mocha|livescript):" \
    "id:146,\
    t:none,\
    t:htmlEntityDecode,\
    t:lowercase,\
    t:removeNulls,\
    t:removeWhitespace"
```

Any transformation functions that you specify in a SecRule will be added to the previous ones specified in SecDefaultAction. It is recommended that you always use t:none in your rules, which prevents them depending on the default configuration. In ModSecurity v2 `t:-name` removes a previously added transformation from the pipeline; t is the only action that accepts the +/- prefix.

## tag

Assigns a tag (category) to a rule or a chain.

{{< secmeta group="Meta-data" v2="2.1.0" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx \bgetparentfolder\b" \
    "id:'958016',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:htmlEntityDecode,\
    t:compressWhiteSpace,\
    t:lowercase,\
    msg:'Cross-site Scripting (XSS) Attack',\
    logdata:'% {TX.0}',\
    tag:'WEB_ATTACK/XSS',\
    tag:'WASCTC/WASC-8',\
    tag:'WASCTC/WASC-22',\
    tag:'OWASP_TOP_10/A2',\
    tag:'OWASP_AppSensor/IE1',\
    tag:'PCI/6.5.1',\
    ctl:auditLogParts=+E,\
    rev:'2.1.3',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.xss_score=+%{tx.critical_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/XSS-%{matched_var_name}=%{tx.0}"
```

The tag information appears along with other rule metadata. The purpose of the tagging mechanism to allow easy automated categorization of events. Multiple tags can be specified on the same rule. Use forward slashes to create a hierarchy of categories (as in the example). Since ModSecurity 2.6.0 (and in all libModSecurity v3 releases) tag supports macro expansion.

## ver

Specifies the rule set version. libModSecurity v3 requires the value to be single-quoted (`ver:'CRS/2.2.4'`); the unquoted form is a parse error.

{{< secmeta group="Meta-data" v2="2.7" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* "@rx \bgetparentfolder\b" \
    "id:'958016',\
    phase:2,\
    block,\
    capture,\
    t:none,\
    t:htmlEntityDecode,\
    t:compressWhiteSpace,\
    t:lowercase,\
    msg:'Cross-site Scripting (XSS) Attack',\
    logdata:'% {TX.0}',\
    tag:'WEB_ATTACK/XSS',\
    tag:'WASCTC/WASC-8',\
    tag:'WASCTC/WASC-22',\
    tag:'OWASP_TOP_10/A2',\
    tag:'OWASP_AppSensor/IE1',\
    tag:'PCI/6.5.1',\
    ctl:auditLogParts=+E,\
    ver:'CRS/2.2.4',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.xss_score=+%{tx.critical_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},\
    setvar:tx.%{rule.id}-WEB_ATTACK/XSS-%{matched_var_name}=%{tx.0}"
```

## xmlns

Configures an XML namespace, which will be used in the execution of XPath expressions. The parameter has the form `prefix=uri`; several xmlns actions may be given on one rule. libModSecurity v3 requires the URI to start with `http://` and to be unquoted or single-quoted (`xmlns:soap='http://...'`).

{{< secmeta group="Data" v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REQUEST_HEADERS:Content-Type "@rx text/xml" \
    "id:147,\
    phase:1,\
    pass,\
    ctl:requestBodyProcessor=XML,\
    ctl:requestBodyAccess=On,\
    xmlns:xsd=" http://www.w3.org/2001/XMLSchema"
SecRule XML:/soap:Envelope/soap:Body/q1:getInput/id() "@rx 123" \
    "id:148,\
    phase:2,\
    deny"
```
