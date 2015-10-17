/*
 * changes to previous injection implementations
 * - no support for data-injection anymore, switch to new data-inject
 * - no support for data-href-next anymore, switch to data-inject: next-href
 * - XXX: add support for forms, see remnants in inject1 and ajaxify
 */
define([
    "jquery",
    "pat-ajax",
    "pat-parser",
    "pat-logger",
    "pat-registry",
    "pat-utils",
    "pat-htmlparser",
    "pat-jquery-ext"  // for :scrollable for autoLoading-visible
], function($, ajax, Parser, logger, registry, utils, htmlparser) {
    var log = logger.getLogger("pat.inject"),
        parser = new Parser("inject"),
        TEXT_NODE = 3;

    parser.addArgument("selector");
    parser.addArgument("target");
    parser.addArgument("data-type", "html");
    parser.addArgument("next-href");
    parser.addArgument("source");
    parser.addArgument("trigger", "default", ["default", "autoload", "autoload-visible"]);
    /* Once injection has completed successfully, pat-inject will trigger
     * an event for each hook: pat-inject-hook-$(hook)
     */
    parser.addArgument("hooks", [], ["raptor"], true);
    parser.addArgument("class"); // Add a class to the injected content.
    parser.addArgument("history");
    // XXX: this should not be here but the parser would bail on
    // unknown parameters and expand/collapsible need to pass the url
    // to us
    parser.addArgument("url");

    var _ = {
        name: "inject",
        trigger: "a.pat-inject, form.pat-inject, .pat-subform.pat-inject",
        init: function inject_init($el, opts) {
            if ($el.length > 1) {
                return $el.each(function() { _.init($(this), opts); });
            }
            var cfgs = _.extractConfig($el, opts);
            // if the injection shall add a history entry and HTML5 pushState
            // is missing, then don't initialize the injection.
            if (cfgs.some(function(e){return e.history === "record";}) &&
                    !("pushState" in history))
                return $el;
            $el.data("pat-inject", cfgs);

            // In case next-href is specified the anchor's href will
            // be set to it after the injection is triggered. In case
            // the next href already exists, we do not activate the
            // injection but instead just change the anchors href.
            //
            // XXX: This is used in only one project for linked
            // fullcalendars, it's sanity is wonky and we should
            // probably solve it differently. -- Maybe it's cool
            // after all.
            var $nexthref = $(cfgs[0].nextHref);
            if ($el.is("a") && $nexthref.length > 0) {
                log.debug("Skipping as next href already exists", $nexthref);
                // XXX: reconsider how the injection enters exhausted state
                return $el.attr({href: (window.location.href.split("#")[0] || "") +
                                 cfgs[0].nextHref});
            }

            switch (cfgs[0].trigger) {
                case "default":
                    // setup event handlers
                    if ($el.is("a")) {
                        $el.on("click.pat-inject", _.onClick);
                    } else if ($el.is("form")) {
                        $el.on("submit.pat-inject", _.onSubmit)
                        .on("click.pat-inject", "[type=submit]", ajax.onClickSubmit)
                        .on("click.pat-inject", "[type=submit][formaction], [type=image][formaction]", _.onFormActionSubmit);
                    } else if ($el.is(".pat-subform")) {
                        log.debug("Initializing subform with injection");
                    }
                    break;
                case "autoload":
                    _.onClick.apply($el[0], []);
                    break;
                case "autoload-visible":
                    _._initAutoloadVisible($el);
                    break;
            }
            log.debug("initialised:", $el);
            return $el;
        },

        destroy: function inject_destroy($el) {
            $el.off(".pat-inject");
            $el.data("pat-inject", null);
            return $el;
        },

        onClick: function inject_onClick(ev) {
            var cfgs = $(this).data("pat-inject"),
                $el = $(this);
            if (ev)
                ev.preventDefault();
            $el.trigger("patterns-inject-triggered");
            _.execute(cfgs, $el);
        },

        onSubmit: function inject_onSubmit(ev) {
            var cfgs = $(this).data("pat-inject"),
                $el = $(this);
            if (ev)
                ev.preventDefault();
            $el.trigger("patterns-inject-triggered");
            _.execute(cfgs, $el);
        },

        onFormActionSubmit: function inject_onFormActionSubmit(ev) {
            ajax.onClickSubmit(ev); // make sure the submitting button is sent with the form

            var $button = $(ev.target),
                formaction = $button.attr("formaction"),
                $form = $button.parents(".pat-inject").first(),
                opts = {url: formaction},
                cfgs = _.extractConfig($form, opts);

            ev.preventDefault();
            $form.trigger("patterns-inject-triggered");
            _.execute(cfgs, $form);
        },

        submitSubform: function inject_submitSubform($sub) {
            var $el = $sub.parents("form"),
                cfgs = $sub.data("pat-inject");
            try {
                $el.trigger("patterns-inject-triggered");
            } catch (e) {
                log.error("patterns-inject-triggered", e);
            }
            _.execute(cfgs, $el);
        },

        extractConfig: function inject_extractConfig($el, opts) {
            opts = $.extend({}, opts);

            var cfgs = parser.parse($el, opts, true);
            cfgs.forEach(function inject_extractConfig_each(cfg) {
                var urlparts, defaultSelector;
                // opts and cfg have priority, fallback to href/action
                cfg.url = opts.url || cfg.url || $el.attr("href") ||
                    $el.attr("action") || $el.parents("form").attr("action") ||
                    "";

                // separate selector from url
                urlparts = cfg.url.split("#");
                cfg.url = urlparts[0];

                // if no selector, check for selector as part of original url
                defaultSelector = urlparts[1] && "#" + urlparts[1] || "body";

                if (urlparts.length > 2) {
                    log.warn("Ignoring additional source ids:", urlparts.slice(2));
                }

                cfg.selector = cfg.selector || defaultSelector;
            });
            return cfgs;
        },
        // verify and post-process config
        // XXX: this should return a command instead of messing around on the config
        verifyConfig: function inject_verifyConfig(cfgs, $el) {
            var url = cfgs[0].url;

            // verification for each cfg in the array needs to succeed
            return cfgs.every(function inject_verifyConfig_each(cfg) {
                // in case of multi-injection, all injections need to use
                // the same url
                if (cfg.url !== url) {
                    log.error("Unsupported different urls for multi-inject");
                    return false;
                }

                // defaults
                cfg.source = cfg.source || cfg.selector;
                cfg.target = cfg.target || cfg.selector;

                if (!_._extractModifiers(cfg))
                    return false;

                // make sure target exist
                cfg.$target = cfg.$target || (cfg.target==="self" ? $el : $(cfg.target));
                if (cfg.$target.length === 0) {
                    if (!cfg.target) {
                        log.error("Need target selector", cfg);
                        return false;
                    }
                    cfg.$target = _._createTarget(cfg.target);
                    cfg.$injected = cfg.$target;
                }

                // check if target is "dirty"
                if (cfg.$target.hasClass('is-dirty')) {
                    if (!confirm('Are you sure you want to leave this page?')) {
                      return false;
                    }
                    cfg.$target.removeClass('is-dirty');
                }

                return true;
            });
        },

        _extractModifiers: function inject_extractModifiers(cfg) {
            var source_re = /^(.*?)(::element)?$/,
                target_re = /^(.*?)(::element)?(::after|::before)?$/,
                source_match = source_re.exec(cfg.source),
                target_match = target_re.exec(cfg.target),
                targetMod, targetPosition;

            // source content or element?
            cfg.source = source_match[1];
            // XXX: turn into source processor
            cfg.sourceMod = source_match[2] ? "element" : "content";

            // will be added while the ajax request is in progress
            cfg.targetLoadClasses = "injecting";

            // target content or element?
            targetMod = target_match[2] ? "element" : "content";
            cfg.target = target_match[1];
            cfg.targetLoadClasses += " injecting-" + targetMod;

            // position relative to target
            targetPosition = (target_match[3] || "::").slice(2);
            if (targetPosition)
                cfg.targetLoadClasses += " injecting-" + targetPosition;

            cfg.action = targetMod + targetPosition;
            // Once we start detecting illegal combinations, we'll
            // return false in case of error
            return true;
        },

        // create a target that matches the selector
        //
        // XXX: so far we only support #target and create a div with
        // that id appended to the body.
        _createTarget: function inject_createTarget (selector) {
            var $target;
            if (selector.slice(0,1) !== "#") {
                log.error("only id supported for non-existing target");
                return null;
            }
            $target = $("<div />").attr({id: selector.slice(1)});
            $("body").append($target);
            return $target;
        },

        stopBubblingFromRemovedElement: function ($el, cfgs, ev) {
            /* IE8 fix. Stop event from propagating IF $el will be removed
            * from the DOM. With pat-inject, often $el is the target that
            * will itself be replaced with injected content.
            *
            * IE8 cannot handle events bubbling up from an element removed
            * from the DOM.
            *
            * See: http://stackoverflow.com/questions/7114368/why-is-jquery-remove-throwing-attr-exception-in-ie8
            */
            var s; // jquery selector
            for (var i=0; i<cfgs.length; i++) {
                s = cfgs[i].target;
                if ($el.parents(s).addBack(s) && !ev.isPropagationStopped()) {
                    ev.stopPropagation();
                    return;
                }
            }
        },

        _performInjection: function ($el, $source, cfg, trigger) {
            /* Called after the XHR has succeeded and we have a new $source
             * element to inject.
             */
            if (cfg.sourceMod === "content") {
                $source = $source.contents();
            }
            var $src;
            // $source.clone() does not work with shived elements in IE8
            if (document.all && document.querySelector &&
                !document.addEventListener) {
                $src = $source.map(function() {
                    return $(this.outerHTML)[0];
                });
            } else {
                $src = $source.safeClone();
            }
            var $target = $(this),
                $injected = cfg.$injected || $src;

            $src.findInclusive("img").on("load", function() {
                $(this).trigger("pat-inject-content-loaded");
            });
            // Now the injection actually happens.
            if (_._inject(trigger, $src, $target, cfg)) { _._afterInjection($el, $injected, cfg); }
            // History support.
            if ((cfg.history === "record") && ("pushState" in history)) {
                history.pushState({'url': cfg.url}, "", cfg.url);
            }
        },

        _afterInjection: function ($el, $injected, cfg) {
            /* Set a class on the injected elements and fire the
             * patterns-injected event.
             */
            $injected.filter(function() {
                // setting data on textnode fails in IE8
                return this.nodeType !== TEXT_NODE;
            }).data("pat-injected", {origin: cfg.url});

            if ($injected.length === 1 && $injected[0].nodeType == TEXT_NODE) {
                // Only one element injected, and it was a text node.
                // So we trigger "patterns-injected" on the parent.
                // The event handler should check whether the
                // injected element and the triggered element are
                // the same.
                $injected.parent().trigger("patterns-injected", [cfg, $el[0], $injected[0]]);
            } else {
                $injected.each(function () {
                    // patterns-injected event will be triggered for each injected (non-text) element.
                    if (this.nodeType !== TEXT_NODE) {
                        $(this).addClass(cfg["class"]).trigger("patterns-injected", [cfg, $el[0], this]);
                    }
                });
            }
        },

        _onInjectSuccess: function ($el, cfgs, ev) {
            var sources$,
                data = ev && ev.jqxhr && ev.jqxhr.responseText;
            if (!data) {
                log.warn("No response content, aborting", ev);
                return;
            }
            $.each(cfgs[0].hooks || [], function (idx, hook) {
                $el.trigger("pat-inject-hook-"+hook);
            });
            _.stopBubblingFromRemovedElement($el, cfgs, ev);
            sources$ = _.callTypeHandler(cfgs[0].dataType, "sources", $el, [cfgs, data, ev]);
            cfgs.forEach(function(cfg, idx) {
                cfg.$target.each(function() {
                    _._performInjection.apply(this, [$el, sources$[idx], cfg, ev.target]);
                });
            });
            if (cfgs[0].nextHref) {
                $el.attr({href: (window.location.href.split("#")[0] || "") +
                            cfgs[0].nextHref});
                _.destroy($el);
            }
            $el.off("pat-ajax-success.pat-inject");
            $el.off("pat-ajax-error.pat-inject");
        },

        _onInjectError: function ($el, cfgs) {
            cfgs.forEach(function(cfg) {
                if ("$injected" in cfg)
                    cfg.$injected.remove();
            });
            $el.off("pat-ajax-success.pat-inject");
            $el.off("pat-ajax-error.pat-inject");
        },

        execute: function inject_execute(cfgs, $el) {
            // get a kinda deep copy, we scribble on it
            cfgs = cfgs.map(function(cfg) {
                return $.extend({}, cfg);
            });
            if (!_.verifyConfig(cfgs, $el)) {
                return;
            }
            // possibility for spinners on targets
            cfgs.forEach(function(cfg) { cfg.$target.addClass(cfg.targetLoadClasses); });

            $el.on("pat-ajax-success.pat-inject", this._onInjectSuccess.bind(this, $el, cfgs));
            $el.on("pat-ajax-error.pat-inject", this._onInjectError.bind(this, $el, cfgs));

            if (cfgs[0].url.length) {
                ajax.request($el, {url: cfgs[0].url});
            } else {
                // If there is no url specified, then content is being fetched
                // from the same page.
                // No need to do an ajax request for this, so we spoof the ajax
                // event.
                $el.trigger({
                    type: "pat-ajax-success",
                    jqxhr: {
                        responseText:  $("body").html()
                    }
                });
            }
        },

        _inject: function inject_inject(trigger, $source, $target, cfg) {
            // action to jquery method mapping, except for "content"
            // and "element"
            var method = {
                contentbefore: "prepend",
                contentafter:  "append",
                elementbefore: "before",
                elementafter:  "after"
            }[cfg.action];

            if ($source.length === 0) {
                log.warn("Aborting injection, source not found:", $source);
                $(trigger).trigger("pat-inject-missingSource",
                        {url: cfg.url,
                         selector: cfg.source});
                return false;
            }
            if ($target.length === 0) {
                log.warn("Aborting injection, target not found:", $target);
                $(trigger).trigger("pat-inject-missingTarget",
                        {selector: cfg.target});
                return false;
            }
            if (cfg.action === "content")
                $target.empty().append($source);
            else if (cfg.action === "element")
                $target.replaceWith($source);
            else
                $target[method]($source);

            return true;
        },

        _sourcesFromHtml: function inject_sourcesFromHtml(html, url, sources) {
            var $html = _._parseRawHtml(html, url);
            return sources.map(function inject_sourcesFromHtml_map(source) {
                if (source === "body")
                    source = "#__original_body";

                var $source = $html.find(source);

                if ($source.length === 0)
                    log.warn("No source elements for selector:", source, $html);

                $source.find("a[href^=\"#\"]").each(function () {
                    var href = this.getAttribute("href");
                    if (href.indexOf("#{1}") !== -1) {
                        // We ignore hrefs containing #{1} because they're not
                        // valid and only applicable in the context of
                        // pat-clone.
                        return;
                    }
                    // Skip in-document links pointing to an id that is inside
                    // this fragment.
                    if (href.length === 1)  // Special case for top-of-page links
                        this.href=url;
                    else if (!$source.find(href).length)
                        this.href=url+href;
                });

                return $source;
            });
        },

        _link_attributes: {
            A: "href",
            FORM: "action",
            IMG: "src",
            SOURCE: "src",
            VIDEO: "src"
        },

        _rebaseHTML_via_HTMLParser: function inject_rebaseHTML_via_HTMLParser(base, html) {
            var output = [],
                i, link_attribute, value;

            htmlparser.HTMLParser(html, {
                start: function(tag, attrs, unary) {
                    output.push("<"+tag);
                    link_attribute = _._link_attributes[tag.toUpperCase()];
                    for (i=0; i<attrs.length; i++) {
                        if (attrs[i].name.toLowerCase() === link_attribute) {
                            value = attrs[i].value;
                            // Do not rewrite Zope views or in-document links.
                            // In-document links will be processed later after
                            // extracting the right fragment.
                            if (value.slice(0, 2) !== "@@" && value[0] !== "#") {
                                value = utils.rebaseURL(base, value);
                                value = value.replace(/(^|[^\\])"/g, "$1\\\"");
                            }
                        }  else
                            value = attrs[i].escaped;
                        output.push(" " + attrs[i].name + "=\"" + value + "\"");
                    }
                    output.push(unary ? "/>" : ">");
                },

                end: function(tag) {
                    output.push("</"+tag+">");
                },

                chars: function(text) {
                    output.push(text);
                },

                comment: function(text) {
                    output.push("<!--"+text+"-->");
                }
            });
            return output.join("");
        },

        _rebaseAttrs: {
            A: "href",
            FORM: "action",
            IMG: "data-pat-inject-rebase-src",
            SOURCE: "data-pat-inject-rebase-src",
            VIDEO: "data-pat-inject-rebase-src"
        },

        _rebaseHTML: function inject_rebaseHTML(base, html) {
            var $page = $(html.replace(
                /(\s)(src\s*)=/gi,
                "$1src=\"\" data-pat-inject-rebase-$2="
            ).trim()).wrapAll("<div>").parent();

            $page.find(Object.keys(_._rebaseAttrs).join(",")).each(function() {
                var $this = $(this),
                    attrName = _._rebaseAttrs[this.tagName],
                    value = $this.attr(attrName);

                if (value && value.slice(0, 2) !== "@@" && value[0] !== "#" &&
                    value.slice(0, 7) !== "mailto:") {
                    value = utils.rebaseURL(base, value);
                    $this.attr(attrName, value);
                }
            });
            // XXX: IE8 changes the order of attributes in html. The following
            // lines move data-pat-inject-rebase-src to src.
            $page.find("[data-pat-inject-rebase-src]").each(function() {
                var $el = $(this);
                $el.attr("src", $el.attr("data-pat-inject-rebase-src"))
                   .removeAttr("data-pat-inject-rebase-src");
            });

            return $page.html().replace(
                    /src="" data-pat-inject-rebase-/g, ""
                ).trim();
        },

        _parseRawHtml: function inject_parseRawHtml(html, url) {
            url = url || "";

            // remove script tags and head and replace body by a div
            var clean_html = html
                    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
                    .replace(/<head\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/head>/gi, "")
                    .replace(/<body([^>]*?)>/gi, "<div id=\"__original_body\">")
                    .replace(/<\/body([^>]*?)>/gi, "</div>");
            try {
                clean_html = _._rebaseHTML(url, clean_html);
            } catch (e) {
                log.error("Error rebasing urls", e);
            }
            var $html = $("<div/>").html(clean_html);

            if ($html.children().length === 0)
                log.warn("Parsing html resulted in empty jquery object:", clean_html);

            return $html;
        },

        // XXX: hack
        _initAutoloadVisible: function inject_initAutoloadVisible($el) {
            // ignore executed autoloads
            if ($el.data("pat-inject-autoloaded"))
                return false;

            var $scrollable = $el.parents(":scrollable"),
                checkVisibility;

            // function to trigger the autoload and mark as triggered
            function trigger() {
                $el.data("pat-inject-autoloaded", true);
                _.onClick.apply($el[0], []);
                return true;
            }

            // Use case 1: a (heigh-constrained) scrollable parent
            if ($scrollable.length) {
                // if scrollable parent and visible -> trigger it
                // we only look at the closest scrollable parent, no nesting
                checkVisibility = utils.debounce(function inject_checkVisibility_scrollable() {
                    if ($el.data("patterns.autoload"))
                        return false;
                    var reltop = $el.offset().top - $scrollable.offset().top - 1000,
                        doTrigger = reltop <= $scrollable.innerHeight();
                    if (doTrigger) {
                        // checkVisibility was possibly installed as a scroll
                        // handler and has now served its purpose -> remove
                        $($scrollable[0]).off("scroll", checkVisibility);
                        $(window).off("resize.pat-autoload", checkVisibility);
                        return trigger();
                    }
                    return false;
                }, 100);
                if (checkVisibility())
                    return true;

                // wait to become visible - again only immediate scrollable parent
                $($scrollable[0]).on("scroll", checkVisibility);
                $(window).on("resize.pat-autoload", checkVisibility);
            } else {
                // Use case 2: scrolling the entire page
                checkVisibility = utils.debounce(function inject_checkVisibility_not_scrollable() {
                    if ($el.data("patterns.autoload"))
                        return false;
                    if (!utils.elementInViewport($el[0]))
                        return false;

                    $(window).off(".pat-autoload", checkVisibility);
                    return trigger();
                }, 100);
                if (checkVisibility())
                    return true;
                $(window).on("resize.pat-autoload scroll.pat-autoload",
                        checkVisibility);
            }
            return false;
        },

        // XXX: simple so far to see what the team thinks of the idea
        registerTypeHandler: function inject_registerTypeHandler(type, handler) {
            _.handlers[type] = handler;
        },

        callTypeHandler: function inject_callTypeHandler(type, fn, context, params) {
            type = type || "html";

            if (_.handlers[type] && $.isFunction(_.handlers[type][fn])) {
                return _.handlers[type][fn].apply(context, params);
            } else {
                return null;
            }
        },

        handlers: {
            "html": {
                sources: function(cfgs, data) {
                    var sources = cfgs.map(function(cfg) { return cfg.source; });
                    return _._sourcesFromHtml(data, cfgs[0].url, sources);
                }
            }
        }
    };

    $(document).on("patterns-injected", function(ev, cfg) {
        cfg.$target.removeClass(cfg.targetLoadClasses);
    });

    $(window).bind("popstate", function (event) {
        // popstate also triggers on traditional anchors
        if (!event.originalEvent.state && ("replaceState" in history)) {
            try {
                history.replaceState("anchor", "", document.location.href);
            } catch (e) {
                log.debug(e);
            }
            return;
        }
        // popstate event can be fired when history.back() is called. If
        // event.state is null, then we are at the first "pageload" state
        // and there's nothing left to do, so we do nothing.
        if (event.state) {
            window.location.reload();
        }
    });

    // this entry ensures that the initally loaded page can be reached with
    // the back button
    if ("replaceState" in history) {
        try {
            history.replaceState("pageload", "", document.location.href);
        } catch (e) {
            log.debug(e);
        }
    }

    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
