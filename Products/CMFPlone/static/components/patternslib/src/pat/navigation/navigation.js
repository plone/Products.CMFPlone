define([
    "jquery",
    "pat-logger",
    "pat-registry"
], function($, logger, registry) {
    var log = logger.getLogger("pat.navigation");

    var _ = {
        name: "navigation",
        trigger: "nav, .navigation, .pat-navigation",
        init: function($el) {
            return $el.each(function() {
                var $el = $(this);
                var curpath = window.location.pathname;
                log.debug("current path:", curpath);

                // check whether to load
                if ($el.hasClass("navigation-load-current")) {
                    $el.find("a.current, .current a").click();
                    // check for current elements injected here
                    $el.on("patterns-injected-scanned", function(ev) {
                        var $target = $(ev.target);
                        if ($target.is("a.current"))
                            $target.click();
                        if ($target.is(".current"))
                            $target.find("a").click();
                        _._updatenavpath($el);
                    });
                }

                // An anchor within this navigation triggered injection
                $el.on("patterns-inject-triggered", "a", function(ev) {
                    var $target = $(ev.target);
                    // remove all set current classes
                    $el.find(".current").removeClass("current");
                    // set .current on target
                    $target.addClass("current");
                    // If target's parent is an LI, also set current there
                    $target.parent("li").addClass("current");
                    _._updatenavpath($el);
                });

                // set current class if it is not set
                if ($el.find(".current").length === 0) {
                    $el.find("li a").each(function() {
                        var $a = $(this),
                            $li = $a.parents("li:first"),
                            url = $a.attr("href"),
                            path;
                        if (typeof url === "undefined") {
                            return;
                        }
                        path = _._pathfromurl(url);
                        log.debug("checking url:", url, "extracted path:", path);
                        if (_._match(curpath, path)) {
                            log.debug("found match", $li);
                            $li.addClass("current");
                        }
                    });
                }
                _._updatenavpath($el);
            });
        },
        _updatenavpath: function($el) {
            $el.find(".navigation-in-path").removeClass("navigation-in-path");
            $el.find("li:has(.current)").addClass("navigation-in-path");
        },
        _match: function(curpath, path) {
            if (!path) {
                log.debug("path empty");
                return false;
            }
            // current path needs to end in the anchor's path
            if (path !== curpath.slice(- path.length)) {
                log.debug(curpath, "does not end in", path);
                return false;
            }
            // XXX: we might need more exclusion tests
            return true;
        },
        _pathfromurl: function(url) {
            var path = url.split("#")[0].split("://");
            if (path.length > 2) {
                log.error("weird url", url);
                return "";
            }
            if (path.length === 1) return path[0];
            return path[1].split("/").slice(1).join("/");
        }
    };
    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
