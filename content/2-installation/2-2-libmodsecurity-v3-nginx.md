---
title: libModSecurity v3 with NGINX
weight: 2
---

The [ModSecurity-nginx connector](https://github.com/owasp-modsecurity/ModSecurity-nginx) links libModSecurity
into NGINX as a third-party module. Unlike the old (v2-era) standalone module, it is a thin layer between NGINX
and the library: install libModSecurity first (see [Building libModSecurity v3 from source]({{% relref "2-1-building-libmodsecurity" %}})),
then build the connector against your NGINX source.

## Compilation

Get the connector source. The current release is v{{< param modsec_nginx_latest >}}:

```bash
wget https://github.com/owasp-modsecurity/ModSecurity-nginx/releases/download/v{{< param modsec_nginx_latest >}}/ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity-nginx/releases/download/v{{< param modsec_nginx_latest >}}/ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.asc
gpg --verify ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz.asc ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
tar xzf ModSecurity-nginx-v{{< param modsec_nginx_latest >}}.tar.gz
```

or clone the development branch with `git clone https://github.com/owasp-modsecurity/ModSecurity-nginx`.

From the NGINX source directory, add the connector as a static module:

```bash
./configure --add-module=/path/to/ModSecurity-nginx
make
sudo make install
```

Or build it as a dynamic module. The NGINX source version must then match the NGINX binary you load it into:

```bash
./configure --add-dynamic-module=/path/to/ModSecurity-nginx --with-compat
make modules
```

and load it with `load_module modules/ngx_http_modsecurity_module.so;` at the top of `nginx.conf`.

## Configuration directives

The connector adds the following directives, all valid in the `http`, `server` and `location` contexts.

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

Downloads the configuration from a URL, authenticating with the given key:

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

{{< secmeta syntax="modsecurity_use_error_log on | off" default="on" v3="yes" v2="no" >}}

Controls whether ModSecurity messages are also written to the NGINX error log.
