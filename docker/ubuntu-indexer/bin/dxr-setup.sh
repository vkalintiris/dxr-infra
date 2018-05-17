#!/bin/bash

set -ve

### Check that we are running as root
test `whoami` == 'root';

### Add jenkins user
useradd -u 1000 -d /home/jenkins -s /bin/bash -m jenkins;

mkdir /home/jenkins/src

# Configure mercurial
mkdir /home/jenkins/.mozbuild && chown jenkins:jenkins /home/jenkins/.mozbuild
cat <<EOM > /home/jenkins/.hgrc
[ui]
username = jenkins <jenkins@nowhere>
[diff]
git = 1
showfunc = 1
unified = 8
EOM
chown jenkins:jenkins /home/jenkins/.hgrc

# Get current blessed rev
REV=$(curl -s https://api.github.com/repos/mozilla/dxr/git/refs/heads/ci | jq -r '.object.sha')
if [[ ${REV} =~ ^[![:xdigit:]{32,40}]$ ]]; then
    echo "bad dxr rev $REV"
    exit 1
fi
git clone --recursive https://github.com/mozilla/dxr && \
    (cd dxr && git checkout $REV)

export PATH=/usr/lib/llvm-3.9/bin/:${PATH}
env VIRTUAL_ENV=`pwd`/venv CC=clang CXX=clang++ make -C dxr

chown -R jenkins:jenkins /home/jenkins

# Remove this script
rm $0; echo "Deleted $0";
