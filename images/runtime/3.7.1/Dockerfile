FROM python:3.7.1-slim-stretch

RUN addgroup --gid 1000 --system fn && adduser --system --uid 1000 --ingroup fn fn

# "apt" per CVE-2019-3462
# "systemd" per CVE-2018-16865
# "openssl" per CVE-2018-0732
# "glibc" per CWE-119 | CVE-2017-15671
# "multiarch-support" per CWE-119 | CVE-2017-15671
# "libapt-pkg5.0" per CVE-2019-3462
# "libudev1" per CVE-2018-16865
RUN apt-get upgrade -qy && \
  apt-get update && apt-get install -qy --no-install-recommends \
  apt systemd openssl libc6 multiarch-support libapt-pkg5.0 libudev1 libssl1.1 perl-base && \
  apt-get download libc-bin && \
  dpkg -x libc-bin*.deb unpackdir/ && \
  cp unpackdir/sbin/ldconfig /sbin/ && \
  apt-get install --reinstall libc-bin && \
  apt-get clean
