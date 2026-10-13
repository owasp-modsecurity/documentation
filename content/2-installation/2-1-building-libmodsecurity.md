---
title: Building libModSecurity v3 from source
weight: 1
---

libModSecurity is a C++17 library. On Unix-like systems it is built with autotools; Windows builds use CMake and
Conan and are described in the [Windows build README](https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/build/win32/README.md).
The library does nothing on its own: after installing it, add a connector for your web server, see
[libModSecurity v3 with NGINX]({{% relref "2-2-libmodsecurity-v3-nginx" %}}) and
[libModSecurity v3 with Apache]({{% relref "2-3-libmodsecurity-v3-apache" %}}).

If you only need a working installation, your distribution most likely packages the library and the NGINX
connector already; see [Distribution packages for libModSecurity v3]({{% relref "2-4-distribution-recipes" %}}).
Build from source when you need the current release before your distribution ships it, a build option the
package does not enable (LMDB, Lua, ssdeep), or the development branch.

## Dependencies

| Library | Status | What it enables |
|---|---|---|
| C++17 compiler, GNU autotools, `pkg-config` | required | the build itself |
| [YAJL](https://github.com/lloyd/yajl) 2.x | required | JSON request bodies, JSON audit log, the test suite |
| PCRE2 (`libpcre2-8`) | required, default | `@rx` and every other regular-expression user. Legacy PCRE 8.x is used instead only with `--with-pcre` |
| libxml2 >= 2.6.29 | optional, auto-detected | XML request body processor, `XML` variable, `@validateDTD`, `@validateSchema` |
| libcurl >= 7.15.1 | optional, auto-detected | `SecRemoteRules`, remote `@pmFromFile`/`@ipMatchFromFile` files, the Status Engine |
| Lua 5.1 to 5.5 or LuaJIT | optional, auto-detected | `SecRuleScript`, `exec` and `@inspectFile` with Lua scripts |
| libmaxminddb | optional, auto-detected | `@geoLookup` with GeoLite2/GeoIP2 databases |
| libfuzzy (ssdeep) | optional, auto-detected | `@fuzzyHash` |
| LMDB | optional, opt-in | on-disk persistent collections (`SecDataDir`); without it collections live in process memory |
| Flex and Bison | only with `--enable-parser-generation` | regenerating the SecLang parser; the release tarball and the git tree ship a generated parser |

When an optional library is missing, the corresponding operator or directive is compiled out and a configuration
using it fails to load. LMDB is special: even when the library is installed, it is not used unless you pass
`--with-lmdb` explicitly.

{{% notice warning %}}
The legacy MaxMind GeoIP C API (libGeoIP, `--with-geoip`) is still accepted but deprecated and no longer
maintained upstream. Use libmaxminddb with a GeoLite2 or GeoIP2 database instead.
{{% /notice %}}

The git tree also carries submodules under `others/`: `libinjection` (`@detectSQLi`, `@detectXSS`) and
`mbedtls` (hashing and base64 helpers). Both are required for a source build and must be initialized after cloning;
the release tarball bundles them.

Package names for the development headers, for the two most common families:

```bash
# Debian and Ubuntu
sudo apt install build-essential automake libtool pkg-config libyajl-dev libpcre2-dev libxml2-dev \
    libcurl4-openssl-dev liblua5.4-dev libmaxminddb-dev libfuzzy-dev liblmdb-dev
# Fedora, RHEL and EPEL
sudo dnf install gcc-c++ automake libtool pkgconf yajl-devel pcre2-devel libxml2-devel \
    libcurl-devel lua-devel libmaxminddb-devel ssdeep-devel lmdb-devel
```

## Get the source

**Stable release (recommended).** The current release is v{{< param modsec_v3_latest >}}. The release tarball
already bundles the git submodules and is signed:

```bash
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.sha256
wget https://github.com/owasp-modsecurity/ModSecurity/releases/download/v{{< param modsec_v3_latest >}}/modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.asc
sha256sum -c modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.sha256
gpg --verify modsecurity-v{{< param modsec_v3_latest >}}.tar.gz.asc modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
tar xzf modsecurity-v{{< param modsec_v3_latest >}}.tar.gz
cd modsecurity-v{{< param modsec_v3_latest >}}
```

**Development branch.** For the latest code, clone `v3/master` and initialize the submodules:

```bash
git clone --branch v3/master https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule update --init --recursive
```

Verify that every submodule shows a commit hash in `git submodule status`; a leading `-` means it was not
initialized and the build will fail.

## Build

```bash
./build.sh        # git checkout only: generates the configure script
./configure
make
sudo make install
```

The library is installed under `/usr/local/modsecurity` by default (`--prefix` changes that). Because it is a
dynamic library, that location must be known to the dynamic linker: add `/usr/local/modsecurity/lib` to
`/etc/ld.so.conf.d/` and run `ldconfig`, or set `LD_LIBRARY_PATH`. The `modsecurity.pc` file installed under
`lib/pkgconfig` lets other software find the library through `pkg-config`.

Run the unit and regression tests after building:

```bash
make check
```

## Configure options

Every optional library has a `--with-NAME=PATH` option that points at an installation prefix, and a
`--without-NAME` form that disables the feature even when the library is present:

| Option | Default | Effect |
|---|---|---|
| `--with-pcre2=PATH` | auto-detected | PCRE2, the regular-expression engine used by default |
| `--with-pcre=PATH` | off | build against legacy PCRE 8.x instead of PCRE2 |
| `--with-yajl=PATH` | auto-detected, required | YAJL location |
| `--with-libxml=PATH` | auto-detected | libxml2 |
| `--with-curl=PATH` | auto-detected | libcurl; versions from 7.34.0 enable TLS 1.2 for remote rule downloads |
| `--with-lua=PATH` | auto-detected | Lua (5.1 to 5.5 or LuaJIT) |
| `--with-maxmind=PATH` | auto-detected | libmaxminddb for `@geoLookup` |
| `--with-geoip=PATH` | auto-detected | legacy libGeoIP for `@geoLookup` (deprecated) |
| `--with-ssdeep=PATH` | auto-detected | libfuzzy for `@fuzzyHash` |
| `--with-lmdb[=PATH]` | off | LMDB-backed persistent collections |

Feature switches:

| Option | Default | Effect |
|---|---|---|
| `--enable-parser-generation` | off | regenerate the SecLang parser with Flex and Bison instead of using the shipped one. Needed only when you change `src/parser/*.yy` or `*.ll` |
| `--disable-examples` | examples built | skip the example programs in `examples/` |
| `--disable-debug-logs` | debug logs built | compile `SecDebugLog` support out (`NO_LOGS`) for a slightly faster library; the regression tests cannot run without it |
| `--enable-assertions` | off | keep `assert()` checks (undefines `NDEBUG`) |
| `--enable-mutex-on-pm` | off | serialize `@pm` and `@pmFromFile` evaluation with a mutex; only for debugging suspected races in multi-threaded connectors |
| `--enable-afl-fuzz` | off | build the AFL fuzzing utilities |
| `--enable-valgrind` | off | run the unit tests under Valgrind (`--disable-valgrind-memcheck` and friends select the tools) |
| `--enable-doxygen-*` / `--disable-doxygen-*` | HTML only | which Doxygen outputs `make doxygen-doc` produces |

{{% notice note %}}
The output of `./configure --help` is misleading for the library options: because of how they are generated,
only `--with-yajl` is listed, but all of the `--with-*` options above are accepted. The summary that configure
prints at the end shows which libraries were found.
{{% /notice %}}
