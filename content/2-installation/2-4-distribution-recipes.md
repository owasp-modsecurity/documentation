---
title: Distribution packages for libModSecurity v3
weight: 4
---

Every major distribution packages libModSecurity, and most also package the NGINX connector built against it.
The packaged versions lag behind the upstream release, sometimes by several minor versions, but the distributions
backport security fixes to the version they ship. Versions in the package repositories as of October 2026:

| Distribution | Library package | Version | NGINX connector package | Version |
|---|---|---|---|---|
| Debian 12 (bookworm) | `libmodsecurity3` | 3.0.9 | `libnginx-mod-http-modsecurity` | 1.0.3 |
| Debian 13 (trixie) | `libmodsecurity3t64` | 3.0.14 | `libnginx-mod-http-modsecurity` | 1.0.3 |
| Ubuntu 22.04 LTS | `libmodsecurity3` | 3.0.6 | none | |
| Ubuntu 24.04 LTS | `libmodsecurity3` | 3.0.12 | `libnginx-mod-http-modsecurity` | 1.0.3 |
| Ubuntu 26.04 LTS | `libmodsecurity3t64` | 3.0.14 | `libnginx-mod-http-modsecurity` | 1.0.3 |
| RHEL 8 family (EPEL 8) | `libmodsecurity` | 3.0.15 | none | |
| RHEL 9 family (EPEL 9) | `libmodsecurity` | 3.0.17 | `nginx-mod-modsecurity` | 1.0.4 |
| Fedora 43 | `libmodsecurity` | 3.0.16 | `nginx-mod-modsecurity` | 1.0.4 |
| Fedora 44 | `libmodsecurity` | 3.0.17 | `nginx-mod-modsecurity` | 1.0.4 |
| openSUSE Leap 15.6 | `libmodsecurity3` (source `modsecurity`) | 3.0.10 | none | |
| openSUSE Tumbleweed | `libmodsecurity3` (source `modsecurity`) | 3.0.15 | none | |
| Arch Linux | `libmodsecurity` | 3.0.17 | `nginx-mod-modsecurity` | 1.0.4 |
| Gentoo | `dev-libs/modsecurity` | 3.0.16 | `www-nginx/ngx-modsecurity` | 1.0.4 |
| FreeBSD ports | `security/modsecurity3` | 3.0.17 | `security/modsecurity3-nginx` | 1.0.4 |
| macOS (Homebrew) | `modsecurity` | 3.0.17 | none | |

The development headers are in `libmodsecurity-dev` (Debian, Ubuntu) or `libmodsecurity-devel` (Fedora, EPEL,
openSUSE); install them when you build a connector yourself. The OWASP CRS rule set is packaged as
`modsecurity-crs` on Debian and Ubuntu and `mod_security_crs` on Fedora and EPEL. Alpine Linux and Amazon Linux
2023 do not package libModSecurity; use the container images or build from source there.

See [libModSecurity v3 with NGINX]({{% relref "2-2-libmodsecurity-v3-nginx#distribution-packages" %}}) for how the
Debian and Fedora connector packages are laid out and enabled.

## The digitalwave repository

[modsecurity.digitalwave.hu](https://modsecurity.digitalwave.hu/) is an APT repository for Debian and Ubuntu
maintained by Ervin Hegedüs, co-leader of the ModSecurity project and the Debian maintainer of these packages.
It builds the current `v2/master` and `v3/master` branches, the NGINX connector and the latest OWASP CRS release
for every supported Debian and Ubuntu version, as the same packages the distributions ship, so you get the
engine fixes months before they reach a distribution release. Packages are for amd64 only. As of October 2026 it
provides:

| Package | Content | Debian 11, 12, 13 and Ubuntu 22.04, 24.04, 26.04 |
|---|---|---|
| `libapache2-mod-security2` | ModSecurity v2 for Apache | 2.9.16 pre-release |
| `libmodsecurity3` / `libmodsecurity3t64`, `libmodsecurity-dev` | libModSecurity | 3.0.18 pre-release |
| `libnginx-mod-http-modsecurity` | NGINX connector | 1.0.5 pre-release (Debian 12, 13, Ubuntu 24.04, 26.04); on Ubuntu 22.04 as part of a rebuilt `nginx` 1.18.0 |
| `modsecurity-crs` | OWASP CRS | 3.3.10 |

The packages live in the `<release>-backports` suite of the repository. Ubuntu 22.04 also needs the plain
`<release>` suite, which carries the rebuilt `nginx` packages the connector is part of there. Add the key, the
suite and an APT pin so that only the ModSecurity packages come from this repository:

```bash
sudo apt install apt-transport-https lsb-release ca-certificates curl
# Debian 12 and later
sudo wget -qO - https://modsecurity.digitalwave.hu/archive.key | sudo tee /etc/apt/trusted.gpg.d/modsecurity-digitalwave.asc
# Ubuntu 24.04 and later
sudo wget -qO - https://modsecurity.digitalwave.hu/dwmodsec.gpg | sudo tee /etc/apt/trusted.gpg.d/modsecurity-digitalwave.gpg

# Debian (use .../ubuntu/ on Ubuntu)
echo "deb http://modsecurity.digitalwave.hu/debian/ $(lsb_release -sc)-backports main" | sudo tee /etc/apt/sources.list.d/dwmodsec.list

cat << EOF2 | sudo tee /etc/apt/preferences.d/99modsecurity
Package: *libnginx-mod-http-modsecurity*
Pin: origin modsecurity.digitalwave.hu
Pin-Priority: 900

Package: *libapache2-mod-security2*
Pin: origin modsecurity.digitalwave.hu
Pin-Priority: 900

Package: *modsecurity-crs*
Pin: origin modsecurity.digitalwave.hu
Pin-Priority: 900

Package: *libmodsecurity*
Pin: origin modsecurity.digitalwave.hu
Pin-Priority: 900
EOF2
sudo apt update
sudo apt install libnginx-mod-http-modsecurity modsecurity-crs   # or libapache2-mod-security2
```

Debian 11 and Ubuntu 22.04 use `apt-key add -` for the key and need both the `<release>` and
`<release>-backports` lines; the repository page has the exact commands for every release, the full version
matrix and the configuration walkthrough. Run `apt-cache policy libmodsecurity3` afterwards to confirm the
candidate comes from `modsecurity.digitalwave.hu`. If you previously installed the distribution's own package,
run `apt clean` first.

## Containers

The OWASP CRS project publishes images with NGINX and libModSecurity. `owasp/modsecurity` contains NGINX with the
connector and no rules (tags `nginx`, `3-<timestamp>`, with `-alpine` variants); `owasp/modsecurity-crs` bundles
the OWASP CRS on top of it and is the image most deployments want. See
<https://github.com/coreruleset/modsecurity-crs-docker> for the tags and the environment variables that
configure the engine.

```bash
docker run -p 8080:8080 owasp/modsecurity-crs:nginx
```

## Building packages

To build a newer version as a distribution package, rebuild the distribution's own packaging against the new
release rather than starting from scratch; see
[Building distribution packages]({{% relref "2-7-package-generation" %}}).
