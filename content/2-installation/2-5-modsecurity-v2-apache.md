---
title: ModSecurity v2 for Apache
weight: 5
---

ModSecurity v2 is an Apache httpd module (`mod_security2`). The current release is v{{< param modsec_v2_latest >}}. You can install it from your distribution's package repository, which is the quickest route and gets you security updates through the normal package channels, or build it from source to get the latest release.

## Prerequisites

### Apache httpd 2.x

ModSecurity 2.x works with Apache httpd 2.0.x or later (2.4.x is the version in common use today). To build from source you need the Apache development files (the `apxs` tool and headers), which distributions package as `httpd-devel` or `apache2-dev`.

### mod_unique_id

Make sure you have `mod_unique_id` loaded. It is packaged with Apache httpd and ModSecurity uses it for the `UNIQUE_ID` variable and audit log entry identifiers.

### libapr and libapr-util

Required. <https://apr.apache.org/>. APR-util must be compiled with crypto support if you intend to use the `crypto` parameter of [SecRemoteRules]({{% relref "3-reference-manual/3-2-configuration-directives#secremoterules" %}}); otherwise configure prints a warning and continues.

### libpcre2 (or libpcre)

Required. ModSecurity 2.9.x uses PCRE2 by default (<https://www.pcre.org/>). The legacy PCRE 8.x library is still supported: pass `--with-pcre=PATH` to configure to use it, in which case the PCRE2 check is skipped.

### libxml2

Required. <https://gitlab.gnome.org/GNOME/libxml2>. Used by the XML request body processor and the `@validateDTD`/`@validateSchema` operators.

### libyajl

Needed for the JSON request body processor. Configure detects it automatically (`--with-yajl=PATH` to point at a custom location); without it ModSecurity builds without JSON support.

### liblua 5.x

Optional; only needed for [SecRuleScript]({{% relref "3-reference-manual/3-2-configuration-directives#secrulescript" %}}) and the `exec` action with Lua scripts. Lua 5.1 through 5.5 are supported (`--with-lua=PATH`). <https://www.lua.org/download.html>

{{% notice note %}}

ModSecurity requires the dynamic Lua library. It is not built by default in the Lua source distribution, so the binary package of your distribution is recommended.

{{% /notice %}}

### libcurl

Optional. Needed for [SecRemoteRules]({{% relref "3-reference-manual/3-2-configuration-directives#secremoterules" %}}) and for the ModSecurity Log Collector (mlogc), which sends audit logs to a central repository. Without libcurl, configure disables building mlogc. <https://curl.se/libcurl/>

{{% notice note %}}

Many have had issues with libcurl linked with the GnuTLS library for SSL/TLS support. It is recommended that the OpenSSL library be used for SSL/TLS support in libcurl.

{{% /notice %}}

### libfuzzy (ssdeep)

Optional; only needed for the `@fuzzyHash` operator (`--with-ssdeep=PATH`).

## Distribution Packages

Every major distribution packages ModSecurity v2 for Apache. Packaged versions lag behind the upstream release, sometimes by several minor versions, but the distributions backport security fixes to the version they ship, so an older version number does not by itself mean an unpatched module. If you need a feature from a newer release, build from source instead.

Versions in the distributions' package repositories as of October 2026:

| Distribution | Package | Version |
|---|---|---|
| Debian 12 (bookworm) | `libapache2-mod-security2` | 2.9.7 |
| Debian 13 (trixie) | `libapache2-mod-security2` | 2.9.11 |
| Ubuntu 22.04 LTS | `libapache2-mod-security2` | 2.9.5 |
| Ubuntu 24.04 LTS | `libapache2-mod-security2` | 2.9.7 |
| Ubuntu 26.04 LTS | `libapache2-mod-security2` | 2.9.12 |
| RHEL 8 and 9, AlmaLinux, Rocky Linux, CentOS Stream (EPEL) | `mod_security` | 2.9.6 |
| RHEL 10 family (EPEL 10) | `mod_security` | 2.9.14 |
| Fedora 43 and 44 | `mod_security` | 2.9.14 |
| openSUSE Leap 15.6 | `apache2-mod_security2` | 2.9.4 |
| openSUSE Tumbleweed | `apache2-mod_security2` | 2.9.12 |
| FreeBSD ports | `www/mod_security` (`ap24-mod_security`) | 2.9.15 |
| Gentoo | `www-apache/mod_security` | 2.9.14 |
| macOS (MacPorts) | `www/mod_security2` | 2.9.15 |

Alpine Linux, Arch Linux and Amazon Linux 2023 do not package ModSecurity v2; build from source or use the container image there. The OWASP CRS project separately packages the [OWASP CRS](https://coreruleset.org/) rule set for most of these distributions (`modsecurity-crs` on Debian and Ubuntu, `mod_security_crs` on Fedora and EPEL).

### Debian and Ubuntu

``` bash
sudo apt install libapache2-mod-security2
sudo cp /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
sudo a2enmod security2
sudo systemctl restart apache2
```

The package enables the module through `/etc/apache2/mods-available/security2.load` and `security2.conf`. The latter sets `SecDataDir /var/cache/modsecurity` and includes every `*.conf` file in `/etc/modsecurity/`, so that directory is where your `modsecurity.conf` and any local rule files go; `unicode.mapping` is already installed there. The audit log goes to `/var/log/apache2/modsec_audit.log` by default. The shipped `modsecurity.conf-recommended` leaves the engine in `DetectionOnly`; switch `SecRuleEngine` to `On` once you have reviewed the logs.

### RHEL, AlmaLinux, Rocky Linux, CentOS Stream

The module comes from EPEL (Extra Packages for Enterprise Linux):

``` bash
sudo dnf install epel-release        # on RHEL itself: dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(rpm -E %rhel).noarch.rpm
sudo dnf install mod_security
sudo systemctl restart httpd
```

### Fedora

``` bash
sudo dnf install mod_security
sudo systemctl restart httpd
```

On Fedora and EPEL the module is loaded by `/etc/httpd/conf.modules.d/10-mod_security.conf` (which also loads `mod_unique_id` if needed) and configured by `/etc/httpd/conf.d/mod_security.conf`. That file carries the recommended base configuration with `SecRuleEngine On` already set, response body access off, logs under `/var/log/httpd/`, persistent data under `/var/lib/mod_security`, and it includes `/etc/httpd/modsecurity.d/*.conf`, `modsecurity.d/activated_rules/*.conf` and `modsecurity.d/local_rules/*.conf`. Put your own rules in `local_rules/`.

### openSUSE

``` bash
sudo zypper install apache2-mod_security2
sudo a2enmod security2
sudo systemctl restart apache2
```

Run `rpm -ql apache2-mod_security2` to see where the package placed its configuration and the recommended configuration file.

### FreeBSD

``` bash
pkg install ap24-mod_security
```

Or build the port from `www/mod_security`. The port installs the module into the Apache modules directory and the sample configuration files under `/usr/local/etc/modsecurity/`; add the `LoadModule security2_module libexec/apache24/mod_security2.so` line to `httpd.conf` and include your configuration from there.

### Gentoo

``` bash
emerge www-apache/mod_security
```

Add `-D SECURITY` to `APACHE2_OPTS` in `/etc/conf.d/apache2` to load the module.

### Containers

The OWASP CRS project publishes ready-to-run images for Docker and compatible runtimes. `owasp/modsecurity` contains Apache httpd with ModSecurity v2 and no rules (tags `apache`, `2-<timestamp>`, with `-alpine` variants); `owasp/modsecurity-crs` bundles the OWASP CRS on top of it and is the image most deployments want. See <https://github.com/coreruleset/modsecurity-crs-docker> for the tags and the environment variables that configure the engine.

``` bash
docker run -p 8080:8080 owasp/modsecurity-crs:apache
```

## Building from Source

### From the release tarball

Releases are published on GitHub as a signed source tarball (no binaries). Install the prerequisites above with their development headers first (for example `apt install apache2-dev libpcre2-dev libxml2-dev libyajl-dev liblua5.4-dev libcurl4-openssl-dev` on Debian and Ubuntu, or `dnf install httpd-devel pcre2-devel libxml2-devel yajl-devel lua-devel libcurl-devel` on Fedora and RHEL), then:

```bash
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.sha256
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.asc
sha256sum -c modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.sha256
gpg --verify modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.asc modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
tar xzf modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
cd modsecurity-v{{< param modsec_v2_latest >}}
./configure
make
make install
```

### From git

The repository is hosted on GitHub: <https://github.com/owasp-modsecurity/ModSecurity>. The v2 code lives on the `v2/master` branch (the default branch is v3). The list of changes made since the last stable release is in the file `CHANGES`. A git checkout needs the autotools (`autoconf`, `automake`, `libtool`) in addition to the prerequisites above, and the libinjection submodule:

``` bash
git clone --branch v2/master https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule update --init --recursive
./autogen.sh
./configure
make
make install
```

### Configure options

Run the configure script to generate a Makefile. Typically no options are needed (`./configure --help` lists them all); the one you are most likely to need is the location of the `apxs` command installed by Apache httpd:

``` bash
./configure --with-apxs=/path/to/httpd-2.x.y/bin/apxs
```

Options worth knowing:

1. **--enable-pcre-jit** - Enables JIT support from PCRE >= 8.20 / PCRE2 that can improve regex performance.
2. **--enable-pcre-study** - Enables PCRE pattern studying (`WITH_PCRE_STUDY`), which can give a slight performance edge.
3. **--enable-lua-cache** - Enables Lua VM caching that can improve Lua script performance. The difference only appears if ModSecurity must run more than one script per transaction.
4. **--enable-request-early** - Since ModSecurity 2.6 phase 1 runs in Apache's fixups hook; this option moves it back to the post-read-request hook (see [Processing Phases]({{% relref "3-reference-manual/3-1-processing-phases" %}})).
5. **--enable-htaccess-config** - Allows the following directives to be used in `.htaccess` files when `AllowOverride Options` is set: `SecAction`, `SecRule`, `SecRuleRemoveById`, `SecRuleRemoveByMsg`, `SecRuleRemoveByTag`, `SecRuleUpdateActionById`, `SecRuleUpdateTargetById`, `SecRuleUpdateTargetByMsg` and `SecRuleUpdateTargetByTag`.

{{% notice note %}}

There are certain configure options that are meant for debugging and other development use. If enabled, these options can substantially impact performance. These options include all `--enable-debug-*` options as well as the `--enable-performance-measurement` option.

{{% /notice %}}

### Testing and installing

Optionally run the unit and regression tests before installing:

``` bash
make test
```

{{% notice note %}}

Most common test failures are related to not finding the required headers and/or libraries. If you have problems, open an issue with the full output and error from the build.

{{% /notice %}}

Optionally build the ModSecurity Log Collector with `make mlogc`; to install it, review the `INSTALL` file in the `mlogc` directory of the distribution. `make install` copies `mod_security2.so` into the Apache modules directory reported by `apxs`; if your layout differs, copy it by hand, for example `cp /usr/local/modsecurity/lib/mod_security2.so /usr/local/apache/modules/`.

### Windows

ModSecurity for Apache httpd on Windows is built with CMake and Visual Studio. The steps and the tested dependency versions are described in [README_WINDOWS.md](https://github.com/owasp-modsecurity/ModSecurity/blob/v2/master/README_WINDOWS.md) in the v2 source tree; Apache must be built from source with the same compiler. For IIS see [ModSecurity v2 for IIS]({{% relref "2-installation/2-6-modsecurity-v2-iis" %}}).

## Loading and Configuring the Module

Skip this section if you installed a distribution package: the package already loads the module and includes a configuration directory, as described above.

On UNIX (and on Windows if the DLLs are not in the Apache `bin` directory) you may need to load libxml2 and Lua before ModSecurity if they are not found automatically:

``` apache
LoadFile /usr/lib/libxml2.so
LoadFile /usr/lib/liblua5.4.so
```

Load the ModSecurity module in `httpd.conf` with:

``` apache
LoadModule security2_module modules/mod_security2.so
```

Copy `modsecurity.conf-recommended` from the source tree to your Apache configuration directory as `modsecurity.conf`, together with `unicode.mapping`, and include it from `httpd.conf`. See [Recommended Base Configuration]({{% relref "3-reference-manual/3-10-recommended-base-configuration" %}}). Then add a rule set, typically the [OWASP CRS](https://coreruleset.org/), and restart Apache httpd. You should now have ModSecurity 2.x up and running.

## Build Notes

{{% notice note %}}

If you have compiled Apache yourself you might experience problems compiling ModSecurity against PCRE. This is because Apache bundles PCRE but this library is also typically provided by the operating system. Most vendor-packaged Apache distributions are configured to use an external PCRE library, so this should not be a problem.

{{% /notice %}}

You want to avoid Apache using the bundled PCRE library and ModSecurity linking against the one provided by the operating system. The easiest way to do this is to compile Apache against the PCRE library provided by the operating system (or against the latest PCRE2 version downloaded from the PCRE site) using Apache's `--with-pcre` configure switch. If you are not in a position to recompile Apache, then, to compile ModSecurity successfully, you need access to the bundled PCRE headers (they are available only in the Apache source code) and must point ModSecurity at them via its `--with-pcre` or `--with-pcre2` configure option.

Non-gcc compilers may have problems running out-of-the-box as the current build system was designed around the gcc compiler and some compiler/linker flags may differ. To use a non-gcc compiler you may need some manual Makefile tweaks if issues cannot be solved by exporting custom `CFLAGS` and `CPPFLAGS` environment variables.

If you are upgrading from ModSecurity 1.x, see [Migrating from 1.x to 2.x]({{% relref "6-migration/6-2-migrating-from-1x-to-2x" %}}).
