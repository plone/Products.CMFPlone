/**
 * Patterns registry - Central registry and scan logic for patterns
 *
 * Copyright 2012-2013 Simplon B.V.
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2013 Marko Durkovic
 * Copyright 2013 Rok Garbas
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
    "pat-logger",
    "pat-utils",
    // below here modules that are only loaded
    "pat-compat",
    "pat-jquery-ext"
], function($, logger, utils) {
    var log = logger.getLogger("registry");

    var disable_re = /patterns-disable=([^&]+)/g,
        dont_catch_re = /patterns-dont-catch/g,
        dont_catch = false,
        disabled = {}, match;

    while ((match=disable_re.exec(window.location.search)) !== null) {
        disabled[match[1]] = true;
        log.info('Pattern disabled via url config:', match[1]);
    }

    while ((match=dont_catch_re.exec(window.location.search)) !== null) {
        dont_catch = true;
        log.info('I will not catch init exceptions');
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
                log.info('loaded: ' + Object.keys(registry.patterns).sort().join(', '));
                registry.scan(document.body);
                registry.initialized = true;
                log.info('finished initial scan.');
            });
        },

        scan: function registry_scan(content, patterns, trigger) {
            var $content = $(content),
                all = [], allsel,
                $match, plog;

            // If no list of patterns was specified, we scan for all patterns
            patterns = patterns || Object.keys(registry.patterns);

            // selector for all patterns
            patterns.forEach(function registry_scan_loop(name) {
                if (disabled[name]) {
                    log.debug('Skipping disabled pattern:', name);
                    return;
                }
                var pattern = registry.patterns[name];
                if (pattern.transform) {
                    try {
                        pattern.transform($content);
                    } catch (e) {
                        if (dont_catch) { throw(e); }
                        log.error("Transform error for pattern" + name, e);
                    }
                }
                if (pattern.trigger) {
                    all.push(pattern.trigger);
                }
            });
            // Find all elements that belong to any pattern.
            allsel = all.join(",");
            $match = $content.findInclusive(allsel);
            $match = $match.filter(function() { return $(this).parents('pre').length === 0; });
            $match = $match.filter(":not(.cant-touch-this)");

            // walk list backwards and initialize patterns inside-out.
            $match.toArray().reduceRight(function registry_pattern_init(acc, el) {
                var pattern, $el = $(el);
                for (var name in registry.patterns) {
                    pattern = registry.patterns[name];
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
                }
            }, null);
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
                $.fn[plugin_name.replace(/^pat/, "pattern")] = utils.jqueryPlugin(pattern);
            }
            log.debug("Registered pattern:", name, pattern);
            if (registry.initialized) {
                registry.scan(document.body, [name]);
            }
            return true;
        }
    };

    $(document).on("patterns-injected.patterns",
            function registry_onInject(ev, inject_config, inject_trigger) {
                registry.scan(ev.target, null, {type: "injection", element: inject_trigger});
                $(ev.target).trigger("patterns-injected-scanned");
            });

    return registry;
});
// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
