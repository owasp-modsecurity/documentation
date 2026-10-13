---
title: ModSecurity v2 for Microsoft IIS
weight: 6
---

ModSecurity for IIS (`ModSecurityIIS.dll`) is an IIS native module built from the ModSecurity v2 source tree (`v2/master`, directory `iis/`). It shares the engine, the rule language and the configuration file format with the Apache module; only the way the module is loaded and configured differs.

## Prerequisites

- Windows Server with IIS 7 or later.
- The Microsoft Visual C++ Redistributable matching the compiler the module was built with (the build scripts in the repository use Visual Studio 2019). Install the 32-bit or 64-bit version according to the application pool architecture.
- The dependency DLLs that ship alongside the module: APR and APR-util, PCRE, libxml2, Lua, libcurl, YAJL, zlib and libfuzzy. The build scripts produce them together with `ModSecurityIIS.dll` and `mlogc.exe`.

## Obtaining the Module

The project publishes source releases only (<https://github.com/owasp-modsecurity/ModSecurity/releases>); no Windows binaries or MSI installers are attached to current releases. To build the module and, optionally, the MSI installer, use the scripts in the `iis/` directory of the v2 tree (`build_release.bat` builds the dependencies and the module for x86 and amd64, `build_msi.bat` builds the WiX installer). The general Windows build notes are in [README_WINDOWS.md](https://github.com/owasp-modsecurity/ModSecurity/blob/v2/master/README_WINDOWS.md).

If you use a third-party installer or binary package, make sure it comes from a source you trust and matches the version you expect.

Any installation errors or warning messages from the MSI installer are logged in the Application event log under the `ModSecurityIIS Installer` source. The installer does not install the OWASP CRS; download it from the [CRS project](https://coreruleset.org/) and include it from your ModSecurity configuration file.

## Manually Installing and Troubleshooting Setup of ModSecurity Module on IIS

### Configuration

After the installation the module will be running in all websites by default. To remove it from a website add to web.config:

``` xml
<modules>
    <remove name="ModSecurityIIS" />
</modules>
```

To configure the module in a website add to web.config:

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <ModSecurity enabled="true" configFile="c:\inetpub\wwwroot\modsecurity.conf" />
    </system.webServer>
</configuration>
```

where `configFile` is a standard ModSecurity configuration file (start from `modsecurity.conf-recommended`, see [Recommended Base Configuration]({{% relref "3-reference-manual/3-10-recommended-base-configuration" %}})). A relative path can also be used. To load the OWASP CRS, add `Include` directives for `crs-setup.conf` and the `rules\*.conf` files to that configuration file.

Events from the module will show up in the "Application" Windows event log.

## Common Problems

If after installation the protected website responds with HTTP 503 error and event ID 2280 keeps getting logged in the application event log:

``` text
Log Name:      Application
Source:        Microsoft-Windows-IIS-W3SVC-WP
Event ID:      2280
Task Category: None
Level:         Error
Keywords:      Classic
User:          N/A
Description:
The Module DLL C:\Windows\system32\inetsrv\modsecurityiis.dll failed to load.  The data is the error.
```

most likely it means that the installation process has failed and the ModSecurityIIS.dll module is missing one or more libraries that it depends on. Repeating installation of the prerequisites and the module files should fix the problem. A dependency walker tool such as [Dependencies](https://github.com/lucasg/Dependencies) can be used to figure out which library is missing or cannot be loaded.

See also [IIS Troubleshooting]({{% relref "5-troubleshooting/5-2-iis-troubleshooting" %}}).
