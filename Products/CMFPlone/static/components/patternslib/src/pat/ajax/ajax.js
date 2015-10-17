/**
 * Patterns ajax - AJAX injection for forms and anchors
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012-2013 Marko Durkovic
 */
define([
    "jquery",
    "pat-logger",
    "pat-parser",
    "pat-registry",
    "jquery.form"
], function($, logger, Parser, registry) {
    var log = logger.getLogger("pat.ajax"),
        parser = new Parser("ajax");

    parser.addArgument("url", function($el) {
        return ($el.is("a") ? $el.attr("href") :
                ($el.is("form") ? $el.attr("action") : "")).split("#")[0];
    });

    var _ = {
        name: "ajax",
        trigger: ".pat-ajax",
        parser: parser,
        init: function($el) {
            $el.off(".pat-ajax");
            $el.filter("a").on("click.pat-ajax", _.onTriggerEvents);
            $el.filter("form")
                .on("submit.pat-ajax", _.onTriggerEvents)
                .on("click.pat-ajax", "[type=submit]", _.onClickSubmit);
            $el.filter(":not(form,a)").each(function() {
                log.warn("Unsupported element:", this);
            });
            return $el;
        },
        destroy: function($el) {
            $el.off(".pat-ajax");
        },
        onClickSubmit: function(event) {
            var $form = $(event.target).parents("form").first(),
                name = event.target.name,
                value = $(event.target).val(),
                data = {};
            if (name) {
                data[name] = value;
            }
            $form.data("pat-ajax.clicked-data", data);
        },
        onTriggerEvents: function(event) {
            if (event) {
                event.preventDefault();
            }
            _.request($(this));
        },
        request: function($el, opts) {
            return $el.each(function() {
                _._request($(this), opts);
            });
        },
        _request: function($el, opts) {
            var cfg = _.parser.parse($el, opts),
                onError = function(jqxhr, status, error) {
                    // error can also stem from a javascript
                    // exception, not only errors described in the
                    // jqxhr.
                    log.error("load error for " + cfg.url + ":", error, jqxhr);
                    $el.trigger({
                        type: "pat-ajax-error",
                        error: error,
                        jqxhr: jqxhr
                    });
                },
                onSuccess = function(data, status, jqxhr) {
                    log.debug("success: jqxhr:", jqxhr);
                    $el.trigger({
                        type: "pat-ajax-success",
                        jqxhr: jqxhr
                    });
                },
                args = {
                    context: $el,
                    data: $el.data("pat-ajax.clicked-data"),
                    url: cfg.url,
                    error: onError,
                    success: onSuccess
                };

            $el.removeData("pat-ajax.clicked-data");
            log.debug("request:", args, $el[0]);
            if ($el.is("form")) {
                $el.ajaxSubmit(args);
            } else {
                $.ajax(args);
            }
        }
    };

    registry.register(_);
    return _;
});
