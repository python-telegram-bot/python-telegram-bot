#!/bin/bash

set -e

cleanup() {
    rm -rf debian
}

trap cleanup EXIT

cp -R contrib/debian .
debuild -us -uc
debian/rules clean
