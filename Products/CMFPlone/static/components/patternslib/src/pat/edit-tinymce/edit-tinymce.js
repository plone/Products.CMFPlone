define([
    "jquery",
    "pat-parser",
    "pat-logger",
    "pat-registry",
    "pat-utils",
    "jquery.textchange",
    "tinymce"
], function($, Parser, logger, registry, utils) {
    var log = logger.getLogger("pat.editTinyMCE"),
        parser = new Parser("edit-tinymce");

    parser.addArgument("tinymce-baseurl");

    var _ = {
        name: "editTinyMCE",
        trigger: "form textarea.pat-edit-tinymce",
        init: function($el, opts) {
            var $form = $el.parents("form"),
                id = $el.attr("id");

            // make sure the textarea has an id
            if (!id) {
                var formid = $form.attr("id"),
                    name = $el.attr("name");
                if (!formid) {
                    log.error("Textarea or parent form needs an id", $el, $form);
                    return false;
                }
                if (!name) {
                    log.error("Textarea needs a name", $el);
                    return false;
                }
                id = formid + "_" + name;
                if ($("#"+id).length > 0) {
                    log.error("Textarea needs an id", $el);
                    return false;
                }
                $el.attr({id: id});
            }

            // read configuration
            var cfg = $el.data("tinymce-json");
            if (!cfg) {
                log.info("data-tinymce-json empty, using default config", $el);
                cfg = {};
            }
            cfg.elements = id;
            cfg.mode = "exact";
            cfg.readonly = Boolean($el.attr("readonly"));

            // get arguments
            var args = parser.parse($el, opts);

            if (!args.tinymceBaseurl) {
                log.error("tinymce-baseurl has to point to TinyMCE resources");
                return false;
            }

            var base_url = window.location.toString(), idx;
            if ((idx=base_url.indexOf("?"))!==-1)
                base_url=base_url.slice(0, idx);

            // handle rebasing of own urls if we were injected
            var parents = $el.parents().filter(function() {
                return $(this).data("pat-injected");
            });
            if (parents.length)
                base_url = utils.rebaseURL(base_url, parents.first().data("pat-injected").origin);
            if (cfg.content_css)
                cfg.content_css = utils.rebaseURL(base_url, cfg.content_css);

            if (args.tinymceBaseurl.indexOf("://")!==-1 || args.tinymceBaseurl[0]==="/") {
                // tinyMCE.baseURL must be absolute
                tinyMCE.baseURL = window.location.protocol + "//" +
                    window.location.host+"/" + args.tinymceBaseurl;
            } else {
                tinyMCE.baseURL = utils.rebaseURL(base_url, args.tinymceBaseurl);
            }
            tinyMCE.baseURI = new tinyMCE.util.URI(tinyMCE.baseURL);

            cfg.oninit = function() {
                var editors = tinyMCE.editors.filter(function(e) {
                        return e.id === id;
                    }),
                    ed = editors[editors.length-1];

                var handler = function() {
                    tinyMCE.editors[id].save();
                    $el.trigger("input-change");
                };

                var setAttribHandler = function(ed, el) {
                    // handle image resize
                    if (el.tagName === "IMG") {
                        handler();
                    }
                };

                var clickHandler = function() {
                    $el.trigger("click");
                };

                ed.onKeyUp.add(handler);
                ed.onChange.add(handler);
                ed.onUndo.add(handler);
                ed.onRedo.add(handler);
                ed.onSetAttrib.add(setAttribHandler);
                ed.onClick.add(clickHandler);
            };

            // initialize editor
            tinyMCE.init(cfg);

            return $el;
        },

        destroy: function() {
            // XXX
        }
    };

    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
