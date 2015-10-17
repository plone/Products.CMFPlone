/**
 * Patterns autosuggest - suggestion/completion support
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012 JC Brand
 * Copyright 2013 Marko Durkovic
 */
define([
    "jquery",
    "pat-logger",
    "pat-parser",
    "pat-registry",
    "select2"
], function($, logger, Parser, registry) {
    "use strict";
    var log = logger.getLogger("calendar");
    var parser = new Parser("autosuggest");
    parser.addArgument("ajax-data-type", "JSON");
    parser.addArgument("ajax-search-index", "");
    parser.addArgument("ajax-url", "");
    parser.addArgument("allow-new-words", true); // Should custom tags be allowed?
    parser.addArgument("max-selection-size", 0);
    parser.addArgument("placeholder", function($el) { return $el.attr("placeholder") || "Enter text"; });
    parser.addArgument("prefill", function($el) { return $el.val(); });
    parser.addArgument("prefill-json", ""); // JSON format for pre-filling
    parser.addArgument("words", "");
    parser.addArgument("words-json");

    // "selection-classes" allows you to add custom CSS classes to currently
    // selected elements.
    // The value passed in must be an object with each id being the text inside
    // a selection and value being a list of classes to be added to the
    // selection.
    // e.g. {'BMW': ['selected', 'car'], 'BMX': ['selected', 'bicycle']}
    parser.addArgument("selection-classes", "");

    parser.addAlias("maximum-selection-size", "max-selection-size");
    parser.addAlias("data", "prefill-json");
    parser.addAlias("pre-fill", "prefill");

    var _ = {
        name: "autosuggest",
        trigger: ".pat-autosuggest",
        init: function($el, opts) {
            if ($el.length > 1) {
                return $el.each(function() { _.init($(this), opts); });
            }
            var pat_config = parser.parse($el, opts);
            var config = {
                placeholder: $el.attr("readonly") ? "" : pat_config.placeholder,
                tokenSeparators: [","],
                openOnEnter: false,
                maximumSelectionSize: pat_config.maxSelectionSize
            };

            if (pat_config.selectionClasses) {
                // We need to customize the formatting/markup of the selection
                config.formatSelection = function(obj, container) {
                    var selectionClasses = null;
                    try {
                        selectionClasses = $.parseJSON(pat_config.selectionClasses)[obj.text];
                    } catch(SyntaxError) {
                        log.error("SyntaxError: non-JSON data given to pat-autosuggest (selection-classes)");
                    }
                    if (selectionClasses) {
                        // According to Cornelis the classes need to be applied on
                        // the <li>, which is the container's parent
                        container.parent().addClass(selectionClasses.join(" "));
                    }
                    return obj.text;
                };
            }

            if ($el[0].tagName === "INPUT") {
                config = this.configureInput($el, pat_config, config);
            }
            $el.select2(config);
            $el.on("pat-update", function (e, data) {
                if (data.pattern === "depends") {
                    if (data.enabled === true) {
                        $el.select2("enable", true);
                    } else if (data.enabled === false) {
                        $el.select2("disable", true);
                    }

                }
            });

            // suppress propagation for second input field
            $el.prev().on("input-change input-defocus input-change-delayed",
                function(e) { e.stopPropagation(); }
            );

            // Clear the values when a reset button is pressed
            $el.closest("form").find("button[type=reset]").on("click", function () {
                $el.select2("val", "");
            });
            return $el;
        },

        configureInput: function ($el, pat_config, select2_config) {
            var d, data, words, ids = [], prefill;

            select2_config.createSearchChoice = function(term, data) {
                if (pat_config.allowNewWords) {
                    if ($(data).filter(function() { return this.text.localeCompare(term) === 0; }).length === 0) {
                        return { id: term, text: term };
                    }
                }
                else {
                    return null;
                }
            };

            if (pat_config.wordsJson && pat_config.wordsJson.length) {
                try {
                    words = $.parseJSON(pat_config.wordsJson);
                } catch(SyntaxError) {
                    words = [];
                    log.error("SyntaxError: non-JSON data given to pat-autosuggest");
                }
                if (! Array.isArray(words)) {
                    words = $.map(words, function (v, k) { return {id: k, text: v}; });
                }
            } else {
                words = pat_config.words ? pat_config.words.split(/\s*,\s*/) : [];
            }
            select2_config.tags = words;

            if (pat_config.prefill && pat_config.prefill.length) {
                prefill = pat_config.prefill.split(",");
                $el.val(prefill);
                select2_config.initSelection = function (element, callback) {
                    var i, data = [],
                    values = element.val().split(",");
                    for (i=0; i<values.length; i++) {
                        data.push({id: values[i], text: values[i]});
                    }
                    callback(data);
                };
            }

            if (pat_config.prefillJson.length) {
                /* We support two types of JSON data for prefill data:
                 *   {"john-snow": "John Snow", "tywin-lannister": "Tywin Lannister"}
                 * or
                 *   [
                 *    {"id": "john-snow", "text": "John Snow"},
                 *    {"id": "tywin-lannister", "text":"Tywin Lannister"}
                 *   ]
                 */
                try {
                    data = $.parseJSON(pat_config.prefillJson);
                    for (d in data) {
                        if (typeof d === "object") {
                            ids.push(d.id);
                        } else {
                            ids.push(d);
                        }
                    }
                    $el.val(ids);
                    select2_config.initSelection = function (element, callback) {
                        var d, _data = [];
                        for (d in data) {
                            if (typeof d === "object") {
                                _data.push({id: d.id, text: d.text});
                            } else {
                                _data.push({id: d, text: data[d]});
                            }
                        }
                        callback(_data);
                    };
                } catch(SyntaxError) {
                    log.error("SyntaxError: non-JSON data given to pat-autosuggest");
                }
            }

            if ((pat_config.ajax) && (pat_config.ajax.url)) {
                select2_config = $.extend(true, {
                    minimumInputLength: 2,
                    ajax: {
                        url: pat_config.ajax.url,
                        dataType: pat_config.ajax["data-type"],
                        type: "POST",
                        quietMillis: 400,
                        data: function (term, page) {
                            return {
                                index: pat_config.ajax["search-index"],
                                q: term, // search term
                                page_limit: 10,
                                page: page
                            };
                        },
                        results: function (data, page) {
                            // parse the results into the format expected by Select2.
                            // data must be a list of objects with keys "id" and "text"
                            return {results: data, page: page};
                        }
                    }
                }, select2_config);
            }
            return select2_config;
        },

        destroy: function($el) {
            $el.off(".pat-autosuggest");
            $el.select2("destroy");
        },

        transform: function($content) {
            $content.findInclusive("input[type=text].pat-autosuggest").each(function() {
                var $src = $(this),
                    $dest = $("<input type='hidden'/>").insertAfter($src);

                // measure in IE8, otherwise hidden will have width 0
                if (document.all && !document.addEventListener) {
                    $dest.css("width", $src.outerWidth(false)+"px");
                }
                $src.detach();
                $.each($src.prop("attributes"), function() {
                    if (this.name !== "type") {
                        $dest.attr(this.name, this.value);
                    }
                });
                $src.remove();
            });
        }
    };
    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
