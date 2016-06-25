/**
 * Patterns registry - Central registry and scan logic for patterns
 *
 * Copyright 2012-2013 Simplon B.V.
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2013 Marko Durkovic
 * Copyright 2013 Rok Garbas
 * Copyright 2014-2015 Syslab.com GmBH, JC Brand
 */

/*
 * changes to previous patterns.register/scan mechanism
 * - if you want initialised class, do it in init
 * - init returns set of elements actually initialised
 * - handle once within init
 * - no turnstile anymore
 * - set pattern.jquery_plugin if you want it
 */
define([
    "jquery",
    "underscore",
    "pat-logger",
    "pat-utils",
    // below here modules that are only loaded
    "pat-compat",
    "pat-jquery-ext"
], function($, _, logger, utils) {
    var log = logger.getLogger("registry"),
        disable_re = /patterns-disable=([^&]+)/g,
        dont_catch_re = /patterns-dont-catch/g,
        dont_catch = false,
        disabled = {}, match;

    while ((match=disable_re.exec(window.location.search)) !== null) {
        disabled[match[1]] = true;
        log.info("Pattern disabled via url config:", match[1]);
    }

    while ((match=dont_catch_re.exec(window.location.search)) !== null) {
        dont_catch = true;
        log.info("I will not catch init exceptions");
    }

    var registry = {
        patterns: {},
        // as long as the registry is not initialized, pattern
        // registration just registers a pattern. Once init is called,
        // the DOM is scanned. After that registering a new pattern
        // results in rescanning the DOM only for this pattern.
        initialized: false,
        init: function registry_init() {
            $(document).ready(function() {
                log.info("loaded: " + Object.keys(registry.patterns).sort().join(", "));
                registry.scan(document.body);
                registry.initialized = true;
                log.info("finished initial scan.");
            });
        },

        clear: function clearRegistry() {
            // Removes all patterns from the registry. Currently only being
            // used in tests.
            this.patterns = {};
        },

        transformPattern: function(name, content) {
            /* Call the transform method on the pattern with the given name, if
             * it exists.
             */
            if (disabled[name]) {
                log.debug("Skipping disabled pattern:", name);
                return;
            }
            var pattern = registry.patterns[name];
            if (pattern.transform) {
                try {
                    pattern.transform($(content));
                } catch (e) {
                    if (dont_catch) { throw(e); }
                    log.error("Transform error for pattern" + name, e);
                }
            }
        },

        initPattern: function(name, el, trigger) {
            /* Initialize the pattern with the provided name and in the context
             * of the passed in DOM element.
             */
            var $el = $(el);
            var pattern = registry.patterns[name];
            if (pattern.init) {
                plog = logger.getLogger("pat." + name);
                if ($el.is(pattern.trigger)) {
                    plog.debug("Initialising:", $el);
                    try {
                        pattern.init($el, null, trigger);
                        plog.debug("done.");
                    } catch (e) {
                        if (dont_catch) { throw(e); }
                        plog.error("Caught error:", e);
                    }
                }
            }
        },

        orderPatterns: function (patterns) {
            // XXX: Bit of a hack. We need the validation pattern to be
            // parsed and initiated before the inject pattern. So we make
            // sure here, that it appears first. Not sure what would be
            // the best solution. Perhaps some kind of way to register
            // patterns "before" or "after" other patterns.
            if (_.contains(patterns, "validation") && _.contains(patterns, "inject")) {
                patterns.splice(patterns.indexOf("validation"), 1);
                patterns.unshift("validation");
            }
            return patterns;
        },

        scan: function registryScan(content, patterns, trigger) {
            var selectors = [], $match, plog;
            patterns = this.orderPatterns(patterns || Object.keys(registry.patterns));
            patterns.forEach(_.partial(this.transformPattern, _, content));
            patterns = _.each(patterns, function (name) {
                var pattern = registry.patterns[name];
                if (pattern.trigger) {
                    selectors.unshift(pattern.trigger);
                }
            });
            $match = $(content).findInclusive(selectors.join(",")); // Find all DOM elements belonging to a pattern
            $match = $match.filter(function() { return $(this).parents("pre").length === 0; });
            $match = $match.filter(":not(.cant-touch-this)");

            // walk list backwards and initialize patterns inside-out.
            $match.toArray().reduceRight(function registryInitPattern(acc, el) {
                patterns.forEach(_.partial(this.initPattern, _, el, trigger));
            }.bind(this), null);
            $("body").addClass("patterns-loaded");
        },

        register: function registry_register(pattern, name) {
            var plugin_name, jquery_plugin;
            name = name || pattern.name;
            if (!name) {
                log.error("Pattern lacks a name:", pattern);
                return false;
            }
            if (registry.patterns[name]) {
                log.error("Already have a pattern called: " + name);
                return false;
            }

            // register pattern to be used for scanning new content
            registry.patterns[name] = pattern;

            // register pattern as jquery plugin
            if (pattern.jquery_plugin) {
                plugin_name = ("pat-" + name)
                        .replace(/-([a-zA-Z])/g, function(match, p1) {
                            return p1.toUpperCase();
                        });
                $.fn[plugin_name] = utils.jqueryPlugin(pattern);
                // BBB 2012-12-10 and also for Mockup patterns.
                $.fn[plugin_name.replace(/^pat/, "pattern")] = $.fn[plugin_name];
            }
            log.debug("Registered pattern:", name, pattern);
            if (registry.initialized) {
                registry.scan(document.body, [name]);
            }
            return true;
        }
    };
    return registry;
});
// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
