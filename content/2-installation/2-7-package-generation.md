---
title: Building distribution packages
weight: 7
---

Distribution packages lag behind upstream releases, so it is common to need a package of a newer ModSecurity version, or one built with different options, for a distribution that does not ship it yet. The quickest way to get one is to rebuild the distribution's own packaging against the newer source tarball rather than writing a spec or `debian/` directory from scratch: the packaging already carries the configuration layout, the module loading snippets and the dependencies the distribution expects.

## ModSecurity v2 (Apache)

### Debian and Ubuntu

The packaging lives at <https://salsa.debian.org/debian/modsecurity-apache> (source package `modsecurity-apache`, binary `libapache2-mod-security2`). To rebuild it against a newer upstream release:

``` bash
sudo apt install build-essential devscripts
sudo apt build-dep modsecurity-apache
apt source modsecurity-apache
cd modsecurity-apache-*/
uupdate --upstream-version {{< param modsec_v2_latest >}} ../modsecurity-v{{< param modsec_v2_latest >}}.tar.gz
cd ../modsecurity-apache-{{< param modsec_v2_latest >}}/
dpkg-buildpackage -us -uc -b
```

The resulting `libapache2-mod-security2_*.deb` lands in the parent directory. Download the release tarball as described in [ModSecurity v2 for Apache]({{% relref "2-installation/2-5-modsecurity-v2-apache#from-the-release-tarball" %}}) first; `apt source` needs a `deb-src` entry in your APT sources.

### Fedora, RHEL and EPEL

The packaging lives at <https://src.fedoraproject.org/rpms/mod_security> (`mod_security.spec`, the `mod_security.conf` base configuration and the `10-mod_security.conf` module snippet). To rebuild it against a newer upstream release:

``` bash
sudo dnf install fedpkg rpm-build rpmdevtools
fedpkg clone -a rpms/mod_security
cd mod_security
sudo dnf builddep mod_security.spec
rpmdev-bumpspec --new {{< param modsec_v2_latest >}} mod_security.spec
spectool -g -R mod_security.spec
fedpkg --release rawhide local      # or: rpmbuild -ba mod_security.spec
```

Use the branch that matches your target (`epel9`, `epel10`, `f44`, ...). Check the spec's `%prep` section for patches that no longer apply to the newer source; drop them if upstream already contains the fix.

### Other systems

- **FreeBSD**: the port is `www/mod_security`; bump `PORTVERSION` in its `Makefile`, run `make makesum` and build with `make package`.
- **openSUSE**: the package is `apache2-mod_security2` in the `Apache:Modules` project on the Open Build Service; branch it with `osc branch` and update the `Version` and source tarball in the spec.
- **Gentoo**: copy the `www-apache/mod_security` ebuild to a local overlay under the new version and run `ebuild ... manifest`.

## libModSecurity v3

The same approach applies to the v3 library and the nginx connector: Debian and Ubuntu package `libmodsecurity3` (source package `modsecurity`) and `libnginx-mod-http-modsecurity`; Fedora and EPEL package `libmodsecurity` but no nginx connector. Rebuild those packaging sources against the newer release with the commands above.
