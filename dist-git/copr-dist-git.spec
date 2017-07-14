Name:       copr-dist-git
Version:    0.32
Release:    1%{?dist}
Summary:    Copr services for Dist Git server

Group:      Applications/Productivity
License:    GPLv2+
URL:        https://pagure.io/copr/copr
# Source is created by
# git clone https://pagure.io/copr/copr.git
# cd copr/dist-git
# tito build --tgz
Source0: %{name}-%{version}.tar.gz

BuildArch:  noarch
ExclusiveArch: %{ix86} x86_64 %{arm} aarch64 ppc64le powerpc64le s390x %{mips}

BuildRequires: systemd
BuildRequires: dist-git
BuildRequires: python-bunch
BuildRequires: python-requests
BuildRequires: python-munch
BuildRequires: pyrpkg >= 1.47
# check
BuildRequires: python-six
BuildRequires: python-netaddr
BuildRequires: python-dateutil
BuildRequires: pytest
BuildRequires: python-pytest-cov
BuildRequires: python-mock
%if 0%{?el7}
BuildRequires: python-psutil
%else
BuildRequires: python2-psutil
%endif
BuildRequires: pytz

%if 0%{?fedora} > 23
# BuildRequires also because of build-time tests
BuildRequires: python2-jinja2
Requires: python2-jinja2
%else
BuildRequires: python-jinja2
Requires: python-jinja2
%endif

Requires: systemd
Requires: dist-git
Requires: python-bunch
Requires: python-requests
%if 0%{?el7}
Requires: python-psutil
%else
Requires: python2-psutil
%endif
Requires: python-jinja2
Requires: pyrpkg >= 1.47
Requires: httpd
Requires: git-svn
Requires: python-munch
Requires: pyp2rpm
Requires: rubygem-gem2rpm

%{?fedora:Requires(post): policycoreutils-python-utils}
%{?rhel:Requires(post): policycoreutils-python}

%description
COPR is lightweight build system. It allows you to create new project in WebUI
and submit new builds and COPR will create yum repository from latest builds.

This package contains Copr services for Dist Git server.


%prep
%setup -q


%build

%pre
getent group packager >/dev/null || groupadd -r packager
getent group copr-dist-git >/dev/null || groupadd -r copr-dist-git
getent group apache >/dev/null || groupadd -r apache
getent passwd copr-dist-git >/dev/null || \
useradd -r -m -g copr-dist-git -G packager,docker,apache -c "copr-dist-git user" copr-dist-git
/usr/bin/passwd -l copr-dist-git >/dev/null

exit 0

%install

install -d %{buildroot}%{_datadir}/copr/dist_git
install -d %{buildroot}%{_sysconfdir}/copr
install -d %{buildroot}%{_sysconfdir}/logrotate.d/
install -d %{buildroot}%{_sysconfdir}/httpd/conf.d/
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_var}/log/copr-dist-git
install -d %{buildroot}%{_sharedstatedir}/copr-dist-git
install -d %{buildroot}%{_bindir}/

cp -a dist_git/* %{buildroot}%{_datadir}/copr/dist_git
cp -a conf/copr-dist-git.conf.example %{buildroot}%{_sysconfdir}/copr/copr-dist-git.conf
cp -a conf/httpd/copr-dist-git.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/copr-dist-git.conf
cp -a copr-dist-git.service %{buildroot}%{_unitdir}/
cp -a run/* %{buildroot}%{_bindir}/

cp -a conf/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/copr-dist-git

# for ghost files
touch %{buildroot}%{_var}/log/copr-dist-git/main.log

%check

%if 0%{?fedora} >= 21
# too old `pytest` in epel repo
PYTHONPATH=.:$PYTHONPATH python -B -m pytest \
  -v --cov-report term-missing --cov ./dist_git ./tests/
%endif

%post
# change context to be readable by cgit
semanage fcontext -a -t httpd_sys_content_t '/var/lib/copr-dist-git(/.*)?'
restorecon -rv /var/lib/copr-dist-git
%systemd_post copr-dist-git.service

%preun
%systemd_preun copr-dist-git.service

%postun
%systemd_postun_with_restart copr-dist-git.service

%files
%license LICENSE

%{_bindir}/*
%dir %{_datadir}/copr 
%{_datadir}/copr/*
%dir %{_sysconfdir}/copr
%config(noreplace) %attr(0640, root, copr-dist-git) %{_sysconfdir}/copr/copr-dist-git.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/httpd/conf.d/copr-dist-git.conf

%dir %attr(0755, copr-dist-git, copr-dist-git) %{_sharedstatedir}/copr-dist-git/

%{_unitdir}/copr-dist-git.service

%dir %{_sysconfdir}/logrotate.d
%config(noreplace) %{_sysconfdir}/logrotate.d/copr-dist-git
%attr(0755, copr-dist-git, copr-dist-git) %{_var}/log/copr-dist-git
%attr(0644, copr-dist-git, copr-dist-git) %{_var}/log/copr-dist-git/main.log
%ghost %{_var}/log/copr-dist-git/*.log

%changelog
* Fri Jul 14 2017 clime <clime@redhat.com> 0.32-1
- srpms are now not being built on dist-git
- MockSCM and Tito methods unified into single source

* Fri Jul 07 2017 clime <clime@redhat.com> 0.31-1
- remove no longer required condition for a scm import to run
- .spec build implemented
- fedora:25 image offers the needed en_US.UTF-8 locale now
- Dockerfile with less layers

* Fri Jun 09 2017 clime <clime@redhat.com> 0.30-1
- import build task only once
- remove unsupported --depth from git svn command
- add dep on git-svn
- better exception handling in MockScmProvider
- fix 'git svn clone' and add exception handling for clone part in MockScm provider

* Thu Jun 01 2017 clime <clime@redhat.com> 0.29-1
- Bug 1457888 - Mock SCM method fails to build a package
- increase depth for git clone so that required tags that tito needs are downloaded

* Wed May 31 2017 clime <clime@redhat.com> 0.28-1
- add --depth 1 for git clone in GitProvider
- add missing 'which' for tito && git-annex builds
- arbitrary dist-git branching support
- use MockScmProvider without mock-scm to solve performance problems
- add "powerpc64le" into list of archs to allow building for

* Mon May 15 2017 clime <clime@redhat.com> 0.27-1
- Bug 1447102 - fedpkg build fail during import phase

* Wed Apr 12 2017 clime <clime@redhat.com> 0.26-1
- follow docker ExclusiveArches spec directive
- replace leftover username in lograte config
- fix README

* Mon Apr 10 2017 clime <clime@redhat.com> 0.25-1
- compatibility fixes for the latest dist-git (upstream)
- improved error logging and exception handling of external commands
- improve repo creation & srpm import logging and exception handling
- replace copr-service user by copr-dist-git and useradd the user
- Bug 1426033 - git-annex missing, cannot use tito.builder.GitAnnexBuilder
- replace fedorahosted links
- error logging of pyrpkg upload into lookaside
- update langpack hack in dist-git Dockerfile

* Thu Jan 26 2017 clime <clime@redhat.com> 0.24-1
- install mock-scm in docker image from official fedora repos
- upgrade docker image to f25
- Fixes for building COPR Backend and Dist-git on EL7
- fix copy hack for new internal pyrpkg API

* Thu Dec 01 2016 clime <clime@redhat.com> 0.23-1
- use other than epel chroot for scm building
- use newest mock
- run mock-scm inside of docker
- add README information about how docker image is built
- stripped down impl of building from dist-git
- fixed unittests
- refactor VM.run method
- remove exited containers
- add possibility to run dist-git in single thread
- refactor lookaside my_upload slightly
- Bug 1377780 - Multiple failed tasks with: Importing SRPM into Dist Git failed.

* Mon Sep 19 2016 clime <clime@redhat.com> 0.22-1
- fix Git&Tito subdirectory use-case

* Mon Sep 19 2016 clime <clime@redhat.com> 0.21-1
- Git&Tito, pyp2rpm, gem2rpm now run in docker

* Mon Aug 15 2016 clime <clime@redhat.com> 0.20-1
- try to obtain multiple tasks at once
- Add python2-psutil requirement
- inform frontend about terminated task
- log when starting and finishing workers
- log timeout value from worker
- run mock with --uniqueext
- implement timeout-based terminating
- parallelization by pool of workers

* Fri May 27 2016 clime <clime@redhat.com> 0.19-1
- strip whitespaces from the gem name

* Thu May 26 2016 clime <clime@redhat.com> 0.18-1
- implemented building from rubygems

* Fri Apr 22 2016 Miroslav Suchý <msuchy@redhat.com> 0.17-1
- support for pyrpkg-1.43
- typo in method name
- use os.listdir instead of Popen
- sort imports
- more verbose logging of exception

* Tue Apr 12 2016 Miroslav Suchý <msuchy@redhat.com> 0.16-1
- clean up after dist-git import
- assure python_versions type for pypi builds
- 1322553 - checkout specific branch

* Fri Mar 18 2016 Miroslav Suchý <msuchy@redhat.com> 0.15-1
- own /etc/logrotate.d
- own /usr/share/copr
- trailing dot in description

* Mon Mar 14 2016 Jakub Kadlčík <jkadlcik@redhat.com> 0.14-1
- per task logging for users
- don't assume the SCM repo has the same name as the package
- added policycoreutils-python-utils dependency
- do shallow git clone for mock-scm
- support building from PyPI

* Fri Jan 29 2016 Miroslav Suchý <msuchy@redhat.com> 0.13-1
- [dist-git] error handling based on subprocess return codes instead of output
  to stderr (e.g. git outputs progress to stderr) + missing catch for
  GitException in do_import (results in better error messages in frontend, see
  bz#1295540)

* Mon Jan 25 2016 Miroslav Suchý <msuchy@redhat.com> 0.12-1
- pass --scm-option spec=foo to mock-scm (msuchy@redhat.com)

* Thu Jan 21 2016 clime <clime@redhat.com> 0.11-1
- tito added to requirements

* Sat Jan 16 2016 clime <clime@redhat.com> 0.10-1
- fixed do_import test
- workaround for BZ 1283101

* Mon Nov 16 2015 Miroslav Suchý <msuchy@redhat.com> 0.9-1
- make more abstract exceptions
- implement support for multiple Mock SCMs
- split SourceDownloader to multiple SourceProvider classes
- refactor duplicate code from GIT_AND_TITO and GIT_AND_MOCK
- require mock-scm
- implement mock support in dist-git
- do not check cert when downloading srpm

* Mon Nov 02 2015 Miroslav Suchý <msuchy@redhat.com> 0.8-1
- add Git and Tito errors
- tito support
- hotfix for resubmit button

* Tue Sep 15 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.7-1
- provide build failure details
- replace urllib.urlretrieve with requests.get to catch non-200 HTTP  status codes

* Fri Aug 14 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.6-1
- [dist-git][rhbz: #1253335] Running rpkg in the dedicated process.

* Wed Aug 05 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.5-1
- don't run tests during %check on epel

* Wed Aug 05 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.4-1
- additional BuildRequires to run tests

* Tue Aug 04 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.3-1
- fixed commit message to include package name and version
- added initial tests; renamed folder with sources to use underscore instead of dash
- mark build as failed for any error during import
- don't break on the post failure to frontend
- get pkg name + version during import
- Use /var/lib/copr-dist-git/ to store pkg listing.
- refresh cgit after import

* Thu Jul 23 2015 Valentin Gologuzov <vgologuz@redhat.com> 0.2-1
- new package built with tito

* Thu Jun 25 2015 Adam Samalik <asamalik@redhat.com> 0.1
- basic package
