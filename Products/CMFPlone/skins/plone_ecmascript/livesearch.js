/*
    Live (interactive) full text search, wired to search gadget.

    Provides global: livesearch
*/

/*jslint nomen:false */

var livesearch = (function () {

    // Delay in milliseconds until the search starts after the last key was
    // pressed. This keeps the number of requests to the server low.
    var _search_delay = 400,
        // Delay in milliseconds until the results window closes after the
        // searchbox looses focus.
        _hide_delay = 400,

        // stores information for each searchbox on the page
        _search_handlers = {},

        // constants for better compression
        _LSHighlight = "LSHighlight";

    function _searchfactory($form, $inputnode) {
        // returns the search functions in a dictionary.
        // we need a factory to get a local scope for the event, this is
        // necessary, because IE doesn't have a way to get the target of
        // an event in a way we need it.
        var $lastsearch = null,
            $request = null,
            $cache = {},
            $querytarget = $form.attr('action').replace(/search$/g,"") + "livesearch_reply",
            $$result = $form.find('div.LSResult'),
            $shadow = $form.find('div.LSShadow'),
            $path = $form.find('input[name=path]');

        function _hide() {
            // hides the result window
            $$result.hide();
            $lastsearch = null;
        }

        function _hide_delayed() {
            // hides the result window after a short delay
            window.setTimeout(
                'livesearch.hide("' + $form.attr('id') + '")',
                _hide_delay);
        }

        function _show($data) {
            // shows the result
            $$result.show();
            $shadow.html($data);
        }

        function _search() {
            // does the actual search
            if ($lastsearch === $inputnode.value) {
                // do nothing if the input didn't change
                return;
            }
            $lastsearch = $inputnode.value;

            if ($request && $request.readyState < 4) {
                // abort any pending request
                $request.abort();
            }

            // Do nothing as long as we have less then two characters -
            // the search results makes no sense, and it's harder on the server.
            if ($inputnode.value.length < 2) {
                _hide();
                return;
            }

            var $$query = { q: $inputnode.value };
            if ($path.length && $path[0].checked) {
                $$query.path = $path.val();
            }
            // turn into a string for use as a cache key
            $$query = jQuery.param($$query);

            // check cache
            if ($cache[$$query]) {
                _show($cache[$$query]);
                return;
            }

            // the search request (retrieve as text, not a document)
            $request = jQuery.get($querytarget, $$query, function($data) {
                // show results if there are any and cache them
                _show($data);
                $cache[$$query] = $data;
            }, 'text');
        }

        function _search_delayed() {
            // search after a small delay, used by onfocus
            window.setTimeout(
                'livesearch.search("' + $form.attr('id') + '")',
                _search_delay);
        }

        return {
            hide: _hide,
            hide_delayed: _hide_delayed,
            search: _search,
            search_delayed: _search_delayed
        };
    }

    function _keyhandlerfactory($form) {
        // returns the key event handler functions in a dictionary.
        // we need a factory to get a local scope for the event, this is
        // necessary, because IE doesn't have a way to get the target of
        // an event in a way we need it.
        var $timeout = null,
            $$result = $form.find('div.LSResult'),
            $shadow = $form.find('div.LSShadow');

        function _keyUp() {
            // select the previous element
            var $cur = $shadow.find('li.LSHighlight').removeClass(_LSHighlight),
                $prev = $cur.prev('li');

            if (!$prev.length) {
                $prev = $shadow.find('li:last');
            }
            $prev.addClass(_LSHighlight);
            return false;
        }

        function _keyDown() {
            // select the next element
            var $cur = $shadow.find('li.LSHighlight').removeClass(_LSHighlight),
                $next = $cur.next('li');

            if (!$next.length) {$next = $shadow.find('li:first');}
            $next.addClass(_LSHighlight);
            return false;
        }

        function _keyEscape() {
            // hide results window
            $shadow.find('li.LSHighlight').removeClass(_LSHighlight);
            $$result.hide();
        }

        function _handler($event) {
            // dispatch to specific functions and handle the search timer
            window.clearTimeout($timeout);
            switch ($event.keyCode) {
                case 38: return _keyUp();
                case 40: return _keyDown();
                case 27: return _keyEscape();
                case 37: break; // keyLeft
                case 39: break; // keyRight
                default:
                    $timeout = window.setTimeout(
                        'livesearch.search("' + $form.attr('id') + '")',
                        _search_delay);
            }
        }

        function _submit() {
            // check whether a search result was selected with the keyboard
            // and open it
            var $target = $shadow.find('li.LSHighlight a').attr('href');
            if (!$target) {return;}
            window.location = $target;
            return false;
        }

        return {
            handler: _handler,
            submit: _submit
        };
    }

    function _setup(i) {
        // add an id which is used by other functions to find the correct node
        var $id = 'livesearch' + i,
            $form = jQuery(this).parents('form:first'),
            $key_handler = _keyhandlerfactory($form);

        _search_handlers[$id] = _searchfactory($form, this);

        $form.attr('id', $id).submit($key_handler.submit);
        jQuery(this).attr('autocomplete','off')
               .keydown($key_handler.handler)
               .focus(_search_handlers[$id].search_delayed)
               .blur(_search_handlers[$id].hide_delayed);
    }

    jQuery(function() {
        // find all search fields and set them up
        jQuery("#searchGadget,input.portlet-search-gadget").each(_setup);
    });

    return {
        search: function(id) {
            _search_handlers[id].search();
        },
        hide: function(id) {
            _search_handlers[id].hide();
        }
    };
}());
