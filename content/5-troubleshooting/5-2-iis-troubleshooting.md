---
title: IIS Troubleshooting
weight: 2
---

This topic introduces tools and options to troubleshooting the IIS version of ModSecurity. It covers the installation process but it was not only limited to that.

## Running the installer in verbose mode

ModSecurity installer was created using the [Wix Toolset](http://wixtoolset.org/), a popular tool to produce msi installers. The idea of the installer is to provide an easy way to install and configure ModSecurity on a given machine. If one of those (install or configure) fails, the installer aborts and it should revert any changes that it has made on the system.

Sometimes the installer aborts the installation process but it is not verbose enough to help the developers to fix or even identify a eventual problems. It is intend to be that way avoiding confusing a regular user. There is a option to run the installer in a fashion that it does produce textual log that can be attached to bugs or eventually  be read by the user in order to identify what was the real problem behind the error dialog.

In order the generate such log, open a command prompt as administrator, go the msi folder and type:
```
msiexec /i ModSecurityIIS_A.B.C-Zb.msi /l*v log.txt
```
Proceed normally on the installation steps. After the installation halts, have a look at _log.txt_ in the 
same folder of the installer. There should be valuable information to identify problems. If you don't feel confortable to identify the problem, [open an issue](https://github.com/SpiderLabs/ModSecurity/issues) with the message that was presented on the error dialog box and attach the _log.txt_ to the Issue.

### Broken Uninstall

This should not happens to regular users, but, developers playing around the installer may be in a situation that the uninstall process is broken and he is not able to uninstall ModSecurity or even install a newest version. In that situation we recommend the utilization of _Microsoft FixIt_ to force the removal of the package. Keep in mind that file may be left behind. Manual check is necessary after the forced removal.

In order to use the _Microsoft FixIt_ visit the website: [http://support.microsoft.com/mats/program_install_and_uninstall](http://support.microsoft.com/mats/program_install_and_uninstall)

## Looking for missing dependencies

ModSecurity itself is distributed along with some dependencies, as an example but not limited to the libapr. Dependencies may changed according to the version. Not all dependencies are part of ModSecurity as an example of the Visual C++ Redistribution files which is not part of the currently release (see bug [#627](https://github.com/owasp-modsecurity/ModSecurity/issues/628), to check if your version contains those C++ Redistribution files). Some dependencies are expected to be loaded from the system but sometimes, due to version changes or specific configuration of the server those dependencies are not found, leading ModSecurity to fail to be loaded. While not loaded the error messages are not verbose enough to help the user to identify the missing symbol or library.

In order to identify that all dependencies are match, we recommend the utilization of [dumpbin](https://learn.microsoft.com/en-us/cpp/build/reference/dumpbin-reference). _Dumpbin_ is a utility that is part of the Visual Studio package and it should be in your path after the execution of the _vcvars_ batch script. The path to the script and the mane may vary from version to version of Visual Studio, on Win 8.1 using Visual Studio 2013, here is the path:
```
C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat
```

After execute such batch script the _dumpbin_ should be available in your path. Having _dumpbin_ on path, change the directory to the path where the ModSecurityIIS.dll is installed and type:
```
dumpbin /imports /dependents ModSecurityIIS.dll libapr-1.dll libaprutil-1.dll libxml2.dll lua5.1.dll pcre.dll > c:\somedir\deps.txt
```
After that, this _deps.txt_ file should be generated. Have a look at this file, it should contains information if there is a missing symbol or not. If there is a missing symbol or library try to install it. If you have problems on these steps or to identify the missing library ask for support in our development mailing list.

## Add/Removes ModSecurity from IIS using AppCmd.

The installer makes usage of _AppCmd_ to add/remove ModSecurity from IIS, the installer process is divided into two different steps: Module Installation and Site Configuration, as explained in the sub sections bellow.

The installer uses AppCmd to configure ModSecurity, there are other methods
to perform the configuration, those are described at: [IIS Modules Overview](http://www.iis.net/learn/get-started/introduction-to-iis/iis-modules-overview).

### Module Installation

The first part of the ModSecurityIIS setup, is to inform the IIS to load the ModSecurityIIS as a global module, for that, the following commands are use to add/remove it:

#### Add
```
appcmd.exe install module /name:"ModSecurity IIS" /image:"C:\Program Files (x86)\ModSecurity IIS\inetsrv\ModSecurityIIS.dll"
```

#### Remove
```
appcmd.exe uninstall module /module.name:"ModSecurity IIS"
```

### Site Configuration

The second part of this IIS configuration is to enable ModSecurity for a site. Note that the first step must be completed prior to the second step, otherwise it will not be possible. In order to enable ModSecurity, the following commands are used by the installer:

#### Add
```
appcmd.exe set config /section:"system.webServer/ModSecurity" /"enabled:true" /"configFile:C:\Program Files (x86)\ModSecurity IIS\modsecurity_iis.conf"
```

#### Remove
```
appcmd.exe clear config -section:"system.webServer/ModSecurity"
```

## Looking at ModSecurity event Logs

While running or even during the installation phase, ModSecurityIIS produces valuable information on the _Windows Logs'_. To check on those event logs, open the _Event Viwer_ and have a look at _Application_ under the _Windows Logs_ folder.

During the installation the logs were generated from the MsiInstaller source. After that, at runtime, logs were generated using ModSecurutyIIS as source.


## Accessing data on Network Shares

In order to access shares via an IIS ModSecurity configuration file they must included with quad slashes. 

For instance: 
```
SecAuditLog \\\\192.168.1.120\test\temp\index2.log
SecAuditLogStorageDir \\\\192.168.1.120\test\temp
Include \\\\192.168.1.120\test\temp.conf
```

Accessing shares via mapped drives does not work.
