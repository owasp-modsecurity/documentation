---
title: Transformation Functions
weight: 4
---

Transformation functions are used to alter input data before it is used in matching (i.e., operator execution). The input data is never modified, actually—whenever you request a transformation function to be used, ModSecurity will create a copy of the data, transform it, and then run the operator against the result.

{{% notice note %}}

There are no default transformation functions, as there were in the first generation of ModSecurity (1.x).

{{% /notice %}}

In the following example, the request parameter values are converted to lowercase before matching:

`SecRule ARGS "xp_cmdshell" "t:lowercase,id:91"`

Multiple transformation actions can be used in the same rule, forming a transformation pipeline. The transformations will be performed in the order in which they appear in the rule.

In most cases, the order in which transformations are performed is very important. In the following example, a series of transformation functions is performed to counter evasion. Performing the transformations in any other order would allow a skillful attacker to evade detection:

`SecRule ARGS "(asfunction|javascript|vbscript|data|mocha|livescript):" "id:92,t:none,t:htmlEntityDecode,t:lowercase,t:removeNulls,t:removeWhitespace"`

{{% notice warning %}}

It is currently possible to use SecDefaultAction to specify a default list of transformation functions, which will be applied to all rules that follow the SecDefaultAction directive. However, this practice is not recommended, because it means that mistakes are very easy to make. It is recommended that you always specify the transformation functions that are needed by a particular rule, starting the list with t:none (which clears the possibly inherited transformation functions).

{{% /notice %}}

Transformation names are matched case-insensitively by both engines (for example `t:cmdline` and `t:cmdLine` are the same function).

ModSecurity v2 can cache transformation results per transaction and phase through [SecCacheTransformations]({{% relref "3-reference-manual/3-2-configuration-directives#seccachetransformations" %}}); the feature was deprecated in 2.5.6 and is off by default. libModSecurity v3 does not implement transformation caching and rejects the directive with "SecCacheTransformations is not supported".

The remainder of this section documents the transformation functions currently available in ModSecurity.

## base64Decode

{{< secmeta v2="yes" v3="3.0.1" >}}

Decodes a Base64-encoded string.

``` apache
SecRule REQUEST_HEADERS:Authorization "^Basic ([a-zA-Z0-9]+=*)$" "phase:1,id:93,capture,chain,logdata:%{TX.1}"
  SecRule TX:1 ^(\w+): t:base64Decode,capture,chain
    SecRule TX:1 ^(admin|root|backup)$
```

The two engines treat malformed input differently. ModSecurity v2 (`apr_base64_decode`) decodes up to the first byte outside the Base64 alphabet and discards the rest. libModSecurity v3 (which uses a strict decoder) rejects the whole input and leaves the value unchanged when it contains a byte outside the alphabet, when its length is not a multiple of four (missing padding), or when data follows the padding; it does ignore line breaks (and spaces right before one or at the end of the value). It also stops at the first NUL byte in the input. Use base64DecodeExt when a forgiving decoder is wanted.

{{% notice note %}}

Be careful when applying base64Decode with other transformations. The order of your transformation matters in this case as certain transformations may change or invalidate the base64 encoded string prior to being decoded (i.e t:lowercase, etc). This of course means that it is also very difficult to write a single rule that checks for a base64decoded value OR an unencoded value with transformations, it is best to write two rules in this situation.

{{% /notice %}}

## sqlHexDecode

{{< secmeta v2="2.6.3" v3="yes" >}}

Decode sql hex data. Example (0x414243) will be decoded to (ABC). Available as of 2.6.3.

Both engines decode `0x` (or `0X`) followed by at least one complete pair of hexadecimal digits, and keep a bare `0x` that is not followed by a complete pair. ModSecurity v2 processes the value as a C string: it copies the byte that follows a decoded literal without examining it (so `0x410x42` yields `A0x42`), and the value is truncated at a decoded NUL byte. libModSecurity v3 re-examines every byte and preserves decoded NUL bytes.

## base64DecodeExt

{{< secmeta v2="2.6.0" v3="3.0.1" >}}

Decodes a Base64-encoded string. Unlike base64Decode, this version uses a more forgiving implementation that ignores whitespace and misplaced padding. Available under this name as of 2.6.0 (earlier development releases called it decodeBase64Ext).

Both engines accept the URL-safe alphabet (`-` and `_`) since ModSecurity 2.9.15 and libModSecurity 3.0.17. ModSecurity v2 skips only space, tab, CR, LF and padding (`=`) characters: any other byte outside the Base64 alphabet makes the whole decode fail and the output is an empty string. It also stops decoding at the first NUL byte in the input. libModSecurity v3 skips every byte outside the alphabet and processes every byte.

See blog post on Base64Decoding evasion issues on PHP sites - <http://blog.spiderlabs.com/2010/04/impedance-mismatch-and-base64.html>

## base64Encode

{{< secmeta v2="yes" v3="3.0.1" >}}

Encodes input string using Base64 encoding.

## cmdLine

{{< secmeta v2="2.6.0" v3="yes" >}}

{{% notice note %}}

This is a community contribution developed by Marc Stern [1](http://www.linkedin.com/in/marcstern)

{{% /notice %}}

In Windows and Unix, commands may be escaped by different means, such as:

- c^ommand /c ...
- "command" /c ...
- command,/c ...
- backslash in the middle of a Unix command

The cmdLine transformation function avoids this problem by manipulating the variable content in the following ways:

- deleting all backslashes [\\
- deleting all double quotes ["]
- deleting all single quotes [']
- deleting all carets [^]
- deleting spaces before a slash [/]
- deleting spaces before an open parenthesis [(]
- replacing all commas [,] and semicolon [;] into a space
- replacing all multiple spaces (including tab, carriage return and newline) into one space
- transform all characters to lowercase

ModSecurity v2 registers this function as `cmdline`; because transformation names are matched case-insensitively, `t:cmdLine` works as well. libModSecurity v3 accepts `t:cmdLine` in rules in any letter case too; only its internal transformation factory, which the Lua API (`m.getvar`, `m.getvars`) uses to look up transformation names, compares names case-sensitively and knows this function solely as `cmd_line` (compressWhitespace is also accepted there as `compress_whitespace`; every other name is spelled as in this manual). ModSecurity v2 processes the value as a C string and stops at the first NUL byte; libModSecurity v3 processes every byte.

**Example Usage:**

``` apache
SecRule ARGS "(?:command(?:.com)?|cmd(?:.exe)?)(?:/.*)?/[ck]" "phase:2,id:94,t:none, t:cmdLine"
```

## compressWhitespace

{{< secmeta v2="yes" v3="yes" >}}

Converts any of the whitespace characters (0x20, \f, \t, \n, \r, \v, 0xa0) to spaces (ASCII 0x20), compressing multiple consecutive space characters into one.

libModSecurity v3 does not treat the byte 0xa0 (non-breaking space) as whitespace in this function; only ModSecurity v2 compresses it. Both engines treat 0xa0 as whitespace in removeWhitespace.

## cssDecode

{{< secmeta v2="2.5.7" v3="yes" >}}

Decodes characters encoded using the CSS 2.x escape rules [syndata.html#characters](http://www.w3.org/TR/CSS2/). This function uses only up to two bytes in the decoding process, meaning that it is useful to uncover ASCII characters encoded using CSS encoding (that wouldn’t normally be encoded), or to counter evasion, which is a combination of a backslash and non-hexadecimal characters (e.g., ja\vascript is equivalent to javascript).

## escapeSeqDecode

{{< secmeta v2="yes" v3="3.0.3" >}}

Decodes ANSI C escape sequences: `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`, `\\`, `\?`, `\'`, `\"`, `\xHH` (exactly two hexadecimal digits, `\XHH` is also accepted), `\OOO` (one to three octal digits, producing a single byte). A backslash before a byte that does not begin a recognized sequence is dropped and the byte is kept (`\8` becomes `8`, `\xag` becomes `xag`); only a lone trailing backslash is left in the output. Both engines behave the same way; libModSecurity v3 accepts the function since 3.0.3 (earlier 3.0.x releases fail to parse it).

## hexDecode

{{< secmeta v2="yes" v3="yes" >}}

Decodes a string that has been encoded using the same algorithm as the one used in hexEncode (see following entry).

Neither engine validates the input: every pair of characters is converted to a byte even when it contains non-hexadecimal characters (which yield meaningless bytes), and a trailing unpaired character is dropped.

## hexEncode

{{< secmeta v2="yes" v3="yes" >}}

Encodes string (possibly containing binary characters) by replacing each input byte with two hexadecimal characters. For example, xyz is encoded as 78797a.

## htmlEntityDecode

{{< secmeta v2="yes" v3="yes" >}}

Decodes the characters encoded as HTML entities. The following variants are supported:

- `&#xHH` and `&#xHH;` (where H is any hexadecimal number)
- `&#DDD` and `&#DDD;` (where D is any decimal number)
- `&quot;` and `&quot`
- `&nbsp;` and `&nbsp`
- `&lt;` and `&lt`
- `&gt;` and `&gt`
- `&amp;` and `&amp`

This function always converts one HTML entity into one byte, possibly resulting in a loss of information (if the entity refers to a character that cannot be represented with the single byte). It is thus useful to uncover bytes that would otherwise not need to be encoded, but it cannot do anything meaningful with the characters from the range above 0xff.

Since ModSecurity 2.9.15 and libModSecurity 3.0.17 both engines decode every named entity that expands to a single ASCII character (U+0000–U+007F, for example `&colon;`, `&lpar;` and `&sol;`) plus `&nbsp;` and `&shy;`, matched case-insensitively against the full entity name; earlier releases only knew `quot`, `amp`, `lt`, `gt` and `nbsp`, which allowed evasions such as `javascript&colon;` (GHSA-cxqf-vgrr-xxrv). Named entities for characters outside that range are left as is.

## jsDecode

{{< secmeta v2="2.5.0" v3="yes" >}}

Decodes JavaScript escape sequences: `\uHHHH`, `\xHH`, `\OOO` (one to three octal digits, producing a single byte), `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`; a backslash before any other byte is removed and the byte is kept. If a \uHHHH code is in the range of FF01-FF5E (the full width ASCII codes), then the higher byte is used to detect and adjust the lower byte. Otherwise, only the lower byte will be used and the higher byte zeroed (leading to possible loss of information).

## length

{{< secmeta v2="2.5.0" v3="yes" >}}

Looks up the length of the input string in bytes, placing it (as string) in output. For example, if it gets ABCDE on input, this transformation function will return 5 on output.

## lowercase

{{< secmeta v2="yes" v3="yes" >}}

Converts all characters to lowercase using the current C locale.

## md5

{{< secmeta v2="yes" v3="yes" >}}

Calculates an MD5 hash from the data in input. The computed hash is in a raw binary form and may need encoded into text to be printed (or logged). Hash functions are commonly used in combination with hexEncode (for example: t:md5,t:hexEncode).

## none

{{< secmeta v2="yes" v3="yes" >}}

Not an actual transformation function, but an instruction to ModSecurity to remove all transformation functions associated with the current rule.

## normalisePath

{{< secmeta v2="yes" v3="yes" >}}

See normalizePath. Both spellings are accepted by ModSecurity v2 and libModSecurity v3.

## normalizePath

{{< secmeta v2="2.6.0" v3="yes" >}}

Removes multiple slashes, directory self-references, and directory back-references (except when at the beginning of the input) from input string.

{{% notice note %}}

As of ModSecurity 2.6.0 normalisePath has been renamed to normalizePath (MODSEC-103). NormalisePath is kept for backwards compatibility in current versions of both engines, but should not be used.

{{% /notice %}}

## normalisePathWin

{{< secmeta v2="yes" v3="yes" >}}

See normalizePathWin. Both spellings are accepted by ModSecurity v2 and libModSecurity v3.

## normalizePathWin

{{< secmeta v2="2.6.0" v3="yes" >}}

Same as normalizePath, but first converts backslash characters to forward slashes.

{{% notice note %}}

As of ModSecurity 2.6.0 normalisePathWin has been renamed to normalizePathWin (MODSEC-103). NormalisePathWin is kept for backwards compatibility in current versions of both engines, but should not be used.

{{% /notice %}}

## parityEven7bit

{{< secmeta v2="2.5.7" v3="yes" >}}

Calculates even parity of 7-bit data replacing the 8th bit of each target byte with the calculated parity bit.

## parityOdd7bit

{{< secmeta v2="2.5.7" v3="yes" >}}

Calculates odd parity of 7-bit data replacing the 8th bit of each target byte with the calculated parity bit.

## parityZero7bit

{{< secmeta v2="2.5.7" v3="yes" >}}

Calculates zero parity of 7-bit data replacing the 8th bit of each target byte with a zero-parity bit, which allows inspection of even/odd parity 7-bit data as ASCII7 data.

## removeNulls

{{< secmeta v2="yes" v3="yes" >}}

Removes all NUL bytes from input.

## removeWhitespace

{{< secmeta v2="yes" v3="yes" >}}

Removes all whitespace characters from input.

libModSecurity v3 removes the C-locale whitespace characters (space, `\t`, `\n`, `\v`, `\f`, `\r`), the byte 0xa0 and also every 0xc2 byte (the UTF-8 lead byte of the non-breaking space U+00A0), so it also strips the lead byte of any other UTF-8 character in the range U+0080–U+00BF.

## replaceComments

{{< secmeta v2="yes" v3="yes" >}}

Replaces each occurrence of a C-style comment (/* ... */) with a single space (multiple consecutive occurrences of which will not be compressed). Unterminated comments will also be replaced with a space (ASCII 0x20). However, a standalone termination of a comment (*/) will not be acted upon.

## removeCommentsChar

{{< secmeta v2="2.6.2" v3="yes" >}}

Removes common comments chars (`/*`, `*/`, `<!--`, `-->`, `--`, `#`).

## removeComments

{{< secmeta v2="2.6.2" v3="yes" >}}

Removes each occurrence of comment (`/* ... */`, `<!-- ... -->`, `--`, `#`). Multiple consecutive occurrences of which will not be compressed.

In both engines, `/* ... */` and `<!-- ... -->` comments are removed entirely (an unterminated one is replaced with a single space), while `--` and `#` start a comment that extends to the end of the input, so everything from that point on is removed. Adjacent comments (for example `/**//**/`) are handled correctly since ModSecurity 2.9.15 and libModSecurity 3.0.17.

{{% notice note %}}

**This transformation is known to be unreliable, might cause some unexpected behavior and could be deprecated soon in a future release. Refer to issue [#1207](https://github.com/owasp-modsecurity/ModSecurity/issues/1207) for further information.**.

{{% /notice %}}

## replaceNulls

{{< secmeta v2="yes" v3="yes" >}}

Replaces NUL bytes in input with space characters (ASCII 0x20).

## urlDecode

{{< secmeta v2="yes" v3="yes" >}}

Decodes a URL-encoded input string. Invalid encodings (i.e., the ones that use non-hexadecimal characters, or the ones that are at the end of string and have one or two bytes missing) are not converted, but no error is raised. To detect invalid encodings, use the @validateUrlEncoding operator on the input data first. The transformation function should not be used against variables that have already been URL-decoded (such as request parameters) unless it is your intention to perform URL decoding twice!

## uppercase

{{< secmeta v2="no" v3="yes" >}}

Converts all characters to uppercase using the current C locale.

This function exists only in libModSecurity v3; ModSecurity v2 does not register it and a rule using `t:uppercase` fails to load there.

## urlDecodeUni

{{< secmeta v2="yes" v3="yes" >}}

Like urlDecode, but with support for the Microsoft-specific %u encoding. If the code is in the range of FF01-FF5E (the full-width ASCII codes), then the higher byte is used to detect and adjust the lower byte. Otherwise, only the lower byte will be used and the higher byte zeroed.

When a [SecUnicodeMapFile]({{% relref "3-reference-manual/3-2-configuration-directives#secunicodemapfile" %}}) is loaded and a code page is selected, both engines map the `%uHHHH` code point through that table before falling back to the rules above. ModSecurity v2 takes the code page from the second argument of SecUnicodeMapFile or from [SecUnicodeCodePage]({{% relref "3-reference-manual/3-2-configuration-directives#secunicodecodepage" %}}); libModSecurity v3 requires it as the second argument of SecUnicodeMapFile and does not recognize SecUnicodeCodePage (a configuration error). Invalid `%` sequences are left as is.

## urlEncode

{{< secmeta v2="yes" v3="3.0.3" >}}

Encodes input string using URL encoding. Letters, digits and `*` are kept as they are, a space becomes `+`, and every other byte becomes `%HH` (lowercase hexadecimal).

## utf8toUnicode

{{< secmeta v2="2.7.0" v3="yes" >}}

Converts all UTF-8 character sequences to Unicode (using '%uHHHH' format, lowercase hexadecimal). This help input normalization specially for non-english languages minimizing false-positives and false-negatives. ModSecurity v2 registers this function as `Utf8toUnicode`; because transformation names are matched case-insensitively, `t:utf8toUnicode` works as well.

Malformed input is handled differently: ModSecurity v2 leaves malformed bytes (invalid lead or continuation bytes, overlong forms, surrogates and code points above U+10FFFF) unchanged, while libModSecurity v3 drops a lead byte whose sequence is incomplete or invalid and, for an overlong form or a surrogate (U+D800–U+DFFF), emits the `%uHHHH` code anyway followed by the raw lead byte. ModSecurity v2 encodes a NUL byte together with the byte that follows it as `%u00HH`; libModSecurity v3 drops a NUL byte that is followed by another byte. libModSecurity v3 writes code points above U+FFFF with five hexadecimal digits (for example `%u1f600`).

## sha1

{{< secmeta v2="yes" v3="yes" >}}

Calculates a SHA1 hash from the input string. The computed hash is in a raw binary form and may need encoded into text to be printed (or logged). Hash functions are commonly used in combination with hexEncode (for example, t:sha1,t:hexEncode).

## trimLeft

{{< secmeta v2="2.5.0" v3="3.0.3" >}}

Removes whitespace from the left side of the input string.

## trimRight

{{< secmeta v2="2.5.0" v3="3.0.3" >}}

Removes whitespace from the right side of the input string.

## trim

{{< secmeta v2="2.5.0" v3="yes" >}}

Removes whitespace from both the left and right sides of the input string.
