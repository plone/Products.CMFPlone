/**
 * Patterns toggle - toggle class on click
 *
 * Copyright 2012-2014 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger",
    "pat-parser",
    "pat-store"
], function($, patterns, logger, Parser, store) {
    var log = logger.getLogger("pat.toggle"),
        parser = new Parser("toggle");

    parser.addArgument("selector");
    parser.addArgument("attr", "class");
    parser.addArgument("value");
    parser.addArgument("store", "none", ["none", "session", "local"]);

    function ClassToggler(values) {
        this.values=values.slice(0);
        if (this.values.length>1)
            this.values.push(values[0]);
    }

    ClassToggler.prototype = {
        toggle: function Toggler_toggle(el) {
            var current = this.get(el),
                next = this.next(current);
            this.set(el, next);
            return next;
        },

        get: function Toggler_get(el) {
            var classes = el.className.split(/\s+/);
            for (var i=0; i<this.values.length;i++)
                if (classes.indexOf(this.values[i])!==-1)
                    return this.values[i];
            return null;
        },

        set: function Toggler_set(el, value) {
            var classes = el.className.split(/\s+/),
                values = this.values;
            classes=classes.filter(function(v) { return v.length && values.indexOf(v)===-1;});
            if (value)
                classes.push(value);
            el.className=classes.join(" ");
        },

        next: function Toggler_next(current) {
            if (this.values.length===1)
                return current ? null : this.values[0];
            for (var i=0; i<(this.values.length-1); i++)
                if (this.values[i]===current)
                    return this.values[i+1];
            return this.values[0];
       }
    };

    function AttributeToggler(attribute) {
        this.attribute=attribute;
    }

    AttributeToggler.prototype = new ClassToggler([]);
    AttributeToggler.prototype.get=function AttributeToggler_get(el) {
        return !!el[this.attribute];
    };

    AttributeToggler.prototype.set=function AttributeToggler_set(el, value) {
        if (value)
            el[this.attribute]=value;
        else
            el.removeAttribute(this.attribute);
    };

    AttributeToggler.prototype.next=function AttributeToggler_next(value) {
        return !value;
    };


    var toggle = {
        name: "toggle",
        trigger: ".pat-toggle",

        // Hook for testing
        _ClassToggler: ClassToggler,
        _AttributeToggler: AttributeToggler,

        init: function toggle_init($el) {
            return $el.each(function toggle_init_el() {
                var $trigger = $(this),
                    options = toggle._validateOptions(this, parser.parse($trigger, true));

                if (!options.length)
                    return;

                for (var i=0; i<options.length; i++)
                    if (options[i].value_storage) {
                        var victims, state, last_state;
                        victims = $(options[i].selector);
                        if (!victims.length)
                            continue;
                        state=options[i].toggler.get(victims[0]);
                        last_state=options[i].value_storage.get();
                        if (state!==last_state && last_state !== null)
                            for (var j=0; j<victims.length; j++)
                                options[i].toggler.set(victims[j], last_state);
                }

                $trigger
                    .off(".toggle")
                    .on("click.toggle", null, options, toggle._onClick)
                    .on("keypress.toggle", null, options, toggle._onKeyPress);
            });
        },

        _makeToggler: function toggle_makeToggler(options) {
            if (options.attr==="class") {
                var values = options.value.split(/\s+/);
                values=values.filter(function(v) { return v.length; });
               return new this._ClassToggler(values);
           } else
                return new this._AttributeToggler(options.attr);
        },

        _validateOptions: function toggle_validateOptions(trigger, options) {
            var correct=[],
                i, option, store_error;

            if (!options.length)
                return correct;

            for (i=0; i<options.length; i++) {
                option=options[i];
                if (!option.selector) {
                    log.error("Toggle pattern requires a selector.");
                    continue;
                }
                if (option.attr!=="class" && option.value) {
                    log.warn("Values are not supported attributes other than class.");
                    continue;
                }
                if (option.attr==="class" && !option.value) {
                    log.error("Toggle pattern needs values for class attributes.");
                    continue;
                }

                if (i && option.store!=="none") {
                    log.warn("store option can only be set on first argument");
                    option.store="none";
                }

                if (option.store!=="none") {
                    if (!trigger.id) {
                        log.warn("state persistance requested, but element has no id");
                        option.store="none";
                    } else if (!store.supported) {
                        store_error="browser does not support webstorage";
                        log.warn("state persistance requested, but browser does not support webstorage");
                        option.store="none";
                    } else {
                        var storage = (option.store==="local" ? store.local : store.session)(toggle.name);
                        option.value_storage = new store.ValueStorage(storage, (trigger.id+"-"+i));
                    }
                }
                option.toggler=this._makeToggler(option);
                correct.push(option);
            }

            return correct;
        },

        _onClick: function toggle_onClick(event) {
            var options = event.data,
                updated = false,
                option, victims, toggler, next_state, j;

            for (var i=0; i<options.length; i++) {
                option=options[i];
                victims = $(option.selector);
                if (!victims.length)
                    continue;
                toggler=option.toggler;
                next_state=toggler.toggle(victims[0]);
                for (j=1; j<victims.length; j++)
                    toggler.set(victims[j], next_state);
                if (option.value_storage)
                    option.value_storage.set(next_state);
                updated = true;
            }
            if (updated) {
                $(this).trigger("pat-update", {pattern: "toggle"});
            }
            event.preventDefault();
        },

        _onKeyPress : function toggle_onKeyPress(event) {
            var keycode = event.keyCode ? event.keyCode : event.which;
            if (keycode==="13")
                $(this).trigger("click", event);
        }
    };

    patterns.register(toggle);
    return toggle;
});
