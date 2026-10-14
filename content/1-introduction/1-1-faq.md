---
title: Frequently Asked Questions
weight: 1
---

### Who Leads the ModSecurity Project?

ModSecurity was created by Ivan Ristić and was later developed and sponsored by Trustwave (SpiderLabs). In January 2024 Trustwave transferred stewardship of the code to the [OWASP ModSecurity project](https://owasp.org/www-project-modsecurity/), which maintains both the v2 and the v3 code lines today. The current project leaders are listed on the OWASP project page; the active maintainers are visible on the [GitHub organization](https://github.com/owasp-modsecurity).

## Background and Support

### What exactly is ModSecurity?

ModSecurity is an open source, free web application firewall (WAF) engine. WAFs establish an external security layer that detects and prevents attacks before they reach web applications. ModSecurity provides protection from a range of attacks against web applications and allows for HTTP traffic monitoring and real-time analysis with little or no changes to existing infrastructure. See the [Introduction]({{% relref "1-introduction" %}}).

### Which version of ModSecurity should I be using? v2.9.x or v3.0.x?

Both code lines are supported and actively maintained by OWASP (current releases: v{{< param modsec_v2_latest >}} and v{{< param modsec_v3_latest >}}). The web server you run decides:

- **Apache httpd**: ModSecurity v2 (`mod_security2`, branch `v2/master`). The v3 Apache connector exists but is not production ready.
- **Microsoft IIS**: ModSecurity v2 (the IIS module is built from the same v2 tree).
- **NGINX**: libModSecurity v3 with the [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx) connector. NGINX support was removed from the v2 tree in 2.9.13.
- **Your own application or another server**: libModSecurity v3, through its C or C++ API.

Both versions run the OWASP CRS. The rule language is the same; the differences in behavior and the features v3 does not implement are listed in [Migrating from v2 to v3]({{% relref "6-migration/6-1-migrating-from-2x-to-3x" %}}).

### Where do I get more help on ModSecurity?

- Issues and feature requests: <https://github.com/owasp-modsecurity/ModSecurity/issues> (use the connector repository, for example [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx/issues), when the problem is in the connector).
- Questions are welcome in the same issue tracker; label them as questions and search closed issues first.
- Security vulnerabilities: follow the [security policy](https://github.com/owasp-modsecurity/ModSecurity/security/policy) or email `modsecurity@owasp.org`. Do not open a public issue.
- OWASP CRS questions belong to the [CRS project](https://coreruleset.org/), which is run by a separate team.

Commercial support is not offered by the project itself. Several vendors package ModSecurity and the CRS and support them as part of their products.

### Is there anything that I should do prior to creating a new issue?

Yes. There is a good chance that the issue you are facing has already been discussed and, in many cases, either a fix has been produced or a workaround or mitigation has been suggested. Search open and closed issues first. If you cannot find an answer, create a new issue, follow the issue template and supply as much pertinent information as possible: ModSecurity version, connector or web server version, the rule involved and a debug log excerpt.

### Will I always get an immediate response to my issue?

GitHub issues are handled on a best-effort basis by volunteers. You may also get assistance from other members of the ModSecurity community.

### How do I report a security vulnerability?

Do not open a public issue. Report it privately by creating a draft security advisory on GitHub for the affected repository, for example [ModSecurity](https://github.com/owasp-modsecurity/ModSecurity/security/advisories/new), [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx/security/advisories/new) or [ModSecurity-apache](https://github.com/owasp-modsecurity/ModSecurity-apache/security/advisories/new). The maintainers triage the report there, coordinate a fix and publish the advisory together with the fixed release. Reporters are credited in the advisory.

If you cannot use GitHub, email `modsecurity@owasp.org` instead.

### What about the mailing lists?

The SourceForge mailing lists that the project used in the past are no longer in use. Use GitHub issues instead. Release announcements are published on the GitHub releases pages of each repository.

### Where can I find books about Web Application Firewalls and ModSecurity?

The books below predate the v3 code line, but the rule language and the concepts they explain still apply.

#### ModSecurity Handbook

ModSecurity Handbook is "The definitive guide to the popular open source web application firewall", written by Ivan Ristić (original author of ModSecurity), later updated by Christian Folini. The book is available from Feisty Duck in hard copy or digital form.

#### Web Application Defender's Cookbook: Battling Hackers and Defending Users

The Web Application Defender's Cookbook: Battling Hackers and Protecting Users is a book written by the former ModSecurity Project Lead Ryan Barnett. The book outlines critical defensive techniques to protect web applications and includes example ModSecurity rules/scripts.

#### ModSecurity 2.5

ModSecurity 2.5 is "A complete guide to using ModSecurity", written by Magnus Mischel. The book is available from Packt Publishing in both hard copy and digital forms.

#### Apache Security

Apache Security is a comprehensive Apache Security resource, written by Ivan Ristić for O'Reilly.

#### Preventing Web Attacks with Apache

Preventing Web Attacks with Apache. Building on his groundbreaking SANS presentations on Apache security, Ryan C. Barnett reveals why your Web servers represent such a compelling target, how significant exploits are performed, and how they can be defended against.

## Getting Started

### What type(s) of security models does ModSecurity support?

There is a common misconception that ModSecurity can only be used for negative policy enforcement. This is not the case. ModSecurity does not have any default security model "out-of-the-box." It is up to the user to implement appropriate rules to achieve the desired security model. That being said, these are the security models which are most often employed:

Negative Security Model - looks for known bad, malicious requests. This method is effective at blocking a large number of automated attacks, however it is not the best approach for identifying new attack vectors. Using too many negative rules may also negatively impact performance.

Positive Security Model - When positive security model is deployed, only requests that are known to be valid are accepted, with everything else rejected. This approach works best with applications that are heavily used but rarely updated.

Virtual Patching - Its rule language makes ModSecurity an ideal external patching tool. External patching is all about reducing the window of opportunity. Time needed to patch application vulnerabilities often runs to weeks in many organizations. With ModSecurity, applications can be patched from the outside, without touching the application source code (and even without any access to it), making your systems secure until a proper patch is produced.

Extrusion Detection Model - ModSecurity can also monitor outbound data and identify and block information disclosure issues such as leaking detailed error messages or Social Security Numbers or Credit Card Numbers.

### I hear that ModSecurity can be run in embedded-mode, what does that mean exactly?

The term "embedded" simply refers to the fact that ModSecurity is running inside the webserver process. Most WAFs function as totally separate hosts and sit in front of the web servers. Running in embedded-mode has some tradeoffs that should be considered:

Advantages

- Easy to add to an existing web server.
- Not a point of failure with respect to traffic.

Disadvantages

- ModSecurity can only protect the local web server.
- ModSecurity will consume local resources such as CPU and RAM.
- Management of log files and configurations can become difficult if you have multiple installations.

### I hear that ModSecurity can be run in reverse-proxy mode. How does that differ from embedded-mode?

The only difference with this deployment vs. an embedded one is that the web server itself is configured to function as a reverse proxy.

Advantages

- Single point of access functions as a choke point so you consolidate applying security settings and makes management easier.
- Network topology is hidden from the outside world so it will be more difficult for attackers to enumerate your web platforms.
- Increased performance if SSL accelerators/caching used.
- You can implement vulnerability filters to protect any vulnerable web server or application on the back-end (IIS, ASP, PHP, etc.). See related section on Virtual Patching.

Disadvantages

- A potential traffic bottleneck if the reverse proxy can not handle the network load.
- A potential point of failure: if the reverse proxy goes down it may cause a denial of service to the web applications that are behind it.
- Requires changes to the network.

## Configuring ModSecurity

### Should I initially set the SecRuleEngine to On?

No. Every rule set can have false positives in new environments. A new installation should initially run with [SecRuleEngine]({{% relref "3-reference-manual/3-2-configuration-directives#secruleengine" %}}) set to `DetectionOnly` (the setting shipped in `modsecurity.conf-recommended`). After running ModSecurity in detection-only mode for a while, review the events generated and decide if any modification to the rule set should be made before moving to blocking mode.

### How do I get ModSecurity to inspect request and response bodies?

You need to set the following two directives:

``` seclang
SecRequestBodyAccess On

SecResponseBodyAccess On
```

### How can I verify exactly how ModSecurity is processing rules and requests?

You need to enable the debug log with [SecDebugLog]({{% relref "3-reference-manual/3-2-configuration-directives#secdebuglog" %}}) and increase the log level with [SecDebugLogLevel]({{% relref "3-reference-manual/3-2-configuration-directives#secdebugloglevel" %}}). If you set the debug log level to 9, it will tell you exactly what tasks it is completing along with what data it is acting upon. Do be aware that while the increased debug log level does help from a troubleshooting perspective, it does negatively impact performance. See [Debugging]({{% relref "5-troubleshooting/5-1-debugging" %}}).

## ModSecurity Rules Language

### What are the OWASP ModSecurity Core Rules (CRS) and should I use them?

Using ModSecurity requires rules. Installations commonly use one or more of the following:

- A generic rule set that provides generic protection from unknown vulnerabilities
- A rule set addressing known CVEs in specific applications
- Custom rules

The most widely used generic rule set is the [OWASP CRS](https://coreruleset.org/), which is managed by a separate OWASP project. It runs on both ModSecurity v2 and v3.

### How do I allow an IP address to bypass ModSecurity?

The first issue to realize is that the allow action is only applied to the current phase. This means that if a rule matches in a subsequent phase it may still take a disruptive action. The recommended rule configuration to allow a remote IP address to bypass ModSecurity rules is to do the following (where 192.168.1.100 should be substituted with the desired IP address):

``` seclang
SecRule REMOTE_ADDR "@ipMatch 192.168.1.100" \
    "id:1000,\
    phase:1,\
    allow,\
    nolog,\
    ctl:ruleEngine=Off"
```

If you want to allow uninterrupted access to the remote IP address, however you still want to log rule alerts, then you can use this rule:

``` seclang
SecRule REMOTE_ADDR "@ipMatch 192.168.1.100" \
    "id:1000,\
    phase:1,\
    allow,\
    nolog,\
    ctl:ruleEngine=DetectionOnly"
```

If you want to disable both the rule and audit engines, then you can optionally add another ctl action:

``` seclang
SecRule REMOTE_ADDR "@ipMatch 192.168.1.100" \
    "id:1000,\
    phase:1,\
    allow,\
    nolog,\
    ctl:ruleEngine=Off,\
    ctl:auditEngine=Off"
```

### How do I handle False Positives and creating Custom Rules?

It is inevitable; you will run into some False Positive hits when using web application firewalls. This is not something that is unique to ModSecurity. All web application firewalls will generate false positives from time to time. The directives [SecRuleRemoveById]({{% relref "3-reference-manual/3-2-configuration-directives#secruleremovebyid" %}}), [SecRuleUpdateTargetById]({{% relref "3-reference-manual/3-2-configuration-directives#secruleupdatetargetbyid" %}}) and the [ctl]({{% relref "3-reference-manual/3-5-actions#ctl" %}}) action are the tools for excluding rules or targets. If you use the OWASP CRS, follow the [CRS documentation on false positives and tuning](https://coreruleset.org/docs/concepts/false_positives_tuning/).

### Will using a large amount of negative filtering rules impact performance?

Yes. Each and every rule that you implement will consume resources (RAM, CPU, etc...). The two most important factors to consider with creating ModSecurity rules are the total number of rules and the Regular Expression optimizations. A single rule with a complex regular expression is significantly faster than multiple rules with simple regular expressions. Unfortunately, it is quite easy to create inefficient RegEx patterns. Optimizing RegExs by utilizing Grouping Only/Non-Capturing Parentheses can cut the validation time by up to 50%. The OWASP CRS is optimized for performance.

### What is a Virtual Patch and why should I care?

Fixing identified vulnerabilities in web applications always requires time. Organizations often do not have access to a commercial application's source code and are at the vendor's mercy while waiting for a patch. Even if they have access to the code, implementing a patch in development takes time. This leaves a window of opportunity for the attacker to exploit. External patching (also called "just-in-time patching" and "virtual patching") is one of the biggest advantages of web application firewalls as they can fix this problem externally. A fix for a specific vulnerability is usually very easy to design and in most cases it can be done in less than 15 minutes.

<https://cheatsheetseries.owasp.org/cheatsheets/Virtual_Patching_Cheat_Sheet.html>

## Managing Alerts

### How do I manage ModSecurity logs if I have multiple installations?

If you have more than one ModSecurity installation, you have undoubtedly run into issues with consolidating, analyzing and responding to alert messages. The original "Serial" format of the audit log is multi-line with all records held within one file, which makes remote logging difficult. Two options exist:

- Both v2 and v3 can write the audit log in JSON format ([SecAuditLogFormat]({{% relref "3-reference-manual/3-2-configuration-directives#secauditlogformat" %}}) `JSON`), one entry per line, which any log shipper can forward to a central system.
- ModSecurity v2 ships the ModSecurity Log Collector (mlogc), which sends individual audit log entries to a remote host in near real time. mlogc is not part of v3.

### Can I send ModSecurity alert log data through Syslog?

Yes. If you already have a central Syslog infrastructure and/or a SIEM, you might want to forward the short ModSecurity alert messages that appear in the web server error log; both Apache and NGINX can send their error logs to syslog. However, the data being forwarded is a very small subset of the entire transaction. It is only a warning message and not enough information to conduct proper incident response to determine if there was a false positive or if it was a legitimate attack. In order to determine this information, you need access to the ModSecurity audit log files. See [Logging and Data Formats]({{% relref "4-logging" %}}).
