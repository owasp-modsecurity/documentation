---
title: Debugging ModSecurity
weight: 1
---

This page contains information about how to debug ModSecurity. This is not a complete guide or a developer guide, this contains basic information that may help the bug reporting process. Sometimes reproducing problems is not easy due to platform specific issues or even configurations. It is even worse when log files do not contain a specific reference to what might be leading ModSecurity to fail (process is killed before log is saved for instance). In this kind of situation we recommend the utilization of tools such as GDB, which is able to acquire details on the faulty function. 

Here we explain some debugging techniques that are applicable to Nginx and Apache in a Linux environment. Debugging in other platforms are is possible, however, they are not covered by this specific post. For more information about IIS, visit the [IIS Troubleshooting guide]({{% relref "5-troubleshooting/5-2-iis-troubleshooting" %}}). 

## General debug instructions

Debugging ModSecurity means debugging the HTTP server. ModSecurity works as a server add-on/module/plugin/extension, as a result, it is part of the same process ID (PID) of the server.

Before starting the debug process, make sure that ModSecurity is compiled with the debugging parameter (**"-g"** for those who are using gcc). Another gcc parameter that is desired is the **"-O0"**, which will disable the compiler optimization, making GDB's output more friendly. Independent of the target HTTP server, ModSecurity should be compiled with those special flags. These flags can be added during the configuration phase, as follows:

```
CFLAGS="-g -O0" ./configure ...normal configure parameters...
```

It is recommended that one keeps the debugging process as simple as possible, to do so, the elimination of features such as multi-threading by the HTTP server is recommended. The instructions on how to disable threads/workers is dependent on your server, as explained on the sub-sections bellow.

### Apache

Apache webservers accept a special command line parameter: "-X", that starts the server in debug mode and doesn't detach it from the console. This flag should be passed straight to the **apache2** or **httpd** binary, along with any other options, such as the configuration file that should be used. The parameter should **not be passed to the apachectl** script, instead, the http/apache2 file should be used directly. If you are using Ubuntu your Apache will probably be at: /usr/sbin/apache2. If you are using Fedora this will probably be at: /usr/sbin/httpd.

This setup may affect the behavior of the HTTP server in a way that makes impossible or more difficult to reproduce a given bug, if this is the case, you may wish to ask for help in our mailing list and check out Apache's debugging instructions at: [https://httpd.apache.org/dev/debugging.html](https://httpd.apache.org/dev/debugging.html).

### Nginx

Different from Apache where a parameter is expected to place the server in debugging mode, Nginx expects debugging information within the configuration files. To keep Nginx attached to the console, a user can set **daemon** to **off**. Threads can be disabled by having **master_process** set to **off**. As demonstrated below:

```
daemon off;
master_process off;
```

By adding a directives similar to the above to Nginx's configuration, it will be executed as a single thread and it won't detach from the console. If the problem is not reproducible under these circumstances other techniques can be used as discussed at: [http://wiki.nginx.org/Debugging](http://wiki.nginx.org/Debugging). Besides the debugging parameters that should be passed to gcc, it is also recommend to use the option **--with-debug** in the Nginx's configuration script. The recommended configuration options are illustrated bellow:

```
CFLAGS="-g -O0" ./configure --with-debug ...normal paramanters...
```

## Running GDB

As defined on GDB's website: "GDB, the GNU Project debugger, allows you to see what is going on `inside' another program while it executes -- or what another program was doing at the moment it crashed." The utilization of GDB is recommended to understand and report ModSecurity crashes. This section is not intend to give an advanced usage guide of GDB, instead, it is just about how print a stack trace in a situation where the HTTP server died.

GDB can be attached to process that are already running or it can be attached in the beginning of the execution. In this document the second option will be explained. It is very simple to get GDB to "watch" a process; the target binary should be passed as a parameter to GDB, for instance:

```
$ gdb /usr/sbin/apache2
GNU gdb (GDB) 7.6.1-ubuntu
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>...
...
```

Notice that this does not start the target software yet. In order to start the software "run" most be typed in the GDB console. Parameters to the target process are expected to be pasts in the GDB console, as parameters of the command: "run", as demonstrated bellow:

```
(gdb) run -X
Starting program: /usr/sbin/apache2 -X
[Thread debugging using libthread_db enabled]
...
```

After really starting the process (that is, after executing the "run" command), the HTTP server should be working as if there is no GDB. The next step is try to reproduce the bug. Once the bug is reproduced the process will crash and as a result, the GDB command "bt full" can be used to extract information about the crash.A Demonstration of all these steps can be found below:

```
(zimmerle@zlinux)-(~/core/spider-modsec/tests)$ gdb /usr/sbin/apache2
GNU gdb (GDB) 7.6.1-ubuntu
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>...
Reading symbols from /usr/sbin/apache2...(no debugging symbols found)...done.
(gdb) run -d -X -f /home/zimmerle/core/spider-modsec/tests/regression/server_root/conf/httpd.conf -c 'Listen localhost:8088' -c 'Include /home/zimmerle/core/spider-modsec/tests/regression/server_root/conf/config_10-request-directives.t_000003.conf' -k start
Starting program: /usr/sbin/apache2 -d -X -f /home/zimmerle/core/spider-modsec/tests/regression/server_root/conf/httpd.conf -c 'Listen localhost:8088' -c 'Include /home/zimmerle/core/spider-modsec/tests/regression/server_root/conf/config_10-request-directives.t_000003.conf' -k start
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Program received signal SIGABRT, Aborted.
0x00007ffff7196f77 in __GI_raise (sig=sig@entry=6) at ../nptl/sysdeps/unix/sysv/linux/raise.c:56
56	../nptl/sysdeps/unix/sysv/linux/raise.c: No such file or directory.
(gdb) bt full
#0  0x00007ffff7196f77 in __GI_raise (sig=sig@entry=6) at ../nptl/sysdeps/unix/sysv/linux/raise.c:56
        resultvar = 0
        pid = 62396
        selftid = 62396
#1  0x00007ffff719a5e8 in __GI_abort () at abort.c:90
        save_stage = 2
        act = {__sigaction_handler = {sa_handler = 0x7ffff7163d18, sa_sigaction = 0x7ffff7163d18}, sa_mask = {__val = {0, 140737353784168, 140737338818848, 140737488346464, 140737339657820, 0, 6, 28, 0, 140737354072104, 140737353784208, 140737353784216, 140737345047185,
              1, 140733193388080, 140737488346216}}, sa_flags = -9232, sa_restorer = 0x12}
        sigs = {__val = {32, 0 <repeats 15 times>}}
#2  0x00007ffff603eac0 in msc_escape (string=0x7ffff7faa490 "phase:2,deny,chain,id:500219", buff=0x0, buff_length=0, opt=20) at msc_escape.c:133
        i = 28
        length_only = 1
        escaped_string_length = 28
#3  0x00007ffff605250f in _log_escape (mp=0x7ffff7ff0028, input=0x7ffff7faa490 "phase:2,deny,chain,id:500219", input_len=28, escape_quotes=1, escape_colon=0, escape_re=0) at msc_util.c:1335
        length = 0
        res = 0
        options = 20
        buffer = 0x0
#4  0x00007ffff605209a in log_escape (mp=0x7ffff7ff0028, text=0x7ffff7faa470 "phase:2,deny,chain,id:500219") at msc_util.c:1210
No locals.
#5  0x00007ffff6064651 in msre_rule_generate_unparsed (pool=0x7ffff7ff0028, rule=0x7ffff7faa088, targets=0x7ffff7fa9b90 "ARGS:a", args=0x7ffff7fa9b98 "@streq 1", actions=0x0) at re.c:2240
        unparsed = 0x0
        r_targets = 0x7ffff7fa9b90 "ARGS:a"
        r_args = 0x7ffff7fa9b98 "@streq 1"
        r_actions = 0x7ffff7faa470 "phase:2,deny,chain,id:500219"
#6  0x00007ffff6064b41 in msre_rule_create (ruleset=0x7ffff7fa9bc8, type=0, fn=0x7ffff7facdc0 "/home/zimmerle/core/spider-modsec/tests/regression/server_root/conf/config_10-request-directives.t_000003.conf", line=5, targets=0x7ffff7fa9b90 "ARGS:a",
    args=0x7ffff7fa9b98 "@streq 1", actions=0x7ffff7fa9ba8 "phase:2,deny,chain,id:500219", error_msg=0x7fffffffdde8) at re.c:2353
        rule = 0x7ffff7faa088
        my_error_msg = 0x0
        argsp = 0x7ffff7fa9b98 "@streq 1"
        rc = 1
#7  0x00007ffff602737c in add_rule (cmd=0x7fffffffe140, dcfg=0x7ffff7fb0810, type=0, p1=0x7ffff7fa9b90 "ARGS:a", p2=0x7ffff7fa9b98 "@streq 1", p3=0x7ffff7fa9ba8 "phase:2,deny,chain,id:500219") at apache2_config.c:759
        my_error_msg = 0x0
        rid = 0x0
        rule = 0x0
        offset = 0
#8  0x00007ffff6029ca9 in cmd_rule (cmd=0x7fffffffe140, _dcfg=0x7ffff7fb0810, p1=0x7ffff7fa9b90 "ARGS:a", p2=0x7ffff7fa9b98 "@streq 1", p3=0x7ffff7fa9ba8 "phase:2,deny,chain,id:500219") at apache2_config.c:2043
No locals.
#9  0x00005555555a7083 in ?? ()
No symbol table info available.
#10 0x00005555555a96ff in ap_walk_config ()
No symbol table info available.
#11 0x00005555555aa859 in ap_process_config_tree ()
No symbol table info available.
#12 0x00005555555888d6 in main ()
No symbol table info available.
(gdb)
```
