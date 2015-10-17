/**
 * Patterns checklist - Easily (un)check all checkboxes
 *
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 * Copyright 2012-2013 Florian Friesdorf
 */
define([
    "jquery",
    "pat-jquery-ext",
    "pat-parser",
    "pat-registry"
], function($, dummy, Parser, registry) {
    var parser = new Parser("checklist");
    parser.addArgument("select", ".select-all");
    parser.addArgument("deselect", ".deselect-all");

    var _ = {
        name: "checklist",
        trigger: ".pat-checklist",
        jquery_plugin: true,

        init: function($el, opts) {
            return $el.each(function() {
                var $trigger = $(this),
                    options = parser.parse($trigger, opts, false);

                $trigger.data("patternChecklist", options);
                $trigger.scopedFind(options.select)
                    .on("click.pat-checklist", {trigger: $trigger}, _.onSelectAll);
                $trigger.scopedFind(options.deselect)
                    .on("click.pat-checklist", {trigger: $trigger}, _.onDeselectAll);
                $trigger.on("change.pat-checklist", {trigger: $trigger}, _.onChange);
                // update select/deselect button status
                _.onChange({data: {trigger: $trigger}});
            });
        },

        destroy: function($el) {
            return $el.each(function() {
                var $trigger = $(this),
                    options = $trigger.data("patternChecklist");
                $trigger.scopedFind(options.select).off(".pat-checklist");
                $trigger.scopedFind(options.deselect).off(".pat-checklist");
                $trigger.off(".pat-checklist", "input[type=checkbox]");
                $trigger.data("patternChecklist", null);
            });
        },

        onChange: function(event) {
            var $trigger = event.data.trigger,
                options = $trigger.data("patternChecklist"),
                deselect = $trigger.scopedFind(options.deselect),
                select = $trigger.scopedFind(options.select);
            if ($trigger.find("input[type=checkbox]:visible:checked").length===0) {
                deselect.prop("disabled", true);
            } else {
                deselect.prop("disabled", false);
            }

            if ($trigger.find("input[type=checkbox]:visible:not(:checked)").length===0) {
                select.prop("disabled", true);
            } else {
                select.prop("disabled", false);
            }
        },

        onSelectAll: function(event) {
            var $trigger = event.data.trigger,
                options = $trigger.data("patternChecklist");
            $trigger.find("input[type=checkbox]:not(:checked)").each(function () {
                $(this).prop("checked", true).trigger("change");
            });
            $trigger.scopedFind(options.deselect).each(function () {
                $(this).prop("disabled", false);
            });
            $trigger.scopedFind(options.select).each(function () {
                $(this).attr({disabled: "disabled"});
            });
            event.preventDefault();
        },

        onDeselectAll: function(event) {
            var $trigger = event.data.trigger,
                options = $trigger.data("patternChecklist");
            $trigger.find("input[type=checkbox]:checked").each(function () {
                $(this).prop("checked", false).trigger("change");
            });
            $trigger.scopedFind(options.select).each(function () {
                $(this).prop("disabled", false);
            });
            $trigger.scopedFind(options.deselect).each(function () {
                $(this).attr({disabled: "disabled"});
            });
            event.preventDefault();
        }
    };
    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
