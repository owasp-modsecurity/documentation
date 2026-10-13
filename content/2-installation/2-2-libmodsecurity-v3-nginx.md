---
title: libModSecurity v3 with NGINX
weight: 2
---

The [ModSecurity-nginx connector](https://github.com/owasp-modsecurity/ModSecurity-nginx) links libModSecurity
into NGINX as a third-party module. Unlike the old (v2-era) standalone module, it is a thin layer between NGINX
and the library: the rules engine, the body processors and the logging all live in libModSecurity. The current
connector release is v{{< param modsec_nginx_latest >}}.

## Distribution packages

Most distributions ship the connector as a dynamic NGINX module built against their own `nginx` and
`libmodsecurity` packages, which is the easiest way to get a working setup. Versions as of October 2026:

| Distribution | Package | Connector | libModSecurity |
|---|---|---|---|
| Debian 12 (bookworm) | `libnginx-mod-http-modsecurity` | 1.0.3 | 3.0.9 |
| Debian 13 (trixie) | `libnginx-mod-http-modsecurity` | 1.0.3 | 3.0.14 |
| Ubuntu 24.04 LTS | `libnginx-mod-http-modsecurity` | 1.0.3 | 3.0.12 |
| Ubuntu 26.04 LTS | `libnginx-mod-http-modsecurity` | 1.0.3 | 3.0.14 |
| Fedora 43 and 44, EPEL 9 | `nginx-mod-modsecurity` | 1.0.4 | 3.0.16 / 3.0.17 |
| Arch Linux | `nginx-mod-modsecurity` | 1.0.4 | 3.0.17 |
| Gentoo | `www-nginx/ngx-modsecurity` | 1.0.4 | 3.0.16 |
| FreeBSD ports | `security/modsecurity3-nginx` | 1.0.4 | 3.0.17 |

Ubuntu 22.04 has no connector package in the main archive. Debian, Ubuntu and the Red Hat family also have
the current development builds of both the connector and the library in the
[digitalwave repository]({{% relref "2-4-distribution-recipes#the-digitalwave-repository" %}}), maintained by one of the
ModSecurity project leaders.

On Debian and Ubuntu:

```bash
sudo apt install libnginx-mod-http-modsecurity modsecurity-crs
```

The package enables the module through `/etc/nginx/modules-enabled/50-mod-http-modsecurity.conf` and installs
`modsecurity.conf` (the recommended base configuration, `SecRuleEngine DetectionOnly`), `unicode.mapping` and
`modsecurity_includes.conf` into `/etc/nginx/`, plus a sample site at
`/etc/nginx/sites-available/default-modsecurity.conf`. Turn it on per server or location with `modsecurity on;`
and `modsecurity_rules_file /etc/nginx/modsecurity_includes.conf;`, and include the CRS from that file by
uncommenting the `owasp-crs.load` line. libModSecurity has no `IncludeOptional`, so replace that directive by
`Include` in the files the CRS package installs. NGINX reports most CRS events at `error_log ... info;`.

On Fedora and EPEL:

```bash
sudo dnf install nginx-mod-modsecurity
```

The module is loaded from `/usr/share/nginx/modules/mod-modsecurity.conf`, the base configuration is installed
as `/etc/nginx/modsecurity.conf`, and `/etc/nginx/nginx.conf.modsecurity` is a sample server configuration; add
the `modsecurity` directives to your own server blocks as shown below.

## Compilation

Get the connector source:

```bash
wget https://github.com/owasp-modsecurity/ModSecurity-nginx/releases/download/v{{< param modsec_nginx_latest >}}/ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity-nginx/releases/download/v{{< param modsec_nginx_latest >}}/ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.sha256
wget https://github.com/owasp-modsecurity/ModSecurity-nginx/releases/download/v{{< param modsec_nginx_latest >}}/ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.asc
sha256sum -c ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.sha256
gpg --verify ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.asc ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
tar xzf ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
```

or clone the development branch with `git clone https://github.com/owasp-modsecurity/ModSecurity-nginx`.
Install libModSecurity first (see [Building libModSecurity v3 from source]({{% relref "2-1-building-libmodsecurity" %}})
or your distribution's `libmodsecurity-dev` / `libmodsecurity-devel` package). The connector's `config`
script looks for the library under `/usr/local/modsecurity`; for any other location export `MODSECURITY_INC`
(the directory holding `modsecurity/modsecurity.h`) and `MODSECURITY_LIB` (the directory holding
`libmodsecurity.so`) before running NGINX's `configure`.

From the NGINX source directory, add the connector as a static module:

```bash
./configure --add-module=/path/to/ModSecurity-nginx
make
sudo make install
```

Or build it as a dynamic module. The NGINX source version and configure arguments must then match the NGINX
binary you load it into (`nginx -V` prints them):

```bash
./configure --add-dynamic-module=/path/to/ModSecurity-nginx --with-compat
make modules
```

and load it with `load_module modules/ngx_http_modsecurity_module.so;` at the top of `nginx.conf`.

The connector runs ModSecurity phase 1 in NGINX's rewrite phase, phase 2 in the preaccess phase (the
development branch has moved it to the access phase, after `allow`/`deny` and `auth_*`), phases 3 and 4 in the
header and body filters, and phase 5 in the log phase.

## Configuration directives

The connector adds the following directives, all valid in the `http`, `server` and `location` contexts. The
`modsecurity_rules*` directives may be repeated and accumulate; a `location` inherits the rules of its `server`.

### modsecurity

{{< secmeta syntax="modsecurity on | off" default="off" v3="yes" v2="no" >}}

Turns ModSecurity on or off for the context. This flag only enables the module in NGINX; the rule engine state
is controlled separately by [SecRuleEngine]({{% relref "3-reference-manual/3-2-configuration-directives#secruleengine" %}}).

### modsecurity_rules_file

{{< secmeta syntax="modsecurity_rules_file <path to rules file>" v3="yes" v2="no" >}}

Loads ModSecurity configuration and rules from a file:

```nginx
server {
    modsecurity on;
    location / {
        root /var/www/html;
        modsecurity_rules_file /etc/my_modsecurity_rules.conf;
    }
}
```

### modsecurity_rules_remote

{{< secmeta syntax="modsecurity_rules_remote <key> <URL to rules>" v3="yes" v2="no" >}}

Downloads the configuration from a URL, authenticating with the given key, exactly like
[SecRemoteRules]({{% relref "3-reference-manual/3-2-configuration-directives#secremoterules" %}}) (libModSecurity must be built with libcurl):

```nginx
server {
    modsecurity on;
    location / {
        root /var/www/html;
        modsecurity_rules_remote my-server-key https://my-own-server/rules/download;
    }
}
```

### modsecurity_rules

{{< secmeta syntax="modsecurity_rules <modsecurity rules>" v3="yes" v2="no" >}}

Embeds rules directly in the NGINX configuration, which is handy for per-location overrides:

```nginx
server {
    modsecurity on;
    location / {
        root /var/www/html;
        modsecurity_rules_file /etc/my_modsecurity_rules.conf;
    }
    location /ops {
        root /var/www/html/opts;
        modsecurity_rules '
          SecRuleEngine On
          SecDebugLog /tmp/modsec_debug.log
          SecDebugLogLevel 9
          SecRuleRemoveById 10
        ';
    }
}
```

### modsecurity_transaction_id

{{< secmeta syntax="modsecurity_transaction_id string" v3="yes" v2="no" >}}

Supplies the transaction ID from NGINX instead of letting the library generate one. The string may contain NGINX
variables, so access-log and audit-log entries can be correlated:

```nginx
log_format extended '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" $request_id';

server {
    server_name host1;
    modsecurity on;
    modsecurity_transaction_id "host1-$request_id";
    access_log logs/host1-access.log extended;
    error_log logs/host1-error.log;
    location / {
        ...
    }
}
```

### modsecurity_use_error_log

{{< secmeta syntax="modsecurity_use_error_log on | off" default="on" v3="yes" v2="no" v3note="(connector development branch only, not in v1.0.4)" >}}

Controls whether ModSecurity alert messages are also written to the NGINX error log. This directive exists only
on the connector's `master` branch; the 1.0.4 release does not know it and refuses to start with it in the
configuration. Distribution packages built from release tarballs do not have it either.
