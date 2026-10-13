---
title: Roadmap
weight: 2
---

### Enhancements

#### Data Modification

Add the ability to modify both inbound/outbound data

- [JIRA Resolved: (MODSEC-184) New RegEx operator that allows for data substitution](https://www.modsecurity.org/tracker/browse/MODSEC-184)

#### Improved IP Address Handling

Improve the handling of IP Address and Network Blocks

- [JIRA Resolved: (MODSEC-140) Add a fast IP address and network based matching operator](https://www.modsecurity.org/tracker/browse/MODSEC-140)

#### Improved Logging Sanitization

Ability to sanitize only matched portions of data

- [JIRA Resolved: (MODSEC-146) New sanitize functions](https://www.modsecurity.org/tracker/browse/MODSEC-146)

#### Improve Detection Only Mode

Make sure that we do not block requests when in DetectionOnly mode

- [JIRA Resolved: (MODSEC-104) Never block in detection mode](https://www.modsecurity.org/tracker/browse/MODSEC-104)

#### Improve Exception Handling

Add the ability to dynamically update the variable/target list

- [JIRA Resolved: (MODSEC-57) Disable a rule for one particular argument](https://www.modsecurity.org/tracker/browse/MODSEC-57)

#### Enhance IP/Link Reputation Support

Add the ability to parse the returned IP resolution to identify the specific block lists

- <https://www.modsecurity.org/tracker/browse/MODSEC-151>

Add the ability to query a local GSB DB to help identify malware links

- <https://www.modsecurity.org/tracker/browse/MODSEC-107>

#### Verify SSN Data

Add the ability to verify SSN data

- [JIRA Resolved: (MODSEC-148) Additional validation (verify) routines similar to verifyCC](https://www.modsecurity.org/tracker/browse/MODSEC-148)

#### Improve Reverse Proxy Support

Added SecDisableBackendCompression to handle inspection of compressed response body content

### Performance

Add performance metrics/variables

- Added the PERF_ family of performance variables

### Documentation

- Write more/better examples.
- Enhance ModSecurity internals documentation.
- Better document the different modes of operation.

## Version 2.7

### Better Handling of Different Character Sets

Introduce decoding and validating of various character sets.

- <https://www.modsecurity.org/tracker/browse/MODSEC-194>

### Malicious JavaScript Detection

### Positive Security Modeling

### Implement Response Body Parsing

## Version 3.0 and Beyond

### Portability

- Making ModSecurity able to work with web servers other than Apache.
- Release IIS, SunOne, Java versions of ModSecurity.

### Learning

ModSecurity works well when you know exactly what you want to do. We want to expand what it's capable of so it can help in situations where manual configuration is not an option. Configuration reload without restart.

### Code modularity

- We want to make it possible for others to contribute new functionality to ModSecurity without having to learn everything about its internals.
- Define data formats, which will allow related products to build on top of what ModSecurity already provides.
- Scripting. Improve performance of the scripting implementation (Lua) and further integrate scripting into the engine.
- Rule writing in C, for when you need that extra bit of flexibility and performance.

### Stream Inspection

Add the ability to inspect data at an Apache connection filter level (without buffering)

- [JIRA Resolved: (MODSEC-147) Basic streaming detection on raw request/response](https://www.modsecurity.org/tracker/browse/MODSEC-147)

## Version-Independent Tasks

- Better reverse proxy deployment documentation.
  - Embedded deployment is just one option.
  - Coupled with Apache configured in reverse proxy mode, ModSecurity turns into a network-based web application firewall.
- Best practices and cookbook-style documentation.
  - We understand better documentation is needed to make full use of ModSecurity.
