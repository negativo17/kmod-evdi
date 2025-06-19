%global	kmod_name evdi
%global	debug_package %{nil}

# Build flags are inherited from the kernel
%undefine _auto_set_build_flags

%{!?kversion: %global kversion %(uname -r)}

Name:           kmod-%{kmod_name}
Version:        1.14.10
Release:        3%{?dist}
Summary:        DisplayLink VGA/HDMI display driver kernel module
Epoch:          1
License:        GPLv2
URL:            https://github.com/DisplayLink/%{kmod_name}

Source0:        %{url}/archive/v%{version}.tar.gz#/%{kmod_name}-%{version}.tar.gz
Patch0:         https://github.com/DisplayLink/evdi/commit/ae34f70a02552b41697ba753323427281e977e17.patch
Patch1:         https://github.com/DisplayLink/evdi/commit/3673a4b34d386921fc323ddbd2ef0e000022e2d4.patch
# Required for CentOS Stream (10.1), not required for 10.0:
Patch2:         0001-Revert-CentOS-Stream-10-change.patch

BuildRequires:  elfutils-libelf-devel
BuildRequires:  gcc
BuildRequires:  kernel-abi-stablelists
BuildRequires:  kernel-devel
BuildRequires:  kernel-rpm-macros
BuildRequires:  kmod
BuildRequires:  redhat-rpm-config

Provides:   kabi-modules = %{kversion}
Provides:   %{kmod_name}-kmod = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:   module-init-tools

%description
This package provides the DisplayLink VGA/HDMI display kernel driver module.
It is built to depend upon the specific ABI provided by a range of releases of
the same variant of the Linux kernel and not on any one specific build.

This package provides the %{kmod_name} kernel module(s) built for the Linux
kernel %{kversion}.

%prep
%autosetup -p1 -n %{kmod_name}-%{version}

echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

%build
make -C %{_usrsrc}/kernels/%{kversion} M=$PWD/module modules
find . -name "*.ko"

%install
install -p -m 0644 -D module/evdi.ko %{buildroot}%{_prefix}/lib/modules/%{kversion}/extra/evdi/evdi.ko

install -d %{buildroot}%{_sysconfdir}/depmod.d/
install kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
# Remove the unrequired files.
rm -f %{buildroot}/lib/modules/%{kversion}/modules.*

# Compress modules:
find %{buildroot} -type f -name '*.ko' | xargs %{__strip} --strip-debug
find %{buildroot} -type f -name '*.ko' | xargs xz

%post
if [ -e "/boot/System.map-%{kversion}" ]; then
    %{_sbindir}/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null || :
fi
modules=( $(find %{_prefix}/lib/modules/%{kversion}/extra/%{kmod_name} | grep '\.ko.xz$') )
if [ -x "%{_sbindir}/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | %{_sbindir}/weak-modules --add-modules
fi

%preun
rpm -ql kmod-%{kmod_name}-%{version}-%{release}.%{_target_cpu} | grep '\.ko.xz$' > %{_var}/run/rpm-kmod-%{kmod_name}-modules

%postun
if [ -e "/boot/System.map-%{kversion}" ]; then
    %{_sbindir}/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null || :
fi
modules=( $(cat %{_var}/run/rpm-kmod-%{kmod_name}-modules) )
rm %{_var}/run/rpm-kmod-%{kmod_name}-modules
if [ -x "%{_sbindir}/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | %{_sbindir}/weak-modules --remove-modules
fi

%files
%{_prefix}/lib/modules/%{kversion}/extra/*
%config /etc/depmod.d/kmod-%{kmod_name}.conf

%changelog
* Wed Jun 18 2025 Simone Caronni <negativo17@gmail.com> - 1:1.14.10-3
- Do not set build flags.

* Wed May 21 2025 Simone Caronni <negativo17@gmail.com> - 1:1.14.10-2
- Add upstream patches.

* Wed May 14 2025 Simone Caronni <negativo17@gmail.com> - 1:1.14.10-1
- Update to 1.14.10.

* Thu Mar 27 2025 Simone Caronni <negativo17@gmail.com> - 1:1.14.9-1
- Update to 1.14.9.

* Wed Mar 12 2025 Simone Caronni <negativo17@gmail.com> - 1:1.14.8-2
- Rename source package from nvidia-kmod to kmod-nvidia, the former is now used
  for the akmods variant.
- Use /usr/lib/modules for installing kernel modules and not /lib/modules.
- Drop compress macro and just add a step during install.

* Sun Dec 22 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.8-1
- Update to 1.14.8.

* Fri Dec 06 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.7-2
- Add kernel 6.12 patch and EL 9.5 patch.
- Trim changelog.

* Sun Sep 29 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.7-1
- Update to 1.14.7.

* Thu Aug 15 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.6-1
- Update to 1.14.6 final.

* Mon Aug 12 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.5-2.20240726giteab561a
- Update to latest snapshot to allow building on kernel 6.10.

* Tue Jul 02 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.5-1
- Update to 1.14.5.
- Drop EL7 support.

* Wed Jun 05 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.4-2
- Rebuild for latest kernel.

* Tue Apr 16 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.4-1
- Update to 1.14.4.

* Fri Mar 22 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.2-2
- Sync uname -r with kversion passed from scripts.

* Thu Feb 08 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.2-1
- Update to final 1.14.2.

* Tue Feb 06 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.1-5.20240130gitd21a6ea
- Update to latest snapshot.

* Mon Jan 08 2024 Simone Caronni <negativo17@gmail.com> - 1:1.14.1-4.20240104git0313eca
- Update to latest snapshot.
