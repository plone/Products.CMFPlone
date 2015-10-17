/**
 * Patterns autofocus - enhanced autofocus form elements
 *
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-registry"
], function($, registry) {
    var autofocus = {
        name: "autofocus",
        trigger: ":input.pat-autofocus,:input[autofocus],.enableAutoFocus",

        init: function($el) {
            $el = $el.filter(
                function () {
                    // This function filters out all elements that have
                    // .pat-depends ancestors.
                    // If a .pat-autofocus element has a .pat-depends ancestor, then
                    // autofocus is dependent on that ancestor being visible.
                    var $el = $(this);
                    var $depends_slave = $el.closest(".pat-depends").addBack(".pat-depends");
                    if ($depends_slave.length > 0) {
                        // We register an event handler so that the element is
                        // only autofocused once the .pat-depends ancestor
                        // becomes visible.
                        $depends_slave.on("pat-update", function (e, data) {
                            var $child = $el;
                            if (data.pattern === "depends") {
                                if (((data.transition === "complete") && ($(this).is(":visible"))) ||
                                    ((data.enabled === "true") && ($(this).is("visible")))) {

                                    if ($el.hasClass("select2-offscreen")) {
                                        $child = $el.parent().find(".select2-input");
                                    }
                                    if (!$child.is(":disabled")) {
                                        $child.focus();
                                    }
                                }
                            }
                        });
                        return false;
                    }
                    return true;
                }
            );
            // $el is now only those elements not dependent on .pat-depends
            // criteria.
            for (var i=0; i<$el.length; i+=1) {
                if (!$el.eq(i).val()) {
                    $el.get(i).focus();
                    return;
                }
            }
            $el.eq(0).focus();
        }
    };
    registry.register(autofocus);
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
