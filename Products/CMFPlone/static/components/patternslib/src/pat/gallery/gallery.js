/**
 * Patterns gallery - A simple gallery
 *
 * Copyright 2013 Simplon B.V. - Wichert Akkerman
 */
define("pat-gallery", [
    "jquery",
    "pat-registry",
    "pat-base",
    "pat-parser",
    "photoswipe",
    "photoswipe-ui",
    "tpl!photoswipe-template",
    "underscore"
], function($, patterns, Base, Parser, PhotoSwipe, PhotoSwipeUI, template, _) {
    var parser = new Parser("gallery");
    parser.addArgument("loop", true);
    parser.addArgument("scale-method", "fit", ["fit", "fitNoUpscale", "zoom"]);
    parser.addArgument("delay", 30000);
    parser.addArgument("effect-duration", 250);

    return Base.extend({
        name: "gallery",
        trigger: ".pat-gallery",

        init: function patGalleryInit($el, opts) {
            this.options = parser.parse(this.$el, opts);
            if ($('#photoswipe-template').length === 0) {
                $('body').append(template());
            }
            var images = $("a", this.$el).map(function () {
                return { 'w': 0, 'h': 0, 'src': this.href, 'title': $(this).find('img').attr('title') };
            });
            var pswpElement = document.querySelectorAll('.pswp')[0];
            var options = {
                index: 0,
                scaleMode: this.options.scaleMethod,
                loop: this.options.loop,
                slideshowDelay: this.options.delay,
                hideAnimationDuration: this.options.effectDuration,
                showAnimationDuration: this.options.effectDuration
            };
            $("a", this.$el).click(function (ev) {
                ev.preventDefault();
                if (this.href) {
                    options.index = _.indexOf(_.pluck(images, 'src'), this.href);
                } else {
                    options.index = 0;
                }
                var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI, images, options);
                gallery.listen('gettingData', function(index, item) {
                    // Workaround for the fact that we don't know the image sizes.
                    // https://github.com/dimsemenov/PhotoSwipe/issues/796
                    if (item.w < 1 || item.h < 1) { // unknown size
                        var img = new Image();
                        img.onload = function() { // will get size after load
                            item.w = this.width; // set image width
                            item.h = this.height; // set image height
                            gallery.invalidateCurrItems(); // reinit Items
                            gallery.updateSize(true); // reinit Items
                        };
                        img.src = item.src; // let's download image
                    }
                });
                gallery.init();
            });
        },
    });
});
