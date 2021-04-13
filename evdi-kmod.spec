%global	kmod_name evdi

%global	debug_package %{nil}

# Generate kernel symbols requirements:
%global _use_internal_dependency_generator 0

# If kversion isn't defined on the rpmbuild line, define it here. For Fedora,
# kversion needs always to be defined as there is no kABI support.
%{!?kversion: %global kversion 4.18.0-240.22.1.el8_3}

Name:           %{kmod_name}-kmod
Version:        1.9.1
Release:        1%{?dist}
Summary:        DisplayLink VGA/HDMI display driver kernel module
Epoch:          1
License:        GPLv2
URL:            https://github.com/DisplayLink/evdi

Source0:        https://github.com/DisplayLink/%{kmod_name}/archive/v%{version}.tar.gz#/%{kmod_name}-%{version}.tar.gz
Patch0:         https://github.com/DisplayLink/%{kmod_name}/commit/0f1ad2153de1bc144f2359afa91fbe3fa07e9e7a.patch
Patch1:         el8.patch

BuildRequires:  elfutils-libelf-devel
BuildRequires:  gcc
BuildRequires:  kernel-devel %{?kversion:== %{kversion}}
BuildRequires:  kernel-abi-whitelists %{?kversion:== %{kversion}}
BuildRequires:  kmod
BuildRequires:  redhat-rpm-config

%description
This package provides the DisplayLink VGA/HDMI display kernel driver module.
It is built to depend upon the specific ABI provided by a range of releases of
the same variant of the Linux kernel and not on any one specific build.

%package -n kmod-%{kmod_name}
Summary:    %{kmod_name} kernel module(s)

Provides:   kabi-modules = %{kversion}.%{_target_cpu}
Provides:   %{kmod_name}-kmod = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:   module-init-tools

%description -n kmod-%{kmod_name}
This package provides the %{kmod_name} kernel module(s) built for the Linux kernel
using the %{_target_cpu} family of processors.

%post -n kmod-%{kmod_name}
if [ -e "/boot/System.map-%{kversion}.%{_target_cpu}" ]; then
    /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}.%{_target_cpu}" "%{kversion}.%{_target_cpu}" > /dev/null || :
fi
modules=( $(find /lib/modules/%{kversion}.%{_target_cpu}/extra/%{kmod_name} | grep '\.ko$') )
if [ -x "/usr/sbin/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | /usr/sbin/weak-modules --add-modules
fi

%preun -n kmod-%{kmod_name}
rpm -ql kmod-%{kmod_name}-%{version}-%{release}.%{_target_cpu} | grep '\.ko$' > /var/run/rpm-kmod-%{kmod_name}-modules

%postun -n kmod-%{kmod_name}
if [ -e "/boot/System.map-%{kversion}.%{_target_cpu}" ]; then
    /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}.%{_target_cpu}" "%{kversion}.%{_target_cpu}" > /dev/null || :
fi
modules=( $(cat /var/run/rpm-kmod-%{kmod_name}-modules) )
rm /var/run/rpm-kmod-%{kmod_name}-modules
if [ -x "/usr/sbin/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | /usr/sbin/weak-modules --remove-modules
fi

%prep
%autosetup -p1 -n %{kmod_name}-%{version}

echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

%build
make -C %{_usrsrc}/kernels/%{kversion}.%{_target_cpu} M=$PWD/module modules

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=extra/%{kmod_name}

make -C %{_usrsrc}/kernels/%{kversion}.%{_target_cpu} M=$PWD/module modules_install


install -d %{buildroot}%{_sysconfdir}/depmod.d/
install kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
# Remove the unrequired files.
rm -f %{buildroot}/lib/modules/%{kversion}.%{_target_cpu}/modules.*

%files -n kmod-%{kmod_name}
/lib/modules/%{kversion}.%{_target_cpu}/extra/*
%config /etc/depmod.d/kmod-%{kmod_name}.conf

%changelog
* Tue Apr 13 2021 Simone Caronni <negativo17@gmail.com> - 1:1.9.1-1
- First build.
