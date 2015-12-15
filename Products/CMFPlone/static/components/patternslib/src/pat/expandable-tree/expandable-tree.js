define([
    "jquery",
    "pat-inject",
    "pat-parser",
    "pat-registry"
], function($, inject, Parser, registry) {
    var parser = new Parser("expandable");

    parser.addArgument("load-content");

    var _ = {
        name: "expandable",
        trigger: "ul.pat-expandable",
        jquery_plugin: true,
        init: function($el) {
            // make sure inject folders have a ul
            $el.find(".folder[data-pat-expandable]:not(:has(ul))")
                .append("<ul />");

            // find all folders that contain a ul
            var $folders = $el.find("li.folder:has(ul)");

            // inject span.toggle as first child of each folder
            $folders.prepend("<span class='toggle'></span>");

            // all folders are implicitly closed
            $folders.filter(":not(.open,.closed)").addClass("closed");

            // trigger open event for open folders
            $folders.filter(".open").trigger("patterns-folder-open");

            // wire spans as control elements
            var $ctrls = $el.find("span.toggle");
            $ctrls.each(function() {
                var $ctrl = $(this),
                    $folder = $ctrl.parent();
                $ctrl.on("click.pat-expandable", function() {
                    $folder.toggleClass("open closed")
                        .filter(".open[data-pat-expandable]")
                        .patExpandable("loadContent");
                });
            });
            return $el;
        },
        loadContent: function($el) {
            return $el.each(function() {
                var $el = $(this),
                    url = parser.parse($el).loadContent,
                    components = url.split("#"),
                    base_url = components[0],
                    id = components[1] ? "#" + components[1] : "body",
                    opts = [{
                        url: base_url,
                        source: id,
                        $target: $el.find("ul"),
                        dataType: "html"
                    }];
                inject.execute(opts, $el);
            });
        }

    };
    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
