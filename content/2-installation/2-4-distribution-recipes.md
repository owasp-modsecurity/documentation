---
title: Distribution-specific build recipes
weight: 4
---

This Wiki page contains "copy & paste" recipes to compile libModSecurity (and connectors) in your favorite Linux distribution.

If your distribution is missing and you manage to compile it, don't forget to add it here in this list.


> **Attention:** Before start the compilation process make sure that the _paths are right_, and the _commands are sane_.


## Centos 7 Minimal

Sent by @elialum (See: #1039)

### libModSecurity

```sh
yum install gcc-c++ flex bison yajl yajl-devel curl-devel curl GeoIP-devel doxygen zlib-devel pcre-devel
cd /opt/
git clone https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git checkout -b v3/master origin/v3/master
sh build.sh
git submodule init
git submodule update
./configure
yum install https://archives.fedoraproject.org/pub/archive/fedora/linux/updates/23/x86_64/b/bison-3.0.4-3.fc23.x86_64.rpm
make
make install
```

### nginx connector

```sh
# ensure env vars are set
export MODSECURITY_INC="/opt/ModSecurity/headers/"
export MODSECURITY_LIB="/opt/ModSecurity/src/.libs/"
cd /opt/
git clone https://github.com/owasp-modsecurity/ModSecurity-nginx
wget http://nginx.org/download/nginx-1.9.2.tar.gz
tar -xvzf nginx-1.9.2.tar.gz
cd /opt/nginx-1.9.2
/bin/cp -f /usr/sbin/nginx /usr/sbin/nginx_original_bkp
./configure --add-module=/opt/ModSecurity-nginx 
make
make install
```

## Centos 7 Minimal dynamic

Sent by @chang-zhao (See: #1977)

Check nginx -v for the NGINX version and change appropriately; here it's 1.15.7.

```sh
sudo yum groupinstall 'Development Tools' -y
sudo yum install gcc-c++ flex bison yajl yajl-devel curl-devel curl GeoIP-devel doxygen zlib-devel
sudo yum install lmdb lmdb-devel libxml2 libxml2-devel ssdeep ssdeep-devel lua lua-devel
sudo git clone --depth 1 -b v3/master --single-branch https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
sudo git submodule init
sudo git submodule update
sudo ./build.sh
sudo ./configure
sudo make
sudo make install
sudo git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx.git
sudo wget http://nginx.org/download/nginx-1.15.7.tar.gz
sudo tar zxvf nginx-1.15.7.tar.gz
cd nginx-1.15.7
sudo ./configure --with-compat --add-dynamic-module=../ModSecurity-nginx
sudo make modules
sudo cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules
sudo mkdir /etc/nginx/modsec
sudo cp ~/ModSecurity/unicode.mapping /etc/nginx/modsec/
```

Then add load_module instruction to nginx.conf in the main (top-level) context:

```
load_module modules/ngx_http_modsecurity_module.so;
```

## Amazon Linux

Provided by @csanders-git

### libModSecurity

```sh
yum install gcc-c++ flex bison curl-devel curl libxml2-devel doxygen zlib-devel git automake libtool pcre-devel
cd /opt/
# Steal Fedora's YAJL and YAJL-devel packages
wget https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/23/Everything/x86_64/os/Packages/y/yajl-2.1.0-4.fc23.x86_64.rpm
rpm -i yajl-2.1.0-4.fc23.x86_64.rpm
wget https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/23/Everything/x86_64/os/Packages/y/yajl-devel-2.1.0-4.fc23.x86_64.rpm
rpm -i yajl-devel-2.1.0-4.fc23.x86_64.rpm
# Install latest bison
yum install https://archives.fedoraproject.org/pub/archive/fedora/linux/updates/23/x86_64/b/bison-3.0.4-3.fc23.x86_64.rpm
# Amazon's GeoIP-devel package does not come with geoip.pc (no idea why not)
wget ftp://rpmfind.net/linux/centos/5.11/extras/x86_64/RPMS/GeoIP-data-20090201-1.el5.centos.x86_64.rpm
wget ftp://rpmfind.net/linux/fedora/linux/releases/23/Everything/x86_64/os/Packages/g/GeoIP-1.6.6-1.fc23.x86_64.rpm
wget ftp://rpmfind.net/linux/fedora/linux/releases/23/Everything/x86_64/os/Packages/g/GeoIP-devel-1.6.6-1.fc23.x86_64.rpm
rpm -i GeoIP-1.6.6-1.fc23.x86_64.rpm  GeoIP-data-20090201-1.el5.centos.x86_64.rpm
rpm -i GeoIP-devel-1.6.6-1.fc23.x86_64.rpm
rm -rf *.rpm
git clone https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git checkout -b v3/master origin/v3/master
sh build.sh
git submodule init
git submodule update
./configure
make
make install
```

## Amazon Linux 2

Provided by @csanders-git

### libModSecurity

```
yum install yajl-devel git gcc-c++ flex bison curl-devel curl libxml2-devel doxygen zlib-devel git automake libtool pcre-devel GeoIP-devel lua-devel wget openssl-devel
# Install LMDB
cd /opt/
git clone git clone https://github.com/LMDB/lmdb.git
cd lmdb/libraries/liblmdb
make
make install
# Install SSDEEP
cd /opt/
git clone https://github.com/ssdeep-project/ssdeep
cd ssdeep/
./bootstrap
./configure && make && make install
# Install libmodsecurity
cd /opt/
git clone https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
./build
git submodule init
git submodule update
./configure
make
make install
# Install Nginx + Nginx Connector
cd /opt
git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx.git
# Nginx
wget https://nginx.org/download/nginx-1.15.10.tar.gz
tar -xvzf nginx-1.15.10.tar.gz 
cd nginx-1.15.10/
./configure --with-http_ssl_module --with-http_v2_module --with-compat --add-dynamic-module=/opt/ModSecurity-nginx/
make
make install
```

### nginx connector

```sh
cd /opt/
git clone https://github.com/owasp-modsecurity/ModSecurity-nginx
wget http://nginx.org/download/nginx-1.9.2.tar.gz
tar -xvzf nginx-1.9.2.tar.gz
cd /opt/nginx-1.9.2
./configure --add-module=/opt/ModSecurity-nginx 
make
make install
```

## CentOS 6.x

Provided by @moodygit

### libModSecurity

```sh
$ cd /opt/
$ git clone https://github.com/owasp-modsecurity/ModSecurity
$ cd ModSecurity
$ git checkout -b v3/master origin/v3/master
$ sh build.sh
$ git submodule init
$ git submodule update
$ ./configure
$ make
$ make install
```

### nginx-connector (openresty) 

```sh
$ cd /opt/
$ git clone https://github.com/owasp-modsecurity/ModSecurity-nginx
$ wget https://openresty.org/download/ngx_openresty-1.9.7.1.tar.gz
$ tar -xvzf ngx_openresty-1.9.7.1.tar.gz
$ ./configure --add-module=/opt/ModSecurity-nginx
```

## CentOS 6.5 Minimal

Provided by @csanders-git

### libModSecurity

```sh
yum install -y wget perl cmake
# Add a newer version of GCC that can make c++-11
wget http://people.centos.org/tru/devtools-2/devtools-2.repo -O /etc/yum.repos.d/devtools-2.repo
yum install -y devtoolset-2-gcc-c++ devtoolset-2-binutils
PATH=/opt/rh/devtoolset-2/root/usr/bin:$PATH
cd /opt/
#Install bison
wget http://ftp.gnu.org/gnu/bison/bison-3.0.4.tar.gz
tar -xvzf bison-3.0.4.tar.gz
cd bison-3.0.4
./configure
make
make install
cd /opt/
# Install autoconf
wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.69.tar.gz
tar -xvzf autoconf-2.69.tar.gz
cd autoconf-2.69
./configure
make
make install
cd /opt
# Install libtool
wget http://ftp.gnu.org/gnu/libtool/libtool-2.4.5.tar.gz
tar -xvzf libtool-2.4.5.tar.gz
cd libtool-2.4.5
./configure
make
make install
cd /opt
# Install automake
wget http://ftp.gnu.org/gnu/automake/automake-1.15.tar.gz
tar -xvzf automake-1.15.tar.gz
cd automake-1.15
./configure
make
make install
cd /opt	
# Insteall PCRE-devel
wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.38.tar.gz
tar -xvzf pcre-8.38.tar.gz
cd pcre-8.38
./configure
make
make install
cd /opt/
# Install YAJL2
wget http://github.com/lloyd/yajl/tarball/2.1.0 -O yajl-2.1.0.tar.gz
tar -xvzf yajl-2.1.0.tar.gz
cd lloyd-yajl-66cb08c
./configure
make
make install
cd /opt
# Install Curl
wget http://curl.haxx.se/download/curl-7.46.0.tar.gz
tar -xvzf curl-7.46.0.tar.gz 
cd curl-7.46.0
./configure --prefix=/opt/curl
make
make install
# Little hack because make doesn't respect --with-curl currently
cp -R /opt/curl/include/curl/ /usr/include/
cd /opt/
# Install GeoIP
wget ftp://rpmfind.net/linux/centos/5.11/extras/x86_64/RPMS/GeoIP-data-20090201-1.el5.centos.x86_64.rpm
wget ftp://rpmfind.net/linux/fedora/linux/releases/23/Everything/x86_64/os/Packages/g/GeoIP-1.6.6-1.fc23.x86_64.rpm
wget ftp://rpmfind.net/linux/fedora/linux/releases/23/Everything/x86_64/os/Packages/g/GeoIP-devel-1.6.6-1.fc23.x86_64.rpm
rpm -i GeoIP-1.6.6-1.fc23.x86_64.rpm  GeoIP-data-20090201-1.el5.centos.x86_64.rpm
rpm -i GeoIP-devel-1.6.6-1.fc23.x86_64.rpm
yum install -y libxml2-devel doxygen zlib-devel git flex
git clone https://github.com/csanders-git/ModSecurity
cd ModSecurity
git checkout -b v3/master origin/v3/master
sh build.sh
git submodule init
git submodule update
./configure --with-yajl=/opt/lloyd-yajl-66cb08c/build/yajl-2.1.0/ --with-curl=/opt/curl/
make
make install
```

### nginx-connector (openresty) 

```sh
cd /opt/
git clone https://github.com/owasp-modsecurity/ModSecurity-nginx
wget http://nginx.org/download/nginx-1.9.2.tar.gz
tar -xvzf nginx-1.9.2.tar.gz
cd /opt/nginx-1.9.2
./configure --add-module=/opt/ModSecurity-nginx 
make
make install
```

## Ubuntu 18.04

### libModSecurity

```sh
$ sudo apt-get install git g++ apt-utils autoconf automake build-essential libcurl4-openssl-dev libgeoip-dev liblmdb-dev libpcre++-dev libtool libxml2-dev libyajl-dev pkgconf wget zlib1g-dev

$ git clone https://github.com/owasp-modsecurity/ModSecurity
$ cd ModSecurity/
$ git submodule init
$ git submodule update
$ sh build.sh
$ ./configure
$ make
$ make install
```

## Ubuntu 22.10

Assumes nginx version >=  1.21.5 and preference to use PCRE2.

### libModSecurity

```sh
$ sudo apt-get install git g++ apt-utils autoconf automake build-essential libcurl4-openssl-dev libgeoip-dev liblmdb-dev libpcre2-dev libtool libxml2-dev libyajl-dev pkgconf zlib1g-dev

$ git clone https://github.com/owasp-modsecurity/ModSecurity
$ cd ModSecurity/
$ git submodule init
$ git submodule update
$ sh build.sh
$ ./configure --with-pcre2
$ make
$ make install
```

## Mac OSX 10.13

Sent by @scottcc (See: #1907)

Note: There's probably ways to do this that don't involve `homebrew` - those were not explored.

### libModSecurity

```sh
brew install flex bison zlib curl pcre libffi autoconf automake yajl pkg-config libtool ssdeep luarocks
brew install geoip --with-geoipupdate
brew install doxygen --with-llvm

# Arbitrarily, create a directory to put things in
sudo mkdir -p /usr/local/modsecurity
sudo chown -R $(whoami) /usr/local/modsecurity

cd /usr/local/opt
mkdir ModSecurity
git clone https://github.com/owasp-modsecurity/ModSecurity && cd ModSecurity
git checkout -b v3/master origin/v3/master
sh build.sh
git submodule init && git submodule update
./configure
make
make install
```

### nginx connector

Note: the exports are *slightly* different than other OS's listed above.

```sh
MOD_SECURITY_INC=/usr/local/opt/ModSecurity/headers/
MOD_SECURITY_LIB=/usr/local/opt/ModSecurity/src/.libs/

cd /usr/local/opt/
git clone https://github.com/owasp-modsecurity/ModSecurity-nginx

# NOW edit the brew nginx formula to have two chunks added (brew edit nginx)
    option "with-modsecurity", "Compile with v3 ModSecurity module"

# then later near the bottom, add a chunk that detects this and adds the module
    if build.with? "modsecurity"
        args << "--add-module=/usr/local/opt/ModSecurity-nginx"
    end

# Use homebrew to build it from source with the new argument you just added:
brew install -vd --build-from-source nginx --with-modsecurity
# You should see in the output somewhere that it "found /usr/local/modsecurity", or close to that.

# TEST that with (make sure you see "--add-module=/usr/local/opt/ModSecurity-nginx" in there, likely at end)
nginx -V
```

## AWS Linux - RPM

Sent by Eero Volotinen

ModSecurity compilation for AWS Linux Nginx

- Install aws linux 2

- Install needed packages:

```
amazon-linux-extras install -y nginx1.12
yumdownloader --source nginx
rpm -i nginx-1.12.2-1.amzn2.0.2.src.rpm
```

### libModSecurity

```
yum install -y git rpm-build gperftools-devel openssl-devel pcre-devel zlib-devel \
GeoIP-devel gd-devel perl-devel libxslt-devel perl-ExtUtils-Embed.noarch gcc gcc-c++ autoconf automake libtool
 Clone modsecurity repository & compile modsecurity connector

git clone --depth 1 -b v3/master --single-branch https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule init
git submodule update
./build.sh
./configure
make -j2
#takes about 15 minutes
make install
```

### nginx connector

```
cd /root
mkdir nginx
git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx.git

#unpack correct version from rpm package
tar zxf /root/rpmbuild/SOURCES/nginx-1.12.2.tar.gz
cd nginx-1.12.2/
#generate build string
nginx -V 2>&1 | grep 'configure arguments' | sed "s#configure arguments:#./configure --add-dynamic-module=../ModSecurity-nginx #g" 
# if looks good, compile

nginx -V 2>&1 | grep 'configure arguments' | sed "s#configure arguments:#./configure --add-dynamic-module=../ModSecurity-nginx #g" |bash
make modules
Note. build string looks like this:

./configure --add-dynamic-module=../ModSecurity-nginx --prefix=/usr/share/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib64/nginx/modules --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --http-client-body-temp-path=/var/lib/nginx/tmp/client_body --http-proxy-temp-path=/var/lib/nginx/tmp/proxy --http-fastcgi-temp-path=/var/lib/nginx/tmp/fastcgi --http-uwsgi-temp-path=/var/lib/nginx/tmp/uwsgi --http-scgi-temp-path=/var/lib/nginx/tmp/scgi --pid-path=/run/nginx.pid --lock-path=/run/lock/subsys/nginx --user=nginx --group=nginx --with-file-aio --with-ipv6 --with-http_ssl_module --with-http_v2_module --with-http_realip_module --with-http_addition_module --with-http_xslt_module=dynamic --with-http_image_filter_module=dynamic --with-http_geoip_module=dynamic --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_mp4_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module --with-http_degradation_module --with-http_slice_module --with-http_stub_status_module --with-http_perl_module=dynamic --with-mail=dynamic --with-mail_ssl_module --with-pcre --with-pcre-jit --with-stream=dynamic --with-stream_ssl_module --with-google_perftools_module --with-debug --with-cc-opt='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -m64 -mtune=generic' --with-ld-opt='-Wl,-z,relro -specs=/usr/lib/rpm/redhat/redhat-hardened-ld -Wl,-E'
```

### Build RPM package

```
cd /root
mkdir -p /root/rpmbuild/BUILD
find . -type f -iname 'libmodsecurity.so.3.*' -exec cp {} /root/rpmbuild/BUILD \;
find . -type f -iname 'ngx_http_modsecurity_module.so' -exec cp {} /root/rpmbuild/BUILD \;
#rpm spec file  nginx-modsecurity.spec
cd /root/rpmbuild/SPECS
#create file nginx-modsecurity.spec
rpmbuild -ba nginx-modsecurity.spec
```

### Testing package

```
#copy package needed machine or repo:
/root/rpmbuild/RPMS/x86_64/nginx-modsecurity3-aws-1.0.0-1.x86_64.rpm
rpm -i nginx-modsecurity3-aws-1.0.0-1.x86_64.rpm
systemctl start nginx
systemctl status nginx
```

### RPM SPEC file

```
Name: nginx-modsecurity3-aws
Version: 3.0.3
Release: 1
Group: Applications/System
BuildArch: x86_64
Summary: modsecurity for nginx
License: GPL

%description
Brief description of software package.
Provides: libmodsecurity.so.3 nginx-modsecurity


%prep

%build

%install
mkdir -p %{buildroot}/opt/modsecurity
cp libmodsecurity.so.3.0.3 %buildroot/opt/modsecurity
cp ngx_http_modsecurity_module.so %buildroot/opt/modsecurity
%post
echo 'load_module "/usr/lib64/nginx/modules/ngx_http_modsecurity_module.so";' > /usr/share/nginx/modules/mod-modsecurity.conf
ln -sf /opt/modsecurity/ngx_http_modsecurity_module.so /usr/lib64/nginx/modules/ngx_http_modsecurity_module.so
cat > /etc/ld.so.conf.d/modsecurity.conf << EOF
/opt/modsecurity
EOF
ldconfig
%postun
rm -f /etc/ld.so.conf.d/modsecurity.conf
rm -f /usr/lib64/nginx/modules/ngx_http_modsecurity_module.so
rm -f /usr/share/nginx/modules/mod-modsecurity.conf
ldconfig


%clean

%files
/*
```

## CentOS 7 - RPM

Sent by Eero Volotinen

- Install needed packages:

```
yum -y install epel-release
yum -y install nginx
yumdownloader --source nginx
yum install -y git rpm-build gperftools-devel openssl-devel pcre-devel zlib-devel \
GeoIP-devel gd-devel perl-devel libxslt-devel perl-ExtUtils-Embed.noarch gcc gcc-c++ autoconf automake libtool
rpm -i nginx-1.12.2-2.el7.src.rpm
```

### libModSecurity

```
git clone --depth 1 -b v3/master --single-branch https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
git submodule init
git submodule update
./build.sh
./configure
make -j2
#takes about 15 minutes
make install
```

### nginx connector

```
cd /root
mkdir nginx
git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx.git
#unpack correct version from rpm package
tar zxf /root/rpmbuild/SOURCES/nginx-1.12.2.tar.gz
cd nginx-1.12.2/
#generate build string
nginx -V 2>&1 | grep 'configure arguments' | sed "s#configure arguments:#./configure --add-dynamic-module=../ModSecurity-nginx #g" 
# if looks good, compile

nginx -V 2>&1 | grep 'configure arguments' | sed "s#configure arguments:#./configure --add-dynamic-module=../ModSecurity-nginx #g" |bash
make modules
cd /root
mkdir -p /root/rpmbuild/BUILD
find . -type f -iname 'libmodsecurity.so.3.*' -exec cp {} /root/rpmbuild/BUILD \;
find . -type f -iname 'ngx_http_modsecurity_module.so' -exec cp {} /root/rpmbuild/BUILD \;
```

### Build RPM package

```
#rpm spec file  nginx-modsecurity.spec
cd /root/rpmbuild/SPECS
#create file
#nginx-modsecurity.spec
rpmbuild -ba nginx-modsecurity.spec
```

### Testing package

```
# install package .
rpm -i /root/rpmbuild/RPMS/x86_64/nginx-modsecurity3-centos7-1.0.0-1.x86_64.rpm
```

### RPM SPEC file

```
Name: nginx-modsecurity3-centos7
Version: 3.0.3
Release: 1
Group: Applications/System
BuildArch: x86_64
Summary: modsecurity for nginx
License: GPL

%description
Brief description of software package.
Provides: libmodsecurity.so.3 nginx-modsecurity


%prep

%build

%install
mkdir -p %{buildroot}/opt/modsecurity
cp libmodsecurity.so.3.0.3 %buildroot/opt/modsecurity
cp ngx_http_modsecurity_module.so %buildroot/opt/modsecurity
%post
echo 'load_module "/usr/lib64/nginx/modules/ngx_http_modsecurity_module.so";' > /usr/share/nginx/modules/mod-modsecurity.conf
ln -sf /opt/modsecurity/ngx_http_modsecurity_module.so /usr/lib64/nginx/modules/ngx_http_modsecurity_module.so
cat > /etc/ld.so.conf.d/modsecurity.conf << EOF
/opt/modsecurity
EOF
ldconfig
%postun
rm -f /etc/ld.so.conf.d/modsecurity.conf
rm -f /usr/lib64/nginx/modules/ngx_http_modsecurity_module.so
rm -f /usr/share/nginx/modules/mod-modsecurity.conf
ldconfig


%clean

%files
/*
```
