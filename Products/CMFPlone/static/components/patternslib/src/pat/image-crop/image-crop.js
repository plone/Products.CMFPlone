define([
    "jquery",
    "pat-logger",
    "pat-parser",
    "pat-registry",
    "jcrop"
], function($, logger, Parser, registry) {
    var log = logger.getLogger("pat.image-crop"),
        parser = new Parser("image-crop");

    parser.addArgument("preview-id", "");
    parser.addArgument("preview-height", 0);
    parser.addArgument("preview-width", 0);
    parser.addArgument("aspect-ratio", 1);
    parser.addArgument("form-id", "");
    parser.addArgument("initial-sel", "0 0 0 0");
    parser.addArgument("min-size", "0 0");
    parser.addArgument("max-size", "0 0");
    parser.addArgument("input-prefix", "");

    var _ = {
        name: "image-crop",
        trigger: "img.pat-image-crop",
        bounds: [0, 0],
        inputNames: ["x1", "y1", "x2", "y2", "w", "h"],

        init: function($el, options) {
            // initialize the elements
            return $el.each(function() {
                var $this = $(this),
                    opts = parser.parse($this, options),
                    data = {};

                // Initialize the preview parameters
                if (opts.preview.id.length === 0)
                    data.preview = false;
                else {
                    data.preview = {};
                    data.preview.element = $(opts.preview.id);
                    if (data.preview.element.length === 0) {
                        log.error("Invalid preview element ID supplied: " + opts.preview.id);
                        return;
                    }
                    if (opts.previewWidth > 0 && opts.preview.height > 0) {
                        data.preview.width = opts.preview.width;
                        data.preview.height = opts.preview.height;
                    } else {
                        data.preview.width = data.preview.element.parent().width();
                        data.preview.height = data.preview.element.parent().height();
                    }
                }

                // Set the form ID
                if (opts.formId.length === 0) {
                    // no form ID supplied. Look for the closest parent form element
                    data.form = $this.closest("form");
                    if (data.form.length === 0) {
                        log.error("No form specified or found");
                        return;
                    }
                } else {
                    data.form = $(opts.formId);
                    if (data.form.length === 0) {
                        log.error("Invalid form ID supplied: " + opts.formId);
                    }
                }

                // Setup form inputs
                data.prefix = opts.inputPrefix;
                data.inputs = {};
                for (var i = 0; i < _.inputNames.length; i++)
                    data.inputs[_.inputNames[i]] = _._setupInput(data.form, data.prefix, _.inputNames[i]);

                //
                // Initial coordinates
                //
                var ic = _._parseOpt(opts.initialSel);
                if (ic.length !== 4)
                    log.warn("Invalid coordinates for initial selection");
                else if (ic[2] - ic[0] > 0 && ic[3] - ic[1] > 0)
                    data.initialCoords = ic;

                data.aspectRatio = opts.aspectRatio;
                data.minSize = _._parseOpt(opts.minSize);
                data.maxSize = _._parseOpt(opts.maxSize);

                var handler = function(c) { _.onSelect(c, data); };

                $this.Jcrop({
                    onChange: handler,
                    onSelect: handler,
                    onRelease: handler,
                    aspectRatio: data.aspectRatio,
                    setSelect: data.initialCoords,
                    minSize: data.minSize,
                    maxSize: data.maxSize
                }, function() {
                    data.api = this;
                    _.onSelect(this.tellSelect(), data);
                });
            });
        },

        _setupInput: function($form, prefix, name) {
            var input = $form.find("input[name=" + prefix + name + "]");
            if (input.length === 0)
                input = $("<input type=\"hidden\" name=\"" + prefix + name + "\" />").appendTo($form);
            return input;
        },

        _parseOpt: function(val) {
            var ret = val.replace(/\s{2,}/g, " ").trim().split(" ");
            for (var i = 0; i < ret.length; i++ )
                ret[i] = parseInt(ret[i], 10);
            return ret;
        },

        onSelect: function(c, data) {
            if (data.preview)
                _.updatePreview(c, data);
            _.updateInputs(c, data);
        },

        updatePreview: function(c, data) {
            if (!data.api)
                return;
            if (parseInt(c.w, 10) > 0) {
                var rx = data.preview.width/c.w, ry = data.preview.height/c.h,
                    bounds = data.api.getBounds();

                data.preview.element.css({
                    width: Math.round( rx * bounds[0] ) + "px",
                    height: Math.round( ry * bounds[1] ) + "px",
                    marginLeft: "-" + Math.round(rx * c.x) + "px",
                    marginTop: "-" + Math.round(ry * c.y) + "px"
                });
            }
        },

        updateInputs: function(c, data) {
            if (c && c.w && parseInt(c.w, 10) > 0) {
                data.inputs.x1.attr("value", c.x);
                data.inputs.y1.attr("value", c.y);
                data.inputs.x2.attr("value", c.x2);
                data.inputs.y2.attr("value", c.y2);
                data.inputs.w.attr("value", c.w);
                data.inputs.h.attr("value", c.h);
            }
        }
    };

    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
