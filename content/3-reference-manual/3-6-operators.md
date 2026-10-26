---
title: Operators
weight: 6
---

This section documents the operators currently available in ModSecurity.

ModSecurity v2 and libModSecurity v3 both look operator names up case-insensitively (`@ipmatch`, `@ipMatch` and `@IPMATCH` all resolve to the same operator); the spellings below are the documented ones.

## beginsWith

Returns true if the parameter string is found at the beginning of the input. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect request line that does not begin with "GET"
SecRule REQUEST_LINE "!@beginsWith GET" "id:149"
```

## contains

Returns true if the parameter string is found anywhere in the input. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect ".php" anywhere in the request line
SecRule REQUEST_LINE "@contains .php" "id:150"
```

## containsWord

Returns true if the parameter string (with word boundaries) is found anywhere in the input. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect "select" anywhere in ARGS
SecRule ARGS "@containsWord select" "id:151"
```

Would match on -\
-1 union **select** BENCHMARK(2142500,MD5(CHAR(115,113,108,109,97,112))) FROM wp_users WHERE ID=1 and (ascii(substr(user_login,1,1))&0x01=0) from wp_users where ID=1--

But not on -\
Your site has a wide **select**ion of computers.

## detectSQLi

Returns true if SQL injection payload is found. This operator uses LibInjection to detect SQLi attacks. ModSecurity v2 bundles libinjection 4 since 2.9.13. libModSecurity v3 bundles libinjection 4 (updated to v4.0.0 in 3.0.15); since 3.0.15 a libinjection parser error counts as a match, and with `capture` the libinjection fingerprint is stored in TX:0.

{{< secmeta v2="2.7.4" v3="yes" >}}

**Example:**

``` seclang
# Detect SQL Injection inside request uri data"
SecRule REQUEST_URI "@detectSQLi" "id:152"
```

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## detectXSS

Returns true if XSS injection is found. This operator uses LibInjection to detect XSS attacks. ModSecurity v2 bundles libinjection 4 since 2.9.13. libModSecurity v3 bundles libinjection 4 (updated to v4.0.0 in 3.0.15); since 3.0.15 a libinjection parser error counts as a match, and with `capture` the matched input is stored in TX:0.

{{< secmeta v2="2.8.0" v3="yes" >}}

**Example:**

``` seclang
# Detect XSS Injection inside request body
SecRule REQUEST_BODY "@detectXSS" "id:12345,deny,log"
```

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## endsWith

Returns true if the parameter string is found at the end of the input. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect request line that does not end with "HTTP/1.1"
SecRule REQUEST_LINE "!@endsWith HTTP/1.1" "id:152"
```

## eq

Performs numerical comparison and returns true if the input value is equal to the provided parameter. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect exactly 15 request headers
SecRule &REQUEST_HEADERS_NAMES "@eq 15" "id:153"
```

{{% notice note %}}

If a value is provided that cannot be converted to an integer (i.e a string) this operator will treat that value as 0.

{{% /notice %}}

## fuzzyHash

The fuzzyHash operator uses the ssdeep, which is a program for computing context triggered piecewise hashes (CTPH). Also called fuzzy hashes, CTPH can match inputs that have homologies. Such inputs have sequences of identical bytes in the same order, although bytes in between these sequences may be different in both content and length.

{{< secmeta v2="2.9.0" v3="yes" >}}

The operator takes two parameters: the path of a file containing one ssdeep hash per line (a relative path is resolved against the directory of the configuration file) and a similarity threshold between 1 and 100; the operator matches when any hash scores at least the threshold. ModSecurity v2 must be built with ssdeep support, otherwise the operator fails at run time. libModSecurity v3 must be built with ssdeep support, otherwise the rule is rejected at configuration load; v3 does not check that the threshold lies between 1 and 100 and does not skip comment lines in the hash file.

For further information on ssdeep, visit its site: <http://ssdeep.sourceforge.net/>

**Example:**

``` seclang
SecRule REQUEST_BODY "@rx \@fuzzyHash /path/to/ssdeep/hashes.txt 6" \
    "id:192372,\
    deny,\
    log"
```

## ge

Performs numerical comparison and returns true if the input value is greater than or equal to the provided parameter. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect 15 or more request headers
SecRule &REQUEST_HEADERS_NAMES "@ge 15" "id:154"
```

{{% notice note %}}

If a value is provided that cannot be converted to an integer (i.e a string) this operator will treat that value as 0.

{{% /notice %}}

## geoLookup

Performs a geolocation lookup using the IP address in input against the geolocation database previously configured using SecGeoLookupDb. If the lookup is successful, the obtained information is captured in the GEO collection. ModSecurity v2 reads the legacy MaxMind GeoIP binary format (GeoIP/GeoLiteCity `.dat`) with its own parser. libModSecurity v3 reads the MaxMind DB format (GeoIP2/GeoLite2 `.mmdb`) through libmaxminddb (since 3.0.1), or the legacy `.dat` format through libGeoIP, depending on which library it was built with. With libmaxminddb v3 fills GEO:COUNTRY_CODE, COUNTRY_NAME, COUNTRY_CONTINENT (the continent name), CITY, POSTAL_CODE, LATITUDE and LONGITUDE; COUNTRY_CODE3, REGION, DMA_CODE and AREA_CODE are only filled by the libGeoIP build. A v3 build with neither library rejects any rule using @geoLookup at configuration load, and a lookup without a configured database does not match.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:** The geoLookup operator matches on success and is thus best used in combination with nolog,pass. If you wish to block on a failed lookup (which may be over the top, depending on how accurate the geolocation database is), the following example demonstrates how best to do it:

``` seclang
# Configure geolocation database
SecGeoLookupDb /path/to/GeoLiteCity.dat
...
# Lookup IP address
SecRule REMOTE_ADDR "@geoLookup" "id:155,phase:1,pass,nolog"

# Block IP address for which geolocation failed
SecRule &GEO "@eq 0" "id:156,phase:1,deny,msg:'Failed to lookup IP'"
```

See the GEO variable for an example and more information on various fields available.

## gsbLookup

Performs a local lookup of Google's Safe Browsing using URLs in input against the GSB database previously configured using SecGsbLookupDb. When combined with capture operator it will save the matched url into tx.0 variable.

{{< secmeta syntax=`SecRule TARGET "@gsbLookup REGEX" ACTIONS` v2="2.6.0" v3="no" v3note="(the parser rejects the rule with *Operator: GsbLookup is not yet supported*)" >}}

**Example:** The gsbLookup operator matches on success and is thus best used in combination with a block or redirect action. If you wish to block on successful lookups, the following example demonstrates how best to do it:

``` seclang
# Configure Google Safe Browsing database
SecGsbLookupDb /path/to/GsbMalware.dat
...
# Check response bodies for malicious links
SecRule RESPONSE_BODY "@gsbLookup =\"https?\:\/\/(.*?)\"" \
    "id:157,\
    phase:4,\
    block,\
    capture,\
    log,\
    msg:'Bad url detected in RESPONSE_BODY (Google Safe Browsing Check)',\
    logdata:'http://www.google.com/safebrowsing/diagnostic?site=%{tx.0}'"
```

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## gt

Performs numerical comparison and returns true if the input value is greater than the operator parameter. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect more than 15 headers in a request
SecRule &REQUEST_HEADERS_NAMES "@gt 15" "id:158"
```

{{% notice note %}}

If a value is provided that cannot be converted to an integer (i.e a string) this operator will treat that value as 0.

{{% /notice %}}

## inspectFile

Executes an external program for every variable in the target list. The contents of the variable is provided to the script as the first parameter on the command line. The program must be specified as the first parameter to the operator. As of version 2.5.0, if the supplied program filename is not absolute, it is treated as relative to the directory in which the configuration file resides. Also as of version 2.5.0, if the filename is determined to be a Lua script (based on its .lua extension), the script will be processed by the internal Lua engine. Internally processed scripts will often run faster (there is no process creation overhead) and have full access to the transaction context of ModSecurity. libModSecurity v3 behaves the same way: a relative path is tried against the current working directory and then the configuration file directory, and `.lua` scripts are run by the built-in Lua engine when v3 was built with Lua support (since 3.0.4 the Lua script receives the `FILES_TMPNAMES` value as its argument, as in v2); without Lua support a `.lua` file is executed as an external program.

{{< secmeta v2="yes" v3="yes" >}}

The @inspectFile operator was initially designed for file inspection (hence the name), but it can also be used in any situation that requires decision making using external logic.

An external program must print one line: output starting with `1` means the file is accepted (no match), anything else is treated as a rejection and the operator matches (the output is logged as the reason). A Lua script matches when its `main` function returns a string and does not match when it returns `nil`. In libModSecurity v3 the program must exit with status 0 and print at least two characters for a match to be possible, the output is not logged, and a Lua script matches only when `main` returns a non-empty string.

The OWASP CRS includes a utility script in the /util directory called runav.pl ([util/av-scanning/runav.pl](https://github.com/coreruleset/coreruleset/blob/v3.3/master/util/av-scanning/runav.pl) in CRS 3.3; CRS 4 no longer ships it) that allows the file approval mechanism to integrate with the ClamAV virus scanner. This is especially handy to prevent viruses and exploits from entering the web server through file upload.

``` perl
#!/usr/bin/perl
#
# runav.pl
# Copyright (c) 2004-2011 Trustwave
#
# This script is an interface between ModSecurity and its
# ability to intercept files being uploaded through the
# web server, and ClamAV

$CLAMSCAN = "clamscan";

if ($#ARGV != 0) {
    print "Usage: runav.pl <filename>\n";
    exit;
}

my ($FILE) = shift @ARGV;

$cmd = "$CLAMSCAN --stdout --no-summary $FILE";
$input = `$cmd`;
$input =~ m/^(.+)/;
$error_message = $1;

$output = "0 Unable to parse clamscan output [$1]";

if ($error_message =~ m/: Empty file\.?$/) {
    $output = "1 empty file";
}
elsif ($error_message =~ m/: (.+) ERROR$/) {
    $output = "0 clamscan: $1";
}
elsif ($error_message =~ m/: (.+) FOUND$/) {
    $output = "0 clamscan: $1";
}
elsif ($error_message =~ m/: OK$/) {
    $output = "1 clamscan: OK";
}

print "$output\n";
```

**Example:** Using the runav.pl script:

``` seclang
# Execute external program to validate uploaded files
SecRule FILES_TMPNAMES "@inspectFile /path/to/util/runav.pl" "id:159"
```

Example of using Lua script (placed in the same directory as the configuration file):

``` seclang
SecRule FILES_TMPNAMES "@inspectFile inspect.lua" "id:160"
```

The contents of inspect.lua:

``` lua
function main(filename)
    -- Do something to the file to verify it. In this example, we
    -- read up to 10 characters from the beginning of the file.
    local f = io.open(filename, "rb");
    local d = f:read(10);
    f:close();
   
    -- Return null if there is no reason to believe there is anything
    -- wrong with the file (no match). Returning any text will be taken
    -- to mean a match should be triggered.
    return null;
end
```

{{% notice note %}}

Starting in version 2.9 ModSecurity will not fill the FILES_TMPNAMES variable unless SecTmpSaveUploadedFiles directive is On, or the SecUploadKeepFiles directive is set to RelevantOnly. libModSecurity v3 fills FILES_TMPNAMES when SecTmpSaveUploadedFiles or SecUploadKeepFiles is On (the v3 parser rejects SecUploadKeepFiles RelevantOnly).

{{% /notice %}}

{{% notice note %}}

Use @inspectFile with caution. It may not be safe to use @inspectFile with variables other than FILES_TMPNAMES. Other variables such as "FULL_REQUEST" may contains content that force your platform to fork process out of your control, making possible to an attacker to execute code using the same permissions of your web server. For other variables you may want to look at the Lua script engine. This observation was brought to our attention by "Gryzli", on our users mailing list.

{{% /notice %}}

**Reference:** <https://web.archive.org/web/20121227063516/http://blog.spiderlabs.com:80/2010/10/advanced-topic-of-the-week-preventing-malicious-pdf-file-uploads.html>

**Reference:** <http://sourceforge.net/p/mod-security/mailman/mod-security-users/?viewmonth=201512>

## ipMatch

Performs a fast ipv4 or ipv6 match of REMOTE_ADDR variable data. Can handle the following formats:

{{< secmeta v2="2.6.0" v3="yes" >}}

- Full IPv4 Address - 192.168.1.100
- Network Block/CIDR Address - 192.168.1.0/24
- Full IPv6 Address - 2001:db8:85a3:8d3:1319:8a2e:370:7348
- Network Block/CIDR Address - 2001:db8:85a3:8d3:1319:8a2e:370:0/24

**Examples:**

Individual Address:

``` seclang
SecRule REMOTE_ADDR "@ipMatch 192.168.1.100" "id:161"
```

Multiple Addresses w/network block:

``` seclang
SecRule REMOTE_ADDR "@ipMatch 192.168.1.100,192.168.1.50,10.10.50.0/24" "id:162"
```

## ipMatchF

{{< secmeta v2="2.7.0" v3="yes" >}}

short alias for ipMatchFromFile

## ipMatchFromFile

Performs a fast ipv4 or ipv6 match of REMOTE_ADDR variable, loading data from a file. Can handle the following formats:

{{< secmeta v2="2.7.0" v3="yes" >}}

- Full IPv4 Address - 192.168.1.100
- Network Block/CIDR Address - 192.168.1.0/24
- Full IPv6 Address - 2001:db8:85a3:8d3:1319:8a2e:370:7348
- Network Block/CIDR Address - 2001:db8:85a3:8d3:1319:8a2e:370:0/24

**Examples:**

``` seclang
SecRule REMOTE_ADDR "@ipMatchFromFile ips.txt" "id:163"
```

The file ips.txt may contain:

``` text
192.168.0.1
172.16.0.0/16
10.0.0.0/8
```

{{% notice note %}}

As of v2.9.0-RC1 this operator also supports to load content served by an HTTPS server (`https://` URL instead of a path). libModSecurity v3 supports this in all releases when built with libcurl.

{{% /notice %}}

{{% notice note %}}

When used with content served by a HTTPS server, the directive SecRemoteRulesFailAction can be used to configure a warning instead of an abort, when the remote content could not be retrieved. This applies to ModSecurity v2 only: in libModSecurity v3 a failed download rejects the rule at configuration load regardless of SecRemoteRulesFailAction.

{{% /notice %}}

{{% notice note %}}

Empty lines are ignored. Comment lines (beginning with the # character) are ignored by ModSecurity v2 and by libModSecurity v3 since 3.0.9; v3 also strips a trailing `#` comment from a line, and tries a relative file name against the current working directory before the directory of the rules file.

{{% /notice %}}

## le

Performs numerical comparison and returns true if the input value is less than or equal to the operator parameter. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="yes" v3="yes" >}}

**Example**:

``` seclang
# Detect 15 or fewer headers in a request
SecRule &REQUEST_HEADERS_NAMES "@le 15" "id:164"
```

{{% notice note %}}

If a value is provided that cannot be converted to an integer (i.e a string) this operator will treat that value as 0.

{{% /notice %}}

## lt

Performs numerical comparison and returns true if the input value is less than to the operator parameter. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect fewer than 15 headers in a request
SecRule &REQUEST_HEADERS_NAMES "@lt 15" "id:165"
```

{{% notice note %}}

If a value is provided that cannot be converted to an integer (i.e a string) this operator will treat that value as 0.

{{% /notice %}}

## noMatch

Will force the rule to always return false.

{{< secmeta v2="yes" v3="yes" >}}

## pm

Performs a case-insensitive match of the provided phrases against the desired input value. The operator uses a set-based matching algorithm (Aho-Corasick), which means that it will match any number of keywords in parallel. When matching of a large number of keywords is needed, this operator performs much better than a regular expression.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect suspicious client by looking at the user agent identification
SecRule REQUEST_HEADERS:User-Agent "@pm WebZIP WebCopier Webster WebStripper ... SiteSnagger ProWebWalker CheeseBot" \
    "id:166"
```

{{% notice note %}}

Starting on ModSecurity v2.6.0 this operator supports a snort/suricata content style. ie: "@pm A\|42\|C\|44\|F".

{{% /notice %}}

{{% notice note %}}

This operator does not support macro expansion (as of ModSecurity v2.9.1; neither does libModSecurity v3).

{{% /notice %}}

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## pmf

{{< secmeta v2="yes" v3="yes" >}}

Short alias for pmFromFile.

## pmFromFile

Performs a case-insensitive match of the provided phrases against the desired input value. The operator uses a set-based matching algorithm (Aho-Corasick), which means that it will match any number of keywords in parallel. When matching of a large number of keywords is needed, this operator performs much better than a regular expression.

{{< secmeta v2="2.5.0" v3="yes" >}}

This operator is the same as @pm, except that it takes a list of files as arguments. It will match any one of the phrases listed in the file(s) anywhere in the target value.

**Example:**

``` seclang
# Detect suspicious user agents using the keywords in
# the files /path/to/blacklist1 and blacklist2 (the latter
# must be placed in the same folder as the configuration file)
SecRule REQUEST_HEADERS:User-Agent "@pmFromFile /path/to/blacklist1 blacklist2" \
    "id:167"
```

Notes:

1.  Files must contain exactly one phrase per line. End of line markers (both LF and CRLF) will be stripped from each phrase and any whitespace trimmed from both the beginning and the end. Empty lines and comment lines (those beginning with the # character) will be ignored.
2.  To allow easier inclusion of phrase files with rule sets, relative paths may be used to the phrase files. In this case, the path of the file containing the rule is prepended to the phrase file path.
3.  The @pm operator phrases do not support metacharacters.
4.  Because this operator does not check for boundaries when matching, false positives are possible in some cases. For example, if you want to use @pm for IP address matching, the phrase 1.2.3.4 will potentially match more than one IP address (e.g., it will also match 1.2.3.40 or 1.2.3.41). To avoid the false positives, you can use your own boundaries in phrases. For example, use /1.2.3.4/ instead of just 1.2.3.4. Then, in your rules, also add the boundaries where appropriate. You will find a complete example in the example.

``` seclang
# Prepare custom REMOTE_ADDR variable
SecAction "id:168,phase:1,pass,nolog,setvar:tx.REMOTE_ADDR=/%{REMOTE_ADDR}/"

# Check if REMOTE_ADDR is blacklisted
SecRule TX:REMOTE_ADDR "@pmFromFile blacklist.txt" \
    "id:169,\
    phase:1,\
    deny,\
    msg:'Blacklisted IP address'"
```

The file blacklist.txt may contain:

``` text
# ip-blacklist.txt contents:
# NOTE: All IPs must be prefixed/suffixed with "/" as the rules
#   will add in this character as a boundary to ensure
#   the entire IP is matched.
# SecAction "phase:1,id:170,pass,nolog,setvar:tx.remote_addr='/%{REMOTE_ADDR}/'"
/1.2.3.4/ 
/5.6.7.8/
```

{{% notice warning %}}

Before ModSecurity 2.5.12, the @pmFromFile operator understood only the LF line endings and did not trim the whitespace from phrases. If you are using an older version of ModSecurity, you should take care when editing the phrase files to avoid using the undesired characters in patterns.e files should be one phrase per line. End of line markers will be stripped from the phrases (LF and CRLF), and whitespace is trimmed from both sides of the phrases. Empty lines and comment lines (beginning with a '#') are ignored. To allow easier inclusion of phrase files with rulesets, relative paths may be used to the phrase files. In this case, the path of the file containing the rule is prepended to the phrase file path.

{{% /notice %}}

{{% notice note %}}

Starting on ModSecurity v2.6.0 this operator supports a snort/suricata content style. ie: "A\|42\|C\|44\|F".

{{% /notice %}}

{{% notice note %}}

As of v2.9.0-RC1 this operator also supports to load content served by an HTTPS server. However, only one url can be used at a time.

{{% /notice %}}

{{% notice note %}}

libModSecurity v3 differences: phrases are read verbatim (no whitespace trimming, so a CRLF file leaves a trailing carriage return in every phrase), the `|hex|` notation is not interpreted inside phrase files, a relative file name is tried against the current working directory before the rules file directory, every argument may be an `https://` URL (libcurl build), and a file or URL that cannot be read rejects the rule at configuration load regardless of SecRemoteRulesFailAction. Empty lines and `#` comment lines are skipped since 3.0.4.

{{% /notice %}}

## rbl

Looks up the input value in the RBL (real-time block list) given as parameter. The input value can be an IPv4 address or a hostname; IPv6 addresses are not supported.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REMOTE_ADDR "@rbl sbl-xbl.spamhaus.org" \
    "id:171,\
    phase:1,\
    pass,\
    t:none,\
    nolog,\
    auditlog,\
    msg:'RBL Match for SPAM Source',\
    tag:'AUTOMATION/MALICIOUS',\
    severity:'2',\
    setvar:'tx.msg=%{rule.msg}',\
    setvar:tx.automation_score=+%{tx.warning_anomaly_score},\
    setvar:tx.anomaly_score=+%{tx.warning_anomaly_score},\
    setvar:tx.%{rule.id}-AUTOMATION/MALICIOUS-%{matched_var_name}=%{matched_var},\
    setvar:ip.spammer=1,\
    setvar:ip.previous_rbl_check=1,\
    expirevar:ip.spammer=86400,\
    expirevar:ip.previous_rbl_check=86400,\
    skipAfter:END_RBL_CHECK"
```

{{% notice note %}}

If the RBL used is dnsbl.httpbl.org (Honeypot Project RBL) then the SecHttpBlKey directive must specify the user's registered API key.

{{% /notice %}}

{{% notice note %}}

If the RBL used is either multi.uribl.com or zen.spamhaus.org combined RBLs, it is possible to also parse the return codes in the last octet of the DNS response to identify which specific RBL the IP was found in. libModSecurity v3 recognizes the provider by the substrings `httpbl.org`, `uribl.com` and `spamhaus.org` in the parameter and writes the decoded reason to the debug log only.

{{% /notice %}}

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## rsub

Performs regular expression data substitution when applied to either the STREAM_INPUT_BODY or STREAM_OUTPUT_BODY variables. This operator also supports macro expansion. Starting with ModSecurity 2.7.0 this operator supports the syntax \|hex\| allowing users to use special chars like \n \r

{{< secmeta syntax="@rsub s/regex/str/[id]" v2="2.6.0" v3="no" v3note="(the parser rejects the rule with *Operator: Rsub is not yet supported*; the `STREAM_*` variables do not exist in v3 either)" >}}

**Examples:** Removing HTML Comments from response bodies:

``` seclang
SecStreamOutBodyInspection On
SecRule STREAM_OUTPUT_BODY "@rsub s/<!--.*?-->/ /" \
    "id:172,\
    phase:4,\
    pass,\
    t:none,\
    nolog"
```

{{% notice note %}}

If you plan to manipulate live data by using @rsub with the STREAM_ variables, you must also enable SecContentInjection directive.

{{% /notice %}}

Unlike @rx, the regular expression is compiled through Apache's `ap_regex` API as a POSIX extended regular expression (no DOTALL or DOLLAR_ENDONLY settings). The optional flags after the last delimiter are `i` (case-insensitive match) and `d` (escape the regex metacharacters of the expanded macros when the pattern contains `%{...}`); any other flag is an error. The replacement string may reference the subexpressions of the match with `\1` to `\9`. Patterns containing macros are expanded and compiled on every evaluation.

## rx

Performs a regular expression match of the pattern provided as parameter. **This is the default operator; the rules that do not explicitly specify an operator default to @rx**. ModSecurity v2 builds against PCRE2 by default since 2.9.9 (PCRE2 is supported since 2.9.7; PCRE is used only when `--with-pcre` is given at build time); libModSecurity v3 uses PCRE2 (since 3.0.7, with PCRE only when explicitly requested at build time).

{{< secmeta v2="yes" v3="yes" >}}

**Examples:**

``` seclang
# Detect Nikto
SecRule REQUEST_HEADERS:User-Agent "@rx nikto" "id:173,phase:1,t:lowercase"

# Detect Nikto with a case-insensitive pattern
SecRule REQUEST_HEADERS:User-Agent "@rx (?i)nikto" "id:174,phase:1,t:none"

# Detect Nikto with a case-insensitive pattern
SecRule REQUEST_HEADERS:User-Agent "@rx (?i)nikto" "id:175"
```

Regular expressions are handled by the PCRE library [1](http://www.pcre.org). ModSecurity compiles its regular expressions with the following settings:

1.  The entire input is treated as a single line, even when there are newline characters present.
2.  All matches are case-sensitive. If you wish to perform case-insensitive matching, you can either use the lowercase transformation function or force case-insensitive matching by prefixing the regular expression pattern with the (?i) modifier (a PCRE feature; you will find many similar features in the PCRE documentation).
3.  The PCRE_DOTALL and PCRE_DOLLAR_ENDONLY flags are set during compilation, meaning that a single dot will match any character, including the newlines, and a \$ end anchor will not match a trailing newline character.

Regular expressions are a very powerful tool. You are strongly advised to read the PCRE documentation to get acquainted with its features.

Macro expansion is supported since ModSecurity 2.6.2: a pattern containing `%{...}` is expanded and compiled on every evaluation instead of once at startup.

If the expanded pattern is not a valid regular expression, or a PCRE limit is exceeded, neither @rx nor !@rx matches. The error is visible through the TX:MSC_PCRE_ERROR or TX:MSC_PCRE_LIMITS_EXCEEDED flag. Before 2.9.16, v2 did not set TX:MSC_PCRE_ERROR, and a negated !@rx matched on these errors.

{{% notice note %}}

libModSecurity v3 compiles patterns with PCRE2_DOTALL and PCRE2_MULTILINE instead, so `^` and `$` also match at inner line boundaries. Rules that need line anchors should write `(?m)` explicitly to behave the same in both versions. In v3 a pattern that is invalid at load time rejects the rule, a pattern that becomes invalid after macro expansion does not match and sets MSC_PCRE_ERROR, and an empty pattern matches everything. SecPcreMatchLimit is honored since 3.0.10: when the limit is exceeded the operator does not match and MSC_PCRE_LIMITS_EXCEEDED and TX:MSC_PCRE_LIMITS_EXCEEDED are set to 1.

{{% /notice %}}

{{% notice note %}}

This operator supports the "capture" action. ModSecurity v2 stores the whole match in TX:0 and up to nine subexpressions in TX:1 to TX:9; further subexpressions are not captured. libModSecurity v3 stores every subexpression of the pattern.

{{% /notice %}}

## rxGlobal

Performs a global regular expression match of the pattern provided as parameter. This emulates standard regular expression '/g' functionality, which means that, after a regular expression has been fully matched in a string, the operator will continue searching the string for additional matches of the pattern. This global matching is only useful if the additional captures are desired.

{{< secmeta v2="no" v3="3.0.5" >}}

**Example:**

``` seclang
# From a query argument 'aaa12bbb45ccc', both '12' and '45' will be returned as captures
SecRule ARGS_GET "@rxGlobal [0-9]+" "id:174,phase:1,capture"
```

This operator is more expensive than @rx. Users are advised to use @rxGlobal only when the full captures are needed and prefer @rx in other cases. @rxGlobal exists only in libModSecurity v3 (added in 3.0.5); ModSecurity v2 has no equivalent.

## streq

Performs a string comparison and returns true if the parameter string is identical to the input string. Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect request parameters "foo" that do not # contain "bar", exactly.
SecRule ARGS:foo "!@streq bar" "id:176"
```

## strmatch

Performs a string match of the provided word against the desired input value. In ModSecurity v2 the operator uses the pattern matching Boyer-Moore-Horspool algorithm, which means that it is a single pattern matching operator. This operator performs much better than a regular expression. In libModSecurity v3 the implementation is a plain substring search, comparable to the contains operator, with macro expansion performed on the parameter.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect suspicious client by looking at the user agent identification
SecRule REQUEST_HEADERS:User-Agent "@strmatch WebZIP" "id:177"
```

{{% notice note %}}

Starting on ModSecurity v2.6.0 this operator supports a snort/suricata content style. ie: "@strmatch A\|42\|C\|44\|F". libModSecurity v3 does not parse this notation for @strmatch (it does for @pm).

{{% /notice %}}

## unconditionalMatch

Will force the rule to always return true. This is similar to SecAction however all actions that occur as a result of a rule matching will fire such as the setting of MATCHED_VAR. This can also be part a chained rule.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
SecRule REMOTE_ADDR "@unconditionalMatch" \
    "id:1000,\
    phase:1,\
    pass,\
    t:hexEncode,\
    nolog,\
    setvar:TX.ip_hash=%{MATCHED_VAR}"
```

## validateByteRange

Validates that the byte values used in input fall into the range specified by the operator parameter. This operator matches on an input value that contains bytes that are not in the specified range.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Enforce very strict byte range for request parameters (only
# works for the applications that do not use the languages other
# than English).
SecRule ARGS "@validateByteRange 10, 13, 32-126" "id:178"
```

The validateByteRange is most useful when used to detect the presence of NUL bytes, which don’t have a legitimate use, but which are often used as an evasion technique.

``` seclang
# Do not allow NUL bytes
SecRule ARGS "@validateByteRange 1-255" "id:179"
```

{{% notice note %}}

You can force requests to consist only of bytes from a certain byte range. This can be useful to avoid stack overflow attacks (since they usually contain "random" binary content). The parameter is mandatory: a comma-separated list of byte values and `start-end` ranges, each between 0 and 255; whitespace around the values is tolerated by `atoi()` and anything not listed is reported as outside the range. libModSecurity v3 (since 3.0.14) rejects the rule at configuration load when a value is outside 0 to 255 or a range start is greater than its end.

{{% /notice %}}

validateByteRange is similar to the ModSecurity 1.X SecFilterForceByteRange Directive however since it works in a rule context, it has the following differences:

- You can specify a different range for different variables.
- It has an "event" context (id, msg....)
- It is executed in the flow of rules rather than being a built in pre-check.

## validateDTD

Validates the XML DOM tree against the supplied DTD. The DOM tree must have been built previously using the XML request body processor. This operator matches when the validation fails. libModSecurity v3 requires a build with libxml2 (otherwise the operator is accepted but always matches), resolves the DTD path at configuration load, and also matches when no XML tree was built or the document is not well formed.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Parse the request bodies that contain XML
SecRule REQUEST_HEADERS:Content-Type "@rx ^text/xml$" \
    "id:180,\
    phase:1,\
    pass,\
    t:lowercase,\
    nolog,\
    ctl:requestBodyProcessor=XML"

# Validate XML payload against DTD
SecRule XML "@validateDTD /path/to/xml.dtd" \
    "id:181,\
    phase:2,\
    deny,\
    msg:'Failed DTD validation'"
```

**NOTE:** You must enable the `SecXmlExternalEntity` directive.

## validateHash

Validates REQUEST_URI that contains data protected by the hash engine. Added in ModSecurity 2.7.0 as @validateEncryption and renamed to @validateHash in 2.7.1.

{{< secmeta v2="2.7.1" v3="no" v3note="(the parser rejects the rule with *Operator: ValidateHash is not yet supported*; the hash engine does not exist in v3)" >}}

**Example:**

``` seclang
# Validates requested URI that matches a regular expression.
SecRule REQUEST_URI "@validateHash product_info|product_list" \
    "id:123456,\
    phase:1,\
    deny"
```

## validateSchema

Validates the XML DOM tree against the supplied XML Schema. The DOM tree must have been built previously using the XML request body processor. This operator matches when the validation fails. libModSecurity v3 requires a build with libxml2 (otherwise the operator is accepted but always matches), resolves the schema path at configuration load, and also matches when no XML tree was built or the document is not well formed.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Parse the request bodies that contain XML
SecRule REQUEST_HEADERS:Content-Type "@rx ^text/xml$" \
    "id:190,\
    phase:1,\
    pass,\
    t:lowercase,\
    nolog,\
    ctl:requestBodyProcessor=XML"

# Validate XML payload against DTD
SecRule XML "@validateSchema /path/to/xml.xsd" \
    "id:191,\
    phase:2,\
    deny,\
    msg:'Failed DTD validation'"
```

**NOTE:** You must enable the `SecXmlExternalEntity` directive.

## validateUrlEncoding

Validates the URL-encoded characters in the provided input string.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Validate URL-encoded characters in the request URI
SecRule REQUEST_URI_RAW "@validateUrlEncoding" "id:192"
```

ModSecurity will automatically decode the URL-encoded characters in request parameters, which means that there is little sense in applying the @validateUrlEncoding operator to them —that is, unless you know that some of the request parameters were URL-encoded more than once. Use this operator against raw input, or against the input that you know is URL-encoded. For example, some applications will URL-encode cookies, although that’s not in the standard. Because it is not in the standard, ModSecurity will neither validate nor decode such encodings.

## validateUtf8Encoding

Check whether the input is a valid UTF-8 string.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Make sure all request parameters contain only valid UTF-8
SecRule ARGS "@validateUtf8Encoding" "id:193"
```

The @validateUtf8Encoding operator detects the following problems:

- **Not enough bytes**: ModSecurity accepts one- to four-byte encodings (RFC 3629; a lead byte announcing a five- or six-byte sequence is reported as an invalid character). ModSecurity will locate cases when one or more bytes is/are missing from a character.
- **Invalid characters**: The two most significant bits in most characters should be fixed to 0x80. Some attack techniques use different values as an evasion technique.
- **Overlong characters**: ASCII characters are mapped directly into UTF-8, which means that an ASCII character is one UTF-8 character at the same time. However, in UTF-8 many ASCII characters can also be encoded with two, three, four, five, and six bytes. This is no longer legal in the newer versions of Unicode, but many older implementations still support it. The use of overlong UTF-8 characters is common for evasion.
- **Restricted characters**: code points above U+10FFFF (lead byte 0xF5 or higher) and the UTF-16 surrogate range U+D800 to U+DFFF.

- Most, but not all applications use UTF-8. If you are dealing with an application that does, validating that all request parameters are valid UTF-8 strings is a great way to prevent a number of evasion techniques that use the assorted UTF-8 weaknesses. False positives are likely if you use this operator in an application that does not use UTF-8.
- Many web servers will also allow UTF-8 in request URIs. If yours does, you can verify the request URI using @validateUtf8Encoding.

## verifyCC

Detects credit card numbers in input. This operator will first use the supplied regular expression to perform an initial match, following up with the Luhn algorithm calculation to minimize false positives.

{{< secmeta v2="yes" v3="yes" >}}

**Example:**

``` seclang
# Detect credit card numbers in parameters and
# prevent them from being logged to audit log
SecRule ARGS "@verifyCC \d{13,16}" \
    "id:194,\
    phase:2,\
    pass,\
    nolog,\
    msg:'Potential credit card number',\
    sanitiseMatched"
```

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## verifyCPF

Detects CPF numbers (Brazilian social number) in input. This operator will first use the supplied regular expression to perform an initial match, following up with an algorithm calculation to minimize false positives.

{{< secmeta v2="2.6.0" v3="yes" >}}

**Example:**

``` seclang
# Detect CPF numbers in parameters and
# prevent them from being logged to audit log
SecRule ARGS "@verifyCPF /^([0-9]{3}\.){2}[0-9]{3}-[0-9]{2}$/" \
    "id:195,\
    phase:2,\
    pass,\
    nolog,\
    msg:'Potential CPF number',\
    sanitiseMatched"
```

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## verifySSN

Detects US social security numbers (SSN) in input. This operator will first use the supplied regular expression to perform an initial match, following up with an SSN algorithm calculation to minimize false positives.

{{< secmeta v2="2.6.0" v3="yes" >}}

**Example:**

``` seclang
# Detect social security numbers in parameters and
# prevent them from being logged to audit log
SecRule ARGS "@verifySSN \d{3}-?\d{2}-?\d{4}" \
    "id:196,\
    phase:2,\
    pass,\
    nolog,\
    msg:'Potential social security number',\
    sanitiseMatched"
```

**SSN Format**:

A Social Security number is broken up into 3 sections:

- Area (3 digits)
- Group (2 digits)
- Serial (4 digits)

**verifySSN checks:**

- Must have 9 digits
- Cannot be a sequence number (ie,, 123456789, 012345678)
- Cannot be a repetition sequence number ( ie 11111111 , 222222222)
- Cannot have area and/or group and/or serial zeroed sequences
- Area code must be less than 740
- Area code must be different then 666

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## verifySVNR

Detects Austrian social insurance numbers (Sozialversicherungsnummer, SVNR) in input. This operator will first use the supplied regular expression to perform an initial match, following up with the SVNR check digit calculation to minimize false positives.

{{< secmeta v2="no" v3="3.0.4" >}}

**Example:**

``` seclang
# Detect Austrian social insurance numbers in parameters and
# prevent them from being logged to audit log
SecRule ARGS "@verifySVNR \d{4}\s?\d{6}" \
    "id:198,\
    phase:2,\
    pass,\
    nolog,\
    msg:'Potential SVNR number',\
    sanitiseMatched"
```

**verifySVNR checks:**

- Must have 10 digits (a 4 digit serial number including the check digit, followed by the 6 digit date of birth DDMMYY); other characters are skipped
- Cannot be a sequence number (ie, 0123456789, 1234567890) or a repetition sequence number (ie 1111111111)
- The fourth digit must equal the weighted sum of the other digits modulo 11 (weights 3, 7, 9 for the serial number and 5, 8, 4, 2, 1, 6 for the date of birth; a result of 10 counts as 0)

This operator exists only in libModSecurity v3 (added in 3.0.4); ModSecurity v2 has no equivalent.

{{% notice note %}}

This operator supports the "capture" action.

{{% /notice %}}

## within

Returns true if the input value (the needle) is found anywhere within the @within parameter (the haystack). Macro expansion is performed on the parameter string before comparison.

{{< secmeta v2="2.5.0" v3="yes" >}}

**Example:**

``` seclang
# Detect request methods other than GET, POST and HEAD
SecRule REQUEST_METHOD "!@within GET,POST,HEAD"
```

{{% notice note %}}

There are no delimiters for this operator, it is therefore often necessary to artificially impose some; this can be done using setvar. For instance in the example below, without the imposed delimiters (of '/') this rule would also match on the 'range' header (along with many other combinations), since 'range' is within the provided parameter. With the imposed delimiters, the rule would check for '/range/' when the range header is provided, and therefore would not match since '/range/ is not part of the @within parameter.

{{% /notice %}}

``` seclang
SecRule REQUEST_HEADERS_NAMES "@rx ^.*$" \
    "id:1,\
    block,\
    t:lowercase,\
    setvar:'tx.header_name=/%{tx.0}/',\
    chain"
    SecRule TX:header_name "@within /proxy/ /lock-token/ /content-range/ /translate/ /if/" \
        "t:none"
```
