/**
 * Patternslib pattern for Masonry
 * Copyright 2015 Syslab.com GmBH
 */

(function (root, factory) {
    if (typeof define === "function" && define.amd) {
        define([
            "jquery",
            "pat-registry",
            "pat-parser",
            "pat-base",
            "pat-utils",
            "masonry",
            "imagesloaded"
            ], function() {
                return factory.apply(this, arguments);
        });
    } else {
        factory(root.$, root.patterns, root.patterns.Parser, root.Base, root.Masonry, root.imagesLoaded);
    }
}(this, function($, registry, Parser, Base, utils, Masonry, imagesLoaded) {
    "use strict";
    var parser = new Parser("masonry");
    parser.addArgument("column-width");
    parser.addArgument("container-style", "{ position: 'relative' }");
    parser.addArgument("gutter");
    parser.addArgument("hidden-style", "{ opacity: 0, transform: 'scale(0.001)' }");
    parser.addArgument("is-fit-width", false);
    parser.addArgument("is-origin-left", true);
    parser.addArgument("is-origin-top", true);
    parser.addArgument("item-selector", ".item");
    parser.addArgument("stamp", "");
    parser.addArgument("transition-duration", "0.4s");
    parser.addArgument("visible-style", "{ opacity: 1, transform: 'scale(1)' }");

    return Base.extend({
        name: "masonry",
        trigger: ".pat-masonry",

        init: function masonryInit($el, opts) {
            this.options = parser.parse(this.$el, opts);
            $(document).trigger("clear-imagesloaded-cache");
            this.initMasonry();
            this.$el.imagesLoaded(this.layout.bind(this));
            // Update if something gets injected inside the pat-masonry
            // element.
            this.$el.on("patterns-injected.pat-masonry",
                    utils.debounce(this.update.bind(this), 100));
        },

        initMasonry: function () {
            this.msnry = new Masonry(this.$el[0], {
                columnWidth:         this.getTypeCastedValue(this.options.columnWidth),
                containerStyle:      this.options.containerStyle,
                gutter:              this.getTypeCastedValue(this.options.gutter),
                hiddenStyle:         this.options.hiddenStyle,
                isFitWidth:          this.options.is["fit-width"],
                isInitLayout:        false,
                isOriginLeft:        this.options.is["origin-left"],
                isOriginTOp:         this.options.is["origin-top"],
                itemSelector:        this.options.itemSelector,
                stamp:               this.options.stamp,
                transitionDuration:  this.options.transitionDuration,
                visibleStyle:        this.options.visibleStyle
            });
        },

        update: function () {
            this.msnry.remove();
            this.initMasonry();
            this.layout();
        },

        layout: function () {
            this.$el.removeClass("masonry-ready");
            this.msnry.on("layoutComplete", function() {
                this.$el.addClass("masonry-ready");
            }.bind(this));
            this.msnry.layout();
        },

        getTypeCastedValue: function (original) {
            var val = Number(original);
            return (isNaN(val)) ? (original || 0) : val;
        }
    });
}));
