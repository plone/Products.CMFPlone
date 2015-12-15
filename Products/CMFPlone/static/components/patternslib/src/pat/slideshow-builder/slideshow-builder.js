/**
 * Patterns slideshow builder - Create forms to generate custom slideshows
 *
 * Copyright 2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger"
], function($, patterns, logging) {
    var log = logging.getLogger("slideshow-builder"),

        builder = {
        name: "slideshow-builder",
        trigger: ".pat-slideshow-builder",

        init: function($el) {
            return $el.each(function() {
                var action;

                if (this.tagName.toLowerCase()==="form")
                    action=this.action;
                else {
                    var $form = $(this).closest("form");
                    if ($form.length===0) {
                        log.error("Can not find a containing form", this);
                        return;
                    }
                    action = $form[0].action;
                }

                $.ajax({
                    url: action,
                    context: this,
                    dataType: "html",
                    error: builder.onError,
                    success: builder.onLoad
                });
            });
        },

        onError: function(jqXHR, textStatus, errorThrown) {
            log.error("Error loading slidethis from " + this.action, textStatus, errorThrown, this);
        },

        onLoad: function(html) {
            html=html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
                    .replace(/<head\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/head>/gi, "")
                    .replace(/<body([^>]*?)>/gi, "<div id=\"__original_body\">")
                    .replace(/<\/body([^>]*?)>/gi, "</div>");
            var $fragment = $(html),
                $slides = $fragment.find(".slide[id]"),
                headers = [],
                i;
            if (!$slides.length) {
                log.warn("Could not find any slides in " + this.action, this);
                return;
            }

            for (i=0; i<$slides.length; i++) {
                var slide = $slides[i],
                    $header = $(slide).find("header h2:first");
                if ($header.length)
                    headers.push({id: slide.id, title: $header.text()});
                else
                    log.info("No header found for slide " + slide.id + " from " + this.action, this);
            }

            if (!headers.length) {
                log.warn("No slides with headers found in " + this.action, this);
                return;
            }

            var fieldset = document.createElement("fieldset"),
                label, input;
            fieldset.className="checklist";

            for (i=0; i<headers.length; i++) {
                input=document.createElement("input");
                input.type="checkbox";
                input.name="slides";
                input.value=headers[i].id;
                label=document.createElement("label");
                label.appendChild(input);
                label.appendChild(document.createTextNode(headers[i].title));
                fieldset.appendChild(label);
            }
            this.insertBefore(fieldset, this.firstChild);
            patterns.scan(fieldset);
        }
    };

    patterns.register(builder);
    return builder;
});
