---
title: libModSecurity v3 early release-candidate notes
weight: 2
---

## What is the version 3 earlier release candidate

**ModSecurity version 3 (earlier-rc1) was not released yet.** This wikipage highlights the most important differences between ModSecurity version 2 and v3-erc1 (earlier release candidate 1) **[to be released]**.

The earlier release candidate of ModSecurity version 3 does not target all the features from version 2. Instead, it is targeting to fully support the "OWASP Core Rules Set version 3". Some of the missing pieces have a very low audience, and they will be target in the upcoming releases candidates. The missing pieces are listed in this wikipage.

### Collections update interval.

ModSecurity's persistent collections are saved per thread (or process). From time to time the different values from each thread (or process) are merged into a global storage. A simple counter (for instance: IP:counter) will have different values for the different web server "workers", depending on the process that answers the request. That behavior happens in both versions of ModSecurity (2 and 3). But, the time that is expected to merge the collections is higher in ModSecurity version 2. In practical aspect it means that in ModSecurity version 3 the values for the threads should me more precise.

Another important point to notice is the fact that ModSecurity version 3 does not expire the values for the collections. The collection was built to be very small, thus no need to expire. The expiration maybe taken in care by the backend, once it considers the database to be bigger than expected.

### Missing pieces (Towards version 3 feature complete).

All the missing features belong to a milestone: Feature complete. This milestone can be listed here:  https://github.com/SpiderLabs/ModSecurity/milestone/9
For easy reading, they are also listed below. 

#### Actions
  - exec - https://github.com/owasp-modsecurity/ModSecurity/issues/1050

#### Variables
  - WEBAPPID - https://github.com/owasp-modsecurity/ModSecurity/issues/1027
  - STREAM_INPUT_BODY - https://github.com/owasp-modsecurity/ModSecurity/issues/1021
  - STREAM_OUTPUT_BODY - https://github.com/owasp-modsecurity/ModSecurity/issues/1022
  - USERAGENT_IP - https://github.com/owasp-modsecurity/ModSecurity/issues/1025
  - STATUS_LINE - https://github.com/owasp-modsecurity/ModSecurity/issues/1020
  - SCRIPT_* - https://github.com/owasp-modsecurity/ModSecurity/issues/1017
  - PERF_* - https://github.com/owasp-modsecurity/ModSecurity/issues/1011
  - RESOURCE - https://github.com/owasp-modsecurity/ModSecurity/issues/1014

#### Operators
  - verifySSN - https://github.com/owasp-modsecurity/ModSecurity/issues/1007
  - verifyCPF - https://github.com/owasp-modsecurity/ModSecurity/issues/1006
  - fuzzyHash - https://github.com/owasp-modsecurity/ModSecurity/issues/997
  - gsbLookup - https://github.com/owasp-modsecurity/ModSecurity/issues/998
  - inspectFile - https://github.com/owasp-modsecurity/ModSecurity/issues/999
  - rsub - https://github.com/owasp-modsecurity/ModSecurity/issues/1001
  - validateHash - https://github.com/owasp-modsecurity/ModSecurity/issues/1004

#### Others
  - Support to Lua Scripts - https://github.com/owasp-modsecurity/ModSecurity/issues/994

### What we don't want to support anymore

The list of unsupported features is very minimal at this point, although it may be bigger till the feature complete milestone. The single item is listed below.

- WEBSERVER_ERROR_LOG - https://github.com/owasp-modsecurity/ModSecurity/issues/1028
                      - {{% relref "3-reference-manual/3-3-variables#webserver_error_log" %}}
