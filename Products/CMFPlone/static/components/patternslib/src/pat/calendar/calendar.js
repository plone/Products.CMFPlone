/**
 * Patterns calendar - Calendar with different views for patterns.
 *
 * Copyright 2013-2014 Marko Durkovic
 * Copyright 2014 Florian Friesdorf
 * Copyright 2014 Syslab.com GmbH
 */
define([
    "jquery",
    "pat-logger",
    "pat-parser",
    "pat-store",
    "pat-utils",
    "pat-registry",
    "pat-calendar-moment-timezone-data",
    "jquery.fullcalendar.dnd",
    "jquery.fullcalendar"
], function($, logger, Parser, store, utils, registry) {
    "use strict";
    var log = logger.getLogger("calendar"),
        parser = new Parser("calendar");

    parser.addArgument("calendar-controls", ""); // Calendar controls must have "id" attr set
    parser.addArgument("category-controls", "");
    parser.addArgument("column-day", "dddd M/d");
    parser.addArgument("column-month", "ddd");
    parser.addArgument("column-week", "ddd M/d");
    parser.addArgument("default-view", "month", ["month", "basicWeek", "basicDay", "agendaWeek", "agendaDay"]);
    parser.addArgument("drag-and-drop", true, [true, false]);
    parser.addArgument("drop-external-events", true, [true, false]);
    parser.addArgument("external-event-selector", "");
    parser.addArgument("first-day", "0");
    parser.addArgument("first-hour", "6");
    parser.addArgument("height", "auto");
    parser.addArgument("ignore-url", false);
    parser.addArgument("start-date");
    parser.addArgument("store", "none", ["none", "session", "local"]);
    parser.addArgument("time-format", "h(:mm)t");
    parser.addArgument("title-day", "dddd, MMM d, YYYY");
    parser.addArgument("title-month", "MMMM YYYY");
    parser.addArgument("title-week", "MMM D YYYY");

    var calendar = {
        name: "calendar",
        trigger: ".pat-calendar",
        classMap: {
            month: ".view-month",
            agendaWeek: ".view-week",
            agendaDay: ".view-day"
        },
        dayNames: [ "su", "mo", "tu", "we", "th", "fr", "sa" ],

        _parseSearchString: function() {
            var context = {};
            window.location.search.substr(1).split("&").forEach(function(str) {
                if (str) {
                    var keyValue = str.split("="),
                        key = keyValue[0],
                        value = decodeURIComponent(keyValue[1]);
                    if (value && (value.match(/^\[.*\]$/) ||
                                  value.match(/^\{.*\}$/))) {
                        context[key] = JSON.parse(value);
                    } else {
                        context[key] = value;
                    }
                }
            });
            return context;
        },

        init: function($elem, opts) {
            opts = opts || {};
            var $el = $elem,
                cfg = store.updateOptions($el[0], parser.parse($el)),
                storage = cfg.store === "none" ? null : store[cfg.store](this.name + $el[0].id);
            this.$el = $el;
            this.cfg = cfg;
            this.storage = storage;
            cfg.defaultDate = storage.get("date") || cfg.defaultDate;
            cfg.defaultView = storage.get("view") || cfg.defaultView;
            cfg.tooltipConfig = $el.data("patCalendarTooltip");
            if (cfg.tooltipConfig) {
                var match = cfg.tooltipConfig.match(/url:[ ](.*?)(;|$)/);
                cfg.tooltipConfig = cfg.tooltipConfig.replace(match[0], "");
                cfg.newEventURL = match[1];
            }

            if (cfg.externalEventSelector) {
                $(cfg.externalEventSelector).draggable({
                    zIndex: 200,
                    helper: "clone",
                    appendTo: "body"
                });
            }

            if (!opts.ignoreUrl) {
                var search = calendar._parseSearchString();
                if (search["default-date"]) {
                    cfg.defaultDate = search["default-date"];
                }
                if (search["default-view"]) {
                    cfg.defaultView = search["default-view"];
                }
            }

            var calOpts = {
                axisFormat: cfg.timeFormat,
                columnFormat: cfg.column,
                defaultDate: cfg.defaultDate,
                defaultView: cfg.defaultView,
                droppable: cfg.dropExternalEvents,  // Enable dropping of external elements (i.e. not events)
                editable: cfg.dragAndDrop,          // Enable drag&drop and drag2resize of events
                dropAccept: cfg.externalEventSelector,
                firstDay: (this.dayNames.indexOf(cfg.first.day) >= 0) ? this.dayNames.indexOf(cfg.first.day) : undefined,
                firstHour: cfg.first.hour,
                header: false,
                height: cfg.height !== "auto" ? cfg.height : undefined,
                timeFormat: cfg.timeFormat,
                titleFormat: cfg.title,
                viewRender: calendar.highlightButtons,

                // Callback functions
                // ------------------
                drop: this._externalEventDropped,
                eventDrop: this._changeEventDates,
                eventResize: this._changeEventDates,
                events: function(start, end, timezone, callback) {
                    var events = calendar.parseEvents($el, timezone);
                    callback(events);
                },
                eventAfterRender: function(ev, $event) {
                    if (ev.id !== "pat-calendar-new-event") {
                        return;
                    }
                    /* Take the data from data-pat-calendar-tooltip to
                     * configure a tooltip trigger element.
                     */
                    if (!cfg.tooltipOpen) {
                        cfg.tooltipOpen = true;
                        var url = utils.addURLQueryParameter(cfg.newEventURL, "date", ev.start.format());
                        registry.scan($event.addClass("pat-tooltip").attr({"data-pat-tooltip": cfg.tooltipConfig}).attr({"href": url}));
                        $event.trigger("click.tooltip");
                        $event.on("pat-update", function (event, data) {
                            if (data.pattern === "tooltip" && data.hidden === true) {
                                event.stopPropagation();
                                if ($(this).is(":visible")) {
                                    $el.fullCalendar("removeEvents", ev.id);
                                    cfg.tooltipOpen = false;
                                }
                            }
                        });
                    }
                },
                dayClick: function (moment, ev, view) {
                    /* If "data-pat-calendar-tooltip" was configured, we open
                     * a tooltip when the user clicks on an day in the
                     * calendar.
                     */
                    if (!(cfg.tooltipConfig && cfg.newEventURL)) {
                        return;
                    }
                    var end;
                    if (view.name !== "month") {
                        end = moment.clone().add("minutes", 30);
                    } else {
                        end = undefined;
                    }
                    var id = "pat-calendar-new-event";
                    $el.fullCalendar("removeEvents", id);
                    cfg.tooltipOpen = false;
                    $el.fullCalendar("renderEvent", {
                        title: "New Event",
                        start: moment,
                        end: end,
                        id: id
                    });
                }
            };

            $el.categories = $el.find(".cal-events .cal-event")
                .map(function() {
                    return this.className.split(" ").filter(function(cls) {
                        return (/^cal-cat/).test(cls);
                    });
                });
            this._registerEventRefetchers($el);
            this._registerCategoryControls($el);
            var $controlRoot = cfg.calendarControls ? $(cfg.calendarControls) : $el;
            $el.$controlRoot = $controlRoot;
            cfg.timezone = calOpts.timezone = $controlRoot.find("select.timezone").val();
            $el.fullCalendar(calOpts);
            $el.find(".fc-content").appendTo($el); // move to end of $el
            this._registerRedrawHandlers();
            $el.find(".cal-title").text($el.fullCalendar("getView").title);
            $el.$controlRoot.find(this.classMap[calOpts.defaultView]).addClass("active");
            calendar._registerCalendarControls($el);
            $el.find(".cal-events").css("display", "none");
            this._restoreCalendarControls();
        },

        _addNewEvent: function($el, $event, data) {
            /* Add a new event to the list of events parsed by fullcalendar.
             * Used when dropping a foreign element.
             */
            // FIXME: this code is makes too much assumptions of the structure
            // of the dropped element. Needs to be made more generic, together
            // with parseEvents.
            var $events = $el.find(".cal-events");
            var $details = $event.find("ul.details");
            $details.append($("<li>").append($("<time>").addClass("start").attr("datetime", data.start).text(data.start)));
            $details.append($("<li>").append($("<time>").addClass("end").attr("datetime", data.end).text(data.end)));
            if (data.allDay === true) { $event.addClass("all-day"); }
            $events.append($event);
        },

        _externalEventDropped: function (moment, ev, obj, view) {
            var $event = $(this),
                url = $event.find("a").addBack("a").attr("href"),
                data = {
                    "start": moment.format(),
                    "pat-calendar-event-drop": true
                };
            if (view.name === "month") {
                data.end = moment.clone().format();
                data.allDay = true;
            } else {
                data.end = moment.clone().add("minutes", 30).format();
                data.allDay = false;
            }
            calendar._addNewEvent(calendar.$el, $event, data);
            calendar._refetchEvents(calendar.$el);
            $.getJSON(url, data);
        },

        _changeEventDates: function(evt) {
            /* Called when an event's dates have changed due to a drag&drop or
             * drag&resize action.
             */
            var $event = calendar.findEventByURL(calendar.$el, evt.url),
                regex = /\+[0-9]{2}:[0-9]{2}$/,
                match = evt.start.clone().tz(calendar.cfg.timezone).format().match(regex),
                data = {
                    "allDay": evt.allDay,
                    "pat-calendar-event-drop": true,
                    "start": evt.start.format()
                };
            if (evt.allDay === true) {
                // XXX: In fullcalendar 2 the end-date is no longer inclusive,
                // so we substract a day here.
                data.end = ((evt.end === null) ? evt.start.clone() : evt.end.clone().subtract("days", 1)).format();
            } else {
                data.end = ((evt.end === null) ? evt.start.clone().add("minutes", 30) : evt.end).format();
            }
            var tzstr = (match && match.length > 0) ? match[0] : "";
            var startstr = data.start + tzstr;
            var endstr = data.end + tzstr;
            $event.find("time.start").attr("datetime", startstr).text(startstr);
            $event.find("time.end").attr("datetime", endstr).text(endstr);
            $.getJSON(evt.url, data);
        },

        _refetchEvents: function($el) {
            $el.fullCalendar("refetchEvents");
        },

        _redrawCalendar: function() {
            this.$el.fullCalendar("option", "height", this.$el.find(".fc-content").height());
        },

        _registerRedrawHandlers: function() {
            if (calendar.cfg.height === "auto") {
                calendar._redrawCalendar();

                $(window).on("resize.pat-calendar", function(ev) {
                    if ($(ev.target).hasClass("fc-event")) {
                        // Don't do anything if the element being resized is a
                        // calendar event.
                        // Otherwise drag2resize breaks.
                        return;
                    }
                    calendar.$el.fullCalendar("option", "height", calendar.$el.find(".fc-content").height());
                });
                $(document).on("pat-update.pat-calendar", function(ev, data) {
                    if (data.pattern !== "validate") {
                        setTimeout(function() {
                            calendar.$el.fullCalendar("option", "height", calendar.$el.find(".fc-content").height());
                        }, 300);
                    }
                });
            }
        },

        _registerEventRefetchers: function($el) {
            /* Register handlers for those IO events that necessitate a refetching
             * of the calendar's event objects.
             */
            $el.on("keyup.pat-calendar", ".filter .search-text",
                   utils.debounce(calendar._refetchEvents.bind(calendar, $el), 400));
            $el.on("click.pat-calendar", ".filter .search-text[type=search]",
                   utils.debounce(calendar._refetchEvents.bind(calendar, $el), 400));
            $el.on("change.pat-calendar", ".filter select[name=state]",
                   calendar._refetchEvents.bind(calendar, $el));
            $el.on("change.pat-calendar", ".filter .check-list",
                   calendar._refetchEvents.bind(calendar, $el));
        },

        _registerCategoryControls: function($el) {
            /* The "category controls" are checkboxes that cause different
             * types of events to be shown or hidden.
             *
             * Configured via the "category-controls" parser argument.
             *
             * Events will be refetched.
             */
            var $categoryRoot = calendar.cfg.categoryControls ?
                    $(calendar.cfg.categoryControls) : $el;
            $el.$catControls = $categoryRoot.find("input[type=checkbox]");
            $el.$catControls.on("change.pat-calendar", function() {
                if (this.id) {
                    calendar.storage.set(this.id, this.checked);
                }
                calendar._refetchEvents($el);
             });
        },

        _registerCalendarControls: function($el) {
            /* Register handlers for the calendar control elements.
             *
             * Configured via the "calendar-controls" parser argument.
             */
            $el.$controlRoot.on("click.pat-calendar", ".jump-next", function() {
                $el.fullCalendar("next");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("click.pat-calendar", ".jump-prev", function() {
                $el.fullCalendar("prev");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("click.pat-calendar", ".jump-today", function() {
                $el.fullCalendar("today");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("click.pat-calendar", ".view-month", function() {
                $el.fullCalendar("changeView", "month");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("click.pat-calendar", ".view-week", function() {
                $el.fullCalendar("changeView", "agendaWeek");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("click.pat-calendar", ".view-day", function() {
                $el.fullCalendar("changeView", "agendaDay");
                calendar._viewChanged($el);
            });
            $el.$controlRoot.on("change.pat-calendar", "select.timezone", function() {
                calendar.destroy($el);
                calendar.init($el, {ignoreUrl: true});
            });
        },

        destroy: function($el) {
            $el.off(".pat-calendar");
            $el.$catControls.off(".pat-calendar");
            $el.$controlRoot.off(".pat-calendar");
            $(window).off(".pat-calendar");
            $(document).off(".pat-calendar");
            $(".cal-events .cal-event").off(".pat-calendar");
            $el.fullCalendar("destroy");
        },

        _viewChanged: function($el) {
            // update title
            var $title = $el.find(".cal-title");
            $title.html($el.fullCalendar("getView").title);
            // adjust height
            if (calendar.cfg.height === "auto") {
                $el.fullCalendar("option", "height",
                                 $el.find(".fc-content").height());
            }
            // store current date and view
            var date = $el.fullCalendar("getDate").format(),
                view = $el.fullCalendar("getView").name;
            calendar.storage.set("date", date);
            calendar.storage.set("view", view);
        },

        highlightButtons: function(view, element) {
            var $el = element.parents(".pat-calendar").first(),
                $body = element.parents("body").first(),
                $today = $el.find(".jump-today");
            $today.removeClass("active");
            if (view.name === "agendaDay") {
                var calDate = $el.fullCalendar("getDate"),
                    today = $.fullCalendar.moment();
                if (calDate.date() === today.date() &&
                    calDate.month() === today.month() &&
                    calDate.year() === today.year()) {
                    $today.addClass("active");
                }
            }
            $body.find(".view-month").removeClass("active");
            $body.find(".view-week").removeClass("active");
            $body.find(".view-day").removeClass("active");
            $body.find(calendar.classMap[view.name]).addClass("active");
        },

        findEventByURL: function($el, url) {
            var regex = new RegExp("^"+url+"$");
            return $el.find(".cal-events .cal-event").filter(function() {
                return regex.test($(this).find("a").attr("href"));
            });
        },

        _restoreCalendarControls: function () {
            /* Restore values of the calendar controls as stored in
             * localStorage.
             */
            var calKeys = calendar.storage._allKeys();
            calendar.$el.$catControls.each(function() {
                if (!this.id) {
                    return;
                }
                if (calKeys.indexOf(calendar.storage.prefix + ":" + this.id) !== -1) {
                    if (calendar.storage.get(this.id) === false) {
                        $(this).prop("checked", false).trigger("change");
                        $(this).parent().removeClass("checked");
                        $(this).parent().addClass("unchecked");
                    } else {
                        $(this).prop("checked", true).trigger("change");
                        $(this).parent().removeClass("unchecked");
                        $(this).parent().addClass("checked");
                    }
                }
            });
        },

        parseEvents: function($el, timezone) {
            var $events = $el.find(".cal-events"),
                $filter = $el.find(".filter"),
                searchText,
                regex;

            // parse filters
            if ($filter && $filter.length > 0) {
                searchText = $(".search-text", $filter).val();
                regex = new RegExp(searchText, "i");
            }
            var shownCats = $el.categories.filter(function() {
                var cat = this;
                return $el.$catControls.filter(function() {
                    return this.checked &&
                        $(this)
                            .parents()
                            .andSelf()
                            .hasClass(cat);
                }).length;
            });

            var events = $events.find(".cal-event").filter(function() {
                var $event = $(this);
                if (searchText && !regex.test($event.find(".title").text())) {
                    log.debug("remove due to search-text="+searchText, $event);
                    return false;
                }
                return shownCats.filter(function() {
                    return $event.hasClass(this);
                }).length;
            }).map(function(idx, event) {
                var attr, i;
                // classNames: all event classes without "event" + anchor classes
                var classNames = $(event).attr("class").split(/\s+/)
                    .filter(function(cls) { return (cls !== "cal-event"); })
                    .concat($("a", event).attr("class").split(/\s+/));
                // attrs: all "data-" attrs from anchor
                var allattrs = $("a", event)[0].attributes,
                    attrs = {};
                for (attr, i=0; i<allattrs.length; i++){
                    attr = allattrs.item(i);
                    if (attr.nodeName.slice(0,5) === "data-") {
                        attrs[attr.nodeName] = attr.nodeValue;
                    }
                }

                var location = ($(".location", event).html() || "").trim();
                var startstr = $(".start", event).attr("datetime"),
                    endstr = $(".end", event).attr("datetime"),
                    start = $.fullCalendar.moment.parseZone(startstr),
                    end = $.fullCalendar.moment.parseZone(endstr),
                    allday = $(event).hasClass("all-day");

                if (allday) {
                    // XXX: In fullcalendar 2 the end-date is no longer inclusive, but
                    // it should be. We fix that by adding a day so that the
                    // pat-calendar API stays the same and stays intuitive.
                    end.add("days", 1);
                }
                if (timezone) {
                    start = start.tz(timezone);
                    end = end.tz(timezone);
                }
                var ev = {
                    title: $(".title", event).text().trim() +
                        (location ? (" (" + location + ")") : ""),
                    start: start.format(),
                    end: end.format(),
                    allDay: allday,
                    url: $("a", event).attr("href"),
                    className: classNames,
                    attrs: attrs,
                    editable: $(event).hasClass("editable")
                };
                if (!ev.title) {
                    log.error("No event title for:", event);
                }
                if (!ev.start) {
                    log.error("No event start for:", event);
                }
                if (!ev.url) {
                    log.error("No event url for:", event);
                }
                return ev;
            }).toArray();
            return events;
        }
    };
    registry.register(calendar);
    return calendar;
});
// jshint indent: 4, browser: true, jquery: true, quotmark: double
