GIT = git
NPM = npm

NODE_VERSION = $(shell node -v)
NODE_VERSION_MAJ = $(shell echo $(NODE_VERSION) | cut -f1 -d. | cut -f2 -dv )
NODE_VERSION_MIN = $(shell echo $(NODE_VERSION) | cut -f2 -d.)
NODE_VERSION_LT_011 = $(shell [ $(NODE_VERSION_MAJ) -eq 0 -a $(NODE_VERSION_MIN) -lt 11 ] && echo true)

GRUNT = ./node_modules/grunt-cli/bin/grunt
BOWER = ./node_modules/bower/bin/bower
NODE_PATH = ./node_modules


bootstrap-common: clean
	mkdir -p build

bootstrap: clean bootstrap-common
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
	NODE_PATH=$(NODE_PATH) $(GRUNT) sed:bootstrap

bootstrap-nix: bootstrap-common
	nix-build default.nix -A build -o nixenv
	ln -s nixenv/lib/node_modules/mockup-core/node_modules
	ln -s nixenv/bower_components

jshint:
	NODE_PATH=$(NODE_PATH) $(GRUNT) jshint jscs

test:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test --pattern=$(pattern)

test-once:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_once --pattern=$(pattern)

test-dev:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_dev --pattern=$(pattern)

test-serve:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_serve --pattern=$(pattern)

test-ci:
	NODE_PATH=$(NODE_PATH) $(GRUNT) test_ci

clean:
	rm -rf node_modules
	rm -rf bower_components

clean-deep: clean
	if test -f $(BOWER); then NODE_PATH=$(NODE_PATH) $(BOWER) cache clean; fi

.PHONY: bootstrap jshint test test-once test-dev test-ci clean clean-deep
