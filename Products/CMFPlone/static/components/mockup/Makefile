GIT = git
NPM = npm
NODE_VERSION = $(shell node -v)
NODE_VERSION_MAJ = $(shell echo $(NODE_VERSION) | cut -f1 -d. | cut -f2 -dv )
NODE_VERSION_MIN = $(shell echo $(NODE_VERSION) | cut -f2 -d.)
NODE_VERSION_LT_011 = $(shell [ $(NODE_VERSION_MAJ) -eq 0 -a $(NODE_VERSION_MIN) -lt 11 ] && echo true)

GRUNT = ./node_modules/grunt-cli/bin/grunt
BOWER = ./node_modules/bower/bin/bower
NODE_PATH = ./node_modules

DEBUG =
ifeq ($(debug), true)
	DEBUG = --debug
endif
VERBOSE =
ifeq ($(verbose), true)
	VERBOSE = --verbose
endif


all: test-once bundles docs

stamp-npm: package.json
	npm install
	touch stamp-npm

stamp-bower: stamp-npm bower.json
	$(BOWER) install
	touch stamp-bower

bundles: stamp-bower bundle-widgets bundle-structure bundle-plone
	# ----------------------------------------------------------------------- #
	# cp build/widgets* path/to/plone.app.widgets/plone/app/widgets/static
	# cp build/structure* path/to/wildcard.foldercontents/wildcard/foldercontents/static
	# cp build/plone* path/to/Products.CMFPlone/Products/CMFPlone/static
	# ----------------------------------------------------------------------- #

bundle-widgets:
	mkdir -p build
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-widgets $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bundle-structure:
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-structure $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bundle-plone:
	mkdir -p build
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-plone $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bundle-filemanager:
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-filemanager $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bundle-resourceregistry:
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-resourceregistry $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

docs:
	rm -Rf mockup/docs; mkdir mockup/docs; cp -R .git mockup/docs; cd mockup/docs; $(GIT) checkout gh-pages;
	# if test ! -d mockup/docs; then $(GIT) clone git://github.com/plone/mockup.git -b gh-pages mockup/docs; fi
	rm -rf mockup/docs/dev
	NODE_PATH=$(NODE_PATH) $(GRUNT) bundle-docs $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bootstrap-common:
	mkdir -p build

bootstrap: bootstrap-common
	@echo node version: $(NODE_VERSION)
ifeq ($(NODE_VERSION_LT_011),true)
	# for node < v0.11.x
	$(NPM) link --prefix=.
	# remove lib/node_modules, which contains a symlink to the project root.
	# This leads to infinite recursion at the grunt copy task on make docs.
	rm -rf lib/node_modules
else
	$(NPM) link
endif
	NODE_PATH=$(NODE_PATH) $(BOWER) install --config.interactive=0
	NODE_PATH=$(NODE_PATH) $(GRUNT) sed:bootstrap $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

bootstrap-nix: clean bootstrap-common
	nix-build default.nix -A build -o nixenv
	ln -s nixenv/lib/node_modules/mockup/node_modules
	ln -s nixenv/bower_components

jshint:
	NODE_PATH=$(NODE_PATH) $(GRUNT) jshint jscs $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

watch:
	NODE_PATH=$(NODE_PATH) $(GRUNT) watch $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

test: stamp-bower
	NODE_PATH=$(NODE_PATH) $(GRUNT) test $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js --pattern=$(pattern)

test-once: stamp-bower
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_once $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js --pattern=$(pattern)

test-jenkins: stamp-bower
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_jenkins $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js --pattern=$(pattern)

test-dev:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_dev $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js --pattern=$(pattern)

test-serve:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_serve $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js --pattern=$(pattern)

test-ci:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_ci $(DEBUG) $(VERBOSE) --gruntfile=mockup/Gruntfile.js

clean:
	mkdir -p build
	rm -rf build
	rm -rf node_modules
	rm -rf mockup/bower_components
	rm -f stamp-npm stamp-bower
	rm -rf node_modules src/bower_components

clean-deep: clean
	if test -f $(BOWER); then $(BOWER) cache clean; fi
	if test -f $(NPM); then $(NPM) cache clean; fi

publish-docs:
	echo -e "Publishing 'docs' bundle!\n"; cd mockup/docs; git add -fA .; git commit -m "Publishing docs"; git push -f git@github.com:plone/mockup.git gh-pages; cd ../..;
	# echo -e "Publishing 'docs' bundle!\n"; cd mockup/docs; git add -fA .; git commit -m "Travis build $(TRAVIS_BUILD_NUMBER) pushed to 'docs'."; git push -fq https://$(GH_TOKEN)@github.com/plone/mockup.git gh-pages > /dev/null; cd ..;

i18n-dump:
	NODE_PATH=$(NODE_PATH) $(GRUNT) i18n-dump --gruntfile=mockup/Gruntfile.js 

.PHONY: bundle bundle-widgets bundle-structure bundle-plone docs bootstrap bootstrap-nix jshint test test-once test-dev test-ci publish-docs clean clean-deep
