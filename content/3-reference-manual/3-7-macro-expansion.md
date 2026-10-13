---
title: Macro Expansion
weight: 7
---

Macros allow for using placeholders in rules that will be expanded out to their values at runtime. Only variable expansion is supported; the syntax is the same in ModSecurity v2 and libModSecurity v3.

Format:

``` apache
%{VARIABLE}
%{COLLECTION.VARIABLE}
```

Macro expansion can be used in actions such as [initcol]({{% relref "3-reference-manual/3-5-actions#initcol" %}}), [setsid]({{% relref "3-reference-manual/3-5-actions#setsid" %}}), [setuid]({{% relref "3-reference-manual/3-5-actions#setuid" %}}), [setvar]({{% relref "3-reference-manual/3-5-actions#setvar" %}}), [setenv]({{% relref "3-reference-manual/3-5-actions#setenv" %}}), [logdata]({{% relref "3-reference-manual/3-5-actions#logdata" %}}) and [msg]({{% relref "3-reference-manual/3-5-actions#msg" %}}). Operators that are evaluated at runtime support expansion in their parameter; the entries in [Operators]({{% relref "3-reference-manual/3-6-operators" %}}) note where this applies. Such operators include `@beginsWith`, `@endsWith`, `@contains`, `@within`, `@streq`, `@eq`, `@ge`, `@gt`, `@le` and `@lt`. You can use macro expansion in operators that are "compiled" at load time, such as `@rx`, but the pattern is then recompiled on every evaluation, which has an impact on efficiency.

Some values you may want to expand include: `TX`, `REMOTE_ADDR`, `USERID`, `HIGHEST_SEVERITY`, `MATCHED_VAR`, `MATCHED_VAR_NAME`, `MULTIPART_STRICT_ERROR`, `RULE`, `SESSION` and `SESSIONID`, among others.
