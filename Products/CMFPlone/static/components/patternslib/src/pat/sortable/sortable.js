define([
    "jquery",
    "pat-base",
    "pat-parser"
], function($, Base, Parser) {
    var parser = new Parser("sortable");
    parser.addArgument("selector", "li");

    return Base.extend({
        name: "sortable",
        trigger: ".pat-sortable",

        init: function ($el) {
            this.$form = this.$el.closest('form');
            this.options = parser.parse(this.$el, true);
            this.recordPositions().addHandles().initScrolling();
            this.$el.on('pat-update', this.onPatternUpdate.bind(this));
        },

        onPatternUpdate: function (ev, data) {
            /* Handler which gets called when pat-update is triggered within
             * the .pat-sortable element.
             */
            if (data.pattern == "clone") {
                this.recordPositions();
                data.$el.on("dragstart", this.onDragStart.bind(this));
                data.$el.on("dragend", this.onDragEnd.bind(this));
            }
            return true;
        },

        recordPositions: function () {
            // use only direct descendants to support nested lists
            this.$sortables = this.$el.children().filter(this.options[0].selector);
            this.$sortables.each(function (idx, $el) {
                $(this).data('patterns.sortable', {'position': idx});
            });
            return this;
        },

        addHandles: function () {
            /* Add handles and make them draggable for HTML5 and IE8/9
             * it has to be an "a" tag (or img) to make it draggable in IE8/9
             */
            var $sortables_without_handles = this.$sortables.filter(function() {
                return $(this).find('.sortable-handle').length === 0;
            });
            var $handles = $("<a href=\"#\" class=\"sortable-handle\">⇕</a>").appendTo($sortables_without_handles);
            if("draggable" in document.createElement("span")) {
                $handles.attr("draggable", true);
            } else {
                $handles.on("selectstart", function(event) { event.preventDefault(); });
            }
            $handles.on("dragstart", this.onDragStart.bind(this));
            $handles.on("dragend", this.onDragEnd.bind(this));
            return this;
        },

        initScrolling: function () {
            // invisible scroll activation areas
            var scrollup = $("<div id=\"pat-scroll-up\">&nbsp;</div>"),
                scrolldn = $("<div id=\"pat-scroll-dn\">&nbsp;</div>"),
                scroll = $().add(scrollup).add(scrolldn);
            scrollup.css({ top: 0 });
            scrolldn.css({ bottom: 0 });
            scroll.css({
                position: "fixed", zIndex: 999999,
                height: 32, left: 0, right: 0
            });
            scroll.on("dragover", function(event) {
                event.preventDefault();
                if ($("html,body").is(":animated")) { return; }
                var newpos = $(window).scrollTop() + ($(this).attr("id")==="pat-scroll-up" ? -32 : 32);
                $("html,body").animate({scrollTop: newpos}, 50, "linear");
            });
            return this;
        },

        onDragEnd: function (ev) {
            $(".dragged").removeClass("dragged");
            this.$sortables.unbind(".pat-sortable");
            this.$el.unbind(".pat-sortable");
            $("#pat-scroll-up, #pat-scroll-dn").detach();
            this.submitChangedAmount($(ev.target).closest('.sortable'));
        },

        submitChangedAmount: function ($dragged) {
            /* If we are in a form, then submit the form with the right amount
             * that the sortable element was moved up or down.
             */
            var $amount_input = this.$form.find('.sortable-amount');
            if ($amount_input.length === 0) { return; }
            var old_position = $dragged.data('patterns.sortable').position;
            this.recordPositions();
            var new_position = $dragged.data('patterns.sortable').position;
            var change = Math.abs(new_position - old_position);
            var direction = new_position > old_position && 'down' || 'up';
            if (this.$form.length > 0) {
                $amount_input.val(change);
                if (direction == 'up') {
                    $dragged.find('.sortable-button-up').click();
                } else {
                    $dragged.find('.sortable-button-down').click();
                }
            }
        },

        onDragStart: function (event) {
            var $handle = $(event.target),
                $draggable = $handle.parent();

            // Firefox seems to need this set to any value
            event.originalEvent.dataTransfer.setData("Text", "");
            event.originalEvent.dataTransfer.effectAllowed = ["move"];
            if ("setDragImage" in event.originalEvent.dataTransfer) {
                event.originalEvent.dataTransfer.setDragImage($draggable[0], 0, 0);
            }
            $draggable.addClass("dragged");

            // Scroll the list if near the borders
            this.$el.on("dragover.pat-sortable", function(event) {
                event.preventDefault();
                if (this.$el.is(":animated")) return;

                var pos = event.originalEvent.clientY + $("body").scrollTop();

                if (pos - this.$el.offset().top < 32)
                    this.$el.animate({scrollTop: this.$el.scrollTop()-32}, 50, "linear");
                else if (this.$el.offset().top+this.$el.height() - pos < 32)
                    this.$el.animate({scrollTop: this.$el.scrollTop()+32}, 50, "linear");
            }.bind(this));

            // list elements are only drop targets when one element of the
            // list is being dragged. avoids dragging between lists.
            this.$sortables.on("dragover.pat-sortable", function(event) {
                var $this = $(this),
                    midlineY = $this.offset().top - $(document).scrollTop() + $this.height()/2;

                if ($(this).hasClass("dragged")) {
                    // bail if dropping on self
                    return;
                }
                $this.removeClass("drop-target-above drop-target-below");
                if (event.originalEvent.clientY > midlineY)
                    $this.addClass("drop-target-below");
                else
                    $this.addClass("drop-target-above");
                event.preventDefault();
            });

            this.$sortables.on("dragleave.pat-sortable", function() {
                this.$sortables.removeClass("drop-target-above drop-target-below");
            }.bind(this));

            this.$sortables.on("drop.pat-sortable", function(event) {
                var $sortable = $(this);
                if ($sortable.hasClass("dragged"))
                    return;

                if ($sortable.hasClass("drop-target-below"))
                    $sortable.after($(".dragged"));
                else
                    $sortable.before($(".dragged"));
                $sortable.removeClass("drop-target-above drop-target-below");
                event.preventDefault();
            });
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
