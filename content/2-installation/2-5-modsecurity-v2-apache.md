---
title: ModSecurity v2 for Apache
weight: 5
---

## Prerequisites

### Apache httpd 2.x

ModSecurity 2.x works with Apache httpd 2.0.x or later (2.4.x is the version in common use today). You need the Apache development files (the `apxs` tool and headers), which distributions package as `httpd-devel` or `apache2-dev`.

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

## Installation Methods

Before you begin with installation you will need to choose your preferred installation method. First you need to choose whether to install the latest version of ModSecurity directly from git (best features, but possibly unstable) or use the latest stable release (recommended). If you choose a stable release, it might be possible to install ModSecurity from a binary package provided by your distribution. It is always possible to compile it from source code.

## GitHub Access

If you want to access the latest version of the module you need to get it from the git repository. The list of changes made since the last stable release is in the file `CHANGES`. The repository is hosted on GitHub: <https://github.com/owasp-modsecurity/ModSecurity>. The v2 code lives on the `v2/master` branch (the default branch is v3).

To download the latest v2 source code to your computer, execute:

``` bash
git clone --branch v2/master https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule update --init --recursive
```

Then build:

1.  Generate the configure script - `./autogen.sh`
2.  Run configure script - `./configure`
3.  Run make - `make`
4.  Run make install - `make install`
5.  Copy the new mod_security2.so file into the proper Apache modules directory, if `make install` did not place it there - `cp /usr/local/modsecurity/lib/mod_security2.so /usr/local/apache/modules/`

## Stable Release Download

The current v2 release is v{{< param modsec_v2_latest >}}. Releases are published on GitHub as a signed source
tarball (no binaries):

```bash
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.sha256
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v2_latest >}}/modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.asc
sha256sum -c modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.sha256
gpg --verify modsecurity-v{{< param modsec_v2_latest >}}.tar.gz.asc modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
tar xzf modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
cd modsecurity-v{{< param modsec_v2_latest >}}
```

## Installation Steps

- Stop Apache httpd
- Unpack the ModSecurity archive
- Build

Building differs for UNIX (or UNIX-like) operating systems and Windows.

### UNIX

Run the configure script to generate a Makefile. Typically no options are needed.

``` bash
./configure
```

Options are available for more customization (use `./configure --help` for a full list), but typically you will only need to specify the location of the apxs command installed by Apache httpd with the `--with-apxs` option.

``` bash
./configure --with-apxs=/path/to/httpd-2.x.y/bin/apxs
```

{{% notice note %}}

There are certain configure options that are meant for debugging and other development use. If enabled, these options can substantially impact performance. These options include all `--debug-*` options as well as the `--enable-performance-measurement` option.

{{% /notice %}}

Compile with:

``` bash
make
```

Optionally test with:

``` bash
make CFLAGS=-DMSC_TEST test
```

{{% notice note %}}

Most common test failures are related to not finding the required headers and/or libraries. If you have problems, open an issue with the full output and error from the build.

{{% /notice %}}

Optionally build the ModSecurity Log Collector with:

``` bash
make mlogc
```

Optionally install mlogc: review the `INSTALL` file included in the `mlogc` directory of the distribution. Install the ModSecurity module with:

``` bash
make install
```

### Windows

ModSecurity for Apache httpd on Windows is built with CMake and Visual Studio. The steps and the tested dependency versions are described in [README_WINDOWS.md](https://github.com/owasp-modsecurity/ModSecurity/blob/v2/master/README_WINDOWS.md) in the v2 source tree; Apache must be built from source with the same compiler.

### Edit the main Apache httpd config file (usually httpd.conf)

On UNIX (and on Windows if the DLLs are not in the Apache `bin` directory) you may need to load libxml2 and Lua before ModSecurity if they are not found automatically:

``` apache
LoadFile /usr/lib/libxml2.so
LoadFile /usr/lib/liblua5.4.so
```

Load the ModSecurity module with:

``` apache
LoadModule security2_module modules/mod_security2.so
```

### Configure ModSecurity

Copy `modsecurity.conf-recommended` from the source tree to your Apache configuration directory as `modsecurity.conf`, together with `unicode.mapping`, and include it from `httpd.conf`. See [Recommended Base Configuration]({{% relref "3-reference-manual/3-10-recommended-base-configuration" %}}). Then add a rule set, typically the [OWASP CRS](https://coreruleset.org/).

### Start Apache httpd

You should now have ModSecurity 2.x up and running.

## Build Notes

{{% notice note %}}

If you have compiled Apache yourself you might experience problems compiling ModSecurity against PCRE. This is because Apache bundles PCRE but this library is also typically provided by the operating system. Most vendor-packaged Apache distributions are configured to use an external PCRE library, so this should not be a problem.

{{% /notice %}}

You want to avoid Apache using the bundled PCRE library and ModSecurity linking against the one provided by the operating system. The easiest way to do this is to compile Apache against the PCRE library provided by the operating system (or against the latest PCRE2 version downloaded from the PCRE site) using Apache's `--with-pcre` configure switch. If you are not in a position to recompile Apache, then, to compile ModSecurity successfully, you need access to the bundled PCRE headers (they are available only in the Apache source code) and must point ModSecurity at them via its `--with-pcre` or `--with-pcre2` configure option.

Non-gcc compilers may have problems running out-of-the-box as the current build system was designed around the gcc compiler and some compiler/linker flags may differ. To use a non-gcc compiler you may need some manual Makefile tweaks if issues cannot be solved by exporting custom `CFLAGS` and `CPPFLAGS` environment variables.

If you are upgrading from ModSecurity 1.x, see [Migrating from 1.x to 2.x]({{% relref "6-migration/6-2-migrating-from-1x-to-2x" %}}).

Configure options worth knowing:

1.  **--enable-pcre-jit** - Enables JIT support from PCRE >= 8.20 / PCRE2 that can improve regex performance.
2.  **--enable-pcre-study** - Enables PCRE pattern studying (`WITH_PCRE_STUDY`), which can give a slight performance edge.
3.  **--enable-lua-cache** - Enables Lua VM caching that can improve Lua script performance. The difference only appears if ModSecurity must run more than one script per transaction.
4.  **--enable-request-early** - Since ModSecurity 2.6 phase 1 runs in Apache's fixups hook; this option moves it back to the post-read-request hook (see [Processing Phases]({{% relref "3-reference-manual/3-1-processing-phases" %}})).
5.  **--enable-htaccess-config** - Allows the following directives to be used in `.htaccess` files when `AllowOverride Options` is set:

``` apache
        - SecAction
        - SecRule

        - SecRuleRemoveByMsg
        - SecRuleRemoveByTag
        - SecRuleRemoveById

        - SecRuleUpdateActionById
        - SecRuleUpdateTargetById
        - SecRuleUpdateTargetByTag
        - SecRuleUpdateTargetByMsg
```
