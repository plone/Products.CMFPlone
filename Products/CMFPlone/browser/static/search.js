/* The following line defines global variables defined elsewhere. */
/*globals jQuery, portal_url, alert, history, window, location*/

jQuery(function ($) {

    var query, pushState, popped, initialURL,
        $default_res_container = $('#search-results'),
        $search_filter = $('#search-filter'),
        $search_field = $('#search-field'),
        $search_gadget =  $('#searchGadget'),
        $form_search_page = $("form.searchPage"),
        navigation_root_url = $('link[rel="home"]').attr('href') || window.navigation_root_url || window.portal_url;

    // The globally available method to pull the search results for the
    // 'query' into the element, on which the method is invoked
    $.fn.pullSearchResults = function (query) {
        return this.each(function () {
            var $container = $(this);
            $.get(
                '@@updated_search',
                query,
                function (data) {
                    $container.hide();
                    var $ajax_search_res = $('<div id="ajax-search-res"></div>').html(data),
                        $search_term = $('#search-term');

                    var $data_res = $ajax_search_res.find('#search-results').children(),
                        data_search_term = $ajax_search_res.find('#updated-search-term').text(),
                        data_res_number = $ajax_search_res.find('#updated-search-results-number').text(),
                        data_sorting_opt = $ajax_search_res.find('#updated-sorting-options').html(),
                        new_header = $ajax_search_res.find('#update-search-header');

                    $container.html($data_res);
                    $container.fadeIn();

                    if (!$search_term.length) {
                        // Until now we had queries with empty search term.
                        // we need to fetch the new header, with proper translations
                        if(new_header.length){
                            $('h1.documentFirstHeading').html(new_header.html());
                        }
                    } else {
                        $search_term.text(data_search_term);
                    }

                    $('#search-results-number').text(data_res_number);
                    $('#search-results-bar').find('#sorting-options').html(data_sorting_opt);

                    $('#rss-subscription').find('a.link-feed').attr('href', function () {
                        return navigation_root_url + '/search_rss?' + query;
                    });
                });
        });
    };

    pushState = function (query) {
        // Now we need to update the browser's path bar to reflect
        // the URL we are at now and to push a history state change
        // in the browser's history. 
        // API natively or it needs a polyfill, that provides
        // hash-change events to the older browser
        if (window.history && window.history.pushState){
            var url = navigation_root_url + '/@@search?' + query;
            history.pushState(null, null, url);
        }
    };

    // THE HANDLER FOR 'POPSTATE' EVENT IS COPIED FROM PJAX.JS
    // https://github.com/defunkt/jquery-pjax

    // Used to detect initial (useless) popstate.
    // If history.state exists, assume browser isn't going to fire initial popstate.
    popped = (window.history && 'state' in window.history);
    initialURL = location.href;


    // popstate handler takes care of the back and forward buttons
    //
    $(window).bind('popstate', function (event) {
        var initialPop, str;
        // Ignore initial popstate that some browsers fire on page load
        initialPop = !popped && location.href === initialURL;
        popped = true;
        if (initialPop) {
            return;
        }

        if (!location.search){
            return;
        }

        query = location.search.split('?')[1];
        // We need to make sure we update the search field with the search
        // term from previous query when going back in history
        var results = query.match(/SearchableText=[^&]*/);
        if (results){ // not all pages have results
            str = results[0];
            str = decodeURIComponent(str.replace(/\+/g, ' ')); // we remove '+' used between words
            // in search queries.

        // Now we have something like 'SearchableText=test' in str
        // variable. So, we know when the actual search term begins at
        // position 15 in that string.
        $.merge($search_field.find('input[name="SearchableText"]'), $search_gadget).val(str.substr(15, str.length));

            $default_res_container.pullSearchResults(query);
        }

    });

    $search_filter.find('input.searchPage[type="submit"]').hide();

    // We don't submit the whole form with all the fields when only the
    // search term is being changed. We just alter the current URL to
    // substitute the search term and make a new ajax call to get updated
    // results
    $search_field.find('input.searchButton').click(function (e) {
        var st, queryString = location.search.substring(1),
            re = /([^&=]+)=([^&]*)/g, m, queryParameters = [], key;
        st = $search_field.find('input[name="SearchableText"]').val();
        queryParameters.push({"name":"SearchableText", "value": st});

        // parse query string into array of hash
        while (m = re.exec(queryString)) {
            key = decodeURIComponent(m[1]);
            if (key !== 'SearchableText') {
                // we remove '+' used between words
                queryParameters.push({"name": key, "value": decodeURIComponent(m[2].replace(/\+/g, ' '))});
            }
        }
        queryString = $.param(queryParameters);
        $default_res_container.pullSearchResults(queryString);
        pushState(queryString);
        e.preventDefault();
    });
    $form_search_page.submit(function (e) {
        query = $(this).serialize();
        $default_res_container.pullSearchResults(query);
        pushState(query);
        e.preventDefault();
    });

    // We need to update the site-wide search field (at the top right in
    // stock Plone) when the main search field is updated
    $search_field.find('input[name="SearchableText"]').keyup(function () {
        $search_gadget.val($(this).val());
    });

    // When we click any option in the Filter menu, we need to prevent the
    // menu from being closed as it is dictated by dropdown.js for all
    // dl.actionMenu > dd.actionMenuContent
    $('#search-results-bar').find('dl.actionMenu > dd.actionMenuContent').click(function (e) {
        e.stopImmediatePropagation();
    });

    // Now we can handle the actual menu options and update the search
    // results after any of them has been chosen.
    $search_filter.delegate('input, select', 'change',
        function (e) {
            query = '';
            // only fill query when there is at least one type selected
            // by default we have a checked date radio input button
            if ($search_filter.find('input:checked').length > 1) {
                query = $form_search_page.serialize();
            }
            $default_res_container.pullSearchResults(query);
            pushState(query);
        }
    );

    // Since we replace the whole sorting options with HTML, coming in
    // AJAX response, we should bind the click event with delegate() in order
    // for this to keep working with the HTML elements, coming from AJAX
    // response
    $('#sorting-options').delegate('a', 'click', function (e) {
        if ($(this).attr('data-sort')) {
            $form_search_page.find("input[name='sort_on']").val($(this).attr('data-sort'));
        }
        else {
            $form_search_page.find("input[name='sort_on']").val('');
        }
        query = this.search.split('?')[1];
        $default_res_container.pullSearchResults(query);
        pushState(query);
        e.preventDefault();
    });

    // Handle clicks in the batch navigation bar. Load those with Ajax as
    // well.
    $default_res_container.delegate('.listingBar a', 'click', function (e) {
        query = this.search.split('?')[1];
        $default_res_container.pullSearchResults(query);
        pushState(query);
        e.preventDefault();
    });
});

