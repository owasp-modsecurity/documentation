---
title: libModSecurity v3 with Apache
weight: 3
---

The [ModSecurity-apache connector](https://github.com/owasp-modsecurity/ModSecurity-apache) loads libModSecurity
into Apache HTTP Server as the module `mod_security3`.

{{% notice warning %}}
The Apache connector is **not production ready**. It is incomplete and has not had a stable release.
For Apache, use [ModSecurity v2]({{% relref "2-5-modsecurity-v2-apache" %}}) (`mod_security2`), which is the
maintained and recommended engine on that platform.
{{% /notice %}}

## Compilation

Install libModSecurity first (see [Building libModSecurity v3 from source]({{% relref "2-1-building-libmodsecurity" %}})), then:

```bash
git clone https://github.com/owasp-modsecurity/ModSecurity-apache
cd ModSecurity-apache
./autogen.sh
./configure
make
sudo make install
```

## Usage

Load the module and point it at a rules file. The directives mirror the NGINX connector's:

```apache
LoadModule security3_module modules/mod_security3.so

modsecurity on
modsecurity_rules_file /etc/my_modsecurity_rules.conf
```

`modsecurity_rules_remote <key> <URL>` and `modsecurity_rules '<inline rules>'` are also available, with the same
meaning as in the [NGINX connector]({{% relref "2-2-libmodsecurity-v3-nginx#configuration-directives" %}}).
