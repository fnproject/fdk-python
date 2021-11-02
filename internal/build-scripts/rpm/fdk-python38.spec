%global python3_pkgversion2 %(%{__python3} -c "import sys; sys.stdout.write(sys.version[:3].replace('.', ''))")
%global python3_pkgversion 3
%global python3_pkgversion %{python3_pkgversion2}
%global debug_package %{nil}


%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define srcname fdk
%define rpmname fdk

%define _unpackaged_files_terminate_build 0

%define PKG_EXTENSION -py3-none-any.whl

Name: python38-fdk
Version:       %{_rpm_version}
Release: 1%{?dist}
Url: http://pypi.python.org/pypi/%{srcname}
Summary: Oracle Cloud Infrastructure Python FDK
License: Apache2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

SOURCE0: fdk-%{_rpm_version}.tar.gz
SOURCE1: pbr-5.4.5-py2.py3-none-any.whl
SOURCE2: iso8601-0.1.12-py2.py3-none-any.whl
SOURCE3: pytest-5.4.3-py3-none-any.whl
SOURCE4: pytest-asyncio-0.12.0.tar.gz
SOURCE5: httptools-0.3.0-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64.whl
SOURCE6: pluggy-0.13.1-py2.py3-none-any.whl
SOURCE7: wcwidth-0.2.5-py2.py3-none-any.whl
SOURCE8: py-1.10.0-py2.py3-none-any.whl
SOURCE9: attrs-21.2.0-py2.py3-none-any.whl
SOURCE10: more_itertools-8.10.0-py3-none-any.whl
SOURCE11: packaging-21.2-py3-none-any.whl
SOURCE12: pyparsing-2.4.7-py2.py3-none-any.whl


BuildArch: x86_64

%global _description\
Python FDK for Oracle Cloud Infrastructure.

%description %_description

Summary: %summary

buildrequires: python >= 3.8, < 3.9
requires: python >= 3.8,  < 3.9

provides: python3-%{rpmname} = %{version}-%{release}

%description -n python38-%{rpmname} %_description

%prep
%setup -q -n python
mkdir -p ./packages
mkdir -p ./fdk_dependencies 

cp %{_sourcedir}/* ./fdk_dependencies

cp *whl ./fdk_dependencies


%build
/usr/bin/pip3 install --find-links ./fdk_dependencies --target ./packages --no-cache --no-cache-dir --no-index fdk-%{_rpm_version}%{PKG_EXTENSION} 

initFile=./packages/fdk/__init__.py
sed 4i"import os, sys" -i $initFile
sed 5i"sys.path.insert(0,(os.path.join(os.path.dirname(__file__),'packages')))" -i $initFile

bundled="fdk pbr pytest httptools wcwidth pyparsing py pluggy packaging more_itertools  attrs"

for pkg in $bundled; do
pushd packages/${pkg}-*dist-info
licenseDir=${PWD/packages/package_licenses}
mkdir -p $licenseDir
cp LICENSE* $licenseDir 
popd
done

mkdir -p fdk_dependencies/temp

packagesDir=${PWD/packages}

tar -zxvf ./fdk_dependencies/pytest-asyncio* --directory=fdk_dependencies/temp

pushd fdk_dependencies/temp/pytest-asyncio*
mkdir -p ${packagesDir}/package_licenses/pytest-asyncio
cp LICENSE  ${packagesDir}/package_licenses/pytest-asyncio
popd

rm -rf fdk_dependencies/temp

rm -rf ./fdk_dependencies/*whl
rm -rf ./fdk_dependencies/*tar.gz

%install
mkdir -p %{buildroot}/fdk
mkdir -p %{buildroot}/usr/lib/python3.8/site-packages 

install -d %{buildroot}%{python3_sitelib}/fdk/packages

cp  -r %{_builddir}/* %{buildroot}/fdk/
cp -r %{buildroot}/fdk/python/packages/fdk/* %{buildroot}%{python3_sitelib}/fdk/
mv %{buildroot}/fdk/python/packages/fdk*dist-info %{buildroot}%{python3_sitelib}/

cp -r %{buildroot}/fdk/python/packages/* %{buildroot}%{python3_sitelib}/fdk/packages
rm -rf %{buildroot}%{python3_sitelib}/fdk/packages/fdk*

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
/fdk/*
%{python3_sitelib}/fdk*

%changelog
* Wed Oct 20 2021 Srinivas Myla  <srinivas.myla@oracle.com>
- initial spec file for fdk 0.1.37