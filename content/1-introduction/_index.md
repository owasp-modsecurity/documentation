---
title: Introduction
weight: 1
pre: "<b>1. </b>"
chapter: true
---

ModSecurity is an open source web application firewall (WAF). A WAF adds an external security layer in front of web applications to detect and, if configured to do so, prevent attacks before they reach the application. ModSecurity provides protection from a range of attacks against web applications and allows for HTTP traffic monitoring, logging and real-time analysis with little or no changes to existing infrastructure.

## ModSecurity v2 and libModSecurity v3

ModSecurity is developed as two code lines. Both are maintained by the OWASP ModSecurity project (stewardship was transferred from Trustwave to OWASP in 2024) and both implement the same rule language, so rule sets such as the OWASP CRS run on either.

- **ModSecurity v2** (branch `v2/master`, latest release {{< param modsec_v2_latest >}}) is the original implementation: an Apache httpd module (`mod_security2`) and, built on the same code, a module for Microsoft IIS. Use it when you run Apache httpd or IIS. See [ModSecurity v2 for Apache]({{% relref "2-installation/2-5-modsecurity-v2-apache" %}}) and [ModSecurity v2 for Microsoft IIS]({{% relref "2-installation/2-6-modsecurity-v2-iis" %}}).
- **libModSecurity v3** (branch `v3/master`, latest release {{< param modsec_v3_latest >}}) is a rewrite of the engine as a standalone C++ library with no Apache dependency. Web servers talk to it through separate *connector* projects: [ModSecurity-nginx](https://github.com/owasp-modsecurity/ModSecurity-nginx) is the production-ready connector; [ModSecurity-apache](https://github.com/owasp-modsecurity/ModSecurity-apache) exists but its README states it is not production ready, so Apache users should stay on v2. Use v3 when you run NGINX or embed the library in your own application. See [Building libModSecurity v3 from source]({{% relref "2-installation/2-1-building-libmodsecurity" %}}) and [libModSecurity v3 with NGINX]({{% relref "2-installation/2-2-libmodsecurity-v3-nginx" %}}).

Where this manual describes behavior that differs between the two, the difference is called out in the text. Differences that matter when moving from v2 to v3 are collected in [Migrating from v2 to v3]({{% relref "6-migration/6-1-migrating-from-2x-to-3x" %}}).

## HTTP Traffic Logging

Web servers are typically well-equipped to log traffic in a form useful for marketing analyses, but fall short logging traffic to web applications. In particular, most are not capable of logging the request bodies, which is where most attack payloads travel. ModSecurity makes full HTTP transaction logging possible, allowing complete requests and responses to be logged. Its logging facilities also allow fine-grained decisions to be made about exactly what is logged and when, ensuring only the relevant data is recorded. As some of the request and/or response may contain sensitive data in certain fields, ModSecurity can be configured to mask these fields before they are written to the audit log.

## Real-Time Monitoring and Attack Detection

In addition to providing logging facilities, ModSecurity can monitor the HTTP traffic in real time in order to detect attacks. In this case, ModSecurity operates as a web intrusion detection tool, allowing you to react to suspicious events that take place at your web systems.

## Attack Prevention and Virtual Patching

ModSecurity can also act immediately to prevent attacks from reaching your web applications. There are three commonly used approaches:

1.  Negative security model. A negative security model monitors requests for anomalies, unusual behavior, and common web application attacks. It keeps anomaly scores for each request, IP addresses, application sessions, and user accounts. Requests with high anomaly scores are either logged or rejected altogether.
2.  Positive security model. When a positive security model is deployed, only requests that are known to be valid are accepted, with everything else rejected. This model requires knowledge of the web applications you are protecting. Therefore a positive security model works best with applications that are heavily used but rarely updated so that maintenance of the model is minimized.
3.  Known weaknesses and vulnerabilities. Its rule language makes ModSecurity an ideal external patching tool. External patching (sometimes referred to as Virtual Patching) is about reducing the window of opportunity. Time needed to patch application vulnerabilities often runs to weeks in many organizations. With ModSecurity, applications can be patched from the outside, without touching the application source code (and even without any access to it), making your systems secure until a proper patch is applied to the application.

## Flexible Rule Engine

A flexible rule engine sits in the heart of ModSecurity. It implements the ModSecurity Rule Language (SecLang), which is a specialized programming language designed to work with HTTP transaction data. The ModSecurity Rule Language is designed to be easy to use, yet flexible: common operations are simple while complex operations are possible. ModSecurity ships with no rules of its own; the [OWASP CRS](https://coreruleset.org/) is the commonly used general-purpose rule set and implements protocol validation and detection of common web application security issues. Heavily commented, these rules can be used as a learning tool.

## Embedded-mode Deployment

ModSecurity is an embeddable web application firewall, which means it can be deployed as part of your existing web server infrastructure: Apache httpd and IIS with v2, NGINX with v3. This deployment method has certain advantages:

1.  No changes to existing network. It only takes a few minutes to add ModSecurity to your existing web servers. And because it was designed to be completely passive by default, you are free to deploy it incrementally and only use the features you need. It is equally easy to remove or deactivate it if required.
2.  No single point of failure. Unlike with network-based deployments, you will not be introducing a new point of failure to your system.
3.  Implicit load balancing and scaling. Because it works embedded in web servers, ModSecurity will automatically take advantage of the additional load balancing and scalability features. You will not need to think of load balancing and scaling unless your existing system needs them.
4.  Minimal overhead. Because it works from inside the web server process there is no overhead for network communication and minimal overhead in parsing and data exchange.
5.  No problem with encrypted or compressed content. Many IDS systems have difficulties analyzing SSL traffic. This is not a problem for ModSecurity because it is positioned to work when the traffic is decrypted and decompressed.

## Network-based Deployment

ModSecurity works equally well when deployed as part of a reverse proxy server. In this scenario, one installation of ModSecurity can protect any number of back-end web servers.

## Portability

ModSecurity is known to work well on a wide range of operating systems, including Linux, Windows, FreeBSD, OpenBSD, NetBSD, Solaris, AIX and macOS.

## Licensing

ModSecurity is available under the [Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.txt).
