/**
 * @license
 * Patterns @VERSION@ tooltip - tooltips
 *
 * Copyright 2008-2012 Simplon B.V.
 * Copyright 2011 Humberto Sermeño
 * Copyright 2011 SYSLAB.COM GmbH
 */
define([
    "jquery",
    "pat-logger",
    "pat-registry",
    "pat-parser",
    "pat-inject",
    "pat-remove"
], function($, logger, registry, Parser, inject) {
    var log = logger.getLogger("tooltip"),
        parser = new Parser("tooltip");

    var all_positions = ["tl", "tm", "tr",
                         "rt", "rm", "rb",
                         "br", "bm", "bl",
                         "lb", "lm", "lt"];
    parser.addArgument("position-list", [], all_positions, true);
    parser.addArgument("position-policy", "auto", ["auto", "force"]);
    parser.addArgument("height", "auto", ["auto", "max"]);
    parser.addArgument("trigger", "click", ["click", "hover"]);
    parser.addArgument("closing", "auto", ["auto", "sticky", "close-button"]);
    parser.addArgument("source", "title", ["auto", "ajax", "content", "content-html", "title"]);
    parser.addArgument("ajax-data-type", "html", ["html", "markdown"]);
    parser.addArgument("delay", 0);
    parser.addArgument("class");
    parser.addArgument("target", "body");

    var tooltip = {
        name: "tooltip",
        trigger: ".pat-tooltip",
        jquery_plugin: true,

        count: 0,

        init: function($el, opts) {
            return $el.each(function() {
                var $trigger = $(this),
                    href,
                    options = parser.parse($trigger, opts);

                if (options.source==="auto") {
                    href = $trigger.attr("href");
                    if (typeof(href) !== "string") {
                        log.error("href must be specififed if 'source' is set to 'auto'");
                        return;
                    }
                    if (href.indexOf("#") === 0) {
                        options.source = "content";
                    } else {
                        options.source = "ajax";
                    }
                }

                if (options.source==="title") {
                    options.title=$trigger.attr("title");
                    $trigger.removeAttr("title");
                } else if (options.trigger==="hover") {
                    $trigger.removeAttr("title");
                }
                $trigger
                    .data("patterns.tooltip", options)
                    .on("destroy", $trigger, tooltip.onDestroy);
                tooltip.setupShowEvents($trigger);
                $trigger.addClass("inactive");
            });
        },

        setupShowEvents: function($trigger) {
            var options = $trigger.data("patterns.tooltip");
            if (options.trigger==="click") {
                $trigger.on("click.tooltip", $trigger, tooltip.show);
            } else {
                if (options.delay) {
                    $trigger.on("mouseover.tooltip", $trigger, tooltip.delayedShow);
                } else
                    $trigger.on("mouseover.tooltip", $trigger, tooltip.show);
                // Make sure click on the trigger element becomes a NOP
                $trigger.on("click.tooltip", $trigger, tooltip.blockDefault);
            }
        },

        delayedShow: function(event) {
            var $trigger = event.data,
                options = $trigger.data("patterns.tooltip");

            tooltip.removeShowEvents($trigger);
            $trigger
                .data("patterns.tooltip.timer", setTimeout(
                    function() {
                        tooltip.show(event);
                    }, options.delay))
                .on("mouseleave.tooltip", $trigger, tooltip.cancelDelayedShow);
        },

        cancelDelayedShow: function(event) {
            var $trigger = event.data;

            clearTimeout($trigger.data("patterns.tooltip.timer"));
            tooltip.setupShowEvents($trigger);
        },

        removeShowEvents: function($trigger) {
            $trigger.off(".tooltip");
        },

        setupHideEvents: function($trigger) {
            var $container = tooltip.getContainer($trigger),
                options = $trigger.data("patterns.tooltip");
            $container
                .on("click.tooltip", ".close-panel", $trigger, tooltip.hide);

            if (options.closing==="close-button") {
                // Make sure click on the trigger element becomes a NOP
                $trigger.on("click.tooltip", $trigger, tooltip.blockDefault);
            } else if (options.closing==="sticky" || (options.trigger==="click" && options.closing==="auto")) {
                $container.on("click.tooltip", $trigger, function(ev) {
                    ev.stopPropagation();
                });
                $(document).on("click.tooltip", $trigger, tooltip.hide);
                $(document).on("pat-tooltip-click.tooltip", $trigger, tooltip.hide);
                $trigger.on("click.tooltip", $trigger, tooltip._onClick);
                /* XXX: It's also not clear what this was for, but we
                 * definitely don't want tooltips to close whenever an
                 * injection has happened.
                 * I've added a regression test to prevent this being enabled
                 * again.
                 * If there is a reason why a tooltip must close after an
                 * injection, it needs to be much more specific.
                 
                    // close if something inside the tooltip triggered an injection
                    $container.on("patterns-inject-triggered.tooltip",
                                $trigger, tooltip.hide);
                */
                $container.on("submit.tooltip", ".close-panel", $trigger, tooltip.hide);
            } else {
                $container.on("click.tooltip", $trigger, tooltip.hide);
                $trigger.on("mouseleave.tooltip", $trigger, tooltip.hide);
                $trigger.on("click.tooltip", tooltip.blockDefault);
            }
        },

        _onClick: function(event) {
            // XXX: this handler is necessary in order to suppress the click
            // on the trigger from bubbling. (see show function)
            tooltip.hide(event);
            event.preventDefault();
            event.stopPropagation();
            event.data.trigger("pat-tooltip-click");
        },

        removeHideEvents: function($trigger) {
            var $container = tooltip.getContainer($trigger);
            $(document).off(".tooltip");
            $container.off(".tooltip");
            $container.find(".close-panel").off(".tooltip");
            $trigger.off(".tooltip");
        },

        blockDefault: function(event) {
            event.preventDefault();
        },

        show: function(event) {
            // Stop bubbling, as it causes problems if ancestor
            // is e.g. pat-collapsible.
            if (event.type === "click") {
                event.stopPropagation();
                event.data.trigger("pat-tooltip-click");
            }

            if (event.preventDefault) {
                event.preventDefault();
            }
            var $trigger = event.data,
                $container = tooltip.getContainer($trigger, true),
                namespace = $container.attr("id"),
                options = $trigger.data("patterns.tooltip");

            tooltip.removeShowEvents($trigger);
            // Wrap in a timeout to make sure this click is not used to
            // trigger a hide as well.
            setTimeout(function() { tooltip.setupHideEvents($trigger); }, 50);

            if (options.source==="ajax") {
                var source = $trigger.attr("href").split("#"),
                    target_id = $container.find("progress").attr("id");
                inject.execute([{
                    url: source[0],
                    source: "#" + source[1],
                    target: "#" + target_id + "::element",
                    dataType: options.ajaxDataType
                }], $trigger);
            }

            tooltip.positionContainer($trigger, $container);
            $container.css("visibility", "visible");

            // reposition tooltip everytime we scroll or resize
            $container.parents().add(window).on("scroll." + namespace + " resize." + namespace, function () {
                 tooltip.positionContainer($trigger, $container);
            });

            $trigger.removeClass("inactive").addClass("active");
        },

        hide: function(event) {
            var $trigger = event.data,
                $container = tooltip.getContainer($trigger),
                namespace = $container.attr("id");
            // when another tooltip trigger is clicked, only close the previous tooltip if it does not contain the trigger
            if (event.type !== "pat-tooltip-click" || $container.has(event.target).length <= 0) {
                $container.css("visibility", "hidden");
                $container.parents().add(window).off("." + namespace);
                tooltip.removeHideEvents($trigger);
                tooltip.setupShowEvents($trigger);
                $trigger.removeClass("active").addClass("inactive");
                $trigger.trigger("pat-update", {pattern: "tooltip", hidden: true});
            }
        },

        onDestroy: function(event) {
            var $trigger = event.data,
                $container = $trigger.data("patterns.tooltip.container");
            if ($container!==undefined)
                $container.remove();
        },

        getContainer: function($trigger, create) {
            var $container = $trigger.data("patterns.tooltip.container");

            if (create) {
                if ($container !== undefined) {
                    $container.remove();
                }
                $container = tooltip.createContainer($trigger);
                $trigger.data("patterns.tooltip.container", $container);
            }

            return $container;
        },

        createContainer: function($trigger) {
            var options = $trigger.data("patterns.tooltip"),
                count = ++tooltip.count,
                $content, $container, href;

            $trigger.data("patterns.tooltip.number", count);
            $container = $("<div/>", {"class": "tooltip-container",
                                     "id": "tooltip" + count});
            if (options["class"])
                $container.addClass(options["class"]);
            $container.css("visibility", "hidden");
            switch (options.source) {
            case "ajax":
                $content=$("<progress/>", {"id": "tooltip-load-" + count});
                break;
            case "title":
                $content=$("<p/>").text(options.title);
                break;
            case "content-html":
                $content = $("<div/>").html(options.content);
                break;
            case "content":
                href = $trigger.attr("href");
                if (typeof(href) === "string" && href.indexOf("#") !== -1) {
                    $content = $("#"+href.split("#")[1]).children().clone();
                } else {
                    $content = $trigger.children().clone();
                    if (!$content.length) {
                        $content = $("<p/>").text($trigger.text());
                    }
                }
                registry.scan($content);
                break;
            }
            $container.append(
                $("<div/>").css("display", "block").append($content))
                .append($("<span></span>", {"class": "pointer"}));
            if (options.closing==="close-button") {
                $("<button/>", {"class": "close-panel"})
                    .text("Close")
                    .insertBefore($container.find("*:first"));
            }
            $(options.target).append($container);
            return $container;
        },

        boundingBox: function($el) {
            var box = $el.offset();
            box.height = $el.height();
            box.width = $el.width();
            box.bottom = box.top + box.height;
            box.right = box.left + box.width;
            return box;
        },

        positionStatus: function($trigger, $container) {
            var trigger_box = tooltip.boundingBox($trigger),
                tooltip_box = tooltip.boundingBox($container),
                $window = $(window),
                window_width = $window.width(),
                window_height = $window.height(),
                trigger_center,
                scroll = {},
                space = {};

            scroll.top = $window.scrollTop();
            scroll.left = $window.scrollLeft();
            trigger_center = {top: trigger_box.top + (trigger_box.height/2),
                              left: trigger_box.left + (trigger_box.width/2)};
            space.top = trigger_box.top - scroll.top;
            space.bottom = window_height - space.top - trigger_box.height;
            space.left = trigger_box.left - scroll.left;
            space.right = window_width - space.left - trigger_box.width;

            return {space: space,
                    trigger_center: trigger_center,
                    trigger_box: trigger_box,
                    tooltip_box: tooltip_box,
                    scroll: scroll,
                    window: {width: window_width, height: window_height}
            };
        },

        // Help function to determine the best position for a tooltip.  Takes
        // the positioning status (as generated by positionStatus) as input
        // and returns a two-character position indiciator.
        findBestPosition: function(status) {
            var space = status.space,
                 cls = "";

            if (space.top > Math.max(space.right, space.bottom, space.left)) {
                cls = "b";
            } else if (space.right > Math.max(space.bottom, space.left, space.top)) {
                cls = "l";
            } else if (space.bottom > Math.max(space.left, space.top, space.right)) {
                cls = "t";
            } else {
                cls = "r";
            }

            switch (cls[0]) {
            case "t":
            case "b":
                if (Math.abs(space.left-space.right) < 20) {
                    cls += "m";
                } else if (space.left > space.right) {
                    cls += "r";
                } else {
                    cls += "l";
                }
                break;
            case "l":
            case "r":
                if (Math.abs(space.top-space.bottom) < 20) {
                    cls += "m";
                } else if (space.top > space.bottom) {
                    cls += "b";
                } else {
                    cls += "t";
                }
            }
            return cls;
        },

        isVisible: function(status, position) {
            var space = status.space,
                tooltip_box = status.tooltip_box;

            switch (position[0]) {
            case "t":
                if (tooltip_box.height > space.bottom) {
                    return false;
                }
                break;
            case "r":
                if (tooltip_box.width > space.left) {
                    return false;
                }
                break;
            case "b":
                if (tooltip_box.height > space.top) {
                    return false;
                }
                break;
            case "l":
                if (tooltip_box.width > space.right) {
                    return false;
                }
                break;
            default:
                return false;
            }

            switch (position[0]) {
            case "t":
            case "b":
                switch (position[1]) {
                    case "l":
                        if ((tooltip_box.width-20)>space.right) {
                            return false;
                        }
                        break;
                    case "m":
                        if ((tooltip_box.width/2)>space.left || (tooltip_box.width/2)>space.right) {
                            return false;
                        }
                        break;
                    case "r":
                        if ((tooltip_box.width-20)>space.left) {
                            return false;
                        }
                        break;
                    default:
                        return false;
                }
                break;
            case "l":
            case "r":
                switch (position[1]) {
                    case "t":
                        if ((tooltip_box.height-20)>space.bottom) {
                            return false;
                        }
                        break;
                    case "m":
                        if ((tooltip_box.height/2)>space.top || (tooltip_box.height/2)>space.bottom) {
                            return false;
                        }
                        break;
                    case "b":
                        if ((tooltip_box.height-20)>space.top) {
                            return false;
                        }
                        break;
                    default:
                        return false;
                }
                break;
            }
            return true;
        },

        VALIDPOSITION: /^([lr][tmb]|[tb][lmr])$/,

        positionContainer: function($trigger, $container) {
            var status = tooltip.positionStatus($trigger, $container),
                options = $trigger.data("patterns.tooltip"),
                container_offset = {},
                tip_offset = {},
                position;

            for (var i=0; i<options.position.list.length; i++) {
                if (options.position.policy==="force" || tooltip.isVisible(status, options.position.list[i])) {
                    position = options.position.list[i];
                    break;
                }
            }

            if (!position) {
                position = tooltip.findBestPosition(status);
            }

            var container_margin = 30,
                // FIXME: this 20 is due to a margin placed on the
                // tooltip pointer's CSS. This is not reusable/generic,
                // we'll have to find a different solution.
                tip_margin = 20,
                trigger_box = status.trigger_box,
                tooltip_box = status.tooltip_box,
                trigger_center = status.trigger_center,
                content_css = {"max-height": "", "max-width": ""},
                container_css = {"max-height": "", "max-width": ""},
                bottom_row, x;

            switch (position[0]) {
            case "t":
                container_offset.top = trigger_box.bottom + tip_margin;
                tip_offset.top = -23;
                bottom_row = status.scroll.top + status.window.height;
                content_css["max-height"] = (bottom_row - container_offset.top - container_margin) + "px";
                break;
            case "l":
                container_offset.left = trigger_box.right + tip_margin;
                tip_offset.left = -23;
                x = status.window.width + status.scroll.left;
                content_css["max-width"] = (x - container_offset.left - container_margin) + "px";
                break;
            case "b":
                if (options.height === "max") {
                    container_offset.top = container_margin;
                    content_css["max-height"] = (trigger_box.top - 2*container_margin) + "px";
                } else {
                    container_offset.top = trigger_box.top - tooltip_box.height + 10;
                    tip_offset.top = tooltip_box.height;
                    x = (status.scroll.top + 10) - container_offset.top;
                    if (x>0) {
                        tip_offset.top -= x;
                        content_css["max-height"] = (tooltip_box.height - x) + "px";
                        container_offset.top += x;
                    }
                }
                break;
            case "r":
                if (tooltip_box.width > trigger_box.left) {
                    // Tooltip is too wide, we need to restrict its width.
                    container_offset.left = container_margin;
                    tip_offset.left = trigger_box.left - container_margin;
                    container_css["max-width"] = (trigger_box.left - container_margin) + "px";
                } else {
                    container_offset.left = trigger_box.left - tooltip_box.width - tip_margin;
                    tip_offset.left = tooltip_box.width;
                }
                break;
            }

            switch (position[0]) {
            case "t":
            case "b":
                switch (position[1]) {
                case "l":
                    container_offset.left = trigger_center.left - tip_margin;
                    tip_offset.left = 0;
                    if ((trigger_center.left - tooltip_box.width) < 0) {
                        // Tooltip is too wide, we need to restrict its width.
                        container_css["max-width"] = (status.window.width - trigger_center.left -container_margin) + "px";
                        container_offset.right = container_margin;
                    }
                    break;
                case "m":
                    container_offset.left = trigger_center.left - (tooltip_box.width/2);
                    tip_offset.left = tooltip_box.width/2 - tip_margin/2;
                    break;
                case "r":
                    container_offset.left = trigger_center.left + 29 - tooltip_box.width;
                    tip_offset.left = tooltip_box.width - tip_margin;
                    break;
                }
                break;
            case "l":
            case "r":
                switch (position[1]) {
                    case "t":
                        if (options.height === "max") {
                            container_offset.top = container_margin;
                            tip_offset.top = trigger_box.top - container_margin - tip_margin;
                        } else {
                            container_offset.top = trigger_center.top - container_margin;
                            tip_offset.top = 0;
                        }
                        bottom_row = status.scroll.top + status.window.height;
                        content_css["max-height"] = (bottom_row - container_offset.top - container_margin) + "px";
                        break;
                    case "m":
                        if (options.height === "max") {
                            container_offset.top = container_margin ;
                            bottom_row = status.scroll.top + status.window.height;
                            content_css["max-height"] = (bottom_row - 2*container_margin) + "px";
                            tip_offset.top = trigger_box.top - container_margin;
                        } else {
                            container_offset.top = trigger_center.top - (tooltip_box.height/2);
                            tip_offset.top = tooltip_box.height/2 - tip_margin/2;
                        }
                        break;
                    case "b":
                        if (options.height === "max") {
                            container_offset.top = 2*container_margin;
                            bottom_row = status.scroll.top + status.window.height;
                            content_css.height = (bottom_row - 3*container_margin) + "px";
                            tip_offset.top = trigger_center.top - container_margin - tip_margin;
                        } else {
                            container_offset.top = trigger_center.top - tooltip_box.height;
                            tip_offset.top = trigger_center.top - tip_margin;
                        }
                        break;
                }
                break;
            }

            var $offsetParent = $container.offsetParent();

            if ($offsetParent.length) {
                var offset = $offsetParent.offset();
                container_offset.top -= offset.top;
                container_offset.left -= offset.left;
            }

            $container.css(container_css);
            $container.find("> div").css(content_css);
            $container.removeClass(all_positions.join(" ")).addClass(position);
            $container.css({
                top: container_offset.top+"px",
                left: container_offset.left+"px"
            });
            $container.find(".pointer").css({
                top: tip_offset.top+"px",
                left: tip_offset.left+"px"});
        }
    };

    registry.register(tooltip);
    return tooltip; // XXX Replace for tests
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
