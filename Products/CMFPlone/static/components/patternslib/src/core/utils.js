define([
    "jquery"
], function($) {

    $.fn.safeClone = function () {
        var $clone = this.clone();
        // IE BUG : Placeholder text becomes actual value after deep clone on textarea
        // https://connect.microsoft.com/IE/feedback/details/781612/placeholder-text-becomes-actual-value-after-deep-clone-on-textarea
        if ($.browser.msie !== undefined && true) {
            $clone.findInclusive(':input[placeholder]').each(function(i, item) {
                var $item = $(item);
                if ($item.attr('placeholder') === $item.val()) {
                    $item.val('');
                }
            });
        }
        return $clone;
    };

    // Production steps of ECMA-262, Edition 5, 15.4.4.18
    // Reference: http://es5.github.io/#x15.4.4.18
    if (!Array.prototype.forEach) {
        Array.prototype.forEach = function(callback, thisArg) {
            var T, k;
            if (this === null) {
                throw new TypeError(' this is null or not defined');
            }
            // 1. Let O be the result of calling ToObject passing the |this| value as the argument.
            var O = Object(this);
            // 2. Let lenValue be the result of calling the Get internal method of O with the argument "length".
            // 3. Let len be ToUint32(lenValue).
            var len = O.length >>> 0;
            // 4. If IsCallable(callback) is false, throw a TypeError exception.
            // See: http://es5.github.com/#x9.11
            if (typeof callback !== "function") {
                throw new TypeError(callback + ' is not a function');
            }
            // 5. If thisArg was supplied, let T be thisArg; else let T be undefined.
            if (arguments.length > 1) {
                T = thisArg;
            }
            // 6. Let k be 0
            k = 0;
            // 7. Repeat, while k < len
            while (k < len) {
                var kValue;
                // a. Let Pk be ToString(k).
                //   This is implicit for LHS operands of the in operator
                // b. Let kPresent be the result of calling the HasProperty internal method of O with argument Pk.
                //   This step can be combined with c
                // c. If kPresent is true, then
                if (k in O) {
                    // i. Let kValue be the result of calling the Get internal method of O with argument Pk.
                    kValue = O[k];
                    // ii. Call the Call internal method of callback with T as the this value and
                    // argument list containing kValue, k, and O.
                    callback.call(T, kValue, k, O);
                }
                // d. Increase k by 1.
                k++;
            }
            // 8. return undefined
        };
    }

    var singleBoundJQueryPlugin = function (pattern, method, options) {
        /* This is a jQuery plugin for patterns which are invoked ONCE FOR EACH
         * matched element in the DOM.
         *
         * This is how the Mockup-type patterns behave. They are constructor
         * functions which need to be invoked once per jQuery-wrapped DOM node
         * for all DOM nodes on which the pattern applies.
         */
        var $this = this;
        $this.each(function() {
            var pat, $el = $(this);
            pat = pattern.init($el, options);
            if (method) {
                if (pat[method] === undefined) {
                    $.error("Method " + method +
                            " does not exist on jQuery." + pattern.name);
                    return false;
                }
                if (method.charAt(0) === '_') {
                    $.error("Method " + method +
                            " is private on jQuery." + pattern.name);
                    return false;
                }
                pat[method].apply(pat, [options]);
            }
        });
        return $this;
    };

    var pluralBoundJQueryPlugin = function (pattern, method, options) {
        /* This is a jQuery plugin for patterns which are invoked ONCE FOR ALL
         * matched elements in the DOM.
         *
         * This is how the vanilla Patternslib-type patterns behave. They are
         * simple objects with an init method and this method gets called once
         * with a list of jQuery-wrapped DOM nodes on which the pattern
         * applies.
         */
        var $this = this;
        if (method) {
            if (pattern[method]) {
                return pattern[method].apply($this, [$this].concat([options]));
            } else {
                $.error("Method " + method +
                        " does not exist on jQuery." + pattern.name);
            }
        } else {
            pattern.init.apply($this, [$this].concat([options]));
        }
        return $this;
    };

    var jqueryPlugin = function(pattern) {
        return function(method, options) {
            var $this = this;
            if ($this.length === 0) {
                return $this;
            }
            if (typeof method === 'object') {
                options = method;
                method = undefined;
            }
            if (typeof pattern === "function") {
                return singleBoundJQueryPlugin.call(this, pattern, method, options);
            } else {
                return pluralBoundJQueryPlugin.call(this, pattern, method, options);
            }
        };
    };

    //     Underscore.js 1.3.1
    //     (c) 2009-2012 Jeremy Ashkenas, DocumentCloud Inc.
    //     Underscore is freely distributable under the MIT license.
    //     Portions of Underscore are inspired or borrowed from Prototype,
    //     Oliver Steele's Functional, and John Resig's Micro-Templating.
    //     For all details and documentation:
    //     http://documentcloud.github.com/underscore
    //
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds.
    function debounce(func, wait) {
        var timeout;
        return function debounce_run() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Is a given variable an object?
    function isObject(obj) {
        var type = typeof obj;
        return type === 'function' || type === 'object' && !!obj;
    }

    // Extend a given object with all the properties in passed-in object(s).
    function extend(obj) {
        if (!isObject(obj)) return obj;
        var source, prop;
        for (var i = 1, length = arguments.length; i < length; i++) {
            source = arguments[i];
            for (prop in source) {
                if (hasOwnProperty.call(source, prop)) {
                    obj[prop] = source[prop];
                }
            }
        }
        return obj;
    }
    // END: Taken from Underscore.js until here.

    function rebaseURL(base, url) {
        if (url.indexOf("://")!==-1 || url[0]==="/")
            return url;
        return base.slice(0, base.lastIndexOf("/")+1) + url;
    }

    function findLabel(input) {
        var $label;
        for (var label=input.parentNode; label && label.nodeType!==11; label=label.parentNode) {
            if (label.tagName==="LABEL") {
                return label;
            }
        }
        if (input.id) {
            $label = $("label[for=\""+input.id+"\"]");
        }
        if ($label && $label.length===0 && input.form) {
            $label = $("label[for=\""+input.name+"\"]", input.form);
        }
        if ($label && $label.length) {
            return $label[0];
        } else {
            return null;
        }
    }

    // Taken from http://stackoverflow.com/questions/123999/how-to-tell-if-a-dom-element-is-visible-in-the-current-viewport
    function elementInViewport(el) {
       var rect = el.getBoundingClientRect(),
           docEl = document.documentElement,
           vWidth = window.innerWidth || docEl.clientWidth,
           vHeight = window.innerHeight || docEl.clientHeight;

        if (rect.right<0 || rect.bottom<0 || rect.left>vWidth || rect.top>vHeight)
            return false;
        return true;
    }

    // Taken from http://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex
    function escapeRegExp(str) {
        return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
    }

    function removeWildcardClass($targets, classes) {
        if (classes.indexOf("*")===-1)
            $targets.removeClass(classes);
        else {
            var matcher = classes.replace(/[\-\[\]{}()+?.,\\\^$|#\s]/g, "\\$&");
            matcher = matcher.replace(/[*]/g, ".*");
            matcher = new RegExp("^" + matcher + "$");
            $targets.filter("[class]").each(function() {
                var $this = $(this),
                    classes = $this.attr("class").split(/\s+/),
                    ok=[];
                for (var i=0; i<classes.length; i++)
                    if (!matcher.test(classes[i]))
                        ok.push(classes[i]);
                if (ok.length)
                    $this.attr("class", ok.join(" "));
                else
                    $this.removeAttr("class");
            });
        }
    }

    var transitions = {
        none: {hide: "hide", show: "show"},
        fade: {hide: "fadeOut", show: "fadeIn"},
        slide: {hide: "slideUp", show: "slideDown"}
    };

    function hideOrShow($slave, visible, options, pattern_name) {
        var duration = (options.transition==="css" || options.transition==="none") ? null : options.effect.duration;

        $slave.removeClass("visible hidden in-progress");
        var onComplete = function() {
            $slave
                .removeClass("in-progress")
                .addClass(visible ? "visible" : "hidden")
                .trigger("pat-update",
                        {pattern: pattern_name,
                         transition: "complete"});
        };
        if (!duration) {
            if (options.transition!=="css")
                $slave[visible ? "show" : "hide"]();
            onComplete();
        } else {
            var t = transitions[options.transition];
            $slave
                .addClass("in-progress")
                .trigger("pat-update",
                        {pattern: pattern_name,
                         transition: "start"});
            $slave[visible ? t.show : t.hide]({
                duration: duration,
                easing: options.effect.easing,
                complete: onComplete
            });
        }
    }

    function addURLQueryParameter(fullURL, param, value) {
        /* Using a positive lookahead (?=\=) to find the given parameter,
         * preceded by a ? or &, and followed by a = with a value after
         * than (using a non-greedy selector) and then followed by
         * a & or the end of the string.
         *
         * Taken from http://stackoverflow.com/questions/7640270/adding-modify-query-string-get-variables-in-a-url-with-javascript
         */
        var val = new RegExp('(\\?|\\&)' + param + '=.*?(?=(&|$))'),
            parts = fullURL.toString().split('#'),
            url = parts[0],
            hash = parts[1],
            qstring = /\?.+$/,
            newURL = url;
        // Check if the parameter exists
        if (val.test(url)) {
            // if it does, replace it, using the captured group
            // to determine & or ? at the beginning
            newURL = url.replace(val, '$1' + param + '=' + value);
        } else if (qstring.test(url)) {
            // otherwise, if there is a query string at all
            // add the param to the end of it
            newURL = url + '&' + param + '=' + value;
        } else {
            // if there's no query string, add one
            newURL = url + '?' + param + '=' + value;
        }
        if (hash) { newURL += '#' + hash; }
        return newURL;
    }

    var utils = {
        // pattern pimping - own module?
        jqueryPlugin: jqueryPlugin,
        debounce: debounce,
        escapeRegExp: escapeRegExp,
        isObject: isObject,
        extend: extend,
        rebaseURL: rebaseURL,
        findLabel: findLabel,
        elementInViewport: elementInViewport,
        removeWildcardClass: removeWildcardClass,
        hideOrShow: hideOrShow,
        addURLQueryParameter: addURLQueryParameter
    };
    return utils;
});
