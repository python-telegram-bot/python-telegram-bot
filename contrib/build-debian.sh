#!/bin/bash

cp -R contrib/debian .
debuild -us -uc
debian/rules clean
rm -rf debian

