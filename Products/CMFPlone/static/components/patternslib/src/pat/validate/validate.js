/**
 * Patterns validate - Form vlidation
 *
 * Copyright 2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-parser",
    "pat-base",
    "pat-utils",
    "parsley",
    "parsley.extend"
], function($, Parser, Base, utils) {
    var parser = new Parser("validate");
    parser.addArgument("disable-selector"); // Elements which must be disabled if there are errors

    return Base.extend({
        name: "validate",
        trigger: "form.pat-validate",

        init: function($el, opts) {
            this.errors = 0;
            this.options = parser.parse(this.$el, opts);
            this.$el.noValidate = true;
            var parsley_form = this.initParsley();
            this.$el.on("pat-ajax-before.pat-validate", this.onPreSubmit);
            this.$el.on('pat-update', this.onPatternUpdate.bind(this));
            this.$el.on("click.pat-validate", ".close-panel", function (ev) {
                if (!$(ev.target).hasClass('validate-ignore') && !parsley_form.validate()) {
                    ev.preventDefault();
                    ev.stopPropagation();
                }
            }.bind(this));
        },

        initParsley: function() {
            var field, i;
            var parsley_form = this.$el.parsley({
                trigger: "change keyup",
                successClass: "valid",
                errorClass: "warning",
                errors: {
                    classHandler: this._classHandler,
                    container: this._container
                },
                messages: {
                    beforedate:     "This date should be before another date.",
                    onorbeforedate: "This date should be on or before another date.",
                    afterdate:      "This date should be after another date.",
                    onorafterdate:  "This date should be on or after another date."
                }
            });
            var that = this;
            function _addFieldError(error) {
                that._addFieldError.call(that, this, error);
            }
            function _removeFieldError(constraintName) {
                that._removeFieldError.call(that, this, constraintName);
            }
            for (i=0; i<parsley_form.items.length; i++) {
                field = parsley_form.items[i];
                if (typeof field.UI !== "undefined") {
                    // Parsley 1.2.x
                    field.UI.addError = _addFieldError;
                    field.UI.removeError = _removeFieldError;
                    this.parsley12 = true;
                } else {
                    // Parsley 1.1.x
                    field.addError = _addFieldError;
                    field.removeError = _removeFieldError;
                }
            }
            return parsley_form;
        },

        onPatternUpdate: function (ev, data) {
            /* Handler which gets called when pat-update is triggered within
             * the .pat-validate element.
             */
            // XXX: We should also handle here general pat-inject updates.
            if (data.pattern == "clone") {
                this.$el.data("parsleyForm", null); // XXX: Hack. Remove old data, so that parsley rescans.
                this.initParsley(data.$el);
            }
            return true;
        },

        // Parsley error class handler, used to determine which element will
        // receive the status class.
        _classHandler: function(elem/*, isRadioOrCheckbox */) {
            var $result = elem;
            for (var i=0; i<elem.length; i++) {
                $result=$result.add(utils.findLabel(elem[i]));
                $result=$result.add(elem.eq(i).closest("fieldset"));
            }
            return $result;
        },

        // Parsley hook to determine where error messages are inserted.
        _container: function(/* element, isRadioOrCheckbox */) {
            return $();
        },

        _findErrorMessages: function($el, constraintName) {
            var selector = "em.validation.message[data-validate-constraint="+constraintName+"]",
                $messages = $el.siblings(selector);
            if ($el.is("[type=radio],[type=checkbox]")) {
                var $fieldset = $el.closest("fieldset.checklist");
                if ($fieldset.length)
                    $messages=$fieldset.find(selector);
            }
            return $messages;
        },

        // Parsley method to add an error to a field
        _addFieldError: function(parsley, error) {
            var $el;
            if (this.parsley12) {
                $el = parsley.ParsleyInstance.element;
            } else {
                $el = parsley.element;
            }
            var $position = $el,
                strategy="after";

            if ($el.is("[type=radio],[type=checkbox]")) {
                var $fieldset = $el.closest("fieldset.checklist");
                if ($fieldset.length) {
                    $position=$fieldset;
                    strategy="append";
                }
            }

            for (var constraintName in error) {
                if (this._findErrorMessages($el, constraintName).length) {
                    return;
                }
                var $message = $("<em/>", {"class": "validation warning message"});
                $message.attr("data-validate-constraint", constraintName);
                $message.text(error[constraintName]);
                switch (strategy) {
                    case "append":
                        $message.appendTo($position);
                        break;
                    case "after":
                        $message.insertAfter($position);
                        break;
                }
            }
            this.errors += 1;
            $(this.options.disableSelector).prop('disabled', true).addClass('disabled');
            $position.trigger("pat-update", {pattern: "validate"});
        },

        // Parsley method to remove all error messages for a field
        _removeFieldError: function(parsley, constraintName) {
            var $el;
            if (this.parsley12) {
                $el = parsley.ParsleyInstance.element;
            } else {
                $el = parsley.element;
            }
            var $messages = this._findErrorMessages($el, constraintName);
            $messages.parent().trigger("pat-update", {pattern: "validate"});
            $messages.remove();
            if (this.errors <= 1) {
                $(this.options.disableSelector).prop('disabled', false).removeClass('disabled');
                this.errors = 0;
            } else {
                this.errors -= 1;
            }
        },

        onPreSubmit: function(event, veto) {
            veto.veto |= !$(event.target).parsley("isValid");
            $(event.target).parsley("validate");
        }
    });

});
