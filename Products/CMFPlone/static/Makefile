FONT_DIR      ?= ./fonts

UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
BROWSEROPEN = open
else
BROWSEROPEN = x-www-browser
endif

FONTELLO_HOST ?= http://fontello.com

fontopen:
	@if test ! `which curl` ; then \
		echo 'Install curl first.' >&2 ; \
		exit 128 ; \
		fi
	curl --silent --show-error --fail --output .fontello \
		--form "config=@${FONT_DIR}/config.json" \
		${FONTELLO_HOST}
	${BROWSEROPEN} ${FONTELLO_HOST}/`cat .fontello`

fontsave:
	@if test ! `which unzip` ; then \
		echo 'Install unzip first.' >&2 ; \
		exit 128 ; \
		fi
	@if test ! -e .fontello ; then \
		echo 'Run `make fontopen` first.' >&2 ; \
		exit 128 ; \
		fi
	rm -rf .fontello.src .fontello.zip
	curl --silent --show-error --fail --output .fontello.zip \
		${FONTELLO_HOST}/`cat .fontello`/get
	unzip .fontello.zip -d .fontello.src
	mkdir -p ${FONT_DIR}
	{ \
        set -e ;\
	BASEDIR=$$(find ./.fontello.src -maxdepth 1 -name 'fontello-*');\
	echo Unzipped font in $$BASEDIR;\
	cp $$BASEDIR/config.json ${FONT_DIR}/config.json;\
	cp $$BASEDIR/font/* ${FONT_DIR}/;\
	sed 's/\.\.\/font\//\@\{fontsPrefix\}plone-/g' $$BASEDIR/css/fontello.css >${FONT_DIR}/fontello.less;\
	rm -rf .fontello.src .fontello.zip ;\
        }
