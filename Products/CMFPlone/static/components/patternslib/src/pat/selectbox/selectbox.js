/**
 * Patterns selectbox - Expose select option
 * for (un)checking.
 *
 * Copyright 2012-2014 Simplon B.V. - Wichert Akkerman
 * Copyright 2012 JC Brand
 * Copyright 2012-2013 Florian Friesdorf
 */
define([
    "jquery",
    "pat-registry"
], function($, patterns) {
    var selectbox = {
        name: "selectbox",
        trigger: "select",

        init: function($el) {
            var $forms = $();
            $el.each(function() {
                if (this.form !== null) {
                    var $form = $(this.form);
                    if ($form.data("pat-selectbox.reset"))
                        return;
                    $form.data("pat-selectbox.reset", true);
                    $forms = $forms.add(this.form);
                }
            });

            $el.filter("select:not([multiple])")
                .each(function() {
                    var $el = $(this);
                    // create parent span if not direct child of a label
                    if ($el.parent("label").length === 0)
                        $el.wrap("<span />");
                    selectbox.onChangeSelect.call(this);
                })
                .on("change.pat-selectbox", selectbox.onChangeSelect);

            $forms.on("reset.pat-selectbox", selectbox.onFormReset);
        },

        destroy: function($el) {
            return $el.off(".pat-selectbox");
        },

        onFormReset: function() {
            // This event is triggered before the form is reset, and we need
            // the post-reset state to update our pattern. Use a small delay
            // to fix this.
            var form = this;
            setTimeout(function() {
                $("select:not([multiple])", form).each(selectbox.onChangeSelect);
            }, 50);
        },

        onChangeSelect: function() {
            var $select = $(this);
            $select.parent().attr(
                "data-option",
                $select.find("option:selected").text()
            );
            $select.parent().attr("data-option-value", $select.val());
        }
    };

    patterns.register(selectbox);
    return selectbox;
});

// vim: sw=4 expandtab
