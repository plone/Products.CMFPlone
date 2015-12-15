define([
    "jquery",
    "pat-registry"
], function($, patterns) {
    var menu = {
        name: "menu",
        trigger: "ul.pat-menu",

        init: function($root) {
            return $root.each(function() {
                var $menu = $(this),
                    timer,
                    closeMenu, openMenu,
                    mouseOverHandler, mouseOutHandler;

                openMenu = function($li) {
                    if (timer) {
                        clearTimeout(timer);
                        timer = null;
                    }

                    if (!$li.hasClass("open")) {
                        $li.siblings("li.open").each(function() { closeMenu($menu);});
                        $li.addClass("open").removeClass("closed");
                    }
                };

                closeMenu = function($li) {
                    $li.find("li.open").andSelf().removeClass("open").addClass("closed");
                };

                mouseOverHandler = function() {
                    var $li = $(this);
                    openMenu($li);
                };

                mouseOutHandler = function() {
                    var $li = $(this);

                    if (timer) {
                        clearTimeout(timer);
                        timer=null;
                    }

                    timer = setTimeout(function() { closeMenu($li); }, 1000);
                };

                $root.find("li")
                    .addClass("closed")
                    .filter(":has(ul)").addClass("hasChildren").end()
                    .on("mouseover.pat-menu", mouseOverHandler)
                    .on("mouseout.pat-menu", mouseOutHandler);
            });
        }
    };

    patterns.register(menu);
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
