/**
 * Patterns stacks
 *
 * Copyright 2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-parser",
    "pat-logger",
    "pat-utils",
    "pat-registry"
], function($, Parser, logging, utils, registry) {
    var log = logging.getLogger("stacks"),
        parser = new Parser("stacks");

    parser.addArgument("selector", "> *[id]");
    parser.addArgument("transition", "none", ["none", "css", "fade", "slide"]);
    parser.addArgument("effect-duration", "fast");
    parser.addArgument("effect-easing", "swing");

    var stacks = {
        name: "stacks",
        trigger: ".pat-stacks",
        document: document,

        init: function($el, opts) {
            var fragment = this._currentFragment();

            return $el.each(function() {
                stacks._setupStack(this, opts, fragment);
            });
        },

        _setup: function() {
            $(this.document).on("click", "a", this._onClick);
        },

        _setupStack: function(container, options, selected) {
            var $container = $(container),
                $sheets, $visible, $invisible;
            options=parser.parse($container, options);
            $container.data("pat-stacks", options);
            $sheets=$container.find(options.selector);

            if ($sheets.length < 2) {
                log.warn("Stacks pattern: must have more than one sheet.", $container[0]);
                return;
            }
            $visible = [];
            if (selected) {
                try {
                    $visible = $sheets.filter("#"+selected);
                } catch (e) {
                    selected = undefined;
                }
            }
            if (!$visible.length) {
                $visible=$sheets.first();
                selected=$visible[0].id;
            }
            $invisible=$sheets.not($visible);
            utils.hideOrShow($visible, true, {transition: "none"}, stacks.name);
            utils.hideOrShow($invisible, false, {transition: "none"}, stacks.name);
            stacks._updateAnchors($container, selected);
        },

         _base_URL: function() {
            return this.document.URL.split("#")[0];
         },

        _currentFragment: function() {
            var parts = this.document.URL.split("#");
            if (parts.length===1)
                return null;
            return parts[parts.length-1];
        },

        _onClick: function(e) {
            var base_url = stacks._base_URL(),
                href_parts = e.currentTarget.href.split("#"),
                $stack;
            // Check if this is an in-document link and has a fragment
            if (base_url!==href_parts[0] || !href_parts[1])
                return;
            $stack=$(stacks.trigger+":has(#"+href_parts[1]+")");
            if (!$stack.length)
                return;
            e.preventDefault();
            stacks._updateAnchors($stack, href_parts[1]);
            stacks._switch($stack, href_parts[1]);
        },

        _updateAnchors: function($container, selected) {
            var options = $container.data("pat-stacks"),
                $sheets = $container.find(options.selector),
                base_url = stacks._base_URL();
            for (var i=0; i<$sheets.length; i++) {
                // This may appear odd, but: when querying a browser uses the
                // original href of an anchor as it appeared in the document
                // source, but when you access the href property you always
                // the fully qualified version.
                var sheet = $sheets[i],
                    $anchors = $("a[href=\""+base_url+"#"+sheet.id+"\"],a[href=\"#"+sheet.id+"\"]");
                if (sheet.id===selected)
                    $anchors.addClass("current");
                else
                    $anchors.removeClass("current");
            }
        },

        _switch: function($container, sheet_id) {
            var options = $container.data("pat-stacks"),
                $sheet = $container.find("#"+sheet_id),
                $invisible;
            if (!$sheet.length || $sheet.hasClass("visible"))
                return;
            $invisible=$container.find(options.selector).not($sheet);
            utils.hideOrShow($invisible, false, options, stacks.name);
            utils.hideOrShow($sheet, true, options, stacks.name);
        }
    };

    stacks._setup();
    registry.register(stacks);
    return stacks;
});
