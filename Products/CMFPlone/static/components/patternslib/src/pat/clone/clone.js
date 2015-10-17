/* pat-clone */
define("pat-clone",[
    "jquery",
    "pat-parser",
    "pat-registry",
    "pat-base",
    "pat-logger"
], function($, Parser, registry, Base, logger) {
    "use strict";
    var log = logger.getLogger("pat-clone");
    var parser = new Parser("clone");
    parser.addArgument("max");
    parser.addArgument("template", ":first");
    parser.addArgument("trigger-element", ".add-clone");
    parser.addArgument("remove-element", ".remove-clone");
    parser.addArgument("remove-behaviour", "confirm", ["confirm", "none"]);
    parser.addArgument("remove-confirmation", "Are you sure you want to remove this element?");
    parser.addArgument("clone-element", ".clone");
    parser.addAlias("remove-behavior", "remove-behaviour");
    var TEXT_NODE = 3;

    return Base.extend({
        name: "clone",
        trigger: ".pat-clone",

        init: function patCloneInit($el, opts) {
            this.options = parser.parse(this.$el, opts);
            if (this.options.template.lastIndexOf(":", 0) === 0) {
                this.$template = this.$el.find(this.options.template);
            } else {
                this.$template = $(this.options.template);
            }
            $(document).on("click", this.options.triggerElement, this.clone.bind(this));

            var $clones = this.$el.find(this.options.cloneElement);
            this.num_clones = $clones.length;
            $clones.each(function (idx, clone) {
                var $clone = $(clone);
                $clone.find(this.options.remove.element).on("click", this.confirmRemoval.bind(this, $clone));
            }.bind(this));
        },

        clone: function clone() {
            if (this.num_clones >= this.options.max) {
                alert("Sorry, only "+this.options.max+" elements allowed.");
                return;
            }
            this.num_clones += 1;
            var $clone = this.$template.safeClone();
            var ids = ($clone.attr("id") || "").split(" ");
            $clone.removeAttr("id").removeClass("cant-touch-this");
            $.each(ids, function (idx, id) {
                // Re-add all ids that have the substring #{1} in them, while
                // also replacing that substring with the number of clones.
                if (id.indexOf("#{1}") !== -1) {
                    $clone.attr("id",
                        $clone.attr("id") ? $clone.attr("id") + " " : "" +
                            id.replace("#{1}", this.num_clones));
                }
            }.bind(this));

            $clone.appendTo(this.$el);
            $clone.children().addBack().contents().addBack().filter(this.incrementValues.bind(this));
            $clone.find(this.options.remove.element).on("click", this.confirmRemoval.bind(this, $clone));

            $clone.removeAttr("hidden");
            registry.scan($clone);

            $clone.trigger("pat-update", {'pattern':"clone", '$el': $clone});
            if (this.num_clones >= this.options.max) {
                $(this.options.triggerElement).hide();
            }
        },

        incrementValues: function incrementValues(idx, el) {
            var $el = $(el);
            $el.children().addBack().contents().filter(this.incrementValues.bind(this));
            var callback = function (idx, attr) {
                if (attr.name === "type" || !$el.attr(attr.name)) { return; }
                try {
                    $el.attr(attr.name, $el.attr(attr.name).replace("#{1}", this.num_clones));
                } catch (e) {
                    log.warn(e);
                }
            };
            if (el.nodeType !== TEXT_NODE) {
                $.each(el.attributes, callback.bind(this));
            } else if (el.data.length) {
                el.data = el.data.replace("#{1}", this.num_clones);
            }
        },

        confirmRemoval: function confirmRemoval($el, callback) {
            if (this.options.remove.behaviour === "confirm") {
                if (window.confirm(this.options.remove.confirmation) === true) {
                    this.remove($el);
                }
            } else {
                this.remove($el);
            }
        },

        remove: function remove($el) {
            $el.remove();
            this.num_clones -= 1;
            if (this.num_clones < this.options.max) {
                $(this.options.triggerElement).show();
            }
        }
    });
});
// vim: sw=4 expandtab
