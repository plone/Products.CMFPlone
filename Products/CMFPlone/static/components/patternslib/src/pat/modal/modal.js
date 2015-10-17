define([
    "jquery",
    "pat-parser",
    "pat-registry",
    "pat-base",
    "pat-utils",
    "pat-inject"
], function($, Parser, registry, Base, utils, inject) {
    var parser = new Parser("modal");
    parser.addArgument("class");
    parser.addArgument("closing", ["close-button"], ["close-button", "outside"], true);

    return Base.extend({
        name: "modal",
        jquery_plugin: true,
        // div's are turned into modals
        // links, forms and subforms inject modals
        trigger: "div.pat-modal, a.pat-modal, form.pat-modal, .pat-modal.pat-subform",
        init: function ($el, opts, trigger) {
            this.options = parser.parse(this.$el, opts);
            if (trigger && trigger.type === "injection")
                $.extend(this.options, parser.parse($(trigger.element), {}, false, false));
            if (this.$el.is("div")) {
                this._init_div1();
            } else {
                this._init_inject1();
            }
        },

        _init_inject1: function () {
            var opts = {
                target: "#pat-modal",
                "class": "pat-modal" + (this.options["class"] ? " " + this.options["class"] : "")
            };
            // if $el is already inside a modal, do not detach #pat-modal,
            // because this would unnecessarily close the modal itself
            if (!this.$el.closest("#pat-modal")) {
                $("#pat-modal").detach();
            }

            this.$el.on("pat-inject-missingSource pat-inject-missingTarget", function() {
                $("#pat-modal").detach();
            });

            inject.init(this.$el, opts);
        },

        _init_div1: function () {
            var $header = $("<div class='header' />"),
                activeElement = document.activeElement;

            if (this.options.closing.indexOf("close-button")!==-1)
                $("<button type='button' class='close-panel'>Close</button>").appendTo($header);

            // We cannot handle text nodes here
            this.$el.children(":last, :not(:first)")
                .wrapAll("<div class='panel-content' />");
            $(".panel-content", this.$el).before($header);
            this.$el.children(":first:not(.header)").prependTo($header);

            // Restore focus in case the active element was a child of $el and
            // the focus was lost during the wrapping.
            activeElement.focus();
            this._init_handlers();
            this.resize();
            this.setPosition();
        },

        _init_handlers: function() {
            var $el = this.$el;
            $(document).on("click.pat-modal", ".close-panel", this.destroy.bind(this));
            $(document).on("keyup.pat-modal", this._onKeyUp.bind(this));
            if (this.options.closing.indexOf("outside")!==-1)
                $(document).on("click.pat-modal", this._onPossibleOutsideClick.bind(this));

            $(window).on("resize.pat-modal-position",
                utils.debounce(this.resize.bind(this), 400));
            $(document).on("pat-inject-content-loaded.pat-modal-position", "#pat-modal",
                utils.debounce(this.resize.bind(this), 400));
            $(document).on("patterns-injected.pat-modal-position", "#pat-modal,div.pat-modal",
                utils.debounce(this.resize.bind(this), 400));
            $(document).on("pat-update.pat-modal-position", "#pat-modal,div.pat-modal",
                utils.debounce(this.resize.bind(this), 50));
        },

        _onPossibleOutsideClick: function(ev) {
            if (this.$el.has(ev.target)) {
                this.destroy();
            }
        },

        _onKeyUp: function(ev) {
            if (ev.which === 27) {
                this.destroy();
            }
        },

        getTallestChild: function() {
            var $tallest_child;
            $("*", this.$el).each(function () {
                var $child = $(this);
                if (typeof $tallest_child === "undefined") {
                    $tallest_child = $child;
                } else if ($child.outerHeight(true) > $tallest_child.outerHeight(true)) {
                    $tallest_child = $child;
                }
            });
            return $tallest_child;
        },

        setPosition: function() {
            this.$el.css("top", ($(window).innerHeight() - this.$el.height())/2);
        },

        resize: function() {
            var modal_height = this.$el.outerHeight(true);
            var modal_padding = modal_height - this.$el.outerHeight();
            var max_height = $(window).innerHeight() - modal_padding;
            var $tallest_child = this.getTallestChild();
            var tallest_child_height = $tallest_child.outerHeight(true);

            if (tallest_child_height !== modal_height) {
                modal_height = tallest_child_height + modal_padding;
            }
            if (max_height < modal_height) {
                this.$el.addClass("max-height").css("height", max_height);
                this.setPosition();
            } else if (modal_height !== this.$el.height()) {
                this.$el.removeClass("max-height").css("height", modal_height);
                this.setPosition();
            } else {
                return;
            }
            // XXX: This is a hack. When you have a modal inside a
            // modal.max-height, the CSS of the outermost modal affects the
            // innermost .panel-body. By redrawing here, it's fixed.
            //
            // I think ideally the CSS needs to be fixed here, but I need to
            // discuss with Cornelis first.
            if (this.$el.parent().closest(".pat-modal").length > 0) {
                utils.redraw(this.$el.find(".panel-body"));
            }
        },

        destroy: function() {
            $(document).off(".pat-modal");
            this.$el.remove();
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
