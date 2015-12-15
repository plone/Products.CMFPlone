/**
 * Patterns bumper - `bumper' handling for elements
 *
 * Copyright 2012 Humberto Sermeno
 * Copyright 2013 Florian Friesdorf
 * Copyright 2013-2014 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-logger",
    "pat-parser",
    "pat-registry",
    "modernizr",
    "modernizr-csspositionsticky"
], function($, logger, Parser, registry) {
    var parser = new Parser("bumper"),
        log = logger.getLogger("bumper");

    parser.addArgument("margin", 0);
    parser.addArgument("selector");
    parser.addArgument("bump-add", "bumped");
    parser.addArgument("bump-remove");
    parser.addArgument("unbump-add");
    parser.addArgument("unbump-remove", "bumped");
    parser.addArgument("side", "top");

    // XXX Handle resize
    var bumper = {
        name: "bumper",
        trigger: ".pat-bumper",

        init: function bumper_init($el, opts) {
            return $el.each(function bumper_initElement() {
                var container = bumper._findScrollContainer(this),
                    $sticker = $(this),
                    options = parser.parse($sticker, opts);

                if (Modernizr.csspositionsticky) {
                    $sticker.addClass("sticky-supported");
                }
                $sticker.data("pat-bumper:config", options);

                this.style.position="relative";
                if (container===null) {
                    $(window).on("scroll.bumper", null, this, bumper._onScrollWindow);
                    bumper._updateStatus(this);
                } else {
                    if (this.offsetParent!==container) {
                        var old_style = container.style.position;
                        container.style.position="relative";
                        if (this.offsetParent!==container) {
                            container.style.position=old_style;
                            log.error("The offset parent for ", this,
                                      " must be its scrolling container ", container,
                                      "but it is ", this.offsetParent);
                            return;
                        }
                    }
                    $(container).on("scroll.bumper", null, this, bumper._onScrollContainer);
                    bumper._updateStatus(this, container);
                }

                var bumpall = (options.side.indexOf("all") > -1);
                options.bumptop =    bumpall || (options.side.indexOf("top") > -1);
                options.bumpright =  bumpall || (options.side.indexOf("right") > -1);
                options.bumpbottom = bumpall || (options.side.indexOf("bottom") > -1);
                options.bumpleft =   bumpall || (options.side.indexOf("left") > -1);
            });
        },

        _findScrollContainer: function bumper_findScrollContainer(el) {
            var parent = el.parentElement;
            while (parent!==document.body && parent!==null) {
                var overflowY = $(parent).css("overflow-y");
                if ((overflowY==="auto" || overflowY==="scroll"))
                    return parent;
                parent=parent.parentElement;
            }
            return null;
        },

        _markBumped: function bumper_markBumper($sticker, options, is_bumped) {
            var $target = options.selector ? $(options.selector) : $sticker,
                todo = is_bumped ? options.bump : options.unbump;

            if (todo.add)
                $target.addClass(todo.add);
            if (todo.remove)
                $target.removeClass(todo.remove);
        },

        _onScrollContainer: function bumper_onScrollContainer(e) {
            var container = e.currentTarget,
                sticker = e.data;
            bumper._updateStatus(sticker, container);
        },

        _onScrollWindow: function bumper_onScrollWindow(e) {
            bumper._updateStatus(e.data);
        },

        _updateStatus: function(sticker) {
            var $sticker = $(sticker),
                options = $sticker.data("pat-bumper:config"),
                margin = options ? options.margin : 0,
                frame,
                box = bumper._getBoundingBox($sticker, margin),
                delta = {};

            if (arguments.length == 1)
              frame = bumper._getViewport();
            else if (arguments.length == 2)
              frame = bumper._getBoundingBox($(arguments[1]), margin);

            delta.top=sticker.style.top ? parseFloat($sticker.css("top")) : 0;
            delta.left=sticker.style.left ? parseFloat($sticker.css("left")) : 0;

            box.top-=delta.top;
            box.bottom-=delta.top;
            box.left-=delta.left;
            box.right-=delta.left;

            if ((frame.top > box.top) && options.bumptop)
                sticker.style.top=(frame.top - box.top) + "px";
            else if ((frame.bottom < box.bottom) && options.bumpbottom)
                sticker.style.top=(frame.bottom - box.bottom) + "px";
            else
                sticker.style.top="";

            if ((frame.left > box.left) && options.bumpleft)
                sticker.style.left=(frame.left - box.left) + "px";
            else if ((frame.right < box.right) && options.bumpright)
                sticker.style.left=(frame.right - box.right) + "px";
            else
                sticker.style.left="";

            bumper._markBumped($sticker, options, !!(sticker.style.top || sticker.style.left));
        },

        // Calculates the bounding box for the current viewport
        _getViewport: function bumper_getViewport() {
            var $win = $(window),
                view = {
                    top: $win.scrollTop(),
                    left: $win.scrollLeft()
                };

            view.right=view.left + $win.width();
            view.bottom=view.top + $win.height();
            return view;
        },

        /**
         * Calculates the bounding box for a given element, taking margins
         * into consideration
         */
        _getBoundingBox: function bumper_getBoundingBox($sticker, margin) {
            var box = $sticker.offset();
            margin = margin ? margin : 0;
            box.top -= (parseFloat($sticker.css("margin-top")) || 0) + margin;
            box.left -= (parseFloat($sticker.css("margin-left")) || 0) + margin;
            box.right = box.left + $sticker.outerWidth(true) + (2 * margin);
            box.bottom = box.top + $sticker.outerHeight(true) + (2 * margin);
            return box;
        }
    };
    registry.register(bumper);
    return bumper;
});

// vim: sw=4 expandtab
