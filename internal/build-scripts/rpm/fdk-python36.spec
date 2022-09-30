%global python3_pkgversion2 %(%{__python3} -c "import sys; sys.stdout.write(sys.version[:3].replace('.', ''))")
%global python3_pkgversion %{python3_pkgversion2}
%global debug_package %{nil}

%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define srcname fdk
%define rpmname fdk
%define _unpackaged_files_terminate_build 0
%define PKG_EXTENSION -py3-none-any.whl

Name: fn-python36-fdk
Version: %{_rpm_version}
Release: 1%{?dist}
Url: http://pypi.python.org/pypi/%{srcname}
Summary: Oracle Cloud Infrastructure Python FDK
License: Apache2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

SOURCE0: fdk-%{_rpm_version}.tar.gz
SOURCE1: pytest-%{_pytest_version}-py3-none-any.whl
SOURCE2: pbr-%{_pbr_version}-py2.py3-none-any.whl
SOURCE3: iso8601-%{_iso_version}-py3-none-any.whl
SOURCE4: pytest-asyncio-%{_pytest_asyncio_version}.tar.gz
SOURCE5: contextvars-%{_contextvars_version}.tar.gz
SOURCE6: httptools-%{_httptools_version}-cp36-cp36m-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
SOURCE7: zipp-%{_zipp_version}-py3-none-any.whl
SOURCE8: wcwidth-%{_wcwidth_version}-py2.py3-none-any.whl
SOURCE9: typing_extensions-%{_typing_extensions_version}-py3-none-any.whl
SOURCE10: pyparsing-%{_pyparsing_version}-py3-none-any.whl
SOURCE11: py-%{_py_version}-py2.py3-none-any.whl
SOURCE12: pluggy-%{_pluggy_version}-py2.py3-none-any.whl
SOURCE13: packaging-%{_packaging_version}-py3-none-any.whl
SOURCE14: more_itertools-%{_more_itertools_version}-py3-none-any.whl
SOURCE15: importlib_metadata-%{_importlib_metadata_version}-py3-none-any.whl
SOURCE16: immutables-%{_immutables_version}-cp36-cp36m-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
SOURCE17: attrs-%{_attrs_version}-py2.py3-none-any.whl

BuildArch: x86_64
BuildRequires: python3 >= 3.6, python3 < 3.7
Requires: python3 >= 3.6,  python3 < 3.7
Provides: python3-%{rpmname} = %{version}-%{release}

%description 
Python FDK for Oracle Cloud Infrastructure.

%prep
%setup -q -n fdk

%build

%install
/usr/bin/pip3 install --find-links %{_sourcedir} --target %{buildroot}/%{python3_sitelib}/fdk/packages --no-cache --no-cache-dir --no-index fdk-%{_rpm_version}%{PKG_EXTENSION} 
initFile=%{buildroot}%{python3_sitelib}/fdk/packages/fdk/__init__.py
sed 4i"import os, sys" -i $initFile
sed 5i"sys.path.insert(0,(os.path.join(os.path.dirname(__file__),'packages')))" -i $initFile
mv %{buildroot}/%{python3_sitelib}/fdk/packages/fdk*dist-info %{buildroot}%{python3_sitelib}/
mv %{buildroot}%{python3_sitelib}/fdk/packages/fdk/* %{buildroot}%{python3_sitelib}/fdk
rm %{buildroot}/fdk/packages/fdk -rf

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)

%{python3_sitelib}/fdk*

%changelog
* Wed Oct 20 2021 Srinivas Myla  <srinivas.myla@oracle.com>
- initial spec file for fdk 0.1.37
