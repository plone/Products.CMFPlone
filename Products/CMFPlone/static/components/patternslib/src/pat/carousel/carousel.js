/**
 * Patterns carousel
 *
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 * Copyright 2012-2013 Florian Friesdorf
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger",
    "pat-parser",
    "jquery.anythingslider"
], function($, patterns, logger, Parser) {
    var log = logger.getLogger("pat.carousel"),
        parser = new Parser("carousel");

    parser.addArgument("auto-play", false);
    parser.addArgument("loop", true);
    parser.addArgument("resize", false);
    parser.addArgument("expand", false);
    parser.addArgument("control-arrows", true);
    parser.addArgument("control-navigation", false);
    parser.addArgument("control-startstop", false);
    parser.addArgument("time-delay", 3000);
    parser.addArgument("time-animation", 600);

    var carousel = {
        name: "carousel",
        trigger: ".pat-carousel",

        init: function($el, opts) {
            return $el.each(function() {
                var $carousel = $(this),
                    options = parser.parse($carousel, opts),
                    settings = {hashTags: false};

                settings.autoPlay = options.autoPlay;
                settings.stopAtEnd = !options.loop;
                settings.resizeContents = options.resize;
                settings.expand = options.expand;
                settings.buildArrows = options.control.arrows;
                settings.buildNavigation = options.control.navigation;
                settings.buildStartStop = options.control.startstop;
                settings.delay = options.time.delay;
                settings.animationTime = options.time.animation;
                settings.onInitialized = carousel.onInitialized;
                settings.onSlideInit = carousel.onSlideInit;
                carousel.setup($carousel, settings);
            });
        },

	setup: function($el, settings) {
            var loaded = true,
                $images = $el.find("img"),
                img, i;
            for (i=0; loaded && i<$images.length; i++) {
                img=$images[i];
                if (!img.complete || img.naturalWidth===0)
                    loaded=false;
            }
            if (!loaded) {
                log.debug("Delaying carousel setup until images have loaded.");
                setTimeout(function() {
                    carousel.setup($el, settings);
                }, 50);
                return;
            }

            var $carousel = $el.anythingSlider(settings),
                control = $carousel.data("AnythingSlider"),
                $panel_links = $();

            $carousel
                .children().each(function(index) {
                    if (!this.id)
                        return;

                    var $links = $("a[href=#" + this.id+"]");
                    if (index===control.currentPage)
                        $links.addClass("current");
                    else
                        $links.removeClass("current");
                    $links.on("click.pat-carousel", null, {control: control, index: index}, carousel.onPanelLinkClick);
                    $panel_links = $panel_links.add($links);
                }).end()
                .on("slide_complete.pat-carousel", null, $panel_links, carousel.onSlideComplete);
	},

        _loadPanelImages: function(slider, page) {
            var $img;
            log.info("Loading lazy images on panel " + page);
            slider.$items.eq(page).find("img").andSelf().filter("[data-src]").each(function() {
                $img=$(this);
                this.src=$img.attr("data-src");
                $img.removeAttr("data-src");
            });
        },

        onPanelLinkClick: function(event) {
            event.data.control.gotoPage(event.data.index, false);
            event.preventDefault();
        },

        onInitialized: function(event, slider) {
            carousel._loadPanelImages(slider, slider.options.startPanel);
            carousel._loadPanelImages(slider, slider.options.startPanel+1);
            carousel._loadPanelImages(slider, 0);
            carousel._loadPanelImages(slider, slider.pages+1);
        },

        onSlideInit: function(event, slider) {
            carousel._loadPanelImages(slider, slider.targetPage);
        },

        onSlideComplete: function(event, slider) {
            var $panel_links = event.data;
            $panel_links.removeClass("current");
            if (slider.$targetPage[0].id)
                $panel_links.filter("[href=#" + slider.$targetPage[0].id + "]").addClass("current");
            carousel._loadPanelImages(slider, slider.targetPage+1);
        }
    };

    patterns.register(carousel);
    return carousel;  // XXX For testing only
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
