#!/bin/bash
#
# Install requirements that can be cached between docker builds
#

set -e
set -x

apt-get update
apt-get -y dist-upgrade
apt-get clean
rm -rf /var/lib/apt/lists/*

PYPI="https://pypi.sunet.se/simple/"
ping -c 1 -q pypiserver.docker && PYPI="http://pypiserver.docker:8080/simple/"

echo "#############################################################"
echo "$0: Using PyPi URL ${PYPI}"
echo "#############################################################"

/opt/eduid/bin/pip install -i ${PYPI} gunicorn

/opt/eduid/bin/pip freeze

rm -rf /.cache
