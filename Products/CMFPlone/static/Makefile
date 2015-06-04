# Edit here - set path to you directory with config.json & fonts

FONT_DIR      ?= ./fonts

### Don't edit below ###

FONTELLO_HOST ?= http://fontello.com

fontopen:
	@if test ! `which curl` ; then \
		echo 'Install curl first.' >&2 ; \
		exit 128 ; \
		fi
	curl --silent --show-error --fail --output .fontello \
		--form "config=@${FONT_DIR}/config.json" \
		${FONTELLO_HOST}
	open ${FONTELLO_HOST}/`cat .fontello`


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
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/config.json ${FONT_DIR}/config.json
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/font/fontello.eot ${FONT_DIR}/plone-fontello.eot
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/font/fontello.woff ${FONT_DIR}/plone-fontello.woff
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/font/fontello.ttf ${FONT_DIR}/plone-fontello.ttf
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/font/fontello.svg ${FONT_DIR}/plone-fontello.svg
	mv `find ./.fontello.src -maxdepth 1 -name 'fontello-*'`/css/fontello.css ${FONT_DIR}/plone-fontello.less
	sed -i.bak 's/\.\.\/font\//\@\{fontsPrefix\}plone-/g' ${FONT_DIR}/plone-fontello.less
	rm -rf ${FONT_DIR}/plone-fontello.less.bak
	rm -rf .fontello.src .fontello.zip