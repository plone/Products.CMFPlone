/**
 * @license
 * Patterns @VERSION@ focus - Manage focus class on fieldsets
 *
 * Copyright 2012 Simplon B.V.
 */
define([
    "jquery",
    "pat-registry"
], function($, patterns) {
    var focus = {
        name: "focus",

        onNewContent: function() {
            if ($(document.activeElement).is(":input"))
                focus._findRelatives(document.activeElement).addClass("focus");
        },

        _findRelatives: function(el) {
            var $el = $(el),
                $relatives = $(el),
                $label = $();

            $relatives=$relatives.add($el.closest("label"));
            $relatives=$relatives.add($el.closest("fieldset"));

            if (el.id)
                $label=$("label[for='"+el.id+"']");
            if (!$label.length) {
                var $form = $el.closest("form");
                if (!$form.length)
                    $form=$(document.body);
                $label=$form.find("label[for='"+el.name+"']");
            }
            $relatives=$relatives.add($label);
            return $relatives;
        },

        onFocus: function() {
            focus._findRelatives(this).addClass("focus");
        },

        onBlur: function() {
            var $relatives = focus._findRelatives(this);

            $(document).one("mouseup keyup", function() {
                $relatives.filter(":not(:has(:input:focus))").removeClass("focus");
            });
        }
    };

    $(document)
        .on("focus.patterns", ":input", focus.onFocus)
        .on("blur.patterns", ":input", focus.onBlur)
        .on("newContent", focus.onNewContent);
    patterns.register(focus);
    return focus;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
