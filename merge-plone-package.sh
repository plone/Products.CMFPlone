#!/bin/bash
# helper script to merge `plone.app.` packages
# to be used from a plone coredev checkout
# usage: $ merge-plone-package layout

set -e
pkg=$1

../../bin/develop co plone.app.$pkg
../../bin/develop up plone.app.$pkg
git remote add $pkg ../plone.app.$pkg/
git fetch $pkg
git fetch --tags $pkg
git merge -s ours --no-commit $pkg/master
git read-tree --prefix=plone.app.$pkg/ -u $pkg/master
git mv plone.app.$pkg/plone/app/$pkg plone/app/
git mv plone.app.$pkg/README.txt plone/app/$pkg/
git mv plone.app.$pkg/CHANGES.txt plone/app/$pkg/
git rm -rf plone.app.$pkg/plone/
git commit -m "Merge \`plone.app.$pkg\` into \`Products.CMFPlone\`"

echo -e "\n\nPlease clean up the \`plone.app.$pkg\` directory and amend the last commit...\n"
find plone.app.$pkg
