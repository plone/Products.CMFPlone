/**
 * Patterns checkedflag - Add checked flag to checkbox labels and API
 * for (un)checking.
 *
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012-2014 Syslab.com GmBH
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger",
    "pat-utils"
], function($, patterns, logger, utils) {
    var log = logger.getLogger("checkedflag");

    var checkedflag = {
        name: "checkedflag",
        trigger: "input[type=checkbox],input[type=radio],select",
        jquery_plugin: true,

        init: function($el) {
            var $forms = $();
            $el.each(function() {
                if (this.form === null) {
                    return;
                }
                var $form = $(this.form);
                if ($form.data("pat-checkedflag.reset")) {
                    return;
                }
                $form.data("pat-checkedflag.reset", true);
                $forms = $forms.add(this.form);
            });

            $el.filter("[type=checkbox]")
                .each(checkedflag._onChangeCheckbox)
                .on("change.pat-checkedflag", checkedflag._onChangeCheckbox);

            $el.filter("[type=radio]")
                .each(checkedflag._initRadio)
                .on("change.pat-checkedflag", checkedflag._onChangeRadio);

            $el.filter("select:not([multiple])")
                .each(function() {
                    var $el = $(this);
                    // create parent span if not direct child of a label
                    if ($el.parent("label").length === 0) {
                        $el.wrap("<span />");
                    }
                    checkedflag.onChangeSelect.call(this);
                })
                .on("change.pat-checkedflag", checkedflag.onChangeSelect);

            $el.filter("input:disabled").each(function() {
                $(this).closest("label").addClass("disabled");
            });

            $forms.on("reset.pat-checkedflag", checkedflag._onFormReset);
        },

        destroy: function($el) {
            return $el.off(".pat-checkedflag");
        },

        // XXX: so far I was under the assumption that prop is current
        // state and attr is default and current state. Well, this
        // does not seem to be the case. I feel like doing this
        // without jquery.
        set: function($el, val, opts) {
            opts = opts || {};
            // XXX: no support for radio yet
            return $el.each(function() {
                var $el = $(this);
                if ($el.is("input[type=checkbox]")) {
                    var $input = $(this);
                    if (opts.setdefault) {
                        // XXX: implement me
                    } else {
                        // just change the current state
                        // XXX: not sure whether this is correct
                        $input.prop("checked", val);
                    }
                    checkedflag._onChangeCheckbox.call(this);
                } else if ($el.is("select:not([multiple])")) {
                    var $select = $(this);
                    if (opts.setdefault) {
                        // XXX: implement me
                    } else {
                        // just change the current state
                        $select.find("option:selected")
                            .prop("selected", false);
                        $select.find("option[value=\"" + val + "\"]")
                            .prop("selected", true);
                    }
                    checkedflag.onChangeSelect.call(this);
                } else {
                    log.error("Unsupported element", $el[0]);
                }
            });
        },

        _onFormReset: function() {
            // This event is triggered before the form is reset, and we need
            // the post-reset state to update our pattern. Use a small delay
            // to fix this.
            var form = this;
            setTimeout(function() {
                $("input[type=checkbox]", form).each(checkedflag._onChangeCheckbox);
                $("input[type=radio]", form).each(checkedflag._initRadio);
                $("select:not([multiple])", form).each(checkedflag.onChangeSelect);
            }, 50);
        },

        _getLabelAndFieldset: function(el) {
            var $result = $(utils.findLabel(el));
            return $result.add($(el).closest("fieldset"));
        },

        _getSiblingsWithLabelsAndFieldsets: function(el) {
            var selector = "input[name=\""+el.name+"\"]",
                $related = (el.form===null) ? $(selector) : $(selector, el.form),
                $result = $();
            $result = $related=$related.not(el);
            for (var i=0; i<$related.length; i++) {
                $result=$result.add(checkedflag._getLabelAndFieldset($related[i]));
            }
            return $result;
        },

        _onChangeCheckbox: function() {
            var $el = $(this),
                $label = $(utils.findLabel(this)),
                $fieldset = $el.closest("fieldset");

            if ($el.closest("ul.radioList").length) {
                $label=$label.add($el.closest("li"));
            }

            if (this.checked) {
                $label.add($fieldset).removeClass("unchecked").addClass("checked");
            } else {
                $label.addClass("unchecked").removeClass("checked");
                if ($fieldset.find("input:checked").length) {
                    $fieldset.removeClass("unchecked").addClass("checked");
                } else
                    $fieldset.addClass("unchecked").removeClass("checked");
            }
        },

        _initRadio: function() {
            checkedflag._updateRadio(this, false);
        },

        _onChangeRadio: function() {
            checkedflag._updateRadio(this, true);
        },

        _updateRadio: function(input, update_siblings) {
            var $el = $(input),
                $label = $(utils.findLabel(input)),
                $fieldset = $el.closest("fieldset"),
                $siblings = checkedflag._getSiblingsWithLabelsAndFieldsets(input);

            if ($el.closest("ul.radioList").length) {
                $label=$label.add($el.closest("li"));
                $siblings=$siblings.closest("li");
            }

            if (update_siblings) {
                 $siblings.removeClass("checked").addClass("unchecked");
            }
            if (input.checked) {
                $label.add($fieldset).removeClass("unchecked").addClass("checked");
            } else {
                $label.addClass("unchecked").removeClass("checked");
                if ($fieldset.find("input:checked").length) {
                    $fieldset.removeClass("unchecked").addClass("checked");
                } else {
                    $fieldset.addClass("unchecked").removeClass("checked");
                }
            }
        },

        onChangeSelect: function() {
            var $select = $(this);
            $select.parent().attr(
                "data-option",
                $select.find("option:selected").text()
            );
        }
    };

    patterns.register(checkedflag);
    return checkedflag;
});

// vim: sw=4 expandtab
