---
title: Building distribution packages
weight: 7
---

It is very common the need for the generation of customized ModSecurity packages. The need for custom package may be a consequence of the need for new version of ModSecurity, that is not yet available on a given distribution. Or a simple need for a version with specifics configurations/build options.

In this Wiki page, we collect information given by the community on how to generate the packages. Including the packages recipes.

## Version 2.x
### Rpm Packages

The rpm package recipe is available here: 
https://gist.github.com/zimmerle/a2b069f0099c90c142e8#file-0d90c84a7a89d26b9cffb4f987342185fe482118-patch

In order to generate the package, you can use the following (assuming you saved the Gist as mod_security.spec):
```bash
$ rpmbuild mod_security.spec
```
This should download the source for the version specified in the .spec file, build it, and yield a valid RPM package in ~/rpmbuild/RPMS that you can install using 
```bash
$ yum localinstall ~/rpmbuild/RPMS/mod_security.rpm
```
If you choose to install with RPM directly, you'll need to manage dependencies. Newer versions of Fedora use DNF, which supposedly works the same - replace 'yum' with 'dnf' when you install.

The RPM package generation was a contribution from @antonyh, through the pull request #1052. 

### Deb Packages

## Version 3.x
### Rpm Packages
### Deb Packages
