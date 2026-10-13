---
title: Building libModSecurity v3 from source
weight: 1
---

libModSecurity is a C++17 library. On Unix-like systems it is built with autotools; Windows builds are
described in the [Windows build README](https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/build/win32/README.md).
After installing the library, add a connector for your web server: see
[libModSecurity v3 with NGINX]({{% relref "2-2-libmodsecurity-v3-nginx" %}}) or the
[Apache connector](https://github.com/owasp-modsecurity/ModSecurity-apache).

## Dependencies

- **Required:** a C++17 compiler, GNU autotools, Flex and Bison (they build the SecRules language parser), and
  [YAJL](https://github.com/lloyd/yajl) (JSON is used for logging and for the test framework).
- **Regular expressions:** PCRE2 is detected and used by default. Legacy PCRE is used only when `--with-pcre`
  is passed to `./configure`.
- **Optional, feature-gated:** `libxml2` (XML request bodies), `libcurl` (`SecRemoteRules`), LMDB (persistent
  storage), Lua (`SecRuleScript` and `@inspectFile` scripts), and `libmaxminddb` for `@geoLookup`.
  If a library is missing, ModSecurity is compiled without the corresponding operator or directive.

{{% notice warning %}}
The legacy MaxMind **GeoIP C API** (libGeoIP) is deprecated and no longer maintained. Use **libmaxminddb**
with a GeoLite2/GeoIP2 database instead.
{{% /notice %}}

Git submodules under `others/` (`libinjection` for `@detectSQLi` and `@detectXSS`, and `mbedtls` for hashing
and base64 helpers) are effectively required for source builds and must be initialized before building.

## Get the source

**Stable release (recommended).** The current release is v{{< param modsec_v3_latest >}}. The release tarball
already bundles the git submodules, and is signed:

```bash
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.sha256
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.asc
sha256sum -c modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.sha256
gpg --verify modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.asc modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
tar xzf modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
cd modsecurity-v{{< param modsec_v3_latest >}}
```

**Development branch.** For the latest code, clone `v3/master` recursively, or initialize the submodules after cloning:

```bash
git clone --branch v3/master https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule update --init --recursive
```

Verify that every submodule shows a commit hash in `git submodule status`; a leading `-` means it was not
initialized and the build will fail.

## Build

```bash
./build.sh
./configure
make
sudo make install
```

The library is installed under `/usr/local/modsecurity` by default. Because it is a dynamic library, that
location must be known to the dynamic linker (for example through `ldconfig` or `LD_LIBRARY_PATH`).

Run the unit and regression tests after building:

```bash
make check
```

Distribution-specific package lists and copy-and-paste build scripts are collected in
[Distribution-specific build recipes]({{% relref "2-4-distribution-recipes" %}}).
